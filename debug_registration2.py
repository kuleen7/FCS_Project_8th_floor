"""
Debug Registration Issues
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_registration_debug():
    """Debug registration with detailed logging"""
    
    print("🔍 REGISTRATION DEBUG")
    print("=" * 40)
    
    # Test simple user registration
    test_data = {
        "email": "test@test.com",
        "password": "Secure123!",
        "mobile": "1234567890",
        "first_name": "Test",
        "last_name": "User",
        "role": "user"
    }
    
    print(f"📤 Sending data: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=test_data)
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Response Headers: {dict(response.headers)}")
        print(f"📥 Response Text: {response.text}")
        
        if response.status_code != 201:
            print(f"❌ REGISTRATION FAILED")
            
            # Try without role
            print("\n🔍 Testing without role field...")
            test_data_no_role = {
                "email": "test2@test.com",
                "password": "Secure123!",
                "mobile": "1234567891",
                "first_name": "Test",
                "last_name": "User"
            }
            
            response2 = requests.post(f"{BASE_URL}/api/auth/register", json=test_data_no_role)
            print(f"📥 Status Code: {response2.status_code}")
            print(f"📥 Response Text: {response2.text}")
            
        else:
            print(f"✅ REGISTRATION SUCCESS")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_registration_debug()
