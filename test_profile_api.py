"""
Test Profile API endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_profile_api():
    """Test profile API endpoints"""
    
    print("👤 PROFILE API TEST")
    print("=" * 40)
    
    # First, login to get token
    login_data = {
        "email": "recruiter@test.com",
        "password": "Secure123!"
    }
    
    try:
        login_response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
        
        if login_response.status_code == 200:
            login_result = login_response.json()
            token = login_result['token']
            user_id = login_result['user']['id']
            
            print(f"✅ Login successful!")
            print(f"   User ID: {user_id}")
            print(f"   Token: {token[:50]}...")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Test get profile
            print("\n1️⃣ Testing GET /profile/me")
            profile_response = requests.get(f"{BASE_URL}/api/profile/me", headers=headers)
            
            if profile_response.status_code == 200:
                profile = profile_response.json()
                print("✅ GET profile successful!")
                print(f"   Name: {profile['first_name']} {profile['last_name']}")
                print(f"   Email: {profile['email']}")
                print(f"   Role: {profile['role']}")
                print(f"   Privacy: {profile.get('privacy_level', 'public')}")
            else:
                print(f"❌ GET profile failed: {profile_response.status_code}")
                print(f"   Error: {profile_response.text}")
            
            # Test update profile
            print("\n2️⃣ Testing PUT /profile/me")
            update_data = {
                "first_name": "Updated",
                "last_name": "Name",
                "headline": "Senior Software Engineer",
                "location": "San Francisco, CA",
                "bio": "Passionate developer with 5+ years experience",
                "privacy_level": "connections"
            }
            
            update_response = requests.put(f"{BASE_URL}/api/profile/me", json=update_data, headers=headers)
            
            if update_response.status_code == 200:
                result = update_response.json()
                print("✅ UPDATE profile successful!")
                print(f"   Message: {result['message']}")
                print(f"   Updated Name: {result['data']['first_name']} {result['data']['last_name']}")
            else:
                print(f"❌ UPDATE profile failed: {update_response.status_code}")
                print(f"   Error: {update_response.text}")
            
            # Test view profile (should work for own profile)
            print("\n3️⃣ Testing GET /profile/view/{user_id}")
            view_response = requests.get(f"{BASE_URL}/api/profile/view/{user_id}", headers=headers)
            
            if view_response.status_code == 200:
                view_profile = view_response.json()
                print("✅ VIEW profile successful!")
                print(f"   View Name: {view_profile['first_name']} {view_profile['last_name']}")
            else:
                print(f"❌ VIEW profile failed: {view_response.status_code}")
                print(f"   Error: {view_response.text}")
                
        else:
            print(f"❌ Login failed: {login_response.status_code}")
            print(f"   Error: {login_response.text}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_profile_api()
