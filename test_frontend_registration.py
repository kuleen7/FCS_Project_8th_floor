"""
Test Frontend Registration Flow
Tests the complete registration flow with the fixed frontend
"""
import requests
import psycopg2
import time

BASE_URL = "http://localhost:8000"

def test_frontend_registration_flow():
    """Test the complete registration flow as it would work in frontend"""
    
    print("🧪 TESTING FRONTEND REGISTRATION FLOW")
    print("=" * 50)
    
    # Test data - same as what user would enter in frontend
    test_user = {
        "email": "chris@jobsearch.com",
        "password": "Secure123!",
        "mobile": "1234567890",
        "first_name": "Chris",
        "last_name": "Wilson"
    }
    
    print(f"📧 Testing with: {test_user['email']}")
    print(f"📱 Mobile: {test_user['mobile']}")
    print(f"👤 Name: {test_user['first_name']} {test_user['last_name']}")
    print()
    
    # Step 1: Register (simulating frontend registration)
    print("1️⃣ Testing Registration (Frontend API Call)...")
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
        
        if response.status_code == 201:
            result = response.json()
            print("✅ Registration SUCCESS!")
            print(f"   Message: {result['message']}")
            print(f"   User ID: {result['data']['user_id']}")
            user_id = result['data']['user_id']
            
            print(f"\n📱 Frontend would now redirect to: http://localhost:3000/verify-otp")
            print(f"   With email: {test_user['email']}")
            
        else:
            print(f"❌ Registration FAILED!")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration ERROR: {e}")
        return False
    
    # Step 2: Get OTP (simulating user getting OTP from database)
    print("\n2️⃣ Getting OTP (Database Query)...")
    try:
        conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
        cursor = conn.cursor()
        cursor.execute('SELECT otp_code FROM otp_verifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 1', 
                      (user_id,))
        otp = cursor.fetchone()
        conn.close()
        
        if otp:
            print(f"✅ OTP found: {otp[0]}")
            print(f"📱 User would enter this in frontend OTP verification page")
            otp_code = otp[0]
        else:
            print("❌ No OTP found")
            return False
    except Exception as e:
        print(f"❌ OTP ERROR: {e}")
        return False
    
    # Step 3: Verify Email (simulating frontend OTP verification)
    print("\n3️⃣ Testing Email Verification (Frontend API Call)...")
    try:
        verify_response = requests.post(f"{BASE_URL}/api/auth/verify-email", 
                                       json={"email": test_user["email"], "otp_code": otp_code})
        
        if verify_response.status_code == 200:
            result = verify_response.json()
            print("✅ Email verification SUCCESS!")
            print(f"   Message: {result['message']}")
            print(f"📱 Frontend would show success and redirect to login")
        else:
            print(f"❌ Email verification FAILED!")
            print(f"   Status: {verify_response.status_code}")
            print(f"   Error: {verify_response.text}")
            return False
    except Exception as e:
        print(f"❌ Email verification ERROR: {e}")
        return False
    
    # Step 4: Login (simulating frontend login)
    print("\n4️⃣ Testing Login (Frontend API Call)...")
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
            print(f"📱 Frontend would store token and redirect to dashboard")
            
            return True
        else:
            print(f"❌ Login FAILED!")
            print(f"   Status: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            return False
    except Exception as e:
        print(f"❌ Login ERROR: {e}")
        return False

def check_frontend_status():
    """Check if frontend is accessible"""
    print("\n🌐 Frontend Status Check:")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible at http://localhost:3000")
            return True
        else:
            print(f"❌ Frontend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def get_otp_command():
    """Show the command to get OTP"""
    print("\n📱 Quick OTP Command:")
    print("-" * 30)
    print("cd c:\\Users\\siddh_ygv5bws\\OneDrive\\Desktop\\fcs_8_floor-main\\backend")
    print("python get_otp.py")
    print("\nOr run:")
    print("python -c \"")
    print("import psycopg2")
    print("conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')")
    print("cursor = conn.cursor()")
    print("cursor.execute('SELECT otp_code FROM otp_verifications ORDER BY created_at DESC LIMIT 1')")
    print("otp = cursor.fetchone()")
    print("if otp: print('OTP:', otp[0])")
    print("conn.close()\"")

if __name__ == "__main__":
    print("🚀 FRONTEND REGISTRATION FLOW TEST")
    print("=" * 60)
    
    # Check frontend status
    frontend_ok = check_frontend_status()
    
    if not frontend_ok:
        print("\n❌ Frontend is not running!")
        print("Please start the frontend with:")
        print("cd c:\\Users\\siddh_ygv5bws\\OneDrive\\Desktop\\fcs_8_floor-main\\frontend")
        print("npm start")
        exit(1)
    
    # Run the test
    success = test_frontend_registration_flow()
    
    # Show OTP command
    get_otp_command()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 FRONTEND REGISTRATION FLOW WORKS!")
        print("✅ Registration → OTP Verification → Login")
        print("🌐 You can now test in Chrome at http://localhost:3000")
        print("\n📝 Steps to test manually:")
        print("1. Go to http://localhost:3000")
        print("2. Register with chris@jobsearch.com")
        print("3. Get OTP using the command above")
        print("4. Enter OTP in verification page")
        print("5. Login successfully")
    else:
        print("❌ FRONTEND REGISTRATION FLOW FAILED!")
        print("🔧 Check the errors above")
    print("=" * 60)
