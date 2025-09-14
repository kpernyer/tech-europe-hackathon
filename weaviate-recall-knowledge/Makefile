# Weaviate Recall Knowledge - Project Makefile

.PHONY: all help clean install build demo dev stop test health

# Default target
all: install build demo

help: ## Show this help message
	@echo "Weaviate Recall Knowledge"
	@echo "========================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install Python dependencies using uv
	@echo "📦 Installing dependencies for Weaviate Recall Knowledge..."
	@pip install uv
	@uv venv --python 3.11 || true
	@uv pip install -r requirements.txt
	@echo "✅ Dependencies installed"

build: ## Build Docker images
	@echo "🏗️ Building Weaviate Recall Knowledge Docker images..."
	@docker-compose build
	@echo "✅ Docker images built"

demo: ## Start the demo server
	@echo "🎭 Starting Weaviate Recall Knowledge demo..."
	@echo "📍 Demo will be available at: http://localhost:$(WEAVIATE_RECALL_WEB_PORT)"
	@docker-compose up -d
	@echo "✅ Demo server started"
	@echo "💡 Use 'make logs' to view logs, 'make stop' to stop"

dev: demo ## Alias for demo (development mode)

stop: ## Stop all services
	@echo "🛑 Stopping Weaviate Recall Knowledge services..."
	@docker-compose down
	@echo "✅ Services stopped"

clean: ## Clean up containers and data
	@echo "🧹 Cleaning Weaviate Recall Knowledge..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@rm -rf __pycache__ .pytest_cache || true
	@echo "✅ Cleanup complete"

logs: ## Show service logs
	@docker-compose logs -f

health: ## Check service health
	@echo "🏥 Checking Weaviate Recall Knowledge health..."
	@curl -s http://localhost:$(WEAVIATE_RECALL_WEB_PORT)/health || echo "Service not responding"

test: ## Run tests
	@echo "🧪 Running Weaviate Recall Knowledge tests..."
	@uv run python -m pytest test_*.py -v || echo "No tests found"
	@echo "✅ Tests complete"

# Development targets
run-local: install ## Run locally without Docker
	@echo "🔬 Running Weaviate Recall Knowledge locally..."
	@uv run uvicorn server.main:app --host 0.0.0.0 --port $(WEAVIATE_RECALL_WEB_PORT) --reload

# Weaviate-specific targets
setup-schema: ## Setup Weaviate schema
	@echo "📋 Setting up Weaviate schema..."
	@uv run python step2_schema.py || echo "Schema setup failed"

add-documents: ## Add sample documents to Weaviate
	@echo "📚 Adding documents to Weaviate..."
	@uv run python step3_add_data.py || echo "Document upload failed"

search-test: ## Test search functionality
	@echo "🔍 Testing search functionality..."
	@uv run python step4_search.py || echo "Search test failed"

visualize: ## Visualize Weaviate data
	@echo "👁️ Visualizing Weaviate data..."
	@uv run python visualize.py || echo "Visualization failed"

# Environment setup
setup-env: ## Create .env file from template
	@if [ ! -f .env ]; then \
		echo "🔧 Creating .env file..."; \
		echo "OPENAI_API_KEY=your_openai_key_here" > .env; \
		echo "WEAVIATE_URL=http://localhost:8080" >> .env; \
		echo "WEAVIATE_API_KEY=" >> .env; \
		echo "✅ Created .env file - please update with your API keys"; \
	else \
		echo "📋 .env file already exists"; \
	fi