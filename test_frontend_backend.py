"""
Test Frontend-Backend Compatibility
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_frontend_backend_compatibility():
    """Test that frontend can successfully register and login"""
    
    print("🧪 Testing Frontend-Backend Compatibility")
    print("=" * 50)
    
    # Test 1: Registration (frontend format)
    print("\n1. Testing Registration...")
    register_data = {
        "email": "frontend@test.com",
        "password": "Secure123!",
        "mobile": "5551112222",
        "first_name": "Frontend",
        "last_name": "Test"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=register_data)
    
    if response.status_code == 201:
        result = response.json()
        print(f"✅ Registration SUCCESS: {result['message']}")
        print(f"   User ID: {result['data']['user_id']}")
        
        # Get OTP for verification
        import psycopg2
        conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
        cursor = conn.cursor()
        cursor.execute('SELECT otp_code FROM otp_verifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 1', 
                      (result['data']['user_id'],))
        otp = cursor.fetchone()
        conn.close()
        
        if otp:
            # Test 2: Email Verification
            print(f"\n2. Testing Email Verification...")
            verify_response = requests.post(f"{BASE_URL}/api/auth/verify-email", 
                                           json={"email": register_data["email"], "otp_code": otp[0]})
            
            if verify_response.status_code == 200:
                print("✅ Email Verification SUCCESS")
                
                # Test 3: Login (frontend expects token and user)
                print(f"\n3. Testing Login...")
                login_response = requests.post(f"{BASE_URL}/api/auth/login", 
                                              json={"email": register_data["email"], "password": register_data["password"]})
                
                if login_response.status_code == 200:
                    login_result = login_response.json()
                    
                    # Check if response format matches frontend expectations
                    if "token" in login_result and "user" in login_result:
                        print("✅ Login SUCCESS - Frontend Compatible Format")
                        print(f"   Token: {login_result['token'][:50]}...")
                        print(f"   User ID: {login_result['user']['id']}")
                        print(f"   User Name: {login_result['user']['first_name']} {login_result['user']['last_name']}")
                        print(f"   Email: {login_result['user']['email']}")
                        print(f"   Verified: {login_result['user']['is_verified']}")
                        
                        return True
                    else:
                        print("❌ Login FAILED - Wrong response format")
                        print(f"   Expected: {token, user}")
                        print(f"   Got: {list(login_result.keys())}")
                else:
                    print(f"❌ Login FAILED - Status: {login_response.status_code}")
                    print(f"   Error: {login_response.text}")
            else:
                print(f"❌ Email Verification FAILED - Status: {verify_response.status_code}")
                print(f"   Error: {verify_response.text}")
        else:
            print("❌ No OTP found for verification")
    else:
        print(f"❌ Registration FAILED - Status: {response.status_code}")
        print(f"   Error: {response.text}")
    
    return False

if __name__ == "__main__":
    success = test_frontend_backend_compatibility()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! Frontend-Backend is COMPATIBLE")
        print("✅ Users can now register and login through the frontend")
    else:
        print("❌ TESTS FAILED! Frontend-Backend needs fixes")
    print("=" * 50)
