# 🚀 Social Media API

A modern, scalable social media API built with Django REST Framework, following SOLID principles and implementing best practices for enterprise-level applications.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/Django-5.0.6-green.svg)](https://djangoproject.com)
[![DRF](https://img.shields.io/badge/DRF-3.15.2-red.svg)](https://www.django-rest-framework.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Features

- 🔐 **JWT Authentication** - Secure token-based authentication
- 👥 **User Management** - Complete user CRUD operations with following system
- 📝 **Post Management** - Create, read, and manage posts with comments
- 💬 **Comment System** - Full comment functionality on posts
- 🔍 **Advanced Filtering** - Filter posts by author, date, and more
- 📊 **User Statistics** - Comprehensive user analytics and metrics
- 🐳 **Docker Ready** - Complete containerization setup
- 📚 **API Documentation** - Interactive Swagger/OpenAPI documentation
- 🧪 **Comprehensive Testing** - Full test coverage with pytest
- 🔒 **Security First** - Environment-based configuration and security best practices

## 🏗️ Architecture

This project follows **SOLID principles** and implements several design patterns:

- **Repository Pattern** - Abstract data access layer
- **Service Layer Pattern** - Business logic separation
- **Dependency Injection** - Loose coupling between components
- **Single Responsibility Principle** - Each class has one reason to change
- **Open/Closed Principle** - Open for extension, closed for modification

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- PostgreSQL (for production)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd social_media_api
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - API: http://localhost:8000/api/
   - Admin: http://localhost:8000/admin/
   - Documentation: http://localhost:8000/swagger/

### Manual Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## 📚 API Documentation

### Authentication

All endpoints require JWT authentication except where noted.

```bash
# Get access token
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Use token in requests
curl -H "Authorization: Bearer <your_token>" \
  http://localhost:8000/api/users/
```

### Endpoints

#### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/` | List all users |
| `POST` | `/api/users/` | Create new user |
| `GET` | `/api/users/{id}/` | Get user details |
| `GET` | `/api/users/{id}/stats/` | Get user statistics |
| `POST` | `/api/users/{id}/follow/{follow_id}/` | Follow a user |
| `DELETE` | `/api/users/{id}/follow/{follow_id}/` | Unfollow a user |

#### Posts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/posts/` | List all posts |
| `POST` | `/api/posts/` | Create new post |
| `GET` | `/api/posts/{id}/` | Get post details |
| `GET` | `/api/posts/{id}/extended/` | Get post with all comments |

#### Comments

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/posts/{id}/comments/` | List comments for a post |
| `POST` | `/api/posts/{id}/comments/` | Create comment on a post |
| `GET` | `/api/comments/{id}/` | Get comment details |

### Example Requests

#### Create a Post
```bash
curl -X POST http://localhost:8000/api/posts/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Hello, world! This is my first post."}'
```

#### Follow a User
```bash
curl -X POST http://localhost:8000/api/users/1/follow/2/ \
  -H "Authorization: Bearer <your_token>"
```

#### Get User Statistics
```bash
curl -X GET http://localhost:8000/api/users/1/stats/ \
  -H "Authorization: Bearer <your_token>"
```

## 🧪 Testing

Run the test suite:

```bash
# Using pytest
pytest

# Using Django test runner
python manage.py test

# With coverage
pytest --cov=api --cov-report=html
```

## 🐳 Docker

### Development

```bash
# Start all services
docker-compose up

# Start specific service
docker-compose up web

# View logs
docker-compose logs -f web
```

### Production

```bash
# Build production image
docker build -t social-media-api .

# Run with production settings
docker run -p 8000:8000 \
  -e DEBUG=False \
  -e SECRET_KEY=your-secret-key \
  social-media-api
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `True` |
| `SECRET_KEY` | Django secret key | Auto-generated |
| `DATABASE_URL` | Database connection string | SQLite |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `ALLOWED_HOSTS` | Allowed hosts | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | CORS origins | `http://localhost:3000` |

### Database

The application supports multiple databases:

- **SQLite** (development)
- **PostgreSQL** (production)
- **MySQL** (via configuration)

## 📊 Performance

### Optimizations

- Database indexes on frequently queried fields
- Select/related and prefetch_related for efficient queries
- Redis caching for frequently accessed data
- Pagination for large datasets
- Connection pooling in production

### Monitoring

- Django Debug Toolbar (development)
- Custom logging configuration
- Performance metrics collection

## 🔒 Security

### Features

- JWT token authentication
- CORS configuration
- Input validation and sanitization
- SQL injection protection
- XSS protection
- CSRF protection
- Rate limiting (configurable)

### Best Practices

- Environment-based configuration
- No hardcoded secrets
- Regular security updates
- Input validation on all endpoints
- Proper error handling

## 🏗️ Project Structure

```
social_media_api/
├── api/                    # Main application
│   ├── models.py          # Data models
│   ├── serializers.py     # DRF serializers
│   ├── views.py           # API views
│   ├── services.py        # Business logic layer
│   ├── repositories.py    # Data access layer
│   ├── urls.py           # URL configuration
│   └── tests.py          # Test suite
├── social_media_api/      # Project settings
│   ├── settings.py       # Django settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
├── requirements.txt       # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── env.example          # Environment variables template
└── README.md           # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide
- Write comprehensive tests
- Add docstrings to all functions
- Update documentation as needed
- Use type hints where appropriate

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Django REST Framework team
- Django community
- All contributors and maintainers

## 📞 Support

- **Documentation**: Check the [API documentation](http://localhost:8000/swagger/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Made with ❤️ using Django and Python** 