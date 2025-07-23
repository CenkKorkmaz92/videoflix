# 🎬 VideoFlix - Full-Stack Demo

A complete full-stack video streaming application with Django REST API backend and vanilla JavaScript frontend, featuring JWT authentication, email verification, and automatic video processing.

## 🌟 Complete Demo

This repository contains **both frontend and backend** for a comprehensive demonstration of:
- **Backend**: Django REST API with advanced video processing (custom implementation)
- **Frontend**: Responsive vanilla JavaScript SPA (provided by Developer Akademie)
- **Full Integration**: Complete user registration → video upload → streaming workflow

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

2. **Access the complete application**
   - **Frontend**: http://localhost:8000/ (Main application interface)
   - **API**: http://localhost:8000/api/ (REST API endpoints)
   - **Admin**: http://localhost:8000/admin/ (admin@example.com / adminpassword)

💡 **Note**: Everything is automatic! The application includes placeholder images, database setup, sample data, and static file serving during container startup.

## ✨ Full-Stack Features

### Backend (Django REST API)
- 🔐 **JWT Authentication** with email verification
- 🎥 **Automatic Video Processing** (480p, 720p, 1080p HLS segments)
- 📱 **HLS Streaming** with seamless quality switching
- ⚡ **Background Processing** with Redis Queue
- 🖼️ **Real Video Thumbnails** extracted from video frames
- 🎯 **Quality-Specific Streaming** - each resolution served independently

### Frontend (Vanilla JavaScript SPA - Developer Akademie)
- 📱 **Responsive Design** for all screen sizes
- 🎨 **Modern UI/UX** with smooth animations
- 🔐 **Complete Auth Flow** (register, login, email verification)
- 🎥 **Video Upload Interface** with progress tracking
- 📺 **Advanced Video Player** with quality selection
- 🎛️ **User Dashboard** for video management

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

### Backend
- **Framework**: Django 5.2.4 + Django REST Framework
- **Database**: PostgreSQL with Docker volumes
- **Queue**: Redis + RQ for background processing
- **Video**: FFmpeg + HLS.js for streaming
- **Auth**: JWT tokens with email verification

### Frontend  
- **Core**: Vanilla JavaScript ES6+ (no build tools required)
- **Styling**: CSS3 with CSS Grid/Flexbox
- **Architecture**: Single Page Application (SPA)
- **Video Player**: HLS.js integration for adaptive streaming
- **Responsive**: Mobile-first design approach
- **Source**: Provided by Developer Akademie

### Infrastructure
- **Deployment**: Docker Compose multi-container setup
- **Reverse Proxy**: Django serves both API and frontend
- **File Storage**: Docker volumes for persistent data
- **Development**: Hot-reload ready environment

## 🏗️ Frontend Architecture (Developer Akademie)

### File Structure
```
📁 Frontend (Vanilla JavaScript SPA)
├── index.html              # Main entry point
├── styles.css              # Global styles
├── script.js               # Main application logic
├── 📁 assets/              # Images, icons, media
├── 📁 pages/               # Page-specific components
│   ├── auth/               # Login/Register pages
│   ├── videos/             # Video listing/details
│   └── user/               # User dashboard
└── 📁 shared/              # Reusable components
    ├── css/                # Shared stylesheets
    └── js/                 # Shared JavaScript modules
```

### Key Frontend Features
- **🔐 Authentication Flow**: Complete registration → email verification → login
- **🎥 Video Management**: Upload, view, delete with progress tracking  
- **📱 Adaptive Player**: HLS.js with quality switching (480p/720p/1080p)
- **🎨 Responsive Design**: Works on desktop, tablet, and mobile
- **⚡ Real-time Updates**: Dynamic content loading via REST API

### Integration Points
- **API Communication**: Fetch API with JWT token handling
- **File Uploads**: Multipart form data with progress tracking
- **Video Streaming**: Direct HLS manifest consumption
- **User Feedback**: Toast notifications and loading states

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

**VideoFlix - Complete Full-Stack Video Streaming Platform** 🎬🚀  
*Backend: Custom Django REST API implementation*  
*Frontend: Professional UI provided by Developer Akademie*