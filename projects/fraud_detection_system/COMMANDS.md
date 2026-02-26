# 🚀 Fraud Detection System - Command Cheat Sheet

## Initial Setup (Run Once)

### For Mac/Linux:
```bash
chmod +x setup.sh
./setup.sh
```

### For Windows:
```bash
setup.bat
```

### Manual Setup:
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Docker services
docker-compose up -d

# 5. Initialize database
python src/data/database.py
```

---

## Daily Usage Commands

### Start All Services

**Terminal 1 - Start Docker Services:**
```bash
docker-compose up -d
```

**Terminal 2 - Transaction Producer:**
```bash
# Activate venv first, then:
python src/data/transaction_producer.py
```

**Terminal 3 - Fraud Detector:**
```bash
# Activate venv first, then:
python src/models/fraud_detector_consumer.py
```

**Terminal 4 - API Server:**
```bash
# Activate venv first, then:
cd src/api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 5 - Dashboard:**
```bash
# Activate venv first, then:
streamlit run src/monitoring/dashboard.py
```

**Terminal 6 - Jupyter (for training):**
```bash
# Activate venv first, then:
jupyter notebook
```

---

## Docker Commands

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# View logs
docker-compose logs -f

# Check service status
docker-compose ps

# Restart a specific service
docker-compose restart kafka

# Remove all containers and volumes (CAREFUL!)
docker-compose down -v
```

---

## Kafka Commands (inside Docker)

```bash
# List topics
docker exec -it kafka kafka-topics --bootstrap-server localhost:9092 --list

# Consume from transactions topic
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic transactions \
  --from-beginning

# Consume from predictions topic
docker exec -it kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic predictions \
  --from-beginning
```

---

## Database Commands

```bash
# Connect to PostgreSQL
docker exec -it postgres psql -U frauduser -d frauddb

# Inside psql:
\dt                          # List tables
SELECT COUNT(*) FROM transactions;
SELECT COUNT(*) FROM predictions;
SELECT * FROM transactions LIMIT 10;
```

---

## Redis Commands

```bash
# Connect to Redis CLI
docker exec -it redis redis-cli

# Inside redis-cli:
KEYS *                       # List all keys
GET user:USER_0001:transactions
FLUSHALL                     # Clear all data (CAREFUL!)
```

---

## Testing the API

```bash
# Health check
curl http://localhost:8000/health

# Get metrics
curl http://localhost:8000/metrics

# Make a prediction
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

# View API docs
# Open in browser: http://localhost:8000/docs
```

---

## MLflow Commands

```bash
# Start MLflow UI
mlflow ui

# Open in browser: http://localhost:5000

# View experiment runs
mlflow experiments list

# Compare models
mlflow models --help
```

---

## Jupyter Notebook

```bash
# Start Jupyter
jupyter notebook

# Or use VSCode Jupyter extension
# Open notebooks/train_model.ipynb in VSCode
```

---

## Troubleshooting

### Kafka Connection Issues
```bash
# Restart Kafka
docker-compose restart kafka zookeeper

# Wait 30 seconds, then try again
```

### Port Already in Use
```bash
# Find process using port (Mac/Linux)
lsof -i :8000
lsof -i :9092

# Find process using port (Windows)
netstat -ano | findstr :8000

# Kill process
kill -9 <PID>        # Mac/Linux
taskkill /F /PID <PID>  # Windows
```

### Model Not Found
```bash
# Train the model first
jupyter notebook notebooks/train_model.ipynb
# Run all cells
```

### Clean Restart
```bash
# Stop everything
docker-compose down -v

# Start fresh
docker-compose up -d

# Wait 30 seconds
sleep 30

# Reinitialize database
python src/data/database.py
```

---

## Quick Start (Copy-Paste)

### Terminal 1:
```bash
docker-compose up -d && sleep 30 && python src/data/transaction_producer.py
```

### Terminal 2:
```bash
python src/models/fraud_detector_consumer.py
```

### Terminal 3:
```bash
streamlit run src/monitoring/dashboard.py
```

---

## URLs to Bookmark

- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **API Health**: http://localhost:8000/health
- **MLflow UI**: http://localhost:5000

---

## Git Commands (for GitHub)

```bash
# Initialize git
git init

# Add files
git add .

# Commit
git commit -m "Initial commit: Real-time fraud detection system"

# Add remote (replace with your repo)
git remote add origin https://github.com/YOUR_USERNAME/fraud-detection-system.git

# Push
git push -u origin main
```

---

## Performance Testing

```bash
# Generate high-volume transactions (10 per second)
# Modify transaction_producer.py:
# generator.generate_stream(transactions_per_second=10)

# Monitor system resources
docker stats

# Check latency metrics in dashboard
```

---

## Stopping Everything

```bash
# Stop all Python processes (Ctrl+C in each terminal)

# Stop Docker services
docker-compose down

# Keep data:
docker-compose stop

# Remove all data:
docker-compose down -v
```
