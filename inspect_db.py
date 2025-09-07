
import os
from sqlalchemy import create_engine, inspect

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("DATABASE_URL environment variable not set.")
    exit(1)

db_url = db_url.replace("10.56.0.3", "127.0.0.1")

engine = create_engine(db_url)
inspector = inspect(engine)

try:
    schemas = inspector.get_schema_names()
    for schema in schemas:
        print(f"Schema: {schema}")
        tables = inspector.get_table_names(schema=schema)
        if not tables:
            print("  No tables found in this schema.")
            continue
        for table_name in tables:
            print(f"  Table: {table_name}")
            columns = inspector.get_columns(table_name, schema=schema)
            for column in columns:
                print(f"    - {column['name']}: {column['type']}")
except Exception as e:
    print(f"An error occurred: {e}")
