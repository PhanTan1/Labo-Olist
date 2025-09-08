from db_config import get_engine
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
engine = get_engine()

# Step 1: Create the table
with engine.begin() as conn:
    create_table_sql = """
    DROP TABLE IF EXISTS orderItems;
CREATE TABLE orderItems (
    order_id UUID,
    order_item_id SMALLINT NOT NULL,
    product_id UUID NOT NULL,
    seller_id UUID NOT NULL,
    shipping_limit_date TIMESTAMP NOT NULL,
    price DECIMAL (8,2) NOT NULL,
    freight_value DECIMAL(8,2) NOT NULL,

    CONSTRAINT PK__orderItems PRIMARY KEY (order_id)
);
    """
    conn.execute(text(create_table_sql))

# Step 2: Load CSV data
df = pd.read_csv('data/olist_order_items_dataset.csv')
df = df.where(pd.notnull(df), None)

# Step 3: Insert row-by-row to catch errors
with engine.begin() as conn:
    for i, row in df.iterrows():
        try:
            pd.DataFrame([row]).to_sql('orderItems', conn, if_exists='append', index=False, method='multi')
        except (IntegrityError, DataError) as e:
            print(f"❌ Error at row {i}:")
            print(row.to_dict())
            print(f"Exception: {e.orig}")