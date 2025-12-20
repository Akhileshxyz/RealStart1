# RealStart - Real Estate Platform API

A comprehensive real estate platform built with FastAPI, featuring project listings, developer portals, user interactions, and administrative controls.

## Features

### User Features
- User authentication and profile management
- Browse public project listings
- View history and wishlist management
- Market analyzer with landmark information
- Site visit booking system
- Legal consultation requests

### Developer Portal
- Project creation and management
- Lead tracking and analytics dashboard
- Webhook management for real-time notifications
- Team member management with role-based access
- Subscription plans and payment integration

### Admin Portal
- Project approval and management
- Developer account management
- User account management
- Subscription plan management
- Change request handling

### Lawyer Portal
- Legal document verification
- Legal consultation call management

## Tech Stack

- **Framework**: FastAPI
- **Database**: MongoDB (with Beanie ODM)
- **Cache**: Redis
- **Authentication**: JWT with python-jose
- **Password Hashing**: Passlib with Argon2
- **Payment Gateway**: Razorpay
- **Rate Limiting**: SlowAPI

## Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Redis 6.0+
- Git

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/pavandhananjayaofficial/Realstart.git
cd Realstart
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
# Application
PROJECT_NAME=RealStart Auth
DEBUG=True
API_V1_STR=/api/v1

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# MongoDB
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=realstart_db

# File Upload
MAX_FILE_SIZE=10485760
UPLOAD_DIR=./uploads

# Server
HOST=0.0.0.0
PORT=8000

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Redis
REDIS_URL=redis://localhost:6379/0
ENABLE_REDIS_CACHE=True
REDIS_CACHE_TTL_DEFAULT=300
REDIS_CACHE_TTL_USER=600
REDIS_CACHE_TTL_PUBLIC=3600
REDIS_CACHE_TTL_LANDMARKS=21600

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@yourdomain.com

# Razorpay Payment Gateway
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
```

### 5. Start Required Services

#### MongoDB
```bash
# Windows (if installed as service)
net start MongoDB

# Linux/Mac
sudo systemctl start mongod

# Or using Docker
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

#### Redis
```bash
# Windows (if installed as service)
redis-server

# Linux/Mac
sudo systemctl start redis

# Or using Docker
docker run -d -p 6379:6379 --name redis redis:latest
```

### 6. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

## API Endpoints Overview

### Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/admin/login` - Admin login

### Public Projects
- `GET /api/v1/public/projects` - List all projects
- `GET /api/v1/public/projects/{slug}` - Get project details

### User Portal
- `GET /api/v1/users/me` - Get user profile
- `PATCH /api/v1/users/me` - Update user profile
- `GET /api/v1/users/me/history` - View history
- `GET /api/v1/users/me/wishlist` - Get wishlist
- `GET /api/v1/public/landmarks` - List landmarks
- `POST /api/v1/users/me/bookings` - Book site visit

### User Interactions
- `POST /api/v1/users/interactions/{slug}/view` - Log project view
- `POST /api/v1/users/interactions/{slug}/wishlist` - Toggle wishlist
- `POST /api/v1/users/interactions/{slug}/legal-request` - Request legal consultation
- `POST /api/v1/users/interactions/{slug}/book-visit` - Book visit

### Developer Portal
- `POST /api/v1/developers/projects` - Create project
- `GET /api/v1/developers/projects` - List developer projects
- `GET /api/v1/developers/leads` - Get lead analytics
- `POST /api/v1/developers/webhooks` - Create webhook
- `POST /api/v1/developers/team` - Add team member
- `GET /api/v1/developers/subscriptions/plans` - List subscription plans
- `POST /api/v1/developers/subscriptions/orders` - Create subscription order

### Admin Portal
- `GET /api/v1/admin/projects` - List all projects
- `PATCH /api/v1/admin/projects/{id}` - Update project
- `GET /api/v1/admin/developers` - List developers
- `POST /api/v1/admin/subscriptions/plans` - Create subscription plan

### Settings
- `POST /api/v1/settings/change-password` - Change password

### Lawyer Portal
- `GET /api/v1/lawyer/pending-requests` - Get pending legal requests
- `PATCH /api/v1/lawyer/requests/{id}` - Update request status

