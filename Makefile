.PHONY: help install dev build clean docker-build docker-run test lint

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies for both backend and frontend
	@echo "Installing backend dependencies..."
	cd backend && python -m pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

dev: ## Start development servers
	@echo "Starting development servers..."
	cd backend && python main.py &
	cd frontend && npm start

build: ## Build production assets
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "Build complete!"

clean: ## Clean build artifacts and dependencies
	@echo "Cleaning build artifacts..."
	rm -rf frontend/build
	rm -rf frontend/node_modules
	rm -rf backend/__pycache__
	rm -rf backend/*.pyc

docker-build: ## Build Docker images
	@echo "Building Docker images..."
	docker-compose build

docker-run: ## Run with Docker Compose
	@echo "Starting services with Docker Compose..."
	docker-compose up -d

docker-stop: ## Stop Docker services
	@echo "Stopping Docker services..."
	docker-compose down

docker-logs: ## Show Docker logs
	docker-compose logs -f

test: ## Run tests
	@echo "Running backend tests..."
	cd backend && python -m pytest
	@echo "Running frontend tests..."
	cd frontend && npm test

lint: ## Run linters
	@echo "Running Python linting..."
	cd backend && python -m flake8 .
	@echo "Running JavaScript linting..."
	cd frontend && npm run lint

setup-certs: ## Setup self-signed certificates for development
	@echo "Creating self-signed certificates..."
	mkdir -p certs
	openssl req -x509 -newkey rsa:4096 -keyout certs/private_key.pem -out certs/certificate.pem -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/OU=OrgUnit/CN=localhost"
	@echo "Certificates created in certs/ directory"

check-deps: ## Check for dependency updates
	@echo "Checking Python dependencies..."
	cd backend && pip list --outdated
	@echo "Checking Node.js dependencies..."
	cd frontend && npm outdated
