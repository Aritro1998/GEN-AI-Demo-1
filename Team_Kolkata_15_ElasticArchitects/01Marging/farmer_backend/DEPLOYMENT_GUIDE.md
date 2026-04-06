# Deployment & Configuration Guide

## 🚀 Deployment Options

### Option 1: Local Development (Recommended for Starting)

#### Setup
```bash
cd farmer_backend
pip install -r requirements.txt
python run_server.py
```

#### Access
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

#### Pros
- ✅ Zero configuration
- ✅ Automatic database setup
- ✅ Quick startup
- ✅ Perfect for development

#### Cons
- ❌ Single-threaded
- ❌ Not suitable for production
- ❌ Limited concurrency

---

### Option 2: Gunicorn (Recommended for Production)

#### Installation
```bash
pip install gunicorn
```

#### Run with Multiple Workers
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Configuration
```bash
gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --worker-connections 1000 \
  --backlog 2048 \
  --timeout 30 \
  --keepalive 2 \
  --access-logfile - \
  --error-logfile -
```

#### Systemd Service (Linux)
Create `/etc/systemd/system/farmer-backend.service`:
```ini
[Unit]
Description=Farmer Backend API
After=network.target

[Service]
User=www-data
WorkingDirectory=/opt/farmer_backend
ExecStart=/usr/bin/gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable farmer-backend
sudo systemctl start farmer-backend
```

#### Pros
- ✅ Multiple workers for concurrency
- ✅ Production-ready
- ✅ Better performance
- ✅ Process management

#### Cons
- ⚠️ More configuration needed
- ⚠️ Requires separate server setup

---

### Option 3: Docker (Recommended for Container Deployment)

#### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Run with Gunicorn
CMD ["gunicorn", "main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### Build Image
```bash
docker build -t farmer-backend:latest .
```

#### Run Container
```bash
docker run -p 8000:8000 \
  -v $(pwd)/farmer_backend.db:/app/farmer_backend.db \
  --name farmer-backend \
  farmer-backend:latest
```

#### Docker Compose (Multiple Services)

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./farmer_backend.db:/app/farmer_backend.db
    environment:
      - DATABASE_URL=sqlite:///./farmer_backend.db
    restart: always

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
```

Run with Docker Compose:
```bash
docker-compose up -d
```

#### Pros
- ✅ Easy deployment anywhere
- ✅ Isolated environment
- ✅ Version control
- ✅ Easy scaling

#### Cons
- ⚠️ Requires Docker installation
- ⚠️ Slightly higher overhead

---

### Option 4: Cloud Deployment

#### AWS (Elastic Beanstalk)

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Initialize:
```bash
eb init -p python-3.11 farmer-backend
```

3. Create environment:
```bash
eb create farmer-backend-env
```

4. Deploy:
```bash
eb deploy
```

#### Heroku

1. Create `Procfile`:
```
web: gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

2. Deploy:
```bash
git push heroku main
```

#### Google Cloud Run

1. Create `cloudbuild.yaml`

2. Deploy:
```bash
gcloud run deploy farmer-backend --source .
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```bash
# Database
DATABASE_URL=sqlite:///./farmer_backend.db

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000

# CORS
CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]

# Debug
DEBUG=False
```

Update `main.py` to use environment variables:
```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./farmer_backend.db")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

app = FastAPI(
    title="Farmer Backend API",
    description="API for managing disease files",
    debug=DEBUG
)
```

### Database Configuration

#### SQLite (Development)
```python
# model/database.py
DATABASE_URL = "sqlite:///./farmer_backend.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)
```

#### PostgreSQL (Production)
```python
# Install driver
pip install psycopg2-binary

# Update database URL
DATABASE_URL = "postgresql://user:password@localhost:5432/farmer_db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=0
)
```

#### MySQL (Alternative)
```python
# Install driver
pip install mysqlclient

# Update database URL
DATABASE_URL = "mysql+pymysql://user:password@localhost:3306/farmer_db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=0
)
```

### CORS Configuration

Update `main.py` for production:
```python
from fastapi.middleware.cors import CORSMiddleware

