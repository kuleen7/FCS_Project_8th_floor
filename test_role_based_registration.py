"""
Test Role-Based Registration System
Tests all three roles: User, Recruiter, Admin
"""
import requests
import psycopg2
import time

BASE_URL = "http://localhost:8000"

def test_role_based_registration():
    """Test registration for all three roles"""
    
    print("🎭 ROLE-BASED REGISTRATION TEST")
    print("=" * 50)
    
    # Test data for each role
    test_users = [
        {
            "email": "jobseeker@test.com",
            "password": "Secure123!",
            "mobile": "1234567890",
            "first_name": "John",
            "last_name": "Doe",
            "role": "user"
        },
        {
            "email": "recruiter@test.com", 
            "password": "Secure123!",
            "mobile": "2345678901",
            "first_name": "Jane",
            "last_name": "Smith",
            "role": "recruiter",
            "company_name": "Tech Solutions Inc"
        },
        {
            "email": "admin@test.com",
            "password": "Secure123!", 
            "mobile": "3456789012",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin"
        }
    ]
    
    for i, test_user in enumerate(test_users, 1):
        role_name = test_user["role"].title()
        print(f"\n{i+1}. Testing {role_name} Registration")
        print("-" * 40)
        
        try:
            # Register user
            response = requests.post(f"{BASE_URL}/api/auth/register", json=test_user)
            
            if response.status_code == 201:
                result = response.json()
                print(f"✅ Registration SUCCESS!")
                print(f"   Message: {result['message']}")
                print(f"   User ID: {result['data']['user_id']}")
                print(f"   Role: {result['data'].get('role', 'Not specified')}")
                
                # Get OTP
                import time
                time.sleep(1)  # Wait for OTP to be generated
                
                conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
                cursor = conn.cursor()
                cursor.execute('SELECT otp_code FROM otp_verifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 1', 
                              (result['data']['user_id'],))
                otp = cursor.fetchone()
                conn.close()
                
                if otp:
                    print(f"   OTP: {otp[0]}")
                    
                    # Verify OTP
                    verify_response = requests.post(f"{BASE_URL}/api/auth/verify-email", 
                                                   json={"email": test_user["email"], "otp_code": otp[0]})
                    
                    if verify_response.status_code == 200:
                        print(f"✅ Email Verification SUCCESS!")
                        
                        # Login
                        login_response = requests.post(f"{BASE_URL}/api/auth/login", 
                                                       json={"email": test_user["email"], "password": test_user["password"]})
                        
                        if login_response.status_code == 200:
                            login_result = login_response.json()
                            print(f"✅ Login SUCCESS!")
                            print(f"   Token: {login_result['token'][:50]}...")
                            print(f"   User ID: {login_result['user']['id']}")
                            print(f"   Name: {login_result['user']['first_name']} {login_result['user']['last_name']}")
                            print(f"   Role: {login_result['user']['role']}")
                            print(f"   Verified: {login_result['user']['is_verified']}")
                            
                            # Test protected route
                            headers = {"Authorization": f"Bearer {login_result['token']}"}
                            profile_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
                            
                            if profile_response.status_code == 200:
                                print(f"✅ Protected Access SUCCESS!")
                                print(f"   Full flow working for {role_name}!")
                            else:
                                print(f"❌ Protected Access FAILED: {profile_response.status_code}")
                        else:
                            print(f"❌ Login FAILED: {login_response.status_code}")
                            print(f"   Error: {login_response.text}")
                    else:
                        print(f"❌ Email Verification FAILED: {verify_response.status_code}")
                        print(f"   Error: {verify_response.text}")
                else:
                    print(f"❌ OTP not found")
            else:
                print(f"❌ Registration FAILED: {response.status_code}")
                print(f"   Error: {response.text}")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")
            
        print("-" * 40)
    
    print("\n" + "=" * 50)
    print("🎯 ROLE-BASED REGISTRATION TEST COMPLETE")

def check_database_status():
    """Check current database status"""
    print("\n📊 Database Status:")
    print("-" * 30)
    
    try:
        conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
        cursor = conn.cursor()
        
        # Check users by role
        cursor.execute('''
            SELECT role, COUNT(*) as count 
            FROM users 
            GROUP BY role
        ''')
        role_counts = cursor.fetchall()
        
        print("Users by Role:")
        for role, count in role_counts:
            print(f"  {role}: {count}")
        
        cursor.execute('SELECT COUNT(*) as total FROM users')
        total_users = cursor.fetchone()[0]
        print(f"Total Users: {total_users}")
        
        conn.close()
        print("✅ Database accessible")
        
    except Exception as e:
        print(f"❌ Database error: {e}")

def check_frontend_status():
    """Check if frontend is accessible"""
    print("\n🌐 Frontend Status:")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible at http://localhost:3000")
        else:
            print(f"❌ Frontend error: {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")

if __name__ == "__main__":
    print("🚀 ROLE-BASED REGISTRATION SYSTEM TEST")
    print("=" * 60)
    
    # Check system status
    check_frontend_status()
    check_database_status()
    
    print("\n" + "=" * 60)
    print("🧪 Testing Role-Based Registration")
    print("=" * 60)
    
    # Run role-based registration test
    test_role_based_registration()
    
    print("\n" + "=" * 60)
    print("🎉 TEST COMPLETE!")
    print("📱 You can now test role-based registration in frontend")
    print("🌐 Go to http://localhost:3000/register")
    print("\n📝 Test Users:")
    print("  1. jobseeker@test.com / Secure123!")
    print("  2. recruiter@test.com / Secure123! (with company)")
    print("  3. admin@test.com / Secure123!")
    print("\n🎯 Each role should show different dashboard after login!")
