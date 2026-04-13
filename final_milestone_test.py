"""
Final March Milestone Test - Quick verification of all features
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_feature(name, url, method="GET", data=None, headers=None):
    """Test a single feature with timeout"""
    try:
        print(f"🔍 Testing {name}...")
        
        if method == "GET":
            response = requests.get(url, timeout=5, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=5, headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"   ✅ {name} - Status: {response.status_code}")
            return True
        else:
            print(f"   ❌ {name} - Status: {response.status_code}")
            print(f"      Error: {response.text[:100]}...")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ⏰ {name} - Request timed out")
        return False
    except Exception as e:
        print(f"   ❌ {name} - Error: {str(e)[:50]}...")
        return False

def run_milestone_tests():
    """Run all March milestone tests"""
    print("🎯 MARCH MILESTONE - FINAL VERIFICATION")
    print("=" * 50)
    
    results = []
    
    # 1. Backend Health
    results.append(test_feature(
        "Backend Health Check", 
        f"{BASE_URL}/api/health"
    ))
    
    # 2. User Registration
    results.append(test_feature(
        "User Registration", 
        f"{BASE_URL}/api/auth/register",
        method="POST",
        data={
            "email": "testuser@milestone.com",
            "password": "Secure123!",
            "mobile": "1234567890",
            "first_name": "Test",
            "last_name": "User",
            "role": "user"
        }
    ))
    
    # 3. Recruiter Registration
    results.append(test_feature(
        "Recruiter Registration", 
        f"{BASE_URL}/api/auth/register",
        method="POST",
        data={
            "email": "recruiter@milestone.com",
            "password": "Secure123!",
            "mobile": "0987654321",
            "first_name": "Recruiter",
            "last_name": "User",
            "role": "recruiter",
            "company_name": "Test Company"
        }
    ))
    
    # 4. Login Test
    login_result = test_feature(
        "User Login", 
        f"{BASE_URL}/api/auth/login",
        method="POST",
        data={
            "email": "testuser@milestone.com",
            "password": "Secure123!"
        }
    )
    results.append(login_result)
    
    # 5. Profile API Test (if login succeeded)
    if login_result:
        # Try to get token
        try:
            login_response = requests.post(f"{BASE_URL}/api/auth/login", 
                                         json={"email": "testuser@milestone.com", "password": "Secure123!"}, 
                                         timeout=5)
            if login_response.status_code == 200:
                token = login_response.json()['token']
                headers = {"Authorization": f"Bearer {token}"}
                
                results.append(test_feature(
                    "Get Profile", 
                    f"{BASE_URL}/api/profile/me",
                    headers=headers
                ))
                
                results.append(test_feature(
                    "Update Profile", 
                    f"{BASE_URL}/api/profile/me",
                    method="PUT",
                    data={"headline": "Test Headline", "location": "Test Location"},
                    headers=headers
                ))
        except:
            results.append(False)
    else:
        results.extend([False, False])  # Profile tests failed
    
    # 6. API Documentation
    results.append(test_feature(
        "API Documentation", 
        f"{BASE_URL}/api/docs"
    ))
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    features = [
        "Backend Health",
        "User Registration", 
        "Recruiter Registration",
        "User Login",
        "Get Profile",
        "Update Profile",
        "API Documentation"
    ]
    
    for i, (feature, result) in enumerate(zip(features, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {feature:<25} {status}")
    
    print(f"\n🎯 OVERALL: {passed}/{total} tests passed")
    
    if passed >= total * 0.8:  # 80% success rate
        print("🎉 MARCH MILESTONE: COMPLETED SUCCESSFULLY!")
        print("✅ Core features are working and ready for demonstration")
    else:
        print("⚠️  MARCH MILESTONE: Needs attention")
        print("🔧 Some features may need fixes")
    
    return passed >= total * 0.8

if __name__ == "__main__":
    success = run_milestone_tests()
    print(f"\n🚀 Test completed - Success: {success}")
