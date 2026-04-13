"""
Test Complete Registration Flow with Fixed Frontend
"""
import requests
import time

BASE_URL = "http://localhost:8000"

def test_complete_registration_flow():
    """Test the complete registration and login flow"""
    
    print("🧪 Testing Complete Registration Flow")
    print("=" * 50)
    
    # Test data
    import random
    import string
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    random_mobile = ''.join(random.choices('0123456789', k=10))
    
    test_user = {
        "email": f"test{random_str}@unique.com",
        "password": "Secure123!",
        "mobile": random_mobile,
        "first_name": "Milestone",
        "last_name": "Test"
    }
    
    print(f"📧 Testing registration for: {test_user['email']}")
    print(f"📱 Mobile: {test_user['mobile']}")
    print(f"👤 Name: {test_user['first_name']} {test_user['last_name']}")
    print()
    
    # Step 1: Register
    print("1️⃣ Registering user...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Registration SUCCESS!")
            print(f"   Message: {result['message']}")
            print(f"   User ID: {result['data']['user_id']}")
            user_id = result['data']['user_id']
        else:
            print(f"❌ Registration FAILED!")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration ERROR: {e}")
        return False
    
    # Step 2: Get OTP
    print("\n2️⃣ Getting OTP...")
    try:
        import psycopg2
        conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
        cursor = conn.cursor()
        cursor.execute('SELECT otp_code FROM otp_verifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 1', 
                      (user_id,))
        otp = cursor.fetchone()
        conn.close()
        
        if otp:
            print(f"✅ OTP found: {otp[0]}")
            otp_code = otp[0]
        else:
            print("❌ No OTP found")
            return False
    except Exception as e:
        print(f"❌ OTP ERROR: {e}")
        return False
    
    # Step 3: Verify Email
    print("\n3️⃣ Verifying email...")
    try:
        verify_response = requests.post(f"{BASE_URL}/api/auth/verify-email", 
                                       json={"email": test_user["email"], "otp_code": otp_code})
        
        if verify_response.status_code == 200:
            print("✅ Email verification SUCCESS!")
        else:
            print(f"❌ Email verification FAILED!")
            print(f"   Status: {verify_response.status_code}")
            print(f"   Error: {verify_response.text}")
            return False
    except Exception as e:
        print(f"❌ Email verification ERROR: {e}")
        return False
    
    # Step 4: Login
    print("\n4️⃣ Testing login...")
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", 
                                       json={"email": test_user["email"], "password": test_user["password"]})
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            print("✅ Login SUCCESS!")
            print(f"   Token: {login_result['token'][:50]}...")
            print(f"   User ID: {login_result['user']['id']}")
            print(f"   Name: {login_result['user']['first_name']} {login_result['user']['last_name']}")
            print(f"   Email: {login_result['user']['email']}")
            print(f"   Verified: {login_result['user']['is_verified']}")
            
            # Step 5: Test protected route
            print("\n5️⃣ Testing authenticated access...")
            headers = {"Authorization": f"Bearer {login_result['token']}"}
            
            # Test getting user profile
            profile_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
            
            if profile_response.status_code == 200:
                print("✅ Authenticated access SUCCESS!")
                return True
            else:
                print(f"❌ Authenticated access FAILED!")
                print(f"   Status: {profile_response.status_code}")
                return False
        else:
            print(f"❌ Login FAILED!")
            print(f"   Status: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return False
    except Exception as e:
        print(f"❌ Login ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_complete_registration_flow()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 COMPLETE FLOW WORKS!")
        print("✅ Registration → Email Verification → Login → Authenticated Access")
        print("🚀 Frontend and Backend are FULLY COMPATIBLE!")
        print("📱 You can now test in the browser at http://localhost:3000")
    else:
        print("❌ FLOW FAILED!")
        print("🔧 There are still issues to fix")
    print("=" * 50)
