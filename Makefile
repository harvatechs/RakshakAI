# RakshakAI - Makefile
# Quick commands for development and deployment

.PHONY: help install dev test build docker clean

# Default target
help:
	@echo "🛡️  RakshakAI - Available Commands:"
	@echo ""
	@echo "  make install          Install all dependencies"
	@echo "  make dev              Start development environment"
	@echo "  make test             Run all tests"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo "  make train            Train ML model"
	@echo "  make dashboard        Launch Streamlit dashboard"
	@echo "  make backend          Start FastAPI backend"
	@echo "  make docker-up        Start Docker infrastructure"
	@echo "  make docker-down      Stop Docker infrastructure"
	@echo "  make clean            Clean generated files"
	@echo ""

# Installation
install:
	@echo "📦 Installing Python dependencies..."
	pip install -r backend/requirements.txt
	@echo "📦 Installing Node dependencies..."
	cd law_enforcement_portal && npm install
	@echo "✅ Installation complete!"

# Development
dev:
	@echo "🚀 Starting development environment..."
	make docker-up
	@echo "Waiting for services to start..."
	sleep 5
	@echo "✅ Development environment ready!"
	@echo "  - Backend: http://localhost:8000"
	@echo "  - Dashboard: http://localhost:3000"
	@echo "  - Grafana: http://localhost:3000"

# Testing
test:
	@echo "🧪 Running tests..."
	cd backend && python -m pytest ../tests/ -v --tb=short

test-coverage:
	@echo "📊 Running tests with coverage..."
	cd backend && python -m pytest ../tests/ --cov=. --cov-report=html --cov-report=term
	@echo "📈 Coverage report: backend/htmlcov/index.html"

# ML Training
train:
	@echo "🤖 Training ML model..."
	cd ml_pipeline/training && python dataset_generator.py
	cd ml_pipeline/training && python train_classifier.py
	@echo "✅ Model training complete!"

# Dashboard
dashboard:
	@echo "📊 Launching Streamlit dashboard..."
	streamlit run gui_dashboard/app.py

# Backend
backend:
	@echo "⚙️  Starting FastAPI backend..."
	cd backend && uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Docker
docker-up:
	@echo "🐳 Starting Docker infrastructure..."
	cd infrastructure && docker-compose up -d
	docker-up-build:
	@echo "🐳 Building and starting Docker infrastructure..."
	cd infrastructure && docker-compose up --build -d

docker-down:
	@echo "🛑 Stopping Docker infrastructure..."
	cd infrastructure && docker-compose down

docker-logs:
	@echo "📜 Viewing Docker logs..."
	cd infrastructure && docker-compose logs -f

# Cleanup
clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleanup complete!"

# Colab
colab:
	@echo "📓 Opening Google Colab notebook..."
	@echo "Visit: https://colab.research.google.com/github/harvatechs/RakshakAI/blob/main/colab/RakshakAI_Colab.ipynb"

# OSINT Tools
osint-phone:
	@echo "🔍 OSINT Phone Lookup"
	@read -p "Enter phone number: " phone; \
	cd backend && python -c "import asyncio; from osint_tools.scammer_osint import get_osint_tool; \
	async def main(): tool = await get_osint_tool(); result = await tool.investigate_phone_number('$$phone'); print(json.dumps(result, indent=2, default=str)); \
	asyncio.run(main())"

osint-upi:
	@echo "🔍 OSINT UPI Lookup"
	@read -p "Enter UPI ID: " upi; \
	cd backend && python -c "import asyncio; from osint_tools.scammer_osint import get_osint_tool; \
	async def main(): tool = await get_osint_tool(); result = await tool.investigate_upi_id('$$upi'); print(json.dumps(result, indent=2, default=str)); \
	asyncio.run(main())"

# Dataset generation
dataset:
	@echo "📊 Generating synthetic dataset..."
	cd ml_pipeline/training && python dataset_generator.py
	@echo "✅ Dataset generated!"

# Full setup for hackathons
hackathon-setup:
	@echo "🏆 Setting up for hackathon..."
	make install
	make dataset
	make train
	@echo ""
	@echo "✅ Hackathon setup complete!"
	@echo ""
	@echo "Next steps:"
	@echo "  1. Add GEMINI_API_KEY to .env"
	@echo "  2. Run: make dashboard"
	@echo "  3. Or open colab/RakshakAI_Colab.ipynb"

# Production deployment
prod-deploy:
	@echo "🚀 Deploying to production..."
	make docker-up-build
	@echo "✅ Production deployment complete!"
