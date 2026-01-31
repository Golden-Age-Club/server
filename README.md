# Golden Age Casino - USDT Wallet API

> **Telegram Game Backend** with USDT wallet integration, Telegram WebApp authentication, and CCpayment processing.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.4+-green.svg)](https://www.mongodb.com/)

---

## 🎯 Features

- ✅ **Telegram WebApp Authentication** - Secure HMAC-SHA256 validation
- ✅ **JWT Token System** - Session management with configurable expiration
- ✅ **USDT Wallet** - Deposit and withdrawal via CCpayment
- ✅ **MongoDB Integration** - Async operations with Motor driver
- ✅ **Atomic Transactions** - Race-condition safe balance operations
- ✅ **Webhook Processing** - Secure payment notification handling
- ✅ **Auto-Registration** - Seamless user onboarding
- ✅ **Structured Logging** - JSON logs with request ID tracking
- ✅ **Rate Limiting** - DDoS protection
- ✅ **Comprehensive Testing** - Full test suite included

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Telegram Bot Token (from @BotFather)

### Installation

```bash
# Clone repository
cd golden-age-club

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Run application
python -m app.main
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

## 📚 API Endpoints

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Login with Telegram initData |
| `/api/auth/me` | GET | Get current user profile |
| `/api/auth/refresh` | POST | Refresh access token |

### Wallet

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|---------------|
| `/api/wallet/deposit` | POST | Create deposit order | ✅ |
| `/api/wallet/withdraw` | POST | Create withdrawal request | ✅ |
| `/api/wallet/balance` | GET | Get current balance | ✅ |
| `/api/wallet/transactions` | GET | Get transaction history | ✅ |
| `/api/wallet/transaction/{id}` | GET | Get transaction details | ✅ |

### Webhooks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/webhook/ccpayment` | POST | CCpayment webhook notifications |

---

## 🔐 Authentication

The API supports two authentication methods:

### 1. JWT Token (Recommended)

```javascript
// Login to get token
const response = await fetch('/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ 
        init_data: window.Telegram.WebApp.initData 
    })
});

const { access_token } = await response.json();

// Use token in subsequent requests
fetch('/api/wallet/balance', {
    headers: {
        'Authorization': `Bearer ${access_token}`
    }
});
```

### 2. Telegram InitData (Direct)

```javascript
fetch('/api/wallet/balance', {
    headers: {
        'X-Telegram-Init-Data': window.Telegram.WebApp.initData
    }
});
```

---

## 💳 Wallet Operations

### Create Deposit

```javascript
const response = await fetch('/api/wallet/deposit', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        amount: 100.0,
        currency: "USDT.TRC20"
    })
});

const { payment_url, payment_address } = await response.json();
// Redirect user to payment_url or show payment_address
```

### Create Withdrawal

```javascript
const response = await fetch('/api/wallet/withdraw', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({
        amount: 50.0,
        wallet_address: "TYourWalletAddress",
        currency: "USDT.TRC20"
    })
});
```

---

## 🏗️ Project Structure

```
golden-age-club/
├── app/
│   ├── core/
│   │   ├── database.py          # MongoDB connection
│   │   ├── init_db.py           # Database indexes
│   │   └── logging_config.py    # Logging setup
│   ├── middleware/
│   │   ├── auth.py              # JWT & Telegram auth
│   │   └── request_id.py        # Request ID tracking
│   ├── models/
│   │   ├── transaction.py       # Transaction model
│   │   └── user.py              # User model
│   ├── repositories/
│   │   ├── transaction.py       # Transaction data access
│   │   └── user.py              # User data access
│   ├── routes/
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── wallet.py            # Wallet endpoints
│   │   └── webhook.py           # Webhook endpoints
│   ├── schemas/
│   │   ├── user.py              # User schemas
│   │   └── wallet.py            # Wallet schemas
│   ├── services/
│   │   ├── ccpayment.py         # CCpayment integration
│   │   └── wallet.py            # Wallet business logic
│   ├── utils/
│   │   └── telegram_auth.py     # Telegram validation
│   ├── config.py                # Configuration
│   ├── dependencies.py          # Dependency injection
│   └── main.py                  # Application entry point
├── test/
│   ├── conftest.py              # Test fixtures
│   ├── test_auth.py             # Auth tests
│   ├── test_wallet.py           # Wallet tests
│   └── test_webhook.py          # Webhook tests
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── DEPLOYMENT.md                # Deployment guide
└── README.md                    # This file
```

---

## 🧪 Testing

```bash
# Run all tests
pytest test/ -v

# Run specific test file
pytest test/test_auth.py -v

# Run with coverage
pytest test/ --cov=app --cov-report=html
```

---

## 📊 Database Schema

### Users Collection

```javascript
{
  _id: 123456789,              // telegram_id
  telegram_id: 123456789,
  username: "johndoe",
  first_name: "John",
  last_name: "Doe",
  balance: 1000.0,
  is_active: true,
  is_premium: false,
  created_at: ISODate("2024-01-01T00:00:00Z"),
  updated_at: ISODate("2024-01-01T00:00:00Z")
}
```

### Transactions Collection

```javascript
{
  _id: ObjectId("..."),
  user_id: "123456789",
  type: "deposit",              // or "withdrawal"
  amount: 100.0,
  currency: "USDT.TRC20",
  status: "completed",          // pending, processing, completed, failed
  merchant_order_id: "DEP-1234567890-123456789",
  payment_url: "https://...",
  payment_address: "TAddress...",
  created_at: ISODate("..."),
  updated_at: ISODate("..."),
  completed_at: ISODate("...")
}
```

---

## 🔧 Configuration

### Environment Variables

See `.env.example` for all configuration options:

```env
# Required
TELEGRAM_BOT_TOKEN=your_bot_token
CCPAYMENT_APP_ID=your_app_id
CCPAYMENT_APP_SECRET=your_app_secret
JWT_SECRET_KEY=your_secret_key

# Optional
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=casino_db
LOG_LEVEL=INFO
LOG_FORMAT=console
TESTING_MODE=false
```

---

## 📖 Documentation

- **[Deployment Guide](DEPLOYMENT.md)** - Production deployment instructions
- **[API Documentation](http://localhost:8000/docs)** - Interactive API docs (when running)
- **[Codebase Review](docs/codebase_review.md)** - Comprehensive code analysis

---

## 🛡️ Security Features

- ✅ HMAC-SHA256 signature verification (Telegram & CCpayment)
- ✅ Data freshness checks (prevents replay attacks)
- ✅ JWT token expiration
- ✅ CORS restrictions
- ✅ Rate limiting
- ✅ Atomic balance operations (prevents race conditions)
- ✅ Transaction ownership verification
- ✅ Webhook signature validation

---

## 🚀 Production Deployment

See **[DEPLOYMENT.md](DEPLOYMENT.md)** for detailed production deployment instructions.

Quick checklist:
- [ ] Set `TESTING_MODE=false`
- [ ] Configure real credentials
- [ ] Enable HTTPS
- [ ] Set up MongoDB authentication
- [ ] Configure logging (`LOG_FORMAT=json`)
- [ ] Set up monitoring
- [ ] Configure backups

---

## 📝 License

Proprietary - All rights reserved

---

## 👥 Support

For support and questions, contact the development team.

---

## 🎉 Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Motor](https://motor.readthedocs.io/) - Async MongoDB driver
- [python-jose](https://python-jose.readthedocs.io/) - JWT implementation
- [CCpayment](https://ccpayment.com/) - Cryptocurrency payment processing

---

**Made with ❤️ for Golden Age Casino**
