# AI-Powered Financial Insights Platform

A comprehensive AI platform that combines sentiment analysis, fundamental data, and technical indicators to provide explainable stock market predictions and insights.

## 🚀 Features

### Core Capabilities
- **Hybrid Data Integration**: Fuses sentiment (social media, news), fundamental (financials, macro), and technical (price/volume) data
- **Advanced Sentiment Analysis**: BERT/RoBERTa-based models for financial text understanding
- **Real-time Data Pipelines**: Scalable ingestion from multiple data sources
- **Explainable AI**: SHAP and LIME integration for transparent predictions
- **Interactive Dashboard**: Modern React-based UI with real-time updates

### AI/ML Components
- Deep learning models (BERT, RoBERTa, LSTMs, CNNs)
- Time-series analysis for market patterns
- Genetic algorithm-based feature selection
- Adaptive learning with drift detection
- Multi-modal data fusion

## 🏗️ Architecture

```
├── backend/                 # FastAPI backend service
│   ├── app/
│   │   ├── api/            # API routes and endpoints
│   │   ├── models/         # ML models and data models
│   │   ├── services/       # Business logic services
│   │   ├── utils/          # Utility functions
│   │   └── core/           # Core configuration
│   ├── ml/                 # Machine learning components
│   │   ├── sentiment/      # Sentiment analysis models
│   │   ├── technical/      # Technical analysis
│   │   ├── fundamental/    # Fundamental analysis
│   │   └── explainability/ # XAI components
│   └── data/               # Data processing pipelines
├── frontend/               # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── utils/          # Utility functions
│   │   └── hooks/          # Custom React hooks
├── infrastructure/         # Deployment and infrastructure
├── data/                   # Sample data and datasets
└── docs/                   # Documentation
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **PyTorch/TensorFlow**: Deep learning frameworks
- **Transformers**: BERT/RoBERTa models
- **Kafka**: Real-time data streaming
- **PostgreSQL**: Primary database
- **Redis**: Caching and real-time features

### Frontend
- **React 18**: Modern frontend framework
- **TailwindCSS**: Utility-first CSS framework
- **D3.js**: Data visualization
- **WebSockets**: Real-time updates
- **Recharts**: Chart components

### AI/ML
- **BERT/RoBERTa**: Sentiment analysis
- **LSTM/CNN**: Time-series modeling
- **SHAP/LIME**: Explainable AI
- **scikit-learn**: Traditional ML algorithms
- **TA-Lib**: Technical analysis indicators

### Infrastructure
- **Docker**: Containerization
- **AWS/GCP**: Cloud deployment
- **Kubernetes**: Container orchestration
- **Prometheus**: Monitoring

## 🚦 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Docker & Docker Compose

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm start
```

### Docker Setup
```bash
docker-compose up -d
```

## 📊 API Documentation

Once running, access:
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000

## 🔧 Configuration

Environment variables and configuration files:
- `backend/.env`: Backend configuration
- `frontend/.env`: Frontend configuration
- `docker-compose.yml`: Container orchestration

## 📈 Usage Examples

### Real-time Sentiment Analysis
```python
# Get sentiment for a stock
response = requests.get(f"/api/v1/sentiment/{ticker}")
```

### Technical Analysis
```python
# Get technical indicators
response = requests.get(f"/api/v1/technical/{ticker}")
```

### Explainable Predictions
```python
# Get prediction with explanations
response = requests.get(f"/api/v1/predict/{ticker}?explain=true")
```

## 🧪 Testing

```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend && npm test
```

## 📋 Roadmap

- [ ] Enhanced sentiment models
- [ ] Multi-asset support
- [ ] Advanced portfolio analytics
- [ ] Mobile application
- [ ] Market anomaly detection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.