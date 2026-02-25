#!/bin/bash

# Fraud Detection System Setup Script
# This script automates the entire setup process

set -e  # Exit on error

echo "🚀 Setting up Fraud Detection System..."
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo -e "${YELLOW}Step 1: Checking Python installation...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Found $PYTHON_VERSION${NC}"
else
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

# Step 2: Check Docker
echo -e "${YELLOW}Step 2: Checking Docker installation...${NC}"
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✅ Found $DOCKER_VERSION${NC}"
else
    echo "❌ Docker not found. Please install Docker Desktop."
    exit 1
fi

# Step 3: Create virtual environment
echo -e "${YELLOW}Step 3: Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Step 4: Activate and install dependencies
echo -e "${YELLOW}Step 4: Installing Python dependencies...${NC}"
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo -e "${GREEN}✅ Dependencies installed${NC}"

# Step 5: Start Docker services
echo -e "${YELLOW}Step 5: Starting Docker services...${NC}"
docker-compose up -d
echo -e "${GREEN}✅ Docker services starting...${NC}"

# Step 6: Wait for services
echo -e "${YELLOW}Step 6: Waiting for services to be ready (30 seconds)...${NC}"
for i in {30..1}; do
    echo -ne "\r⏳ Waiting... $i seconds remaining   "
    sleep 1
done
echo ""
echo -e "${GREEN}✅ Services should be ready${NC}"

# Step 7: Initialize database
echo -e "${YELLOW}Step 7: Initializing database...${NC}"
python src/data/database.py
echo -e "${GREEN}✅ Database initialized${NC}"

# Final instructions
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Next steps:"
echo ""
echo "1. Train the model:"
echo "   jupyter notebook notebooks/train_model.ipynb"
echo ""
echo "2. Start the system (in separate terminals):"
echo ""
echo "   Terminal 1 - Producer:"
echo "   python src/data/transaction_producer.py"
echo ""
echo "   Terminal 2 - Consumer:"
echo "   python src/models/fraud_detector_consumer.py"
echo ""
echo "   Terminal 3 - API:"
echo "   cd src/api && uvicorn main:app --reload"
echo ""
echo "   Terminal 4 - Dashboard:"
echo "   streamlit run src/monitoring/dashboard.py"
echo ""
echo "3. View the dashboard at: http://localhost:8501"
echo ""
echo -e "${YELLOW}Happy fraud detecting! 🚨${NC}"
