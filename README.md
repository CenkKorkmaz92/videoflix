# 🎬 VideoFlix Backend API

A modern Django REST API for video streaming platform with JWT authentication, email verification, and HLS video processing.

## 🚀 Quick Start

### Prerequisites
- **Docker & Docker Compose**
  - Windows: [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)
  - Mac: [Docker Desktop](https://docs.docker.com/desktop/install/mac-install/)
  - Linux: [Docker Engine](https://docs.docker.com/engine/install/) + [Docker Compose](https://docs.docker.com/compose/install/)

### 🐳 Setup with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/CenkKorkmaz92/videoflix.git
   cd videoflix
   ```

2. **Create environment file**
   ```bash
   # Linux/Mac
   cp .env.template .env
   
   # Windows (Command Prompt)
   copy .env.template .env
   
   # Windows (PowerShell)
   Copy-Item .env.template .env
   ```

3. **Start all services**
   ```bash
   docker-compose up --build
   ```

4. **Wait for services to start**
   ```bash
   # The containers will automatically:
   # - Set up the database
   # - Run migrations  
   # - Create admin user (admin@example.com/adminpassword)
   # - Start the API server
   ```

5. **Add sample videos (optional)**
   ```bash
   docker-compose exec web python manage.py add_sample_videos --download
   ```

6. **Access the API**
   - **API**: http://localhost:8000/api/
   - **Admin Panel**: http://localhost:8000/admin/ (admin@example.com/adminpassword)
   - **API Documentation**: http://localhost:8000/api/ (browsable API)

## 🎯 API Features

- ✅ **User Authentication** - JWT with email verification
- ✅ **Video Management** - Upload, process, stream videos
- ✅ **HLS Streaming** - Adaptive quality streaming
- ✅ **Email System** - Account activation & password reset
- ✅ **Admin Interface** - Video and user management
- ✅ **Background Tasks** - Video processing with Redis/RQ

## 📡 API Endpoints

### Authentication
```
POST /api/register/           # User registration
GET  /api/activate/<token>/   # Email verification
POST /api/login/              # User login
POST /api/logout/             # User logout
POST /api/password_reset/     # Request password reset
```

### Videos
```
GET  /api/video/                    # List all videos
GET  /api/video/<id>/              # Video details
GET  /api/video/<id>/<quality>/    # HLS streaming endpoints
```

##  Email Verification System

**For Testing/Evaluation**: Emails are saved as files in the `emails/` folder.

### How to activate user accounts:
1. User registers via API
2. Check `emails/` folder for activation email (.log file)
3. Find activation link in email content
4. Visit link: `http://localhost:8000/api/activate/{token}`

### Quick activation via Django shell:
```bash
docker-compose exec web python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> user = User.objects.get(email='test@example.com')
>>> user.is_active = True
>>> user.is_email_verified = True
>>> user.save()
```

## 🛠️ Project Structure

```
videoflix/
├── authentication/       # User auth & JWT
├── videos/              # Video management & HLS
├── content/             # Static content management
├── core/                # Django settings & config
├── templates/           # Email templates
├── docker-compose.yml   # Docker services
└── requirements.txt     # Python dependencies
```

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **Environment variable errors** | Make sure you copied `.env.template` to `.env` (use correct command for your OS) |
| **"cp command not found" (Windows)** | Use `copy .env.template .env` instead of `cp` |
| **Database connection error** | Restart containers: `docker-compose restart` |
| **User can't login after registration** | Check `emails/` folder for activation link |
| **Video processing fails** | Ensure FFmpeg is available in Docker container |
| **Redis connection error** | Restart containers: `docker-compose restart` |
| **Permission denied errors** | Check Docker file permissions |

## 🔒 Security Features

- JWT tokens with HttpOnly cookies
- Email verification required
- CORS protection
- Environment-based secrets
- Password strength validation

## 💾 Tech Stack

- **Backend**: Django 5.2.4, Django REST Framework
- **Database**: PostgreSQL
- **Cache/Queue**: Redis, Django-RQ
- **Authentication**: JWT (SimpleJWT)
- **Video Processing**: FFmpeg, HLS
- **Deployment**: Docker, Gunicorn

## 📝 Testing

```bash
# Run tests inside Docker container
docker-compose exec web pytest

# With coverage
docker-compose exec web pytest --cov=.
```

## 🚀 Production Deployment

1. Set environment variables for production
2. Use PostgreSQL database
3. Configure email backend (SMTP)
4. Set `DEBUG=False`
5. Configure static files serving
6. Use Gunicorn with reverse proxy

---

**Backend API for VideoFlix streaming platform** 🎬