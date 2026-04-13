#!/usr/bin/env python3
"""
Test script to verify backend API is working
"""
import requests
import json
from urllib3.exceptions import InsecureRequestWarning

# Disable SSL warnings for self-signed certificate
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

API_BASE = "https://localhost:8000/api"

def test_health_check():
    """Test health check endpoint"""
    print("🏥 Testing health check endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", verify=False)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   Status: {data['status']}")
            print(f"   App: {data['app']}")
            print(f"   Version: {data['version']}")
            print(f"   HTTPS: {data['https']}")
            return True
        else:
            print(f"❌ Health check failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

def test_root_endpoint():
    """Test root endpoint"""
    print("\n📍 Testing root endpoint...")
    try:
        response = requests.get(f"{API_BASE}/", verify=False)
        if response.status_code == 200:
            data = response.json()
            print("✅ Root endpoint passed!")
            print(f"   Message: {data['message']}")
            return True
        else:
            print(f"❌ Root endpoint failed with status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint failed: {str(e)}")
        return False

def test_https():
    """Test HTTPS connection"""
    print("\n🔒 Testing HTTPS connection...")
    try:
        response = requests.get(f"{API_BASE}/health", verify=False)
        if response.url.startswith("https://"):
            print("✅ HTTPS is working!")
            print(f"   URL: {response.url}")
            return True
        else:
            print(f"❌ HTTPS not working, got: {response.url}")
            return False
    except Exception as e:
        print(f"❌ HTTPS test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Backend API Test Suite")
    print("=" * 60)
    
    results = []
    results.append(("Health Check", test_health_check()))
    results.append(("Root Endpoint", test_root_endpoint()))
    results.append(("HTTPS", test_https()))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("-" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is ready.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
