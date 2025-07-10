# VideoFlix Backend

A Django REST API for video streaming with HLS delivery, JWT authentication, and email verification.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- FFmpeg (for video processing)

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd videoflix
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Environment setup**
   ```bash
   cp .env.template .env
   # Edit .env with your database settings
   ```

3. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Run server**
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://127.0.0.1:8000/api/`

## 🔧 Configuration

### Required Environment Variables (.env)
```env
# Database
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=supersecretpassword
DB_HOST=localhost
DB_PORT=5432

# Frontend URL (for email links)
FRONTEND_URL=http://127.0.0.1:5500

# Email (optional - defaults to console)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Frontend Integration
Add your frontend URL to CORS settings in `core/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5500",  # Your frontend URL
]
```

## 📡 API Endpoints

### Authentication
- `POST /api/register/` - User registration
- `GET /api/activate/<uidb64>/<token>/` - Email verification
- `POST /api/login/` - Login (sets HttpOnly cookies)
- `POST /api/logout/` - Logout
- `POST /api/password_reset/` - Request password reset
- `POST /api/password_confirm/<uidb64>/<token>/` - Reset password

### Videos
- `GET /api/video/` - List videos
- `GET /api/video/<id>/<resolution>/index.m3u8` - HLS manifest
- `GET /api/video/<id>/<resolution>/<segment>` - HLS segments

## 🎬 Video Processing

### Add Sample Videos
```bash
python manage.py add_sample_videos --download
```

### Convert to HLS
```bash
# Convert all videos
python manage.py convert_to_hls --all

# Convert specific video  
python manage.py convert_to_hls --video-id 1
```

### Manual User Activation
```bash
python manage.py activate_user --email user@example.com --activate
```

## 🔐 Authentication Flow

1. User registers → receives activation email
2. User clicks activation link → account activated
3. User logs in → receives JWT cookies
4. Protected endpoints require valid JWT

**Note**: Emails are printed to console in development mode.

## 🛠️ Development

### Project Structure
```
videoflix/
├── authentication/     # User auth & JWT
├── videos/            # Video management & HLS
├── content/           # Static content
├── core/             # Django settings
├── templates/        # Email templates
└── manage.py
```

### Testing
```bash
# Run tests
python manage.py test

# Test registration flow
python manage.py shell
>>> from authentication.api.views import *
```

## 🐳 Docker Deployment

```bash
docker-compose up --build
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| CORS errors | Add frontend URL to `CORS_ALLOWED_ORIGINS` |
| Email not working | Check console output for development |
| Video streaming fails | Ensure FFmpeg is installed and videos are processed |
| Authentication issues | Check JWT cookies are being set |

## 📝 Key Features

- ✅ Email-based authentication (no username)
- ✅ JWT with HttpOnly cookies
- ✅ HLS video streaming
- ✅ Email verification & password reset
- ✅ FFmpeg video processing
- ✅ PostgreSQL database
- ✅ CORS-enabled API

## 📚 Documentation

- **API Docs**: Visit `/api/` in browser for interactive docs
- **Admin Panel**: Visit `/admin/` for Django admin
- **Email Templates**: Located in `templates/emails/`