## Project Structure

```
Realstart/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── admin_auth.py
│   │   │   ├── admin_projects.py
│   │   │   ├── admin_subscriptions.py
│   │   │   ├── developer_leads.py
│   │   │   ├── developer_projects.py
│   │   │   ├── developer_subscriptions.py
│   │   │   ├── developer_team.py
│   │   │   ├── developer_webhooks.py
│   │   │   ├── lawyer_portal.py
│   │   │   ├── public_auth.py
│   │   │   ├── public_projects.py
│   │   │   ├── user_interactions.py
│   │   │   └── user_portal.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging_config.py
│   │   ├── permissions.py
│   │   ├── redis_client.py
│   │   └── security.py
│   ├── db/
│   │   └── mongodb.py
│   ├── middleware/
│   │   ├── rate_limit.py
│   │   └── security.py
│   ├── models/
│   │   ├── change_request.py
│   │   ├── developer.py
│   │   ├── landmark.py
│   │   ├── lead.py
│   │   ├── legal_call.py
│   │   ├── project.py
│   │   ├── subscription.py
│   │   ├── team.py
│   │   ├── user.py
│   │   ├── visit.py
│   │   └── webhook.py
│   ├── schemas/
│   │   ├── auth.py
│   │   ├── change_request.py
│   │   ├── developer.py
│   │   ├── landmark.py
│   │   ├── lead.py
│   │   ├── project.py
│   │   ├── subscription.py
│   │   ├── team.py
│   │   ├── user.py
│   │   └── visit.py
│   ├── services/
│   │   ├── permission_service.py
│   │   ├── project_service.py
│   │   ├── subscription_service.py
│   │   └── webhook_service.py
│   ├── utils/
│   │   ├── cache.py
│   │   └── cache_invalidation.py
│   └── main.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## User Roles

1. **BUYER** - Regular users who can browse projects and book visits
2. **DEVELOPER** - Project creators with access to analytics and team management
3. **ADMIN** - System administrators with full access
4. **LAWYER** - Legal professionals handling document verification

## Caching Strategy

The application implements a three-tier caching strategy:

- **Tier 1 (Critical)**: 5 minutes - User sessions, real-time data
- **Tier 2 (Important)**: 10-30 minutes - User-specific data, wishlists
- **Tier 3 (Public)**: 1-6 hours - Public listings, landmarks

## Security Features

- JWT-based authentication
- Argon2 password hashing
- Rate limiting on sensitive endpoints
- CORS configuration
- Security headers middleware
- Request size limitation
- Role-based access control (RBAC)

## Payment Integration

The platform uses Razorpay for subscription payments:

1. Developer selects a subscription plan
2. Creates an order via `/developers/subscriptions/orders`
3. Frontend integrates Razorpay checkout
4. Payment verified via `/developers/subscriptions/verify`
5. Subscription activated upon successful payment

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
# Using black
black app/

# Using isort
isort app/
```

### Linting

```bash
flake8 app/
```

## Production Deployment

### Using Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t realstart-api .
docker run -p 8000:8000 --env-file .env realstart-api
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - mongodb
      - redis

  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

  redis:
    image: redis:latest
    ports:
      - "6379:6379"

volumes:
  mongodb_data:
```

Run with:

```bash
docker-compose up -d
```

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_NAME` | Application name | RealStart Auth |
| `DEBUG` | Debug mode | False |
| `SECRET_KEY` | JWT secret key | Required |
| `MONGODB_URL` | MongoDB connection string | mongodb://localhost:27017 |
| `DATABASE_NAME` | Database name | realstart_db |
| `REDIS_URL` | Redis connection URL | redis://localhost:6379/0 |
| `RAZORPAY_KEY_ID` | Razorpay API key | Required for payments |
| `RAZORPAY_KEY_SECRET` | Razorpay API secret | Required for payments |

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Support

For support, email support@realstart.com or open an issue on GitHub.

## Authors

- Pavan Dhananjaya - [GitHub](https://github.com/pavandhananjayaofficial)

## Acknowledgments

- FastAPI for the amazing framework
- MongoDB for the database
- Redis for caching capabilities
- Razorpay for payment integration
