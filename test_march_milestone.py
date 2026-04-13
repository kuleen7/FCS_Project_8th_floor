"""
March Milestone Feature Test Script
Tests all implemented features to verify they're working correctly
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_feature(name, test_func):
    """Run a test and report results"""
    print(f"\n{'='*50}")
    print(f"Testing: {name}")
    print(f"{'='*50}")
    
    try:
        result = test_func()
        if result:
            print(f"✅ {name} - PASSED")
            return True
        else:
            print(f"❌ {name} - FAILED")
            return False
    except Exception as e:
        print(f"❌ {name} - ERROR: {str(e)}")
        return False

def get_auth_token(email, password):
    """Get authentication token"""
    response = requests.post(f"{BASE_URL}/api/auth/login", 
                            json={"email": email, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    return None

def test_user_registration():
    """Test user registration and verification"""
    # Register new user
    response = requests.post(f"{BASE_URL}/api/auth/register", 
                            json={
                                "email": "testuser@march.com",
                                "password": "Secure123!",
                                "mobile": "5551239999",
                                "first_name": "Test",
                                "last_name": "User"
                            })
    
    if response.status_code != 201:
        return False
    
    user_data = response.json()
    print(f"User registered: {user_data['data']['email']}")
    
    # Get OTP from database (simplified for test)
    import psycopg2
    conn = psycopg2.connect('postgresql://jobplatform:2499@localhost/secure_job_platform')
    cursor = conn.cursor()
    cursor.execute('SELECT code FROM otp_verifications WHERE user_id = %s ORDER BY created_at DESC LIMIT 1', 
                  (user_data['data']['user_id'],))
    otp = cursor.fetchone()
    conn.close()
    
    if not otp:
        return False
    
    # Verify email
    response = requests.post(f"{BASE_URL}/api/auth/verify-email", 
                            json={
                                "email": "testuser@march.com", 
                                "otp_code": otp[0]
                            })
    
    return response.status_code == 200

def test_company_creation():
    """Test company creation"""
    token = get_auth_token("testuser@march.com", "Secure123!")
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/companies/", 
                            headers=headers,
                            json={
                                "name": "March Test Company",
                                "description": "A company for testing March milestone",
                                "location": "Remote"
                            })
    
    if response.status_code == 201:
        company = response.json()
        print(f"Company created: {company['name']} (ID: {company['id']})")
        return True
    return False

def test_job_posting():
    """Test job posting"""
    token = get_auth_token("testuser@march.com", "Secure123!")
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/jobs/", 
                            headers=headers,
                            json={
                                "company_id": 1,  # Assuming first company
                                "title": "Security Engineer",
                                "description": "Develop secure applications",
                                "location": "Remote",
                                "job_type": "remote"
                            })
    
    if response.status_code == 201:
        job = response.json()
        print(f"Job posted: {job['title']} (ID: {job['id']})")
        return True
    return False

def test_encrypted_messaging():
    """Test encrypted messaging"""
    token = get_auth_token("demo@fcs26.com", "Secure123!")
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create conversation
    response = requests.post(f"{BASE_URL}/api/messages/conversations", 
                            headers=headers,
                            json={
                                "type": "one_to_one",
                                "participant_ids": [3]  # user2
                            })
    
    if response.status_code != 201:
        return False
    
    conversation = response.json()
    conv_id = conversation["id"]
    
    # Send encrypted message
    response = requests.post(f"{BASE_URL}/api/messages/conversations/{conv_id}/messages", 
                            headers=headers,
                            json={
                                "conversation_id": conv_id,
                                "content": "This is a secret message!",
                                "message_type": "text"
                            })
    
    if response.status_code == 201:
        message = response.json()
        # Verify encryption
        if "content_encrypted" in message and "content_hash" in message:
            print(f"Encrypted message sent (ID: {message['id']})")
            print(f"Content encrypted: {message['content_encrypted'][:50]}...")
            print(f"Content hash: {message['content_hash']}")
            return True
    
    return False

def test_audit_logging():
    """Test audit logging system"""
    token = get_auth_token("demo@fcs26.com", "Secure123!")
    if not token:
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/audit/logs", headers=headers)
    
    if response.status_code == 200:
        logs = response.json()
        print(f"Audit logs retrieved: {logs['total']} entries found")
        return True
    return False

def test_job_search():
    """Test job search functionality"""
    response = requests.get(f"{BASE_URL}/api/jobs/search", 
                          params={"keywords": "security", "limit": 10})
    
    if response.status_code == 200:
        results = response.json()
        print(f"Job search results: {results['total']} jobs found")
        return True
    return False

def main():
    """Run all March milestone tests"""
    print("🚀 FCS-26 March Milestone Feature Tests")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("User Registration & Verification", test_user_registration),
        ("Company Creation", test_company_creation),
        ("Job Posting", test_job_posting),
        ("Encrypted Messaging", test_encrypted_messaging),
        ("Audit Logging", test_audit_logging),
        ("Job Search", test_job_search),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_feature(test_name, test_func):
            passed += 1
    
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL MARCH MILESTONE FEATURES WORKING!")
    else:
        print(f"\n⚠️  {total - passed} features need attention")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
