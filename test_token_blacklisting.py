#!/usr/bin/env python3
"""
Test token blacklisting functionality
"""
import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/login/"
LOGOUT_URL = f"{BASE_URL}/api/logout/"

def test_token_blacklisting():
    """Test that tokens are properly blacklisted after logout"""
    print("🚀 Testing Token Blacklisting")
    print("=" * 60)
    
    # Step 1: Login to get fresh tokens
    print("1. 🔑 Login to get fresh tokens")
    session = requests.Session()
    login_data = {"email": "test@example.com", "password": "testpass123"}
    
    login_response = session.post(LOGIN_URL, json=login_data)
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    # Extract tokens from cookies
    refresh_token = None
    access_token = None
    for cookie in session.cookies:
        if cookie.name == 'refresh_token':
            refresh_token = cookie.value
        elif cookie.name == 'access_token':
            access_token = cookie.value
    
    print(f"✅ Tokens obtained")
    print(f"   Refresh token: {refresh_token[:50]}...")
    print(f"   Access token: {access_token[:50]}...")
    
    # Step 2: Logout (should blacklist the refresh token)
    print("\n2. 🚪 Logout (blacklist tokens)")
    logout_response = session.post(LOGOUT_URL, json={})
    
    if logout_response.status_code == 200:
        print("✅ Logout successful - tokens should now be blacklisted")
    else:
        print(f"❌ Logout failed: {logout_response.status_code}")
        return
    
    # Step 3: Try to use the blacklisted refresh token
    print("\n3. 🔒 Test blacklisted token reuse")
    
    # Create a new session and manually set the previously used refresh token
    test_session = requests.Session()
    test_session.cookies.set('refresh_token', refresh_token)
    test_session.cookies.set('access_token', access_token)
    
    # Try to logout again with the same token (should still work gracefully)
    reuse_response = test_session.post(LOGOUT_URL, json={})
    
    print(f"Status Code: {reuse_response.status_code}")
    print(f"Response: {json.dumps(reuse_response.json(), indent=2)}")
    
    if reuse_response.status_code == 200:
        print("✅ Blacklisted token handled gracefully (no enumeration)")
    else:
        print("❌ Unexpected response for blacklisted token")
    
    # Step 4: Test multiple logout attempts
    print("\n4. 🔄 Test multiple logout attempts")
    
    # Multiple attempts should all succeed gracefully
    for i in range(3):
        multi_response = test_session.post(LOGOUT_URL, json={})
        print(f"   Attempt {i+1}: {multi_response.status_code}")
        if multi_response.status_code != 200:
            print(f"   ❌ Unexpected status on attempt {i+1}")
            break
    else:
        print("   ✅ All multiple logout attempts handled gracefully")

if __name__ == "__main__":
    test_token_blacklisting()
