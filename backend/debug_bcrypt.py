from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def test_hash(password: str):
    print(f"Testing password: '{password}' (len={len(password)}, type={type(password)})")
    try:
        hashed = pwd_context.hash(password)
        print(f"Success: {hashed[:10]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_hash("password123")
    test_hash("short")
    test_hash("a" * 50)
    test_hash("a" * 72)
    test_hash("a" * 73)
