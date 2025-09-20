"""
Quick test for the deployed Railway server
"""
import requests
import json

def test_deployed_server():
    base_url = "https://web-production-7380.up.railway.app"
    
    print("🚀 Testing Deployed Railway Server")
    print("=" * 45)
    print(f"Server URL: {base_url}")
    print()
    
    tests = [
        ("Home", "/"),
        ("Health Check", "/health"),
        ("Version API", "/api/version?version=1.0.0"),
        ("Stats", "/api/stats")
    ]
    
    for name, endpoint in tests:
        print(f"Testing {name} ({endpoint})...")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)
            print(f"  ✅ Status: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"  📄 Response: {json.dumps(data, indent=2)[:200]}...")
                except:
                    print(f"  📄 Response: {response.text[:100]}...")
            print()
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error: {e}")
            print()
    
    print("=" * 45)
    print("🎯 Test complete!")

if __name__ == "__main__":
    test_deployed_server()