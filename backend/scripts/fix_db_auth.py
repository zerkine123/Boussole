import psycopg2
from psycopg2 import sql
import sys

# Common default passwords for local development
PASSWORDS = [None, "postgres", "password", "admin", "root", "123456"]

def try_connect_and_setup():
    print("Attempting to connect to PostgreSQL as 'postgres' user...")
    
    conn = None
    successful_password = None
    
    for pwd in PASSWORDS:
        try:
            print(f"Trying password: '{pwd if pwd is not None else '<empty>'}'")
            conn = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password=pwd,
                host="localhost",
                port="5432"
            )
            successful_password = pwd
            print("SUCCESS: Connected to PostgreSQL!")
            break
        except psycopg2.OperationalError as e:
            print(f"Failed: {e}")
            pass
            
    if conn is None:
        print("\nERROR: Could not connect to PostgreSQL with standard credentials.")
        print("Please ensure PostgreSQL is running and you know the 'postgres' user password.")
        return

    conn.autocommit = True
    cur = conn.cursor()
    
    # 1. Check/Create User 'boussole'
    try:
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname='boussole'")
        if cur.fetchone():
            print("User 'boussole' already exists. Updating password...")
            cur.execute("ALTER USER boussole WITH PASSWORD 'boussole_password'")
        else:
            print("Creating user 'boussole'...")
            cur.execute("CREATE USER boussole WITH PASSWORD 'boussole_password' CREATEDB")
        print("User 'boussole' setup complete.")
    except Exception as e:
        print(f"Error setting up user: {e}")

    # 2. Check/Create Database 'boussole'
    try:
        cur.execute("SELECT 1 FROM pg_database WHERE datname='boussole'")
        if cur.fetchone():
            print("Database 'boussole' already exists.")
        else:
            print("Creating database 'boussole'...")
            cur.execute("CREATE DATABASE boussole OWNER boussole")
            print("Database 'boussole' created.")
    except Exception as e:
        print(f"Error setting up database: {e}")

    cur.close()
    conn.close()
    print("\n SETUP COMPLETE. You should now be able to run migrations.")

if __name__ == "__main__":
    try_connect_and_setup()
