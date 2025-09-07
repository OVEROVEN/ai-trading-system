#!/usr/bin/env python3
"""
Debug script to test frontend-backend network communication
"""

import requests
import json
import time

def test_network_connection():
    """Test network connectivity between frontend and backend"""
    print("🔍 Frontend-Backend Network Debug Test")
    print("=" * 50)
    
    # Test configurations
    backend_url = "http://localhost:8000"
    frontend_url = "http://localhost:3000"
    
    print("\n1. 🌐 Testing Backend API Health...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend API is healthy")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend API returned {response.status_code}")
    except Exception as e:
        print(f"❌ Backend API connection failed: {e}")
        return False
    
    print("\n2. 🎯 Testing Frontend Accessibility...")
    try:
        response = requests.get(frontend_url, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend is accessible")
        else:
            print(f"❌ Frontend returned {response.status_code}")
    except Exception as e:
        print(f"❌ Frontend connection failed: {e}")
    
    print("\n3. 🔐 Testing Authentication Endpoint...")
    try:
        # Test redemption endpoint without auth (should return 403)
        response = requests.post(
            f"{backend_url}/api/redemption/redeem",
            json={"code": "WEILIANG10"},
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 403:
            print("✅ Authentication protection working correctly")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Redemption endpoint test failed: {e}")
    
    print("\n4. 🔍 Testing CORS Headers...")
    try:
        response = requests.options(f"{backend_url}/api/redemption/redeem", timeout=5)
        print(f"   OPTIONS response: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
    except Exception as e:
        print(f"❌ CORS preflight test failed: {e}")
    
    print("\n5. 📡 Testing Cross-Origin Request Simulation...")
    try:
        # Simulate a request from the frontend
        headers = {
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        response = requests.post(
            f"{backend_url}/api/redemption/redeem",
            json={"code": "WEILIANG10"},
            headers=headers,
            timeout=5
        )
        print(f"   Cross-origin response: {response.status_code}")
        if "Access-Control-Allow-Origin" in response.headers:
            print(f"   ✅ CORS headers present: {response.headers['Access-Control-Allow-Origin']}")
        else:
            print("   ❌ No CORS headers found")
    except Exception as e:
        print(f"❌ Cross-origin test failed: {e}")
    
    print("\n6. ⚡ Testing API Response Time...")
    try:
        start_time = time.time()
        response = requests.get(f"{backend_url}/health", timeout=10)
        response_time = (time.time() - start_time) * 1000
        print(f"   Response time: {response_time:.2f}ms")
        if response_time > 5000:
            print("   ⚠️ Slow response time may cause frontend timeouts")
        else:
            print("   ✅ Response time is acceptable")
    except Exception as e:
        print(f"❌ Response time test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Network Test Complete")
    
    print("\n📋 Potential Issues to Check:")
    print("1. Browser console errors (F12 > Console)")
    print("2. Network tab for failed requests (F12 > Network)")
    print("3. CORS configuration in backend")
    print("4. Frontend API endpoint configuration")
    print("5. Authentication state in frontend")
    
    print(f"\n🌐 Access URLs:")
    print(f"   Frontend: {frontend_url}")
    print(f"   Backend API: {backend_url}/docs")
    
    return True

if __name__ == "__main__":
    test_network_connection()