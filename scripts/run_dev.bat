@echo off
REM Development setup script for AI Car Agent (Windows)

echo 🚀 Setting up AI Car Agent Development Environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.9+ first.
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ first.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
npm install
cd ..

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo ⚙️ Creating .env file from template...
    copy env.example .env
    echo 📝 Please update .env file with your API keys and database configuration.
)

REM Check if .env file has required variables
echo 🔍 Checking environment configuration...
findstr /C:"OPENAI_API_KEY" .env >nul
if errorlevel 1 (
    echo ⚠️ Please update .env file with your API keys:
    echo    - OPENAI_API_KEY
    echo    - GOOGLE_MAPS_API_KEY
    echo    - SENDGRID_API_KEY
)

REM Run database migrations
echo 🔄 Running database migrations...
cd backend
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database tables created')"
cd ..

REM Seed sample data
echo 🌱 Seeding sample data...
python scripts/seed_data.py

echo.
echo 🎉 Development environment setup completed!
echo.
echo 📋 Next steps:
echo 1. Update .env file with your API keys
echo 2. Start the backend:
echo    cd backend ^&^& python app.py
echo.
echo 3. Start the frontend (in a new terminal):
echo    cd frontend ^&^& npm start
echo.
echo 4. Open http://localhost:3000 in your browser
echo.
echo 🐳 Alternative: Use Docker Compose
echo    docker-compose up -d
echo.
echo 📚 For more information, see README.md
pause


