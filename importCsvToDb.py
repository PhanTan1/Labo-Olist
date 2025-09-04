from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError, DataError
import pandas as pd

# Database credentials
username = 'postgres'
password = 'password'
host = 'localhost'
port = '5432'
database = 'olist'

# Create SQLAlchemy engine
engine = create_engine(f'postgresql://{username}:{password}@{host}:{port}/{database}', echo=True)

# Step 1: Create the table
with engine.begin() as conn:
    create_table_sql = """
    DROP TABLE IF EXISTS orderReviews;

    CREATE TABLE orderReviews (
        review_id UUID,
        order_id UUID NOT NULL,
        review_score INT NOT NULL,
        review_comment_title VARCHAR (50),
        review_comment_message VARCHAR (255),
        review_creation_date TIMESTAMP NOT NULL,
        review_answer_timestamp TIMESTAMP NOT NULL,

    CONSTRAINT PK__orderReviews PRIMARY KEY (review_id),
    CONSTRAINT review_score CHECK (review_score BETWEEN 1 AND 5)
);
    """
    conn.execute(text(create_table_sql))

# Step 2: Load CSV data
df = pd.read_csv('data/olist_order_reviews_dataset.csv')
df = df.where(pd.notnull(df), None)

# Step 3: Insert row-by-row to catch errors
with engine.begin() as conn:
    for i, row in df.iterrows():
        try:
            pd.DataFrame([row]).to_sql('orderReviews', conn, if_exists='append', index=False, method='multi')
        except (IntegrityError, DataError) as e:
            print(f"❌ Error at row {i}:")
            print(row.to_dict())
            print(f"Exception: {e.orig}")