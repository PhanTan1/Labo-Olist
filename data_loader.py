import pandas as pd
import uuid
from sqlalchemy import text
from sqlalchemy.exc import DataError
from etl_helpers import ensure_zip_code_exists
from loggers import duplicate_logger, missing_zip_logger

# UUID formatter
def format_guid(value):
    try:
        return str(uuid.UUID(value))
    except (ValueError, TypeError):
        return None

# Tables that don’t need deduplication
FAST_LOAD_TABLES = ['geolocation']

# Primary key mapping
PK_COLUMNS = {
    'customers': ['customer_id'],
    'orders': ['order_id'],
    'order_items': ['order_item_id', 'order_id'],
    'order_payments': ['order_id', 'payment_sequential'],
    'order_reviews': ['review_id'],
    'products': ['product_id'],
    'sellers': ['seller_id']
}

def create_table(engine, create_sql):
    with engine.begin() as conn:
        conn.execute(text(create_sql))

def load_csv_to_table(csv_path, table_name, engine):
    df = pd.read_csv(csv_path)
    df = df.where(pd.notnull(df), None)

    # Log missing zip codes with full row context
    if table_name in ['customers', 'sellers']:
        zip_col = 'customer_zip_code_prefix' if table_name == 'customers' else 'seller_zip_code_prefix'
        if zip_col not in df.columns:
            duplicate_logger.warning(f"Expected zip column '{zip_col}' not found in '{table_name}'")
        else:
            for _, row in df.iterrows():
                zip_code = row.get(zip_col)
                if zip_code is not None:
                    ensure_zip_code_exists(engine, str(zip_code), row.to_dict())

    # Apply UUID formatting
    uuid_cols = {
        'customers': ['customer_id', 'customer_unique_id'],
        'orders': ['order_id', 'customer_id'],
        'order_items': ['order_id', 'product_id', 'seller_id'],
        'order_payments': ['order_id'],
        'order_reviews': ['review_id', 'order_id'],
        'products': ['product_id'],
        'sellers': ['seller_id']
    }
    for col in uuid_cols.get(table_name, []):
        if col in df.columns:
            df[col] = df[col].apply(format_guid)

    # Fast load for simple tables
    if table_name in FAST_LOAD_TABLES:
        df.to_sql(table_name, engine, if_exists='append', index=False)
        print(f"🚀 Fast-loaded {table_name} ({len(df)} rows).")
        duplicate_logger.info(f"Successfully loaded '{table_name}' with {len(df)} rows.")
        return

    # Drop duplicate keys
    pk = PK_COLUMNS.get(table_name)
    if pk:
        dupes = df[df.duplicated(subset=pk, keep='first')]
        if not dupes.empty:
            for _, row in dupes.iterrows():
                duplicate_logger.info(
                    f"Dropped duplicate from '{table_name}': {row.to_dict()}\n"
                    f"Exception: duplicate key value violates unique constraint \"pk__{table_name}\"\n"
                    f"DETAIL: Key ({pk[0]})=({row[pk[0]]}) already exists.\n"
                )
        df = df.drop_duplicates(subset=pk, keep='first')

    # Bulk insert
    try:
        df.to_sql(
            table_name,
            engine,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000
        )
        print(f"✅ Loaded {table_name} ({len(df)} rows).")
        duplicate_logger.info(f"Successfully loaded '{table_name}' with {len(df)} rows.")
    except DataError as err:
        duplicate_logger.error(f"DataError loading '{table_name}': {err}")
        raise
