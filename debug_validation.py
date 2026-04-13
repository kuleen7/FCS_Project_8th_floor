"""
Debug Registration Validation Issue
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_minimal_registration():
    """Test with minimal required data"""
    
    print("🔍 Testing minimal registration...")
    
    # Test with absolute minimum required fields
    minimal_data = {
        "email": "minimal@test.com",
        "password": "Secure123!",
        "mobile": "1234567890",
        "first_name": "Test",
        "last_name": "User"
        # NO ROLE - let backend use default
    }
    
    print(f"Data: {json.dumps(minimal_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=minimal_data)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS with minimal data!")
        else:
            print("❌ FAILED with minimal data!")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_with_role():
    """Test with role field"""
    
    print("\n🔍 Testing with role field...")
    
    # Test with role
    with_role_data = {
        "email": "role@test.com",
        "password": "Secure123!",
        "mobile": "1234567890",
        "first_name": "Test",
        "last_name": "User",
        "role": "user"
    }
    
    print(f"Data: {json.dumps(with_role_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=with_role_data)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            print("✅ SUCCESS with role!")
        else:
            print("❌ FAILED with role!")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_invalid_data():
    """Test with invalid data to see error messages"""
    
    print("\n🔍 Testing with invalid data...")
    
    # Test with missing required fields
    invalid_data = {
        "email": "invalid-email",  # Invalid format
        "password": "123",  # Too short
        "mobile": "123"  # Too short
    }
    
    print(f"Data: {json.dumps(invalid_data, indent=2)}")
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/register", json=invalid_data)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("🚀 REGISTRATION VALIDATION DEBUG")
    print("=" * 50)
    
    # Test minimal registration
    test_minimal_registration()
    
    # Test with role
    test_with_role()
    
    # Test with invalid data
    test_invalid_data()
    
    print("\n" + "=" * 50)
    print("🎯 Check backend logs for detailed error messages")
    print("📱 This will help identify the exact validation issue")
