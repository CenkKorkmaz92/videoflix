# Videoflix Backend

A comprehensive Django-based video streaming platform backend built with clean code principles and modern best practices.

## Features

### 🔐 Authentication & Authorization
- **Custom User Model**: Email-based authentication with verification
- **JWT Token Authentication**: Secure API access with refresh tokens
- **Email Verification**: User account activation via email
- **Password Reset**: Secure password reset flow via email
- **User Management**: Profile management and user preferences

### 🎬 Video Management
- **Video Upload**: Support for multiple video formats (MP4, AVI, MOV, MKV, WMV, FLV, WebM)
- **Video Processing**: Background processing with multiple quality versions
- **Thumbnail Generation**: Automatic thumbnail creation from video frames
- **Genre Classification**: Organize videos by genres with slug-based URLs
- **Search & Filtering**: Full-text search and genre-based filtering

### 📊 User Experience
- **Watch Progress**: Track viewing progress and resume functionality
- **Dashboard**: Personalized content recommendations
- **Continue Watching**: Resume videos from where users left off
- **Video Quality Selection**: Multiple quality options for different bandwidth

### 📄 Content Management
- **Legal Pages**: Privacy policy, imprint, and other static content
- **Admin Interface**: Django admin for content management
- **API Documentation**: RESTful API with comprehensive endpoints

## Technology Stack

- **Framework**: Django 5.2.4 with Django REST Framework
- **Database**: PostgreSQL with psycopg2-binary
- **Caching**: Redis for session management and caching
- **Background Tasks**: Django RQ with Redis Queue
- **File Storage**: Local media storage with static file serving
- **Video Processing**: MoviePy for video manipulation
- **Authentication**: JWT tokens with djangorestframework-simplejwt
- **CORS**: Django CORS headers for frontend integration
- **Testing**: pytest with coverage reporting

## Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis Server
- FFmpeg (for video processing)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd videoflix
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.template .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Run Redis server**
   ```bash
   redis-server
   ```

7. **Start Django RQ worker** (in separate terminal)
   ```bash
   python manage.py rqworker default
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=videoflix
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Frontend URL
FRONTEND_URL=http://localhost:3000
```

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `POST /api/auth/verify-email/<token>/` - Email verification
- `POST /api/auth/password-reset/` - Request password reset
- `POST /api/auth/password-reset-confirm/` - Confirm password reset
- `GET /api/auth/profile/` - Get user profile
- `PUT /api/auth/profile/` - Update user profile

### Video Endpoints
- `GET /api/videos/` - List videos (with search and filtering)
- `GET /api/videos/<id>/` - Get video details
- `POST /api/videos/upload/` - Upload new video
- `DELETE /api/videos/<id>/delete/` - Delete video
- `GET /api/videos/genres/` - List genres
- `GET /api/videos/dashboard/` - Dashboard data
- `POST /api/videos/<id>/progress/` - Update watch progress
- `GET /api/videos/progress/` - Get user's watch progress

### Content Endpoints
- `GET /api/content/` - List content pages
- `GET /api/content/<slug>/` - Get content page by slug

## Project Structure

```
videoflix/
├── authentication/          # User authentication app
│   ├── models.py           # Custom user model
│   ├── serializers.py      # Authentication serializers
│   ├── views.py            # Authentication views
│   ├── utils.py            # Email and utility functions
│   └── urls.py             # Authentication routes
├── videos/                 # Video management app
│   ├── models.py           # Video, Genre, Quality models
│   ├── serializers.py      # Video serializers
│   ├── views.py            # Video views and APIs
│   ├── utils.py            # Video processing utilities
│   └── urls.py             # Video routes
├── content/                # Static content app
│   ├── models.py           # Content page model
│   ├── serializers.py      # Content serializers
│   ├── views.py            # Content views
│   └── urls.py             # Content routes
├── core/                   # Main project configuration
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI configuration
├── media/                  # User uploaded files
├── static/                 # Static files
├── requirements.txt        # Python dependencies
└── manage.py               # Django management script
```

## Testing

Run the test suite:

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test authentication
python manage.py test videos
python manage.py test content

# Run with coverage
pytest --cov=. --cov-report=html
```

## Code Quality

This project follows clean code principles:

- **Single Responsibility**: Each function/class has one clear purpose
- **Descriptive Naming**: Functions and variables use clear, descriptive names
- **Short Functions**: Functions are kept under 20 lines when possible
- **Type Hints**: Python type hints for better code documentation
- **Docstrings**: Comprehensive documentation for all functions and classes
- **Snake Case**: Python naming convention throughout
- **DRY Principle**: Don't Repeat Yourself - reusable utility functions

## Deployment

### Docker Deployment

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Run migrations in container**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py createsuperuser
   ```

### Production Considerations

- Use environment variables for all sensitive configuration
- Enable HTTPS with SSL certificates
- Configure proper CORS settings for your frontend domain
- Set up proper logging and monitoring
- Use a production WSGI server like Gunicorn
- Configure static file serving with a web server like Nginx
- Set up regular database backups
- Monitor Redis memory usage and configure persistence

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions, please open an issue in the GitHub repository.