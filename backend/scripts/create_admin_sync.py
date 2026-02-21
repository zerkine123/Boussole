import psycopg2
import os

try:
    print("Connecting to postgres...")
    conn = psycopg2.connect(
        dbname="boussole",
        user="boussole",
        password="boussole_password",
        host="localhost"
    )
    print("Success!")
    cur = conn.cursor()
    cur.execute("SELECT id, email, is_superuser FROM users")
    users = cur.fetchall()
    print("Users:", users)
    
    # Let's just create an admin directly via SQL here
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    hash_pwd = pwd_context.hash("admin123")
    
    cur.execute("SELECT id FROM users WHERE email='admin@boussole.dz'")
    if not cur.fetchone():
        print("Inserting admin user...")
        cur.execute("""
            INSERT INTO users (email, full_name, hashed_password, is_active, is_superuser)
            VALUES ('admin@boussole.dz', 'Boussole Admin', %s, true, true)
        """, (hash_pwd,))
        conn.commit()
        print("Admin user created!")
    else:
        print("Admin already exists. Updating...")
        cur.execute("""
            UPDATE users SET hashed_password=%s, is_superuser=true WHERE email='admin@boussole.dz'
        """, (hash_pwd,))
        conn.commit()
    print("Done")
except Exception as e:
    print("Error:", e)
