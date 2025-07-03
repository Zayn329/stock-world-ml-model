# AI-Powered Financial Insights Platform - Deployment Guide

## 🚀 Quick Start

This guide will help you deploy the complete AI-powered financial insights platform using Docker Compose.

## 📋 Prerequisites

### System Requirements
- **OS**: Linux, macOS, or Windows with WSL2
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: Minimum 20GB free space
- **CPU**: Multi-core processor (4+ cores recommended)

### Software Dependencies
- **Docker**: Version 20.0+
- **Docker Compose**: Version 2.0+
- **Git**: For cloning the repository

### API Keys (Optional but Recommended)
- **News API**: For real-time news data
- **Alpha Vantage**: For financial data
- **Twitter API**: For social media sentiment
- **OpenAI/Hugging Face**: For enhanced AI models

## 🏗️ Architecture Overview

The platform consists of several microservices:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   ML Services   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (PyTorch)     │
│   Port: 3000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   PostgreSQL    │    │     Redis       │
│   Port: 80/443  │    │   Port: 5432    │    │   Port: 6379    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Monitoring    │    │     Kafka       │    │   Grafana       │
│  (Prometheus)   │    │   Port: 9092    │    │   Port: 3001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/financial-insights-platform.git
cd financial-insights-platform
```

### 2. Configure Environment Variables

Create environment files:

```bash
# Backend configuration
cp backend/.env.example backend/.env

# Frontend configuration
cat > frontend/.env << EOF
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000
GENERATE_SOURCEMAP=false
EOF
```

Edit `backend/.env` with your API keys and configuration:

```bash
# Required: Database configuration
DATABASE_URL=postgresql://postgres:password123@postgres:5432/financial_insights
REDIS_URL=redis://redis:6379/0

# Optional: External API keys for enhanced functionality
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
NEWS_API_KEY=your_news_api_key
TWITTER_BEARER_TOKEN=your_twitter_bearer_token

# Security (Change these in production!)
SECRET_KEY=your-secret-key-change-in-production

# ML Configuration
MODEL_PATH=./models
SENTIMENT_MODEL_NAME=ProsusAI/finbert
```

### 3. Deploy with Docker Compose

#### Option A: Full Deployment (Recommended)

```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

#### Option B: Development Mode

```bash
# Start only core services
docker-compose up -d postgres redis kafka

# Run backend in development mode
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run frontend in development mode (new terminal)
cd frontend
npm install
npm start
```

### 4. Verify Deployment

Check that all services are running:

```bash
# Check service health
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check API documentation
open http://localhost:8000/docs
```

## 🔧 Configuration

### Database Setup

The PostgreSQL database will be automatically initialized. For custom setup:

```bash
# Connect to database
docker-compose exec postgres psql -U postgres -d financial_insights

# Run migrations (if needed)
docker-compose exec backend alembic upgrade head
```

### Model Configuration

The platform uses several AI models:

1. **FinBERT**: For financial sentiment analysis
2. **Technical Indicators**: TA-Lib based analysis
3. **SHAP**: For explainable AI

Models are automatically downloaded on first run. To pre-download:

```bash
# Download models
docker-compose exec backend python -c "
from app.services.model_service import ModelService
import asyncio
async def download():
    service = ModelService()
    await service.initialize_models()
asyncio.run(download())
"
```

### Monitoring Setup

Access monitoring dashboards:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin123)

## 📊 Usage

### Web Interface

1. **Dashboard**: http://localhost:3000
   - Market overview
   - Real-time sentiment
   - Key metrics

2. **Stock Analysis**: http://localhost:3000/analysis
   - Comprehensive stock analysis
   - Sentiment + Technical + Fundamental

3. **Predictions**: http://localhost:3000/predictions
   - AI-powered predictions
   - Confidence intervals

4. **Explain AI**: http://localhost:3000/explain-ai
   - Model interpretability
   - Feature importance

### API Usage

