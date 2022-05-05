from sqlalchemy.sql import select
from sqlalchemy import create_engine, MetaData, Table

DB_USER = "musterpraxis_dwh"
DB_PASSWORD = "password"
DB_NAME = "musterpraxis_dwh"
DB_HOST = "127.0.0.0"
DB_PORT = 3306
DB_CONNSTRING = f"mariadb+mariadbconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DB_CONNSTRING, echo=True)
metadata = MetaData()
patients = Table('patient', metadata, autoload=True, autoload_with=engine)


with engine.connect() as conn:
    query = (select([patients.c.created, patients.c.lastName]).order_by(patients.c.created).limit(10))
    for row in conn.execute(query):
        print(row)

