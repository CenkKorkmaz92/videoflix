# Videoflix Login API Testing - Postman Collection

## Overview
This Postman collection provides comprehensive testing for the Videoflix login endpoint (`POST /api/login/`) with complete coverage of all possible status codes and scenarios.

## Collection File
- **File**: `Videoflix_Login_Complete_Tests.postman_collection.json`
- **Tests**: 20+ test scenarios covering happy paths, error cases, security, and edge cases

## Test Categories

### ✅ Happy Paths (200 Status Codes)
- **Successful Login**: Valid credentials, JWT tokens, HttpOnly cookies

### ❌ Unhappy Paths (400 Status Codes)
- **Invalid Credentials**: Wrong password, nonexistent user
- **Missing Fields**: Missing email, missing password, empty body
- **Invalid Data**: Invalid email format, inactive users
- **Malformed Requests**: Invalid JSON syntax

### 🚫 Method Errors (405 Status Codes)
- **Unsupported Methods**: GET, PUT, DELETE requests

### 📝 Content Type Errors (400/415 Status Codes)
- **Unsupported Media Types**: Form data instead of JSON
- **Invalid JSON**: Malformed request bodies

### 🔒 Security & Edge Cases
- **SQL Injection**: Tests for SQL injection vulnerability
- **XSS Attacks**: Tests for cross-site scripting protection
- **Input Validation**: Long inputs, Unicode characters
- **Performance**: Response time validation

## Prerequisites

### 1. Start Docker Services
```bash
docker-compose up db redis -d
```

### 2. Start Django Server
```bash
python manage.py runserver
```

### 3. Verify Test User Exists
```python
# Create test user if needed
python -c "
import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings'); 
import django; django.setup(); 
from django.contrib.auth import get_user_model; 
User = get_user_model(); 
user, created = User.objects.get_or_create(
    email='test@example.com', 
    defaults={'first_name': 'Test', 'last_name': 'User'}
); 
user.set_password('TestPass123'); 
user.is_active = True; 
user.is_email_verified = True; 
user.save(); 
print(f'Test user {'created' if created else 'updated'}')
"
```

### 4. Run Pre-Test Verification (Optional)
```bash
python test_login_api.py
```

## Import Instructions

### In Postman:
1. Open Postman
2. Click **Import** button
3. Select **Upload Files**
4. Choose `Videoflix_Login_Complete_Tests.postman_collection.json`
5. Click **Import**

### Configure Variables:
The collection includes these variables (pre-configured):
- `base_url`: `http://localhost:8000`
- `api_base`: `{{base_url}}/api`
- `test_email`: `test@example.com`
- `test_password`: `TestPass123`

## Running Tests

### Individual Tests:
- Click on any test in the collection
- Click **Send** to run the test
- View results in the **Test Results** tab

### Run Entire Collection:
1. Right-click on collection name
2. Select **Run collection**
3. Configure test settings:
   - **Iterations**: 1 (or more for load testing)
   - **Delay**: 100ms between requests
   - **Data File**: None needed
4. Click **Run Videoflix Login Tests**

### View Results:
- **Test Results**: Pass/fail status for each assertion
- **Response**: JSON response data
- **Console**: Detailed logging output
- **Test Scripts**: View assertion details

## Expected Results

### Successful Test Run Should Show:
- ✅ **1/1 tests passing** for 200 status code scenarios
- ✅ **Multiple assertions passing** for each error scenario
- ✅ **No 500 server errors** (indicates backend issues)
- ✅ **JWT cookies properly set** on successful login
- ✅ **Proper error messages** for validation failures

### Test Assertions Include:
- Status code validation
- Response structure validation
- Error message verification
- Cookie security settings
- Response time performance
- Security vulnerability checks

## Troubleshooting

### Common Issues:

**Server Not Running (Connection Refused)**
- Ensure Django server is running: `python manage.py runserver`
- Check Docker services: `docker-compose ps`

**Test User Not Found (400 Errors)**
- Run the user creation script above
- Verify PostgreSQL database is connected

**Unexpected 500 Errors**
- Check Django server logs
- Verify all migrations applied: `python manage.py migrate`
- Check database connection

**Cookie Tests Failing**
- Verify JWT settings in `core/settings.py`
- Check `SIMPLE_JWT` configuration

## Security Test Notes

The collection includes security tests for:
- **SQL Injection**: Attempts should be blocked (400 status)
- **XSS Prevention**: Script tags should be sanitized
- **Input Validation**: Long/invalid inputs should be rejected
- **Authentication**: Inactive users should be denied access

All security tests should **fail to exploit** the system (return 400/401 errors).

## Performance Benchmarks

Expected response times:
- **Login Requests**: < 1000ms
- **Error Responses**: < 500ms
- **Method Errors**: < 200ms

## Additional Testing

For extended testing, consider:
- **Load Testing**: Run collection with multiple iterations
- **Stress Testing**: High concurrent user simulation
- **Integration Testing**: Test with real frontend application
- **Automated CI/CD**: Include collection in deployment pipeline

## API Documentation Reference

This collection tests the login endpoint as specified in the API documentation:
- **URL**: `POST /api/login/`
- **Success Response**: `200` with JWT tokens and user info
- **Error Responses**: `400` for validation errors, `405` for method errors
- **Cookies**: HttpOnly `access_token` and `refresh_token`