```bash
# Get sentiment analysis
curl http://localhost:8000/api/v1/sentiment/AAPL

# Get technical analysis
curl http://localhost:8000/api/v1/technical/AAPL

# Create prediction
curl -X POST http://localhost:8000/api/v1/predictions/AAPL \
  -H "Content-Type: application/json" \
  -d '{"prediction_type": "price", "time_horizon": "1d"}'

# Get explainability
curl http://localhost:8000/api/v1/explainability/prediction/{prediction_id}
```

### WebSocket Real-time Updates

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:8000/ws/client123');

// Subscribe to real-time updates
ws.send(JSON.stringify({
  type: 'subscribe',
  topic: 'sentiment_updates'
}));

// Receive updates
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};
```

## 🔒 Security

### Production Security Checklist

- [ ] Change default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure firewall rules
- [ ] Set up authentication
- [ ] Enable API rate limiting
- [ ] Regular security updates

### SSL Configuration

For production HTTPS:

```bash
# Generate SSL certificates
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/private.key \
  -out nginx/ssl/certificate.crt
```

## 📈 Scaling

### Horizontal Scaling

Scale individual services:

```bash
# Scale backend API
docker-compose up -d --scale backend=3

# Scale frontend
docker-compose up -d --scale frontend=2
```

### Performance Optimization

1. **Database**: Add read replicas for heavy read workloads
2. **Redis**: Use Redis Cluster for high availability
3. **ML Models**: Use GPU acceleration for faster inference
4. **Load Balancing**: Add HAProxy or AWS ALB

### Resource Monitoring

Monitor resource usage:

```bash
# Check resource usage
docker stats

# Check logs
docker-compose logs -f backend

# Database performance
docker-compose exec postgres pg_stat_activity
```

## 🐛 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   lsof -i :8000
   
   # Change ports in docker-compose.yml
   ```

2. **Memory Issues**
   ```bash
   # Increase Docker memory limit
   # Check Docker Desktop settings
   
   # Reduce model batch size
   BATCH_SIZE=16
   ```

3. **Model Loading Errors**
   ```bash
   # Clear model cache
   docker-compose exec backend rm -rf /app/cache/*
   
   # Restart services
   docker-compose restart backend
   ```

4. **Database Connection Issues**
   ```bash
   # Check database logs
   docker-compose logs postgres
   
   # Test connection
   docker-compose exec backend python -c "
   from app.core.config import settings
   print(settings.DATABASE_URL)
   "
   ```

### Logs and Debugging

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Enter container for debugging
docker-compose exec backend bash
docker-compose exec postgres psql -U postgres
```

## 🔄 Updates and Maintenance

### Update Procedure

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart services
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head
```

### Backup and Recovery

```bash
# Backup database
docker-compose exec postgres pg_dump -U postgres financial_insights > backup.sql

# Backup models and data
docker-compose exec backend tar -czf models_backup.tar.gz /app/models

# Restore database
docker-compose exec -T postgres psql -U postgres financial_insights < backup.sql
```

## 📞 Support

### Getting Help

1. **Documentation**: Check README.md and API docs
2. **Issues**: Create GitHub issues for bugs
3. **Discussions**: Use GitHub Discussions for questions
4. **Monitoring**: Check Grafana dashboards for system health

### Performance Metrics

The platform tracks:
- API response times
- Model inference latency
- Database query performance
- Memory and CPU usage
- Error rates and uptime

### Development

For development contributions:

```bash
# Install development dependencies
cd backend && pip install -r requirements-dev.txt
cd frontend && npm install

# Run tests
cd backend && pytest
cd frontend && npm test

# Code formatting
cd backend && black . && isort .
cd frontend && npm run format
```

## 🎯 Next Steps

After successful deployment:

1. **Configure Data Sources**: Add your API keys for real data
2. **Train Custom Models**: Use your domain-specific data
3. **Set Up Alerts**: Configure monitoring alerts
4. **Scale Resources**: Adjust based on usage patterns
5. **Add Features**: Extend with custom analysis modules

---

**🎉 Congratulations!** Your AI-powered financial insights platform is now running. Visit http://localhost:3000 to start exploring!