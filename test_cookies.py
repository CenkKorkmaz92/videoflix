#!/usr/bin/env python3
"""
Simple script to test login endpoint cookies
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login/"

def test_login_cookies():
    """Test the login endpoint and inspect cookies"""
    print("🚀 Testing Login Cookies")
    print("=" * 50)
    
    # Valid login test
    valid_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    print(f"POST {LOGIN_URL}")
    print(f"Body: {json.dumps(valid_data, indent=2)}")
    print("-" * 50)
    
    response = requests.post(LOGIN_URL, json=valid_data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print("-" * 50)
    
    # Check cookies
    print("🍪 COOKIES:")
    if response.cookies:
        for cookie in response.cookies:
            print(f"  {cookie.name} = {cookie.value}")
            print(f"    httponly: {cookie.has_nonstandard_attr('httponly')}")
            print(f"    secure: {cookie.secure}")
            print(f"    samesite: {cookie.get_nonstandard_attr('samesite')}")
            print()
    else:
        print("  No cookies found")
    
    # Check headers
    print("📋 HEADERS:")
    for header, value in response.headers.items():
        if 'cookie' in header.lower() or 'set-cookie' in header.lower():
            print(f"  {header}: {value}")
    
    # Test failed login
    print("\n" + "=" * 50)
    print("❌ Testing Failed Login")
    print("=" * 50)
    
    invalid_data = {
        "email": "test@example.com",
        "password": "wrongpassword"
    }
    
    response_fail = requests.post(LOGIN_URL, json=invalid_data)
    print(f"Status Code: {response_fail.status_code}")
    print(f"Response: {json.dumps(response_fail.json(), indent=2)}")
    
    print("🍪 COOKIES:")
    if response_fail.cookies:
        for cookie in response_fail.cookies:
            print(f"  {cookie.name} = {cookie.value}")
    else:
        print("  No cookies found (expected)")

if __name__ == "__main__":
    test_login_cookies()
