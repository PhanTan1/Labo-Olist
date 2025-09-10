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

DROP TABLE IF EXISTS products;
CREATE TABLE products (
        product_id UUID,
        product_category_name VARCHAR (60),
        product_name_length VARCHAR (11),
        product_description_length SMALLINT,
        product_photos_qty SMALLINT,
        product_weight_g INT,
        product_length_cm SMALLINT,
        product_height_cm SMALLINT,
        product_width_cm SMALLINT,

        CONSTRAINT PK__products PRIMARY KEY (product_id),
        CONSTRAINT FK__products FOREIGN KEY (product_category_name) REFERENCES product_category_name_translation(product_category_name)

);
"""
    
    conn.execute(text(create_table_sql))

# Step 2: Load CSV data
df = pd.read_csv('data/olist_products_dataset.csv')
df = df.where(pd.notnull(df), None)

# Step 3: Insert row-by-row to catch errors
with engine.begin() as conn:
    for i, row in df.iterrows():
        try:
            pd.DataFrame([row]).to_sql('products', conn, if_exists='append', index=False, method='multi')
        except (IntegrityError, DataError) as e:
            print(f"❌ Error at row {i}:")
            print(row.to_dict())
            print(f"Exception: {e.orig}")