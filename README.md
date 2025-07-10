# Videoflix

A Django-based video streaming platform with HLS video delivery and JWT authentication.

## Project Overview

This project consists of a Django backend API and an integrated frontend for video streaming. The backend provides user authentication, video management, and HLS (HTTP Live Streaming) video delivery.

## Features

### 🔐 Authentication & Authorization
- **Custom User Model**: Email-based authentication (no username)
- **JWT Cookie Authentication**: HttpOnly cookies for secure token management
- **Email Verification**: Account activation via email links
- **Password Reset**: Secure password reset flow via email

### 🎬 Video Management & Streaming
- **HLS Video Streaming**: Adaptive bitrate streaming with multiple resolutions
- **Video Upload**: Support for video file uploads with FFmpeg processing
- **Automatic HLS Conversion**: Videos are automatically converted to HLS format using mentor's FFmpeg command
- **Genre Classification**: Organize videos by categories
- **Video Metadata**: Title, description, thumbnails, duration tracking

### 🎥 Video API Endpoints
- **GET /api/video/**: List all available videos with metadata
- **GET /api/video/{id}/{resolution}/index.m3u8**: HLS manifest for specific video/resolution
- **GET /api/video/{id}/{resolution}/{segment}**: HLS video segments

### 📹 HLS Video Processing
- **FFmpeg Integration**: Uses mentor's FFmpeg command for HLS conversion
- **Command**: `ffmpeg -i input.mp4 -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls output.m3u8`
- **Automatic Processing**: Videos are automatically converted after upload
- **Management Commands**: Manual video processing and conversion tools

### � Frontend Integration
- **Responsive Design**: Mobile-friendly video streaming interface
- **HLS.js Player**: Modern video player with quality selection
- **Authentication UI**: Registration, login, and activation pages

## Technology Stack

### Backend
- **Framework**: Django 5.2.4 with Django REST Framework
- **Database**: PostgreSQL with psycopg2-binary
- **Authentication**: Custom JWT with HttpOnly cookies
- **CORS**: Django CORS headers for frontend integration
- **Background Tasks**: Django RQ with Redis Queue
- **Email**: Console backend for development

### Frontend
- **HTML/CSS/JavaScript**: Vanilla JavaScript with modern ES6+
- **Video Player**: HLS.js for adaptive video streaming
- **Styling**: Custom CSS with responsive design
- **API Integration**: Fetch API with JWT cookie authentication

## Project Structure

```
videoflix/
├── authentication/          # User authentication app
│   ├── api/                # API layer
│   │   ├── __init__.py
│   │   ├── serializers.py  # Authentication serializers
│   │   └── views.py        # Auth API endpoints
│   ├── models.py           # Custom user model
│   ├── jwt_authentication.py # Custom JWT cookie auth
│   └── urls.py             # Authentication routes
├── videos/                 # Video management app
│   ├── api/                # API layer
│   │   ├── __init__.py
│   │   ├── serializers.py  # Video serializers
│   │   └── views.py        # Video API endpoints
│   ├── models.py           # Video and Genre models
│   └── urls.py             # Video routes
├── content/                # Static content management
│   ├── api/                # API layer
│   │   ├── __init__.py
│   │   ├── serializers.py  # Content serializers
│   │   └── views.py        # Content API endpoints
│   ├── models.py           # Content models
│   └── urls.py             # Content routes
├── core/                   # Main project configuration
│   ├── settings.py         # Django settings
│   └── urls.py             # Main URL configuration
├── assets/                 # Frontend assets (icons, images, fonts)
│   ├── fonts/              # Font files
│   ├── icons/              # Icon assets
│   └── img/                # Image assets
├── pages/                  # HTML pages
│   ├── auth/               # Authentication pages
│   ├── video_list/         # Video listing page
│   ├── imprint/            # Legal imprint page
│   └── privacy/            # Privacy policy page
├── shared/                 # Shared frontend resources
│   ├── css/                # Shared CSS files
│   └── js/                 # Shared JavaScript files
├── tests/                  # Test files and documentation
│   ├── test_*.py           # Python test scripts
│   ├── *.postman_collection.json # Postman API collections
│   └── debug_*.py          # Debug utilities
├── docs/                   # Project documentation
│   └── jsdoc/              # Generated JavaScript documentation
├── index.html              # Landing page
├── styles.css              # Main stylesheet
├── script.js               # Main JavaScript file
└── manage.py               # Django management script
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis Server (optional - for background tasks)
- FFmpeg (optional - for video processing)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd videoflix
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # Mac/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.template .env
   # Edit .env with your database and email settings
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Optional: Setup sample data**
   ```bash
   # Add sample videos with real video files
   python manage.py add_sample_videos --download
   
   # Create placeholder thumbnails
   python manage.py create_placeholders
   
   # Activate a user for testing
   python manage.py activate_user --email user@example.com --activate
   ```

8. **Optional: Convert videos to HLS format**
   ```bash
   # Convert all videos to HLS using mentor's FFmpeg command
   python manage.py convert_to_hls --all
   
   # Convert specific video
   python manage.py convert_to_hls --video-id 1
   
   # Force reconversion
   python manage.py convert_to_hls --all --force
   ```

### FFmpeg Setup (for HLS conversion)
Install FFmpeg for video processing:
- **Windows**: Download from https://ffmpeg.org/download.html
- **Mac**: `brew install ffmpeg`
- **Linux**: `sudo apt-get install ffmpeg`

The HLS conversion uses mentor's FFmpeg command:
```bash
ffmpeg -i input.mp4 -codec: copy -start_number 0 -hls_time 10 -hls_list_size 0 -f hls output.m3u8
```

7. **Access the application**
   - Backend API: http://127.0.0.1:8000/api/
   - Frontend: Open `index.html` in browser or serve with local server

### Serving Frontend Properly

For full functionality, serve the frontend with a local web server:

```bash
# Python built-in server
python -m http.server 3000

# Then update CORS settings in Django to allow http://localhost:3000
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=videoflix_db
DB_USER=videoflix_user
DB_PASSWORD=supersecretpassword
DB_HOST=localhost  # or 'db' for Docker
DB_PORT=5432

# Redis (optional for background tasks)
REDIS_LOCATION=redis://localhost:6379/1

# Email Configuration (for development - console backend)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Frontend URL (for email links)
FRONTEND_URL=http://localhost:3000
```

## API Documentation

### Authentication Endpoints
- `POST /api/register/` - User registration
- `GET /api/activate/<uidb64>/<token>/` - Email verification
- `POST /api/login/` - User login (sets HttpOnly cookies)
- `POST /api/logout/` - User logout (clears cookies)
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/password_reset/` - Request password reset
- `POST /api/password_confirm/<uidb64>/<token>/` - Confirm password reset

### Video Endpoints (Authentication Required)
- `GET /api/video/` - List all videos with metadata
- `GET /api/video/<int:movie_id>/<str:resolution>/index.m3u8` - HLS manifest
- `GET /api/video/<int:movie_id>/<str:resolution>/<str:segment>` - HLS segments

### Content Endpoints
- `GET /api/content/` - List content pages  
- `GET /api/content/<slug>/` - Get specific content page

## Development Notes

### Frontend Integration
- Frontend files are located in the project root (not in a separate `frontend/` folder)
- All paths in HTML files use absolute paths (`/shared/css/...`) which require a web server
- For development, serve frontend with: `python -m http.server 3000`
- Update Django CORS settings to allow your frontend URL

### Authentication Flow
1. User registers via frontend form
2. Backend sends activation email (console in development)
3. User clicks activation link to verify email
4. User can then login and receive JWT cookies
5. Protected routes require valid JWT cookie

### Video Streaming
- Videos are served via HLS (HTTP Live Streaming)
- Multiple resolutions supported (480p, 720p, 1080p)
- Uses HLS.js library for browser compatibility
- Authentication required for all video endpoints

## Documentation

- **API Documentation**: Available through Django REST Framework browsable API at `/api/`
- **JavaScript Documentation**: Generated JSDoc files in `docs/jsdoc/`
- **Test Documentation**: Comprehensive test suites and Postman collections in `tests/`

## Testing

Test files and documentation are located in the `tests/` folder:

```bash
# Run Django tests
python manage.py test

# Test files are in tests/ directory including:
# - Python test scripts (test_*.py)
# - Postman API collections (*.postman_collection.json)  
# - Debug utilities (debug_*.py)
# - Authentication flow tests
# - Video API tests
```

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run migrations in container
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

## Troubleshooting

### Common Issues

1. **Frontend not loading**: Serve with web server, don't open HTML files directly
2. **CORS errors**: Update `CORS_ALLOWED_ORIGINS` in Django settings
3. **Registration not working**: Check that email backend is configured
4. **Video streaming issues**: Ensure video files exist and authentication is working

### Debug Steps
1. Check Django server is running on port 8000
2. Verify database connection and migrations
3. Test API endpoints directly with browser or Postman
4. Check browser console for JavaScript errors
5. Verify CORS settings match your frontend URL

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request