# 🎬 VideoFlix Backend API

A modern Django REST API for video streaming with JWT authentication, email verification, and automatic video processing.

## 🚀 Quick Start

### Prerequisites
- [Docker Desktop](https://docs.docker.com/desktop/)

### Setup
1. **Clone and start**
   ```bash
   git clone https://github.com/CenkKorkmaz92/videoflix.git
   cd videoflix
   copy .env.template .env
   docker-compose up --build
   ```

2. **Setup static files** (Important!)
   ```bash
   docker-compose exec web python manage.py setup_static_files
   ```

3. **Access the app**
   - **API**: http://localhost:8000/api/
   - **Admin**: http://localhost:8000/admin/ (admin@example.com / adminpassword)

## ✨ Features

- 🔐 **JWT Authentication** with email verification
- 🎥 **Automatic Video Processing** (480p, 720p, 1080p)
- 📱 **HLS Streaming** with quality switching
- ⚡ **Background Processing** with Redis Queue
- 🖼️ **Placeholder Images** for smooth frontend experience

## 📡 Key API Endpoints

```bash
# Authentication
POST /api/register/           # Register user
POST /api/login/              # Login
GET  /api/activate/<token>/   # Activate account

# Videos
GET  /api/video/              # List videos
GET  /api/video/<id>/         # Video details  
GET  /api/video/<id>/stream/  # HLS streaming
```

## 🎬 Video Upload & Processing

1. Go to **Admin Panel**: http://localhost:8000/admin/
2. **Videos** → **Add Video** → Upload file
3. **Automatic processing** starts in background
4. Video appears in frontend when `is_processed=True`

⏳ **Processing Time Notice:**
- **Small videos** (~100MB): 2-5 minutes
- **Large videos** (~1GB+): 10-30 minutes  
- **Processing creates**: 480p, 720p, 1080p HLS segments
- **Status**: Check `is_processed` field in admin panel
- **Debug**: View processing logs with `docker-compose logs worker`

💡 **Tip**: Videos are only visible in the frontend after processing completes!

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Frontend rapid refresh | `docker-compose exec web python manage.py setup_static_files` |
| Videos not processing | Check logs: `docker-compose logs worker` |
| Can't login after registration | Check activation email in `emails/` folder |

## 🛠️ Tech Stack

- **Backend**: Django 5.2.4 + DRF
- **Database**: PostgreSQL  
- **Queue**: Redis + RQ
- **Video**: FFmpeg + HLS
- **Deploy**: Docker

## 📧 Email Setup (Optional)

For real email delivery, add to `.env`:
```bash
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
EMAIL_USE_TLS=True
```

---

**VideoFlix - Netflix-style video streaming backend** 🚀