# Golden Age Casino - Deployment Guide

## Prerequisites

- Python 3.8+
- MongoDB 4.4+
- Telegram Bot (from @BotFather)
- CCpayment Account (for production)

---

## Environment Setup

### 1. Clone and Install Dependencies

```bash
# Clone repository
cd golden-age-club

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# CCPayment Configuration (Production)
CCPAYMENT_APP_ID=your_actual_app_id
CCPAYMENT_APP_SECRET=your_actual_app_secret
CCPAYMENT_API_URL=https://admin.ccpayment.com/ccpayment/v2

# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
# For production with authentication:
# MONGODB_URL=mongodb://username:password@host:port/database?authSource=admin
DATABASE_NAME=casino_db

# Application Configuration
API_HOST=0.0.0.0
API_PORT=8000
WEBHOOK_URL=https://yourdomain.com/api/webhook/ccpayment

# Telegram Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather

# JWT Authentication
# Generate with: openssl rand -hex 32
JWT_SECRET_KEY=your_super_secret_jwt_key_here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# CORS Configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://t.me

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json  # Use 'json' for production, 'console' for development

# Testing Mode
TESTING_MODE=false  # MUST be false in production
```

---

## Database Setup

### MongoDB Installation

#### Ubuntu/Debian
```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# Install MongoDB
sudo apt-get update
sudo apt-get install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
```

#### Windows
Download and install from: https://www.mongodb.com/try/download/community

#### Docker
```bash
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v mongodb_data:/data/db \
  mongo:6.0
```

### Database Initialization

The application automatically creates indexes on startup. To manually initialize:

```python
from app.core.database import connect_to_mongo
from app.core.init_db import init_indexes
import asyncio

async def init():
    await connect_to_mongo()
    db = await get_database()
    await init_indexes(db)

asyncio.run(init())
```

---

## Running the Application

### Development Mode

```bash
# With auto-reload
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main script
python -m app.main
```

### Production Mode

#### Using Uvicorn

```bash
# Single worker
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Multiple workers (recommended)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Using Gunicorn (Recommended for Production)

```bash
# Install gunicorn
pip install gunicorn

# Run with uvicorn workers
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

#### Using Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# Build and run
docker build -t golden-age-api .
docker run -d -p 8000:8000 --env-file .env golden-age-api
```

---

## Production Deployment Checklist

### Security

- [ ] Set `TESTING_MODE=false`
- [ ] Generate strong `JWT_SECRET_KEY` (use `openssl rand -hex 32`)
- [ ] Configure real `TELEGRAM_BOT_TOKEN`
- [ ] Configure real `CCPAYMENT_APP_ID` and `CCPAYMENT_APP_SECRET`
- [ ] Set production `ALLOWED_ORIGINS` (your Telegram WebApp domain)
- [ ] Use HTTPS for `WEBHOOK_URL`
- [ ] Enable MongoDB authentication
- [ ] Use environment variables (never commit `.env`)

### Database

- [ ] MongoDB running and accessible
- [ ] Database indexes created (automatic on startup)
- [ ] Database backups configured
- [ ] Connection pooling configured
- [ ] SSL/TLS enabled for MongoDB connection (if remote)

### Application

- [ ] Set `LOG_FORMAT=json` for production
- [ ] Set appropriate `LOG_LEVEL` (INFO or WARNING)
- [ ] Configure multiple workers (4-8 recommended)
- [ ] Set up process manager (systemd, supervisor, PM2)
- [ ] Configure reverse proxy (nginx, caddy)
- [ ] Enable HTTPS/SSL
- [ ] Set up monitoring and alerting

### Testing

- [ ] Test with real Telegram WebApp
- [ ] Test deposit flow with small amount
- [ ] Test withdrawal flow with small amount
- [ ] Test webhook processing
- [ ] Verify database indexes exist
- [ ] Check health endpoint: `curl https://yourdomain.com/health`
- [ ] Review logs for errors

---

## Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Systemd Service Example

Create `/etc/systemd/system/golden-age-api.service`:

```ini
[Unit]
Description=Golden Age USDT Wallet API
After=network.target mongodb.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/opt/golden-age-club
Environment="PATH=/opt/golden-age-club/venv/bin"
EnvironmentFile=/opt/golden-age-club/.env
ExecStart=/opt/golden-age-club/venv/bin/gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable golden-age-api
sudo systemctl start golden-age-api
sudo systemctl status golden-age-api
```

---

## Monitoring

### Health Checks

```bash
# Basic health
curl https://yourdomain.com/health

# Expected response:
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected"
}
```

### Logs

```bash
# View application logs
journalctl -u golden-age-api -f

# View last 100 lines
journalctl -u golden-age-api -n 100
```

### Database Monitoring

```bash
# MongoDB status
mongo --eval "db.serverStatus()"

# Check indexes
mongo casino_db --eval "db.users.getIndexes()"
mongo casino_db --eval "db.transactions.getIndexes()"
```

---

## Backup Strategy

### Database Backup

```bash
# Create backup
mongodump --db casino_db --out /backup/$(date +%Y%m%d)

# Restore backup
mongorestore --db casino_db /backup/20240101/casino_db
```

### Automated Daily Backup

```bash
# Add to crontab
0 2 * * * mongodump --db casino_db --out /backup/$(date +\%Y\%m\%d) && find /backup -mtime +7 -delete
```

---

## Troubleshooting

### Application Won't Start

1. Check logs: `journalctl -u golden-age-api -n 50`
2. Verify MongoDB is running: `systemctl status mongod`
3. Check environment variables: `cat .env`
4. Test manually: `python -m app.main`

### Database Connection Issues

1. Check MongoDB status: `systemctl status mongod`
2. Verify connection string in `.env`
3. Test connection: `mongo mongodb://localhost:27017`
4. Check firewall rules

### Webhook Not Working

1. Verify `WEBHOOK_URL` is accessible from internet
2. Check CCpayment webhook configuration
3. Review webhook logs
4. Test signature verification

### High Memory Usage

1. Reduce number of workers
2. Check for memory leaks in logs
3. Monitor with: `ps aux | grep gunicorn`
4. Consider adding swap space

---

## Scaling

### Horizontal Scaling

- Deploy multiple instances behind load balancer
- Use shared MongoDB instance
- Ensure session state is in database (not in-memory)

### Vertical Scaling

- Increase worker count: `--workers 8`
- Allocate more RAM to MongoDB
- Use faster storage (SSD)

### Database Scaling

- Enable MongoDB replication
- Use MongoDB sharding for large datasets
- Add read replicas for read-heavy workloads

---

## Support

For issues or questions:
- Check logs first
- Review this deployment guide
- Contact support team

---

## Security Best Practices

1. **Never commit `.env` file**
2. **Use strong passwords** for MongoDB
3. **Enable MongoDB authentication** in production
4. **Use HTTPS** for all endpoints
5. **Rotate JWT secrets** periodically
6. **Monitor logs** for suspicious activity
7. **Keep dependencies updated**: `pip list --outdated`
8. **Regular backups** of database
9. **Test disaster recovery** procedures
10. **Use firewall** to restrict access
