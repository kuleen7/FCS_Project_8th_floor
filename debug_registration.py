"""
Debug Registration Issues
"""
import requests
import psycopg2

BASE_URL = "http://localhost:8000"

def check_existing_users():
    """Check what users already exist"""
    conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
    cursor = conn.cursor()
    cursor.execute('SELECT email, mobile FROM users ORDER BY created_at DESC LIMIT 10')
    users = cursor.fetchall()
    conn.close()
    
    print("📋 Already registered users:")
    print("=" * 50)
    for i, (email, mobile) in enumerate(users, 1):
        print(f"{i:2d}. Email: {email}")
        print(f"    Mobile: {mobile}")
        print()
    
    return [email for email, _ in users], [mobile for _, mobile in users]

def test_registration_with_new_data():
    """Test registration with completely new data"""
    emails, mobiles = check_existing_users()
    
    # Generate unique email and mobile
    import random
    import string
    
    # Generate unique email
    while True:
        random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        test_email = f"test{random_str}@newdomain.com"
        if test_email not in emails:
            break
    
    # Generate unique mobile
    while True:
        random_mobile = ''.join(random.choices('0123456789', k=10))
        if random_mobile not in mobiles:
            break
    
    print(f"🧪 Testing with new unique data:")
    print(f"   Email: {test_email}")
    print(f"   Mobile: {random_mobile}")
    print()
    
    # Test registration
    register_data = {
        "email": test_email,
        "password": "Secure123!",
        "mobile": random_mobile,
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Registration SUCCESS!")
            print(f"   Message: {result['message']}")
            print(f"   User ID: {result['data']['user_id']}")
            return True
        else:
            print(f"❌ Registration FAILED!")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Registration ERROR: {e}")
        return False

def test_common_formats():
    """Test common mobile formats that should work"""
    print("\n📱 Testing Common Mobile Formats:")
    print("=" * 40)
    
    test_mobiles = [
        "1234567890",      # 10 digits
        "5551234567",      # 10 digits
        "555-123-4567",    # with dashes
        "(555)1234567",    # with parentheses
        "+15551234567",    # with country code
    ]
    
    for mobile in test_mobiles:
        print(f"   Testing: {mobile} (length: {len(mobile)})")
        if 10 <= len(mobile) <= 15:
            print(f"   ✅ Valid format")
        else:
            print(f"   ❌ Invalid format")

if __name__ == "__main__":
    print("🔍 Registration Debug Tool")
    print("=" * 50)
    
    # Show existing users
    check_existing_users()
    
    # Test common mobile formats
    test_common_formats()
    
    print("\n" + "=" * 50)
    print("🚀 Testing Fresh Registration:")
    print("=" * 50)
    
    # Test with new unique data
    success = test_registration_with_new_data()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SOLUTION: Use unique email and mobile!")
        print("✅ The system works - just avoid duplicates")
    else:
        print("❌ There's still an issue with the backend")
    print("=" * 50)
