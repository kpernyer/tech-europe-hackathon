# OpenAI Voice - Project Makefile

.PHONY: all help clean install build demo dev stop test health

# Default target
all: install build demo

help: ## Show this help message
	@echo "OpenAI Voice"
	@echo "============"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install Node.js dependencies
	@echo "📦 Installing dependencies for OpenAI Voice..."
	@npm install
	@echo "✅ Dependencies installed"

build: ## Build Docker images
	@echo "🏗️ Building OpenAI Voice Docker images..."
	@docker-compose build
	@echo "✅ Docker images built"

demo: ## Start the demo server
	@echo "🏥 Starting Organizational Twin CEO Assistant demo..."
	@echo "📍 Web interface: http://localhost:5173"
	@echo "📍 API server: http://localhost:8787"
	@docker-compose up -d
	@echo "✅ Demo server started"
	@echo "💡 Use 'make logs' to view logs, 'make stop' to stop"

dev: demo ## Alias for demo (development mode)

stop: ## Stop all services
	@echo "🛑 Stopping OpenAI Voice services..."
	@docker-compose down
	@echo "✅ Services stopped"

clean: ## Clean up containers and data
	@echo "🧹 Cleaning OpenAI Voice..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@rm -rf node_modules/.cache || true
	@echo "✅ Cleanup complete"

logs: ## Show service logs
	@docker-compose logs -f

health: ## Check service health
	@echo "🏥 Checking Organizational Twin health..."
	@curl -s http://localhost:8787/healthz || echo "API server not responding"
	@echo ""
	@curl -s http://localhost:5173 > /dev/null && echo "✅ Web interface responding" || echo "❌ Web interface not responding"

test: ## Run tests
	@echo "🧪 Running Organizational Twin tests..."
	@npm run demo-test
	@echo "✅ Tests complete"

demo-conversation: ## Run conversation interpretation demo
	@echo "🗣️ Running conversation interpretation demo..."
	@npm run demo-conversation

# Development targets
run-local: install ## Run locally without Docker
	@echo "🔬 Running OpenAI Voice locally..."
	@npm run dev

# Environment setup
setup-env: ## Create .env file from template
	@if [ ! -f .env ]; then \
		echo "🔧 Creating .env file..."; \
		echo "OPENAI_API_KEY=your_openai_key_here" > .env; \
		echo "PORT=8001" >> .env; \
		echo "✅ Created .env file - please update with your API keys"; \
	else \
		echo "📋 .env file already exists"; \
	fi