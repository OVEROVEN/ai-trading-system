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
        print("Dropping foreign key constraints...")
        conn.execute(text("ALTER TABLE usage_records DROP CONSTRAINT IF EXISTS usage_records_user_id_fkey;"))
        conn.execute(text("ALTER TABLE subscriptions DROP CONSTRAINT IF EXISTS subscriptions_user_id_fkey;"))
        conn.execute(text("ALTER TABLE payments DROP CONSTRAINT IF EXISTS payments_user_id_fkey;"))
        conn.execute(text("ALTER TABLE free_quotas DROP CONSTRAINT IF EXISTS free_quotas_user_id_fkey;"))
        conn.execute(text("ALTER TABLE redemption_codes DROP CONSTRAINT IF EXISTS redemption_codes_used_by_user_id_fkey;"))
        conn.execute(text("ALTER TABLE redemption_history DROP CONSTRAINT IF EXISTS redemption_history_user_id_fkey;"))
        conn.commit()
        print("Foreign key constraints dropped.")

        print("Altering column types...")
        conn.execute(text("ALTER TABLE users ALTER COLUMN id SET DATA TYPE UUID USING (id::uuid);"))
        conn.execute(text("ALTER TABLE usage_records ALTER COLUMN user_id SET DATA TYPE UUID USING (user_id::uuid);"))
        conn.execute(text("ALTER TABLE subscriptions ALTER COLUMN user_id SET DATA TYPE UUID USING (user_id::uuid);"))
        conn.execute(text("ALTER TABLE payments ALTER COLUMN user_id SET DATA TYPE UUID USING (user_id::uuid);"))
        conn.execute(text("ALTER TABLE free_quotas ALTER COLUMN user_id SET DATA TYPE UUID USING (user_id::uuid);"))
        conn.execute(text("ALTER TABLE redemption_codes ALTER COLUMN used_by_user_id SET DATA TYPE UUID USING (used_by_user_id::uuid);"))
        conn.execute(text("ALTER TABLE redemption_history ALTER COLUMN user_id SET DATA TYPE UUID USING (user_id::uuid);"))
        conn.commit()
        print("Column types altered.")

        print("Re-creating foreign key constraints...")
        conn.execute(text("ALTER TABLE usage_records ADD CONSTRAINT usage_records_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);"))
        conn.execute(text("ALTER TABLE subscriptions ADD CONSTRAINT subscriptions_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);"))
        conn.execute(text("ALTER TABLE payments ADD CONSTRAINT payments_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);"))
        conn.execute(text("ALTER TABLE free_quotas ADD CONSTRAINT free_quotas_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);"))
        conn.execute(text("ALTER TABLE redemption_codes ADD CONSTRAINT redemption_codes_used_by_user_id_fkey FOREIGN KEY (used_by_user_id) REFERENCES users(id);"))
        conn.execute(text("ALTER TABLE redemption_history ADD CONSTRAINT redemption_history_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id);"))
        conn.commit()
        print("Foreign key constraints re-created.")

        print("Successfully altered column types and re-created constraints.")
    except Exception as e:
        print(f"An error occurred: {e}")
        conn.rollback()