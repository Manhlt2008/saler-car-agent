#!/bin/bash

# Development setup script for AI Car Agent

echo "🚀 Setting up AI Car Agent Development Environment..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL is not installed. You can use Docker instead."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file from template..."
    cp env.example .env
    echo "📝 Please update .env file with your API keys and database configuration."
fi

# Check if .env file has required variables
echo "🔍 Checking environment configuration..."
if ! grep -q "OPENAI_API_KEY" .env || ! grep -q "GOOGLE_MAPS_API_KEY" .env || ! grep -q "SENDGRID_API_KEY" .env; then
    echo "⚠️  Please update .env file with your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - GOOGLE_MAPS_API_KEY"
    echo "   - SENDGRID_API_KEY"
fi

# Create database if using local PostgreSQL
if command -v psql &> /dev/null; then
    echo "🗄️  Setting up database..."
    createdb car_agent_db 2>/dev/null || echo "Database already exists or using different setup"
fi

# Run database migrations
echo "🔄 Running database migrations..."
cd backend
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database tables created')"
cd ..

# Seed sample data
echo "🌱 Seeding sample data..."
python scripts/seed_data.py

echo ""
echo "🎉 Development environment setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env file with your API keys"
echo "2. Start the backend:"
echo "   cd backend && python app.py"
echo ""
echo "3. Start the frontend (in a new terminal):"
echo "   cd frontend && npm start"
echo ""
echo "4. Open http://localhost:3000 in your browser"
echo ""
echo "🐳 Alternative: Use Docker Compose"
echo "   docker-compose up -d"
echo ""
echo "📚 For more information, see README.md"


