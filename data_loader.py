import pandas as pd
import uuid
import logging
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError, DataError

# Setup logging
logging.basicConfig(filename='duplicate_key_errors.log', level=logging.INFO, format='%(message)s')

def create_table(engine, create_sql):
    with engine.begin() as conn:
        conn.execute(text(create_sql))

def format_guid(value):
    try:
        return str(uuid.UUID(value))
    except (ValueError, TypeError):
        return None

def load_csv_to_table(csv_path, table_name, engine):
    df = pd.read_csv(csv_path)
    df = df.where(pd.notnull(df), None)

    # Format UUIDs for known tables
    uuid_columns = {
        'customers': ['customer_id', 'customer_unique_id'],
        'orders': ['order_id', 'customer_id'],
        'order_items': ['order_id', 'product_id', 'seller_id'],
        'order_payments': ['order_id'],
        'order_reviews': ['review_id', 'order_id'],
        'products': ['product_id'],
        'sellers': ['seller_id']
    }

    for col in uuid_columns.get(table_name, []):
        if col in df.columns:
            df[col] = df[col].apply(format_guid)

    with engine.connect() as conn:
        for i, row in df.iterrows():
            try:
                with conn.begin_nested():
                    pd.DataFrame([row]).to_sql(
                        table_name,
                        conn,
                        if_exists='append',
                        index=False,
                        method='multi'
                    )
            except IntegrityError as e:
                if 'duplicate key value violates unique constraint' in str(e.orig):
                    logging.info(f"❌ Duplicate at row {i} in '{table_name}': {row.to_dict()}")
                    try:
                        with conn.begin_nested():
                            update_sql = generate_update_sql(table_name, row)
                            conn.execute(update_sql, row.to_dict())
                    except Exception as update_error:
                        logging.info(f"⚠️ Update failed at row {i}: {update_error}")
                else:
                    logging.info(f"❌ Other error at row {i}: {e.orig}")

def generate_update_sql(table_name, row):
    # Define primary keys and updatable columns
    update_map = {
        'order_reviews': {
            'pk': 'review_id',
            'fields': [
                'order_id', 'review_score', 'review_comment_title',
                'review_comment_message', 'review_creation_date', 'review_answer_timestamp'
            ]
        },
        'customers': {
            'pk': 'customer_id',
            'fields': ['customer_unique_id', 'customer_zip_code_prefix', 'customer_city', 'customer_state']
        },
        # Add other tables as needed
    }

    if table_name not in update_map:
        raise ValueError(f"No update logic defined for table: {table_name}")

    pk = update_map[table_name]['pk']
    fields = update_map[table_name]['fields']
    set_clause = ",\n    ".join([f"{field} = :{field}" for field in fields])

    return text(f"""
        UPDATE {table_name}
        SET {set_clause}
        WHERE {pk} = :{pk}
    """)
