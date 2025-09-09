from db_config import get_engine
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, DataError
import pandas as pd
import uuid
import logging

# Setup logging
logging.basicConfig(filename='duplicate_review_errors.log', level=logging.INFO, format='%(message)s')

engine = get_engine()

# Load CSV
df = pd.read_csv('data/olist_order_reviews_dataset.csv')
df = df.where(pd.notnull(df), None)

# Format UUIDs
def format_guid(value):
    try:
        return str(uuid.UUID(value))
    except (ValueError, TypeError):
        return None

df['review_id'] = df['review_id'].apply(format_guid)
df['order_id'] = df['order_id'].apply(format_guid)

# Insert row-by-row with isolated transactions
with engine.connect() as conn:
    for i, row in df.iterrows():
        try:
            with conn.begin_nested():  # Isolated savepoint
                pd.DataFrame([row]).to_sql(
                    'order_reviews',
                    conn,
                    if_exists='append',
                    index=False,
                    method='multi'
                )
        except IntegrityError as e:
            if 'duplicate key value violates unique constraint' in str(e.orig):
                logging.info(f"❌ Duplicate at row {i}: {row.to_dict()}")
                try:
                    with conn.begin_nested():
                        update_sql = text("""
                            UPDATE order_reviews
                            SET order_id = :order_id,
                                review_score = :review_score,
                                review_comment_title = :review_comment_title,
                                review_comment_message = :review_comment_message,
                                review_creation_date = :review_creation_date,
                                review_answer_timestamp = :review_answer_timestamp
                            WHERE review_id = :review_id
                        """)
                        conn.execute(update_sql, row.to_dict())
                except Exception as update_error:
                    logging.info(f"⚠️ Update failed at row {i}: {update_error}")
            else:
                logging.info(f"❌ Other error at row {i}: {e.orig}")
