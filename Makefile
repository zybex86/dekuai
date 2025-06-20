# ===================================================================
# 🎮 AutoGen DekuDeals - Docker Production Makefile
# Enterprise-level deployment and management commands
# ===================================================================

.PHONY: help build dev prod test clean logs status shell health setup ci-build ci-deploy ci-deploy-mode ci-quick ci-status ci-test ci-cleanup ci-full

# Variables
VERSION ?= 6.3.0
BUILD_DATE := $(shell date -u +'%Y-%m-%dT%H:%M:%SZ')
VCS_REF := $(shell git rev-parse --short HEAD 2>/dev/null || echo 'unknown')
IMAGE_NAME := autogen-dekudeals
CONTAINER_NAME := autogen-dekudeals

# Colors for output
RED    := \033[31m
GREEN  := \033[32m
YELLOW := \033[33m
BLUE   := \033[34m
RESET  := \033[0m

# ===================================================================
# Help Target
# ===================================================================
help: ## Show this help message
	@echo "$(BLUE)🎮 AutoGen DekuDeals - Docker Management$(RESET)"
	@echo "$(BLUE)================================================$(RESET)"
	@echo ""
	@echo "$(GREEN)Development Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(dev|build|test)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Production Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "(prod|deploy)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(GREEN)Management Commands:$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -vE "(dev|build|test|prod|deploy)" | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BLUE)Environment Variables:$(RESET)"
	@echo "  VERSION=$(VERSION)"
	@echo "  BUILD_DATE=$(BUILD_DATE)"
	@echo "  VCS_REF=$(VCS_REF)"

# ===================================================================
# Setup and Configuration
# ===================================================================
setup: ## Initial setup - create necessary directories and files
	@echo "$(BLUE)🔧 Setting up AutoGen DekuDeals...$(RESET)"
	@mkdir -p cache logs data production/cache production/logs production/data
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)📝 Creating .env from template...$(RESET)"; \
		cp env.example .env; \
		echo "$(GREEN)✅ Please edit .env with your OpenAI API key$(RESET)"; \
	else \
		echo "$(GREEN)✅ .env file already exists$(RESET)"; \
	fi
	@chmod +x entrypoint.sh
	@echo "$(GREEN)✅ Setup completed!$(RESET)"

check-env: ## Check if required environment variables are set
	@echo "$(BLUE)🔍 Checking environment configuration...$(RESET)"
	@if [ -z "$$OPENAI_API_KEY" ] && [ ! -f .env ]; then \
		echo "$(RED)❌ OPENAI_API_KEY not set and no .env file found$(RESET)"; \
		echo "$(YELLOW)💡 Run 'make setup' first$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Environment check passed$(RESET)"

# ===================================================================
# Build Commands
# ===================================================================
build: ## Build Docker image for development
	@echo "$(BLUE)🏗️  Building Docker image...$(RESET)"
	docker build \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		--build-arg VERSION=$(VERSION) \
		--build-arg VCS_REF=$(VCS_REF) \
		-t $(IMAGE_NAME):$(VERSION) \
		-t $(IMAGE_NAME):latest \
		.
	@echo "$(GREEN)✅ Build completed: $(IMAGE_NAME):$(VERSION)$(RESET)"

build-prod: ## Build optimized production image
	@echo "$(BLUE)🏭 Building production Docker image...$(RESET)"
	docker build \
		--build-arg BUILD_DATE=$(BUILD_DATE) \
		--build-arg VERSION=$(VERSION) \
		--build-arg VCS_REF=$(VCS_REF) \
		--target production \
		-t $(IMAGE_NAME):$(VERSION)-prod \
		-t $(IMAGE_NAME):prod \
		.
	@echo "$(GREEN)✅ Production build completed: $(IMAGE_NAME):$(VERSION)-prod$(RESET)"

# ===================================================================
# Development Commands
# ===================================================================
dev: setup check-env build ## Start development environment
	@echo "$(BLUE)🚀 Starting development environment...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)✅ Development environment started$(RESET)"
	@echo "$(YELLOW)📝 Run 'make logs' to see container logs$(RESET)"
	@echo "$(YELLOW)🐚 Run 'make shell' to access container shell$(RESET)"

dev-cli: setup check-env build ## Start development with interactive CLI
	@echo "$(BLUE)🎮 Starting interactive CLI...$(RESET)"
	docker run --rm -it \
		--env-file .env \
		-v $(PWD)/cache:/app/cache \
		-v $(PWD)/logs:/app/logs \
		$(IMAGE_NAME):latest cli

dev-quick: setup check-env build ## Quick game analysis in development
	@read -p "Enter game name: " game; \
	echo "$(BLUE)⚡ Running quick analysis for: $$game$(RESET)"; \
	docker run --rm -it \
		--env-file .env \
		-v $(PWD)/cache:/app/cache \
		-v $(PWD)/logs:/app/logs \
		$(IMAGE_NAME):latest quick "$$game"

# ===================================================================
# Production Commands
# ===================================================================
prod-deploy: setup check-env build-prod ## Deploy to production
	@echo "$(BLUE)🏭 Deploying to production...$(RESET)"
	@mkdir -p production/cache production/logs production/data
	export VERSION=$(VERSION) && \
	export BUILD_DATE=$(BUILD_DATE) && \
	export VCS_REF=$(VCS_REF) && \
	docker-compose -f docker-compose.prod.yml up -d
	@echo "$(GREEN)✅ Production deployment completed$(RESET)"

prod-update: build-prod ## Update production deployment
	@echo "$(BLUE)🔄 Updating production deployment...$(RESET)"
	export VERSION=$(VERSION) && \
	docker-compose -f docker-compose.prod.yml up -d --force-recreate
	@echo "$(GREEN)✅ Production update completed$(RESET)"

prod-stop: ## Stop production environment
	@echo "$(BLUE)🛑 Stopping production environment...$(RESET)"
	docker-compose -f docker-compose.prod.yml down
	@echo "$(GREEN)✅ Production environment stopped$(RESET)"

# ===================================================================
# Testing Commands
# ===================================================================
test: build ## Run test suite
	@echo "$(BLUE)🧪 Running test suite...$(RESET)"
	docker run --rm -it \
		--env-file .env \
		-v $(PWD)/test-results:/app/test-results \
		$(IMAGE_NAME):latest test
	@echo "$(GREEN)✅ Tests completed$(RESET)"

test-comprehensive: build ## Run comprehensive tests
	@echo "$(BLUE)🔬 Running comprehensive test suite...$(RESET)"
	docker run --rm -it \
		--env-file .env \
		-v $(PWD)/cache:/app/cache \
		-v $(PWD)/logs:/app/logs \
		$(IMAGE_NAME):latest --batch-analyze "INSIDE" "Celeste" --batch-type comprehensive
	@echo "$(GREEN)✅ Comprehensive tests completed$(RESET)"

# ===================================================================
# Management Commands
# ===================================================================
logs: ## Show container logs
	@echo "$(BLUE)📜 Showing container logs...$(RESET)"
	docker-compose logs -f autogen-dekudeals

logs-prod: ## Show production logs
	@echo "$(BLUE)📜 Showing production logs...$(RESET)"
	docker-compose -f docker-compose.prod.yml logs -f autogen-dekudeals

status: ## Show container status
	@echo "$(BLUE)📊 Container Status:$(RESET)"
	docker-compose ps

status-prod: ## Show production status
	@echo "$(BLUE)📊 Production Status:$(RESET)"
	docker-compose -f docker-compose.prod.yml ps

shell: ## Access container shell
	@echo "$(BLUE)🐚 Accessing container shell...$(RESET)"
	docker-compose exec autogen-dekudeals /bin/bash

shell-prod: ## Access production container shell
	@echo "$(BLUE)🐚 Accessing production container shell...$(RESET)"
	docker-compose -f docker-compose.prod.yml exec autogen-dekudeals /bin/bash

health: ## Check container health
	@echo "$(BLUE)❤️  Checking container health...$(RESET)"
	docker run --rm \
		--env-file .env \
		$(IMAGE_NAME):latest health

# ===================================================================
# Cleanup Commands
# ===================================================================
stop: ## Stop development environment
	@echo "$(BLUE)🛑 Stopping development environment...$(RESET)"
	docker-compose down
	@echo "$(GREEN)✅ Development environment stopped$(RESET)"

clean: stop ## Clean up containers and images
	@echo "$(BLUE)🧹 Cleaning up...$(RESET)"
	docker-compose down -v --remove-orphans
	docker image prune -f
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

clean-all: ## Clean everything (containers, images, volumes)
	@echo "$(RED)⚠️  This will remove ALL Docker containers, images, and volumes$(RESET)"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		echo "$(BLUE)🧹 Cleaning everything...$(RESET)"; \
		docker-compose down -v --remove-orphans; \
		docker-compose -f docker-compose.prod.yml down -v --remove-orphans; \
		docker system prune -af --volumes; \
		echo "$(GREEN)✅ Complete cleanup finished$(RESET)"; \
	else \
		echo "$(YELLOW)❌ Cleanup cancelled$(RESET)"; \
	fi

# ===================================================================
# CI/CD Pipeline Commands
# ===================================================================
ci-build: ## Run local CI/CD build pipeline
	@echo "$(BLUE)🔨 Running Local CI/CD Build Pipeline...$(RESET)"
	./scripts/local-build.sh $(VERSION)

ci-deploy: ## Run local CI/CD deployment
	@echo "$(BLUE)🚀 Running Local CI/CD Deployment...$(RESET)"
	./scripts/local-deploy.sh

ci-deploy-mode: ## Deploy with specific mode (usage: make ci-deploy-mode MODE=demo)
	@echo "$(BLUE)🎯 Deploying with mode: $(MODE)$(RESET)"
	./scripts/local-deploy.sh -m $(MODE)

ci-quick: ## Quick analysis deployment (usage: make ci-quick GAME="Hollow Knight")
	@echo "$(BLUE)⚡ Quick analysis for: $(GAME)$(RESET)"
	./scripts/local-deploy.sh -m quick "$(GAME)"

ci-status: ## Show CI/CD deployment status
	@echo "$(BLUE)📊 CI/CD Deployment Status:$(RESET)"
	./scripts/local-deploy.sh status

ci-test: ## Test CI/CD deployment
	@echo "$(BLUE)🧪 Testing CI/CD Deployment...$(RESET)"
	./scripts/local-deploy.sh test

ci-cleanup: ## Cleanup CI/CD containers
	@echo "$(BLUE)🧹 Cleaning up CI/CD containers...$(RESET)"
	./scripts/local-deploy.sh cleanup

ci-full: ci-build ci-deploy ## Full CI/CD pipeline (build + deploy)

# ===================================================================
# Utility Commands
# ===================================================================
info: ## Show system information
	@echo "$(BLUE)📋 System Information:$(RESET)"
	@echo "Docker Version: $$(docker --version)"
	@echo "Docker Compose Version: $$(docker compose version)"
	@echo "Image: $(IMAGE_NAME):$(VERSION)"
	@echo "Build Date: $(BUILD_DATE)"
	@echo "VCS Ref: $(VCS_REF)"
	@echo ""
	@echo "$(BLUE)📊 Images:$(RESET)"
	@docker images | grep $(IMAGE_NAME) || echo "No images found"
	@echo ""
	@echo "$(BLUE)📦 Containers:$(RESET)"
	@docker ps -a | grep $(IMAGE_NAME) || echo "No containers found"

version: ## Show version information
	@echo "$(BLUE)AutoGen DekuDeals v$(VERSION)$(RESET)"
	@echo "Build: $(BUILD_DATE)"
	@echo "Commit: $(VCS_REF)"

# Enhanced Makefile for AutoGen DekuDeals System
# ==================================================

.PHONY: help install install-dev clean test test-unit test-integration test-performance test-coverage test-all run demo docker-build docker-run docker-dev format lint setup check pytest-install

# Default target
help:
	@echo "🎮 AutoGen DekuDeals - Available Commands"
	@echo "========================================"
	@echo ""
	@echo "📦 Installation:"
	@echo "  install          Install production dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo "  pytest-install   Install pytest and testing dependencies"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-performance Run performance tests only"
	@echo "  test-edge        Run edge case tests only"
	@echo "  test-coverage    Run tests with coverage report"
	@echo "  test-fast        Run fast tests (no online/slow tests)"
	@echo "  test-all         Run comprehensive test suite"
	@echo ""
	@echo "🚀 Running:"
	@echo "  run              Start the enhanced CLI"
	@echo "  demo             Run system demonstration"
	@echo "  interactive      Start interactive mode"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  docker-build     Build production Docker image"
	@echo "  docker-run       Run production container"
	@echo "  docker-dev       Run development container"
	@echo ""
	@echo "🔧 Development:"
	@echo "  format           Format code with black"
	@echo "  lint             Run linting checks"
	@echo "  clean            Clean cache and temp files"
	@echo "  setup            Complete development setup"
	@echo "  check            Run all checks (format, lint, test)"

# ===============================
# Installation Commands
# ===============================

install:
	@echo "📦 Installing production dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "📦 Installing development dependencies..."
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

pytest-install:
	@echo "🧪 Installing pytest and testing dependencies..."
	pip install pytest==8.3.4 pytest-asyncio==0.24.0 pytest-mock==3.14.0 pytest-cov==6.0.0 pytest-xdist==3.6.0
	@echo "✅ Pytest installation completed!"

# ===============================
# Testing Commands
# ===============================

test: pytest-install
	@echo "🧪 Running all tests..."
	pytest tests/ -v --tb=short

test-unit: pytest-install
	@echo "🔬 Running unit tests..."
	pytest tests/ -v -m "unit" --tb=short

test-integration: pytest-install
	@echo "🔗 Running integration tests..."
	pytest tests/ -v -m "integration" --tb=short

test-performance: pytest-install
	@echo "⚡ Running performance tests..."
	pytest tests/ -v -m "performance" --tb=short

test-edge: pytest-install
	@echo "🚧 Running edge case tests..."
	pytest tests/ -v -m "edge_case" --tb=short

test-coverage: pytest-install
	@echo "📊 Running tests with coverage..."
	pytest tests/ --cov=. --cov-report=html --cov-report=term-missing --cov-report=xml -v

test-fast: pytest-install
	@echo "🏃 Running fast tests (offline only)..."
	pytest tests/ -v -m "not slow and not online" --tb=short

test-all: pytest-install
	@echo "🎯 Running comprehensive test suite..."
	pytest tests/ -v --tb=short --durations=10 --cov=. --cov-report=term-missing

test-parallel: pytest-install
	@echo "🚀 Running tests in parallel..."
	pytest tests/ -v -n auto --tb=short

test-markers: pytest-install
	@echo "🏷️  Available test markers:"
	pytest --markers

test-collect: pytest-install
	@echo "📋 Collecting tests..."
	pytest tests/ --collect-only

# ===============================
# Specific Test Categories
# ===============================

test-core: pytest-install
	@echo "🧪 Testing core functionality..."
	pytest tests/test_core_functionality.py -v --tb=short

test-perf: pytest-install
	@echo "⚡ Testing performance..."
	pytest tests/test_performance.py -v --tb=short

test-int: pytest-install
	@echo "🔗 Testing integration..."
	pytest tests/test_integration.py -v --tb=short

test-edge-cases: pytest-install
	@echo "🚧 Testing edge cases..."
	pytest tests/test_edge_cases.py -v --tb=short

test-utils: pytest-install
	@echo "🛠️ Testing utilities..."
	pytest tests/test_utils.py -v --tb=short

# ===============================
# Running Commands
# ===============================

run:
	@echo "🚀 Starting Enhanced CLI..."
	python enhanced_cli.py --interactive

demo:
	@echo "🎬 Running system demonstration..."
	python simple_demo.py

interactive:
	@echo "🎮 Starting interactive mode..."
	python enhanced_cli.py --interactive

# ===============================
# Legacy Testing (for compatibility)
# ===============================

test-old:
	@echo "🔄 Running legacy tests..."
	python examples/quick_system_test.py

test-comprehensive:
	@echo "📋 Running comprehensive validation..."
	python examples/comprehensive_system_test.py

# ===============================
# Docker Commands
# ===============================

docker-build:
	@echo "🐳 Building Docker image..."
	docker build -t autogen-dekudeals .

docker-run:
	@echo "🚀 Running Docker container..."
	docker run -it --rm autogen-dekudeals

docker-dev:
	@echo "🔧 Running development Docker..."
	docker-compose up --build

# ===============================
# Development Commands
# ===============================

format:
	@echo "🎨 Formatting code with black..."
	black . --line-length 88 --target-version py312

lint:
	@echo "🔍 Running linting checks..."
	@echo "Note: Install flake8 or similar for full linting"
	python -m py_compile enhanced_cli.py
	python -m py_compile agent_tools.py
	python -m py_compile autogen_agents.py

clean:
	@echo "🧹 Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete 2>/dev/null || true
	@echo "✅ Cleanup completed!"

setup: install-dev pytest-install
	@echo "🔧 Setting up development environment..."
	@echo "✅ Development environment ready!"
	@echo ""
	@echo "🎯 Quick Start:"
	@echo "  make test-fast    # Run quick tests"
	@echo "  make run          # Start the application"
	@echo "  make test-all     # Full test suite"

check: format lint test-fast
	@echo "✅ All checks completed!"

# ===============================
# Debug Commands
# ===============================

debug-env:
	@echo "🔍 Environment debugging..."
	@echo "Python version:"
	python --version
	@echo ""
	@echo "Pip packages:"
	pip list | grep -E "(pytest|autogen|openai)"
	@echo ""
	@echo "Current directory:"
	pwd
	@echo ""
	@echo "Available test files:"
	ls -la tests/ 2>/dev/null || echo "No tests directory found"

debug-pytest:
	@echo "🧪 Pytest debugging..."
	pytest --version
	pytest tests/ --collect-only --quiet 2>/dev/null || echo "Cannot collect tests"

# ===============================
# Performance Monitoring
# ===============================

benchmark:
	@echo "📊 Running performance benchmarks..."
	pytest tests/test_performance.py -v --durations=0 -m "performance"

profile:
	@echo "📈 Profiling system performance..."
	python -m cProfile -o profile.stats enhanced_cli.py --help
	@echo "Profile saved to profile.stats"

# ===============================
# Continuous Integration
# ===============================

ci-test: pytest-install
	@echo "🤖 Running CI test suite..."
	pytest tests/ -v --tb=short --junitxml=test-results.xml --cov=. --cov-report=xml

ci-fast: pytest-install
	@echo "🏃 Running fast CI tests..."
	pytest tests/ -v -m "not slow and not online" --tb=short --junitxml=test-results.xml

# ===============================
# Help Commands
# ===============================

test-help:
	@echo "🧪 Testing Help"
	@echo "==============="
	@echo ""
	@echo "Test Markers:"
	@echo "  unit         - Unit tests (fast, no external dependencies)"
	@echo "  integration  - Integration tests (component interactions)"
	@echo "  performance  - Performance and benchmark tests"
	@echo "  edge_case    - Edge cases and error handling"
	@echo "  online       - Tests requiring internet connection"
	@echo "  slow         - Slow tests (may take >10 seconds)"
	@echo "  autogen      - AutoGen agent tests"
	@echo "  ml           - Machine learning component tests"
	@echo "  batch        - Batch processing tests"
	@echo ""
	@echo "Example Usage:"
	@echo "  make test-unit                    # Run only unit tests"
	@echo "  make test ARGS='-k test_search'   # Run tests matching pattern"
	@echo "  make test ARGS='-x'               # Stop on first failure"
	@echo "  make test ARGS='--lf'             # Run last failed tests"

# Allow passing additional arguments to pytest
ifdef ARGS
    PYTEST_ARGS = $(ARGS)
else
    PYTEST_ARGS = 
endif

# Enhanced test command with arguments
test-with-args: pytest-install
	pytest tests/ -v $(PYTEST_ARGS) 