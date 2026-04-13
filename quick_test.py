"""
Quick test to verify backend is working
"""
import requests
import time

def test_backend():
    try:
        print("Testing backend health...")
        response = requests.get("http://localhost:8000/api/health", timeout=3)
        if response.status_code == 200:
            print("✅ Backend is running!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ Backend returned status: {response.status_code}")
            return False
    except requests.exceptions.Timeout:
        print("⏰ Backend request timed out")
        return False
    except requests.exceptions.ConnectionError:
        print("🔌 Backend not available")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Quick Backend Test")
    print("=" * 30)
    
    # Test multiple times
    for i in range(3):
        print(f"\nAttempt {i+1}:")
        if test_backend():
            break
        if i < 2:
            print("Waiting 2 seconds...")
            time.sleep(2)
    
    print("\n🎯 Test complete!")
