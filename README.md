# Slot Machine Admin Backend

**Production-ready admin backend system for slot machine/casino platforms with comprehensive security, audit logging, and role-based access control.**

## 🎯 Features

- **Secure Authentication**: JWT tokens with refresh token rotation, MFA (TOTP), account locking
- **Role-Based Access Control**: 7 system roles with 30+ granular permissions
- **Comprehensive Audit Logging**: All admin actions logged with sensitive data masking
- **MongoDB with Transactions**: Replica set support for ACID transactions
- **Financial Safety**: Optimistic locking, idempotency keys, dual approval workflows
- **Production Ready**: Docker Compose setup, health checks, error handling

## 📋 System Roles

1. **Super Admin** - Full system access
2. **Finance Manager** - Wallet, deposits, withdrawals, financial reports
3. **Risk Manager** - Risk control, fraud prevention, user restrictions
4. **Customer Support** - User management, basic reports
5. **Marketing Manager** - Bonuses, promotions, VIP management
6. **Analyst** - Read-only access to reports
7. **Game Manager** - Game configuration, bet records

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)

### 1. Clone and Setup

```bash
cd golden-age-crm
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` and set:
- `SECRET_KEY` (generate with: `openssl rand -hex 32`)
- `INITIAL_ADMIN_USERNAME`
- `INITIAL_ADMIN_EMAIL`
- `INITIAL_ADMIN_PASSWORD`

### 3. Start Services

```bash
docker-compose up -d
```

This starts:
- MongoDB replica set (3 nodes) on ports 27017, 27018, 27019
- Redis on port 6379
- FastAPI application on port 8000
- MongoDB Express (UI) on port 8081

### 4. Seed Database

```bash
# Wait for MongoDB replica set to initialize (30 seconds)
sleep 30

# Run seeding script
docker-compose exec api python scripts/seed_database.py
```

### 5. Access Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB Express**: http://localhost:8081 (admin/admin123)
- **Health Check**: http://localhost:8000/health

## 📚 API Documentation

### Authentication Endpoints

#### Login
```bash
POST /api/v1/admin/auth/login
{
  "username": "superadmin",
  "password": "ChangeMe123!"
}
```

Response:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer",
    "mfa_required": false,
    "session_id": "sess_..."
  }
}
```

#### Setup MFA
```bash
GET /api/v1/admin/auth/mfa/setup
Authorization: Bearer <access_token>
```

#### Get Current User
```bash
GET /api/v1/admin/auth/me
Authorization: Bearer <access_token>
```

### Admin Management Endpoints

#### Create Admin
```bash
POST /api/v1/admin/admins
Authorization: Bearer <access_token>
{
  "username": "jane.doe",
  "email": "jane@example.com",
  "password": "SecurePass123!",
  "roles": ["customer_support"]
}
```

#### List Admins
```bash
GET /api/v1/admin/admins?status=active&page=1&page_size=20
Authorization: Bearer <access_token>
```

#### Update Admin Status
```bash
PATCH /api/v1/admin/admins/{admin_id}/status
Authorization: Bearer <access_token>
{
  "status": "suspended",
  "reason": "Policy violation"
}
```

## 🏗️ Project Structure

```
golden-age-crm/
├── app/
│   ├── api/v1/          # API endpoints
│   ├── core/            # Security, permissions, audit
│   ├── models/          # Pydantic models
│   ├── schemas/         # Request/response schemas
│   ├── services/        # Business logic
│   ├── middleware/      # Request/response middleware
│   ├── config.py        # Configuration
│   ├── database.py      # MongoDB connection
│   ├── dependencies.py  # FastAPI dependencies
│   └── main.py          # Application entry point
├── scripts/
│   └── seed_database.py # Database seeding
├── docker-compose.yml   # Docker services
├── Dockerfile           # Application container
├── requirements.txt     # Python dependencies
└── .env.example         # Environment template
```

## 🔒 Security Features

### Authentication
- **Password Hashing**: bcrypt with 12 rounds
- **JWT Tokens**: Short-lived access (15 min), long-lived refresh (7 days)
- **MFA**: TOTP with QR code generation
- **Account Locking**: 5 failed attempts = 15 min lockout
- **Session Management**: Redis-based with expiration

### Authorization
- **RBAC**: Role-based access control with permission decorators
- **Wildcard Permissions**: Flexible permission matching
- **Audit Logging**: All actions logged with IP, user agent, before/after state
- **Sensitive Data Masking**: Passwords, tokens, secrets masked in logs

### Data Protection
- **Optimistic Locking**: Version-based concurrency control
- **Idempotency Keys**: Prevent duplicate operations
- **Soft Deletes**: Preserve data integrity
- **TTL Indexes**: Automatic log retention (7 years)

## 🧪 Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/ -v --cov=app

# Run specific test file
pytest tests/test_auth.py -v
```

## 📊 Monitoring

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "environment": "development",
  "database": "connected"
}
```

### Logs
```bash
# View application logs
docker-compose logs -f api

# View MongoDB logs
docker-compose logs -f mongo1
```

## 🔧 Development

### Local Development (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start MongoDB and Redis (via Docker)
docker-compose up -d mongo1 mongo2 mongo3 redis mongo-init

# Run application
python -m app.main
```

### Code Quality

```bash
# Format code
black app/

# Sort imports
isort app/

# Type checking
mypy app/

# Linting
flake8 app/
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | `mongodb://localhost:27017/?replicaSet=rs0` |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT secret key (32+ chars) | **Required** |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiration | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiration | `7` |
| `MFA_ISSUER_NAME` | MFA issuer name | `Slot Admin` |
| `RATE_LIMIT_LOGIN_ATTEMPTS` | Max login attempts | `5` |
| `RATE_LIMIT_LOGIN_WINDOW_MINUTES` | Login rate limit window | `15` |

## 🚨 Production Deployment

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Change initial admin password immediately
- [ ] Set `DEBUG=false`
- [ ] Configure `IP_WHITELIST` for admin access
- [ ] Enable MFA for all admin accounts
- [ ] Use MongoDB Atlas or managed MongoDB service
- [ ] Configure SSL/TLS for MongoDB and Redis
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy
- [ ] Review and adjust rate limits

### Recommended Infrastructure

- **MongoDB**: MongoDB Atlas (M10+ cluster with replica set)
- **Redis**: Redis Cloud or AWS ElastiCache
- **Application**: AWS ECS, Google Cloud Run, or Kubernetes
- **Load Balancer**: AWS ALB, Google Cloud Load Balancer
- **Monitoring**: Datadog, New Relic, or CloudWatch

## 📖 API Reference

Full API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🤝 Contributing

This is a production system. All changes must:
1. Include tests with 80%+ coverage
2. Pass linting and type checking
3. Include audit logging for mutations
4. Follow RBAC permission model
5. Update documentation

## 📄 License

Proprietary - All rights reserved

## 🆘 Support

For issues or questions:
1. Check logs: `docker-compose logs -f api`
2. Verify MongoDB replica set: `docker-compose exec mongo1 mongosh --eval "rs.status()"`
3. Check health endpoint: `curl http://localhost:8000/health`

## 🎉 Next Steps

After Phase 1 completion, implement:
- **Phase 2**: User & Wallet Management
- **Phase 3**: Bets, Games & VIP
- **Phase 4**: Risk Control & Bonus
- **Phase 5**: Reporting & Optimization
- **Phase 6**: Production Readiness

---

**Built with FastAPI, MongoDB, Redis, and ❤️**
