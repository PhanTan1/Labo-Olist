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
df = pd.read_csv('data/olist_products_dataset.csv')
df = df.where(pd.notnull(df), None)

# Create SQLAlchemy engine
engine = get_engine()

# Step 1: Create the table
with engine.begin() as conn:
    create_table_sql = """
DROP TABLE IF EXISTS customers;
CREATE TABLE customers (
    customer_id UUID,
    customer_unique_id UUID NOT NULL,
    customer_zip_code_prefix VARCHAR(5) NOT NULL,
    customer_city VARCHAR(32),
    customer_state VARCHAR(2),

    CONSTRAINT PK__customers PRIMARY KEY (customer_id),
    CONSTRAINT customer_zip_code_prefix_valid CHECK (customer_zip_code_prefix ~ '^\d{4,5}$'),
    CONSTRAINT customer_state_format CHECK (customer_state ~ '^[A-Z]{2}$')
);
"""
    conn.execute(text(create_table_sql))

# Step 2: Load CSV data
df = pd.read_csv('data/olist_customers_dataset.csv')
df = df.where(pd.notnull(df), None)

# Step 3: Insert row-by-row to catch errors
with engine.begin() as conn:
    for i, row in df.iterrows():
        try:
            pd.DataFrame([row]).to_sql('customers', conn, if_exists='append', index=False, method='multi')
        except (IntegrityError, DataError) as e:
            print(f"❌ Error at row {i}:")
            print(row.to_dict())
            print(f"Exception: {e.orig}")