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