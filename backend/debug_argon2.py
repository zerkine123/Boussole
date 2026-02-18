from passlib.context import CryptContext
import argon2

print(f"Argon2 version: {argon2.__version__}")

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def test_hash(password: str):
    print(f"Testing password: '{password}'")
    try:
        hashed = pwd_context.hash(password)
        print(f"Success: {hashed[:10]}...")
        return hashed
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    h = test_hash("password123")
    if h:
        print(f"Verify: {pwd_context.verify('password123', h)}")
