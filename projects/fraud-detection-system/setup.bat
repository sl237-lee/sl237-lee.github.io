@echo off
REM Fraud Detection System Setup Script for Windows

echo ========================================
echo 🚀 Setting up Fraud Detection System...
echo ========================================
echo.

REM Step 1: Check Python
echo Step 1: Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found. Please install Python 3.9 or higher.
    pause
    exit /b 1
)
echo ✅ Python found
echo.

REM Step 2: Check Docker
echo Step 2: Checking Docker installation...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker not found. Please install Docker Desktop.
    pause
    exit /b 1
)
echo ✅ Docker found
echo.

REM Step 3: Create virtual environment
echo Step 3: Creating virtual environment...
if not exist venv (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Step 4: Activate and install dependencies
echo Step 4: Installing Python dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
echo ✅ Dependencies installed
echo.

REM Step 5: Start Docker services
echo Step 5: Starting Docker services...
docker-compose up -d
echo ✅ Docker services starting...
echo.

REM Step 6: Wait for services
echo Step 6: Waiting for services to be ready (30 seconds)...
timeout /t 30 /nobreak >nul
echo ✅ Services should be ready
echo.

REM Step 7: Initialize database
echo Step 7: Initializing database...
python src\data\database.py
echo ✅ Database initialized
echo.

REM Final instructions
echo ========================================
echo 🎉 Setup Complete!
echo ========================================
echo.
echo Next steps:
echo.
echo 1. Train the model:
echo    jupyter notebook notebooks\train_model.ipynb
echo.
echo 2. Start the system (in separate terminals):
echo.
echo    Terminal 1 - Producer:
echo    python src\data\transaction_producer.py
echo.
echo    Terminal 2 - Consumer:
echo    python src\models\fraud_detector_consumer.py
echo.
echo    Terminal 3 - API:
echo    cd src\api ^&^& uvicorn main:app --reload
echo.
echo    Terminal 4 - Dashboard:
echo    streamlit run src\monitoring\dashboard.py
echo.
echo 3. View the dashboard at: http://localhost:8501
echo.
echo Happy fraud detecting! 🚨
echo.
pause
