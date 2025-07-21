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

2. **Access the app**
   - **API**: http://localhost:8000/api/
   - **Admin**: http://localhost:8000/admin/ (admin@example.com / adminpassword)

💡 **Note**: Everything is automatic! Placeholder images, database setup, and static files are created during container startup.

## ✨ Features

- 🔐 **JWT Authentication** with email verification
- 🎥 **Automatic Video Processing** (480p, 720p, 1080p HLS segments)
- 📱 **HLS Streaming** with seamless quality switching
- ⚡ **Background Processing** with Redis Queue
- 🖼️ **Real Video Thumbnails** extracted from video frames
- 🎯 **Quality-Specific Streaming** - each resolution served independently

## 📡 Key API Endpoints

```bash
# Authentication
POST /api/register/           # Register user
POST /api/login/              # Login
GET  /api/activate/<token>/   # Activate account

# Videos
GET  /api/video/                        # List videos
GET  /api/video/<id>/                   # Video details  
GET  /api/video/<id>/<resolution>/index.m3u8  # HLS streaming
```

## 🎬 Video Upload & Processing

### Automatic Thumbnail Generation
- **Real thumbnails**: Extracted automatically from uploaded videos at 2-second mark
- **High-quality frames**: Actual video frames, not generic placeholders  
- **Automatic fallback**: Generic placeholder only if video frame extraction fails
- **No manual setup needed**: Everything works out of the box!

### Upload Process
1. Go to **Admin Panel**: http://localhost:8000/admin/
2. **Videos** → **Add Video** → Upload file
3. **Automatic processing** starts in background:
   - Real thumbnail extraction from video frames
   - Quality-specific HLS generation (480p, 720p, 1080p)
   - Separate streaming segments for each resolution
4. Video appears in frontend when `is_processed=True`

⏳ **Processing Time Notice:**
- **Small videos** (~100MB): 2-5 minutes
- **Large videos** (~1GB+): 10-30 minutes  
- **Processing creates**: Quality-specific HLS segments (480p: ~10MB, 720p: ~47MB, 1080p: ~150MB)
- **Status**: Check `is_processed` field in admin panel
- **Debug**: View processing logs with `docker-compose logs web`

💡 **Tip**: Videos are only visible in the frontend after processing completes!

## 🎯 Quality Switching & HLS Streaming

### How Resolution Switching Works
- Each video is processed into **3 separate HLS streams**:
  - **480p**: Low bandwidth (~400kbps) for mobile/slow connections
  - **720p**: Medium quality (~2Mbps) for standard streaming  
  - **1080p**: High definition (~6Mbps) for premium experience

### API Endpoints for Each Quality
```bash
GET /api/video/1/480p/index.m3u8   # 480p HLS manifest
GET /api/video/1/720p/index.m3u8   # 720p HLS manifest  
GET /api/video/1/1080p/index.m3u8  # 1080p HLS manifest
```

### Quality Differences (Example)
- **480p**: ~10MB total (27 segments) - Perfect for mobile
- **720p**: ~47MB total (27 segments) - Standard HD experience
- **1080p**: ~150MB total (27 segments) - Premium quality

**Frontend Integration**: Use HLS.js to switch between qualities seamlessly!

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| Resolution switching not working | Quality-specific HLS segments are created automatically during processing |
| Videos not processing | Check logs: `docker-compose logs web` |
| Can't login after registration | Check activation email in `emails/` folder |
| Thumbnail not showing | Real thumbnails are extracted during video processing |

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