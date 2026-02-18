import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

POSTGRES_USER = os.getenv("POSTGRES_USER", "boussole")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "boussole_password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "boussole")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

# Default admin credentials (try standard defaults)
ADMIN_USER = "postgres"
ADMIN_PASSWORD = os.getenv("PGADMIN_PASSWORD", "postgres") # You might need to change this if your local postgres has a different password
# Try empty password too if this fails

def create_database():
    print(f"Connecting to PostgreSQL at {POSTGRES_HOST}:{POSTGRES_PORT} as {ADMIN_USER}...")
    
    try:
        # Connect to default 'postgres' database
        conn = psycopg2.connect(
            user=ADMIN_USER,
            password=ADMIN_PASSWORD,
            host=POSTGRES_HOST,
            port=POSTGRES_PORT,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname='{POSTGRES_USER}';")
        if not cur.fetchone():
            print(f"Creating user {POSTGRES_USER}...")
            cur.execute(f"CREATE USER {POSTGRES_USER} WITH PASSWORD '{POSTGRES_PASSWORD}' CREATEDB;")
        else:
            print(f"User {POSTGRES_USER} already exists.")
            
        # Check if database exists
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{POSTGRES_DB}';")
        if not cur.fetchone():
            print(f"Creating database {POSTGRES_DB}...")
            cur.execute(f"CREATE DATABASE {POSTGRES_DB} OWNER {POSTGRES_USER};")
        else:
            print(f"Database {POSTGRES_DB} already exists.")
            
        cur.close()
        conn.close()
        print("Database setup completed successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
        # Try without password if first attempt failed
        if "password authentication failed" in str(e):
             print("Retrying without password...")
             try:
                conn = psycopg2.connect(
                    user=ADMIN_USER,
                    password="", # Empty password
                    host=POSTGRES_HOST,
                    port=POSTGRES_PORT,
                    database="postgres"
                )
                conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
                cur = conn.cursor()
                
                # Check/Create user (duplicate logic, simplified for retry)
                cur.execute(f"SELECT 1 FROM pg_roles WHERE rolname='{POSTGRES_USER}';")
                if not cur.fetchone():
                    cur.execute(f"CREATE USER {POSTGRES_USER} WITH PASSWORD '{POSTGRES_PASSWORD}' CREATEDB;")
                
                cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{POSTGRES_DB}';")
                if not cur.fetchone():
                    cur.execute(f"CREATE DATABASE {POSTGRES_DB} OWNER {POSTGRES_USER};")
                
                cur.close()
                conn.close()
                print("Database setup completed successfully (no password).")
             except Exception as e2:
                 print(f"Retry failed: {e2}")
                 print("Please ensure PostgreSQL is running and you have superuser credentials.")

if __name__ == "__main__":
    create_database()
