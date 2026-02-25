# 🚨 Real-Time E-Commerce Fraud Detection System

A production-grade ML system for detecting fraudulent transactions in real-time with sub-100ms latency.

## 🎯 Project Overview

This project demonstrates:
- **Real-time ML inference** using Kafka streaming
- **Feature engineering & caching** with Redis
- **MLOps best practices** with MLflow
- **Production deployment** with Docker & FastAPI
- **Real-time monitoring** with Streamlit dashboard

## 🏗️ Architecture

```
Transaction Stream → Kafka → Fraud Detector → Predictions Topic
                       ↓              ↓
                    Redis Cache   PostgreSQL
                                      ↓
                               Streamlit Dashboard
```

## 🛠️ Tech Stack

- **Streaming**: Apache Kafka
- **ML Framework**: XGBoost, scikit-learn
- **Feature Store**: Redis
- **Database**: PostgreSQL
- **API**: FastAPI
- **Monitoring**: Streamlit, MLflow
- **Containerization**: Docker

## 📋 Prerequisites

- Python 3.9+
- Docker & Docker Compose
- 8GB+ RAM recommended

## 🚀 Quick Start

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd fraud-detection-system

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start Docker Services

```bash
# Start Kafka, Redis, and PostgreSQL
docker-compose up -d

# Wait for services to be ready (30 seconds)
# Check status:
docker-compose ps
```

### Step 3: Initialize Database

```bash
# Create database tables
python src/data/database.py
```

### Step 4: Train the Model

```bash
# Open Jupyter notebook
jupyter notebook notebooks/train_model.ipynb

# Run all cells to train and save the model
# This will create models/fraud_detector.pkl
```

### Step 5: Run the System

Open **4 separate terminals** in VSCode:

**Terminal 1 - Transaction Producer:**
```bash
python src/data/transaction_producer.py
```

**Terminal 2 - Fraud Detector Consumer:**
```bash
python src/models/fraud_detector_consumer.py
```

**Terminal 3 - FastAPI Service:**
```bash
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 4 - Monitoring Dashboard:**
```bash
streamlit run src/monitoring/dashboard.py
```

### Step 6: View Results

- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **MLflow UI**: `mlflow ui` (port 5000)

## 📊 Expected Results

- **Inference Latency**: < 100ms per transaction
- **Throughput**: 100+ transactions/second
- **Model AUC**: > 0.90
- **Fraud Detection Rate**: ~95%+

## 🎓 Key Features

### 1. Real-Time Processing
- Kafka streaming for transaction ingestion
- Sub-100ms prediction latency
- Scalable consumer architecture

### 2. Advanced ML
- XGBoost classifier with SMOTE for class imbalance
- Feature engineering (time-based, location, behavioral)
- Model versioning with MLflow

### 3. Production-Ready
- Redis caching for user features
- PostgreSQL for transaction storage
- RESTful API for predictions
- Real-time monitoring dashboard

### 4. MLOps Pipeline
- Automated model training
- Experiment tracking
- A/B testing framework ready
- Model drift detection (extensible)

## 📁 Project Structure

```
fraud-detection-system/
├── docker-compose.yml          # Infrastructure setup
├── requirements.txt            # Python dependencies
├── .env                        # Configuration
├── src/
│   ├── data/
│   │   ├── database.py        # Database schema
│   │   └── transaction_producer.py  # Generate transactions
│   ├── models/
│   │   └── fraud_detector_consumer.py  # Real-time inference
│   ├── api/
│   │   └── main.py            # FastAPI service
│   └── monitoring/
│       └── dashboard.py       # Streamlit dashboard
├── notebooks/
│   └── train_model.ipynb      # Model training
└── models/                    # Saved models
```

## 🧪 Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Make prediction
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TEST123",
    "amount": 1500.00,
    "category": "online_retail",
    "hour": 2,
    "day_of_week": 3,
    "latitude": 37.7749,
    "longitude": -122.4194
  }'
```

## 📈 Monitoring & Metrics

The Streamlit dashboard shows:
- Total transactions processed
- Fraud detection rate
- Real-time inference latency
- Transaction distribution
- Recent predictions

## 🔧 Troubleshooting

**Kafka not connecting?**
```bash
# Check if Kafka is running
docker-compose ps

# Restart services
docker-compose restart kafka
```

**Model not found?**
```bash
# Train the model first
jupyter notebook notebooks/train_model.ipynb
```

**Port already in use?**
```bash
# Change ports in docker-compose.yml or .env
```

## 🎯 Next Steps for Enhancement

1. **Add model drift detection** - Monitor prediction distribution
2. **Implement A/B testing** - Compare model versions
3. **Add feature store** - Use Feast for production features
4. **Deploy to cloud** - AWS/GCP with Kubernetes
5. **Add explainability** - SHAP values for predictions

## 📝 LinkedIn Showcase Tips

**Post 1: Architecture**
- Share the architecture diagram
- Highlight real-time processing
- Mention sub-100ms latency

**Post 2: Technical Deep-Dive**
- Explain class imbalance handling (SMOTE)
- Show model performance metrics
- Discuss production considerations

**Post 3: Demo Video**
- Record dashboard showing live predictions
- Demonstrate API usage
- Share GitHub link

## 📄 License

MIT License - Feel free to use for your portfolio!

## 🙏 Acknowledgments

Built with modern MLOps practices for demonstrating production ML systems.

---

**Ready to impress FAANG recruiters?** This project shows you can:
✅ Design scalable ML systems
✅ Handle real-time data streams
✅ Deploy production-ready APIs
✅ Monitor ML systems effectively
