# ⚡ QUICKSTART - Get Running in 10 Minutes

## Prerequisites Check
- [ ] Python 3.9+ installed
- [ ] Docker Desktop installed and running
- [ ] 8GB+ RAM available
- [ ] VSCode installed (recommended)

---

## 🚀 Step-by-Step Setup

### Step 1: Navigate to Project (30 seconds)
```bash
cd fraud-detection-system
```

### Step 2: Run Setup Script (5 minutes)

**Mac/Linux:**
```bash
chmod +x setup.sh
./setup.sh
```

**Windows:**
```bash
setup.bat
```

This will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Start Docker services (Kafka, Redis, PostgreSQL)
- ✅ Initialize database

---

### Step 3: Train the Model (3 minutes)

```bash
# Activate virtual environment first
# Mac/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Start Jupyter
jupyter notebook
```

1. Open `notebooks/train_model.ipynb`
2. Click "Run All" (Kernel → Restart & Run All)
3. Wait for training to complete
4. Verify `models/fraud_detector.pkl` exists

---

### Step 4: Start the System (2 minutes)

Open **4 terminals** in VSCode (split view).

**Terminal 1 - Transaction Producer:**
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
python src/data/transaction_producer.py
```
*You should see: "🚀 Starting transaction stream..."*

**Terminal 2 - Fraud Detector:**
```bash
source venv/bin/activate
python src/models/fraud_detector_consumer.py
```
*You should see: "🚀 Fraud Detector started"*

**Terminal 3 - API (Optional):**
```bash
source venv/bin/activate
cd src/api
uvicorn main:app --reload
```
*API will be at: http://localhost:8000/docs*

**Terminal 4 - Dashboard:**
```bash
source venv/bin/activate
streamlit run src/monitoring/dashboard.py
```
*Dashboard will open at: http://localhost:8501*

---

## ✅ Verification

You should see:

1. **Terminal 1:** Transactions being generated (✅ LEGIT or 🚨 FRAUD)
2. **Terminal 2:** Predictions being made with latency metrics
3. **Dashboard:** Real-time updates with charts and metrics

Example output:
```
✅ ✅ LEGIT | TXN #45 | $234.56 | grocery
🚨 🚨 FRAUD | TXN #46 | $1,245.99 | online_retail
Latency: 47.23ms
```

---

## 🎯 What to Expect

### Dashboard Metrics:
- **Total Transactions:** Increasing counter
- **Fraud Detected:** ~5% of total
- **Average Latency:** <100ms (target met!)
- **Live Charts:** Updating in real-time

### Performance Targets:
- ✅ Inference latency: <100ms
- ✅ Throughput: 2-10 transactions/second
- ✅ Fraud detection: ~95%+ accuracy
- ✅ Model AUC: >0.90

---

## 🐛 Troubleshooting

### Issue: "Kafka connection refused"
**Solution:** Wait 30 seconds for services to start
```bash
docker-compose ps  # Check if all services are running
```

### Issue: "Model not found"
**Solution:** Train the model first
```bash
jupyter notebook notebooks/train_model.ipynb
# Run all cells
```

### Issue: "Port already in use"
**Solution:** Stop the conflicting process
```bash
# Find process (Mac/Linux)
lsof -i :9092

# Find process (Windows)
netstat -ano | findstr :9092

# Or just restart Docker
docker-compose restart
```

### Issue: "Module not found"
**Solution:** Activate virtual environment
```bash
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows
```

---

## 🛑 Stopping the System

### Stop Python Processes:
Press `Ctrl+C` in each terminal

### Stop Docker Services:
```bash
# Keep data
docker-compose stop

# Remove all data
docker-compose down -v
```

---

## 📊 Next Steps

### 1. Test the API
```bash
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

### 2. View MLflow UI
```bash
mlflow ui
# Open: http://localhost:5000
```

### 3. Explore the Database
```bash
docker exec -it postgres psql -U frauduser -d frauddb
# In psql:
SELECT COUNT(*) FROM transactions;
SELECT * FROM predictions LIMIT 10;
```

### 4. Customize Transaction Rate
Edit `src/data/transaction_producer.py`:
```python
generator.generate_stream(transactions_per_second=10)  # Increase load
```

---

## 📝 Daily Restart Commands

```bash
# 1. Start Docker
docker-compose up -d && sleep 30

# 2. Activate venv
source venv/bin/activate

# 3. Start producer (Terminal 1)
python src/data/transaction_producer.py

# 4. Start detector (Terminal 2)
python src/models/fraud_detector_consumer.py

# 5. Start dashboard (Terminal 3)
streamlit run src/monitoring/dashboard.py
```

---

## 🎓 Learning the Codebase

### Key Files to Explore:
1. `src/data/transaction_producer.py` - Data generation
2. `notebooks/train_model.ipynb` - Model training
3. `src/models/fraud_detector_consumer.py` - Real-time inference
4. `src/api/main.py` - REST API
5. `src/monitoring/dashboard.py` - Monitoring

### Architecture Flow:
```
Producer → Kafka → Consumer → Model → Redis/DB → Dashboard
                              ↓
                           FastAPI
```

---

## 📱 LinkedIn Portfolio

Ready to showcase? Check `LINKEDIN_POSTS.md` for:
- Post templates
- Architecture diagrams
- Demo video tips
- Engagement strategies

---

## 🆘 Need Help?

1. Check `COMMANDS.md` for all available commands
2. Review `README.md` for detailed documentation
3. Check Docker logs: `docker-compose logs -f`
4. Restart everything: `docker-compose down -v && ./setup.sh`

---

## ✨ Success Criteria

You're all set when you see:

✅ Dashboard showing live transactions
✅ Latency consistently <100ms
✅ Fraud detection working (🚨 markers)
✅ All Docker services healthy
✅ Model AUC >0.90 in notebook

---

**🎉 Congratulations! Your fraud detection system is running!**

**Next:** Build your LinkedIn post and show the tech world what you built! 🚀
