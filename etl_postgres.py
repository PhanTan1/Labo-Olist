from airflow.decorators import dag, task
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine

SRC_DB_CONFIG = {
    'username': 'postgres',
    'password': 'password',
    'host': 'host.docker.internal',
    'port': '5432',
    'database': 'olist'
}

DST_DB_CONFIG = {
    'username': 'postgres',
    'password': 'password',
    'host': 'host.docker.internal',
    'port': '5432',
    'database': 'olist_DW'
}

def get_engine(db_config):
    url = f"postgresql://{db_config['username']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"
    return create_engine(url)

@task
def etl_vw_fact_order_to_fact_order():
    src_engine = get_engine(SRC_DB_CONFIG)
    dst_engine = get_engine(DST_DB_CONFIG)

    df = pd.read_sql("SELECT * FROM vw_fact_order", src_engine)
    df.to_sql("fact_order", dst_engine, if_exists="append", index=False)

@dag(
    start_date=datetime(2023, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["etl", "postgres"]
)
def etl_olist_to_dw():
    etl_vw_fact_order_to_fact_order()

dag_instance = etl_olist_to_dw()