# Restrict origins for production
allowed_origins = [
    "http://localhost:3000",  # Development
    "https://yourdomain.com",  # Production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

---

## 🔒 Security Configuration

### 1. Add HTTPS

#### Using Let's Encrypt (Linux)
```bash
pip install python-certifi-win32 certifi
```

Or use Nginx as reverse proxy.

### 2. Add Authentication

#### JWT Authentication
```python
# Install PyJWT
pip install python-jose passlib

# In main.py
from fastapi.security import HTTPBearer
from jose import JWTError, jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentialDetails = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, "secret-key", algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

### 3. Rate Limiting

```python
pip install slowapi

from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/disease-files/")
@limiter.limit("10/minute")
async def create_disease_file(...):
    ...
```

### 4. Add Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

---

## 📊 Monitoring & Logging

### Application Monitoring

#### Using Prometheus
```bash
pip install prometheus-fastapi-instrumentator
```

```python
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)
```

Access metrics at: `http://localhost:8000/metrics`

#### Using Sentry for Error Tracking
```bash
pip install sentry-sdk

import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0
)
```

### Database Monitoring

Monitor database performance:
```python
# Enable echo for SQL logging
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Logs all SQL queries
)
```

---

## 🚦 Health Checks & Readiness

### Health Check Endpoint
Already implemented:
```bash
GET /health
```

Response: `{"status": "healthy"}`

### Readiness Check for Kubernetes
Add to `main.py`:
```python
@app.get("/readiness")
def readiness():
    try:
        with Session(engine) as session:
            session.exec(select(DiseaseFilesModel)).first()
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(status_code=503, detail="Not ready")
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: farmer-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: farmer-backend
  template:
    metadata:
      labels:
        app: farmer-backend
    spec:
      containers:
      - name: farmer-backend
        image: farmer-backend:latest
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /readiness
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
```

---

## 📈 Performance Optimization

### 1. Database Query Optimization

```python
# Use indexes
class DiseaseFilesModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    crop_name: str = Field(index=True)  # Indexed
    disease_name: str = Field(index=True)  # Indexed
```

### 2. Caching

```bash
pip install redis
pip install fastapi-cache2
```

```python
from fastapi_cache2 import FastAPICache
from fastapi_cache2.backends.redis import RedisBackend

@app.get("/api/disease-files/")
@cached(namespace="disease_files", expire=300)
async def get_disease_files(...):
    ...
```

### 3. Pagination

```python
@app.get("/api/disease-files/")
async def get_disease_files(
    skip: int = 0,
    limit: int = 10,
    session: Session = Depends(get_session)
):
    return session.exec(
        select(DiseaseFilesModel).offset(skip).limit(limit)
    ).all()
```

### 4. Connection Pooling

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True  # Validate connections before use
)
```

---

## 📋 Pre-Deployment Checklist

- [ ] All tests pass: `python validate.py`
- [ ] All endpoints tested: `python test_endpoints.py`
- [ ] Database URL configured correctly
- [ ] CORS origins restricted
- [ ] Secret keys configured (if using auth)
- [ ] Logging configured
- [ ] Error handling implemented
- [ ] Rate limiting configured
- [ ] HTTPS certificate ready (if applicable)
- [ ] Database backups configured
- [ ] Monitoring setup complete
- [ ] Documentation updated
- [ ] Environment variables set
- [ ] Health check endpoint verified
- [ ] Performance tested under load

---

## 🔄 Continuous Deployment

### GitHub Actions Example
```yaml
name: Deploy Farmer Backend

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Build and push Docker image
      run: |
        docker build -t farmer-backend:${{ github.sha }} .
        docker push myregistry/farmer-backend:${{ github.sha }}
    - name: Deploy to production
      run: |
        kubectl set image deployment/farmer-backend farmer-backend=myregistry/farmer-backend:${{ github.sha }}
```

---

## 🆘 Troubleshooting Deployment

| Issue | Solution |
|-------|----------|
| Port already in use | Use different port or kill existing process |
| Database locked | Remove database file and restart |
| Import errors | `pip install --upgrade -r requirements.txt` |
| CORS errors | Update CORS configuration in main.py |
| Memory issues | Increase worker pool size or use Redis |
| Slow queries | Add indexes and enable caching |
| Connection timeout | Check database URL and network connectivity |

---

## 📞 Getting Help

1. Check server logs: `python run_server.py`
2. Run validation: `python validate.py`
3. Check API docs: http://localhost:8000/docs
4. Review documentation files
5. Check error response messages

---

**Last Updated**: November 2025
**Status**: Production Ready ✅
