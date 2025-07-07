#!/usr/bin/env python3
"""
Test script for the logout endpoint
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login/"
LOGOUT_URL = f"{BASE_URL}/api/logout/"

def test_logout_endpoint():
    """Test the logout endpoint with various scenarios"""
    print("🚀 Testing Logout Endpoint")
    print("=" * 60)
    
    # First, login to get valid tokens
    print("1. 🔑 Login to get tokens")
    login_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    session = requests.Session()
    login_response = session.post(LOGIN_URL, json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    print(f"✅ Login successful: {login_response.status_code}")
    print("Cookies received:")
    for cookie in session.cookies:
        print(f"  {cookie.name} = {cookie.value[:50]}...")
    
    print("\n" + "=" * 60)
    print("2. 🚪 Test successful logout")
    
    # Test successful logout
    logout_response = session.post(LOGOUT_URL, json={})
    
    print(f"Status Code: {logout_response.status_code}")
    print(f"Response: {json.dumps(logout_response.json(), indent=2)}")
    
    # Check if cookies are cleared
    print("Cookies after logout:")
    for cookie in session.cookies:
        print(f"  {cookie.name} = {cookie.value}")
    
    print("\n" + "=" * 60)
    print("3. ❌ Test logout without refresh token")
    
    # Test logout without refresh token (new session)
    fresh_session = requests.Session()
    logout_no_token = fresh_session.post(LOGOUT_URL, json={})
    
    print(f"Status Code: {logout_no_token.status_code}")
    print(f"Response: {json.dumps(logout_no_token.json(), indent=2)}")
    
    print("\n" + "=" * 60)
    print("4. 🔄 Test logout with invalid token")
    
    # Test with invalid token by manually setting a bad cookie
    invalid_session = requests.Session()
    invalid_session.cookies.set('refresh_token', 'invalid_token_value')
    logout_invalid = invalid_session.post(LOGOUT_URL, json={})
    
    print(f"Status Code: {logout_invalid.status_code}")
    print(f"Response: {json.dumps(logout_invalid.json(), indent=2)}")
    
    print("\n" + "=" * 60)
    print("5. 🚫 Test with wrong HTTP method")
    
    # Test GET method (should be 405)
    get_response = requests.get(LOGOUT_URL)
    print(f"GET Status Code: {get_response.status_code}")
    
    # Test PUT method (should be 405)
    put_response = requests.put(LOGOUT_URL, json={})
    print(f"PUT Status Code: {put_response.status_code}")

if __name__ == "__main__":
    test_logout_endpoint()
