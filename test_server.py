"""
Test script for the production update server
"""
import requests
import json

def test_server():
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Production Update Server")
    print("=" * 40)
    
    # Test home endpoint
    print("\n1. Testing Home Endpoint (/)")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test version endpoint
    print("\n2. Testing Version Endpoint (/api/version)")
    try:
        response = requests.get(f"{base_url}/api/version?version=1.0.0")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test health endpoint
    print("\n3. Testing Health Endpoint (/health)")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    # Test stats endpoint
    print("\n4. Testing Stats Endpoint (/api/stats)")
    try:
        response = requests.get(f"{base_url}/api/stats")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"   ERROR: {e}")
    
    print("\n" + "=" * 40)
    print("✅ Server testing complete!")

if __name__ == "__main__":
    test_server()