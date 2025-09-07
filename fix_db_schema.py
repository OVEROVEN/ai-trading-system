
import os
from sqlalchemy import create_engine, text

db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("DATABASE_URL environment variable not set.")
    exit(1)

db_url = db_url.replace("10.56.0.3", "127.0.0.1")

engine = create_engine(db_url)

with engine.connect() as conn:
    try:
        conn.execute(text("ALTER TABLE free_quotas ADD COLUMN bonus_credits INTEGER DEFAULT 0;"))
        conn.execute(text("ALTER TABLE free_quotas ADD COLUMN used_bonus_credits INTEGER DEFAULT 0;"))
        conn.commit()
        print("Successfully added columns to free_quotas table.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()
