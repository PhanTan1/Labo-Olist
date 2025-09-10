from db_config import get_engine
from table_schemas import TABLES
from data_loader import create_table, load_csv_to_table
from post_load_tasks import generate_zip_code_reference, add_foreign_keys

engine = get_engine()

# Step 1: Create all base tables
for table_name, create_sql in TABLES.items():
    print(f"Creating table: {table_name}")
    create_table(engine, create_sql)

# Step 2: Load geolocation first
geo_path = "data/olist_geolocation_dataset.csv"
print(f"Loading data from: {geo_path}")
load_csv_to_table(geo_path, "geolocation", engine)

# Step 3: Generate zip_code_reference from geolocation
generate_zip_code_reference(engine)

# Step 4: Load all other tables except zip_code_reference
for table_name in TABLES:
    if table_name in ["geolocation", "zip_code_reference"]:
        continue
    csv_path = f"data/olist_{table_name}_dataset.csv"
    print(f"Loading data from: {csv_path}")
    load_csv_to_table(csv_path, table_name, engine)

# Step 5: Add foreign key constraints
add_foreign_keys(engine)

print("✅ All tables created, data loaded, and relationships established.")
