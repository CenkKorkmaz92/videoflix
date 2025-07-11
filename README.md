# 🎬 VideoFlix

A modern video streaming platform with Django REST API backend and vanilla JavaScript frontend, featuring HLS video streaming, JWT authentication, and email verification.

## 🚀 Quick Start

### Prere## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **User can't log in after registration** | Check `emails/` folder for activation link and activate account |
| **No activation email found** | Check Django server is running and registration was successful |
| **Activation link doesn't work** | Use backend API: `http://127.0.0.1:8000/api/activate/{uidb64}/{token}` |
| **"Account already activated" message** | User is already active, can proceed to login |
| CORS errors | Check `CORS_ALLOWED_ORIGINS` in settings |
| Email not sending (production) | Check SMTP settings and email credentials |
| Video won't play | Ensure FFmpeg is installed for processing |
| Database connection failed | Make sure PostgreSQL is running |
| Permission denied | Check file permissions for media folder |
- Docker & Docker Compose
- Python 3.8+ (for local development)
- Git

### 🐳 Option 1: Docker Setup (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/CenkKorkmaz92/videoflix.git
   cd videoflix
   ```

2. **Start with Docker**
   ```bash
   docker-compose up --build
   ```

3. **Setup database**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Access the application**
   - Frontend: `http://localhost:5500` (open `index.html` in browser)
   - Backend API: `http://localhost:8000/api/`
   - Admin Panel: `http://localhost:8000/admin/`

### 💻 Option 2: Local Development

1. **Clone and setup environment**
   ```bash
   git clone https://github.com/CenkKorkmaz92/videoflix.git
   cd videoflix
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

2. **Create environment file**
   ```bash
   # Create .env file
   echo SECRET_KEY=django-insecure-school-project-key-12345 > .env
   echo DEBUG=True >> .env
   ```

3. **Start services**
   ```bash
   # Start PostgreSQL and Redis
   docker-compose up -d db redis
   
   # Run migrations
   python manage.py migrate
   python manage.py createsuperuser
   
   # Start Django server
   python manage.py runserver
   ```

4. **Open frontend**
   - Open `index.html` in your browser or use Live Server extension

## 🎯 Features

- ✅ **User Authentication**: Email-based registration with JWT tokens
- ✅ **Video Streaming**: HLS adaptive streaming with quality selection
- ✅ **Email Verification**: Account activation via email
- ✅ **Password Reset**: Secure password recovery
- ✅ **Video Upload**: Admin interface for video management
- ✅ **Responsive Design**: Works on desktop and mobile
- ✅ **Docker Ready**: One-command deployment

## � Email Verification (For Testers)

**Important**: In development mode, emails are NOT sent to real email addresses. Instead, they are saved as files for testing purposes.

### 🔍 How to Activate User Accounts

When someone registers on the frontend:

1. **Registration creates user** but account is inactive
2. **Activation email is saved** to `emails/` folder (not sent via email)
3. **Find the activation link** in the email file
4. **Use the link** to activate the account

### 📁 Step-by-Step for Mentors

1. **After user registers**, check the `emails/` folder in the project directory
2. **Open the newest `.log` file** (e.g., `20250711-105026-1906845821520.log`)
3. **Find the activation link** that looks like:
   ```
   http://127.0.0.1:5500/activate/MjY/csrvg2-cef87f410f3f161f00d3d4a9395868c4
   ```
4. **Copy and paste this URL** into your browser
5. **Account is now activated** and user can log in

### 🚀 Alternative: Direct Backend Activation

You can also activate via the backend API:
```
http://127.0.0.1:8000/api/activate/MjY/csrvg2-cef87f410f3f161f00d3d4a9395868c4
```

### ⚡ Quick Test Commands

```bash
# Manually activate any user via Django shell
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='test@example.com')
>>> user.is_active = True
>>> user.is_email_verified = True
>>> user.save()
```

### 📧 Email Configuration Options

Current setup (in `settings.py`):
```python
# Option 1: Save emails as files (current)
EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'

# Option 2: Print emails to console (alternative)
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Option 3: Send real emails (production only)
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
```

**For console output**: Change to `console.EmailBackend` and emails will appear in the Django server terminal.

---

## �🔧 Configuration

### Environment Variables (.env)
```env
# Required
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database (when using Docker)
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=supersecretpassword
DB_HOST=localhost
DB_PORT=5432

# Frontend URL
FRONTEND_URL=http://127.0.0.1:5500
```

### Adding Sample Videos
```bash
# Add sample videos
python manage.py add_sample_videos --download

# Convert to HLS format
python manage.py convert_to_hls --all
```

## 📡 API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `GET /api/activate/<uidb64>/<token>/` - Email verification  
- `POST /api/login/` - Login
- `POST /api/logout/` - Logout
- `POST /api/password_reset/` - Request password reset

### Videos
- `GET /api/video/` - List all videos
- `GET /api/video/<id>/<resolution>/index.m3u8` - HLS manifest
- `GET /api/video/<id>/<resolution>/<segment>` - HLS segments

## 🛠️ Development

### Project Structure
```
videoflix/
├── backend/
│   ├── authentication/    # User auth & JWT
│   ├── videos/           # Video management & HLS
│   ├── content/          # Static content
│   └── core/            # Django settings
├── frontend/
│   ├── pages/           # Individual pages
│   ├── shared/          # Shared CSS/JS
│   └── assets/          # Images, icons
├── docker-compose.yml   # Docker services
└── requirements.txt     # Python dependencies
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-django pytest-cov

# Run tests with coverage
pytest

# Check code quality
flake8
```

## � Security Features

- JWT tokens with HttpOnly cookies
- CSRF protection
- Environment-based secrets
- Email verification required
- Password strength validation

## � Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS errors | Check `CORS_ALLOWED_ORIGINS` in settings |
| Email not sending | Check console output (development mode) |
| Video won't play | Ensure FFmpeg is installed for processing |
| Database connection failed | Make sure PostgreSQL is running |
| Permission denied | Check file permissions for media folder |

## � Tech Stack

- **Backend**: Django 5.2.4, PostgreSQL, Redis
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Video**: FFmpeg, HLS.js
- **Authentication**: JWT with SimpleJWT
- **Deployment**: Docker, Docker Compose

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## � License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Made with ❤️ for learning Django and modern web development**