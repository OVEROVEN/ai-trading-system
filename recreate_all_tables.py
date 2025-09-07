
import os
from sqlalchemy import create_engine, inspect

# Add project root to Python path
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.auth.models import Base as AuthBase
from src.database.redemption_models import Base as RedemptionBase

def main():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL environment variable not set.")
        exit(1)

    # The proxy is running on localhost
    db_url = db_url.replace("10.56.0.3", "127.0.0.1")

    print(f"Connecting to database...")
    engine = create_engine(db_url)

    with engine.connect() as conn:
        print("Dropping all tables...")
        # Drop tables in reverse order of creation due to dependencies
        RedemptionBase.metadata.drop_all(conn)
        AuthBase.metadata.drop_all(conn)
        print("All tables dropped.")

        print("Creating all tables...")
        AuthBase.metadata.create_all(conn)
        RedemptionBase.metadata.create_all(conn)
        print("All tables created successfully.")

if __name__ == "__main__":
    main()
