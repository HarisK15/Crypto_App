.PHONY: help install test lint format clean run docker-build docker-run docker-stop setup-dev

# Default target
help:
	@echo "Crypto Alert Dashboard - Available Commands:"
	@echo ""
	@echo "Development:"
	@echo "  install      Install Python dependencies"
	@echo "  run          Run the application locally"
	@echo "  test         Run tests with pytest"
	@echo "  lint         Run code linting with flake8"
	@echo "  format       Format code with black"
	@echo "  clean        Clean up temporary files and cache"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build Build Docker image"
	@echo "  docker-run   Run with Docker Compose"
	@echo "  docker-stop  Stop Docker containers"
	@echo ""
	@echo "Setup:"
	@echo "  setup-dev    Setup development environment"
	@echo "  setup-env    Create .env file from template"

# Install dependencies
install:
	pip install -r requirements.txt

# Run the application
run:
	streamlit run app.py

# Run tests
test:
	pytest tests/ -v --cov=. --cov-report=html

# Run linting
lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Format code
format:
	black . --line-length=127
	isort .

# Clean up
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -delete
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf build/
	rm -rf dist/

# Docker commands
docker-build:
	docker build -t crypto-alert-dashboard .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

# Development setup
setup-dev: install setup-env
	@echo "Development environment setup complete!"
	@echo "Next steps:"
	@echo "1. Edit .env file with your API keys"
	@echo "2. Run 'make run' to start the application"

# Create environment file
setup-env:
	@if [ ! -f .env ]; then \
		cp env_template.txt .env; \
		echo "Created .env file from template"; \
		echo "Please edit .env with your actual values"; \
	else \
		echo ".env file already exists"; \
	fi

# Database operations
db-init:
	python -c "from database import db_manager; print('Database initialized')"

db-backup:
	python -c "from database import db_manager; db_manager.backup_database('backups/manual_backup.db')"

db-stats:
	python -c "from database import db_manager; import json; print(json.dumps(db_manager.get_database_stats(), indent=2))"

# Production deployment
deploy-prod:
	@echo "Deploying to production..."
	docker-compose -f docker-compose.yml up -d --build
	@echo "Production deployment complete!"

# Health check
health-check:
	@echo "Checking application health..."
	@curl -f http://localhost:8501/_stcore/health || echo "Application not responding"

# Full development cycle
dev-cycle: clean install format lint test
	@echo "Development cycle complete!"

# Quick start for new developers
quickstart: setup-dev
	@echo ""
	@echo "🚀 Quick Start Guide:"
	@echo "1. Edit .env file with your API keys"
	@echo "2. Run 'make run' to start the app"
	@echo "3. Open http://localhost:8501 in your browser"
	@echo "4. Add some coins to your watchlist"
	@echo "5. Set price alerts and enjoy!"
