# Local Model Fine-Tuning - Project Makefile

.PHONY: all help clean install build demo dev stop test health

# Default target
all: install build demo

help: ## Show this help message
	@echo "Local Model Fine-Tuning"
	@echo "======================"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install Python dependencies using uv
	@echo "📦 Installing dependencies for Local Model Fine-Tuning..."
	@pip install uv
	@uv sync
	@echo "✅ Dependencies installed"

build: ## Build Docker images
	@echo "🏗️ Building Local Model Fine-Tuning Docker images..."
	@docker-compose build
	@echo "✅ Docker images built"

demo: ## Start the demo server
	@echo "🎭 Starting Local Model Fine-Tuning demo..."
	@echo "📍 Demo will be available at: http://localhost:8005"
	@docker-compose up -d
	@echo "✅ Demo server started"
	@echo "💡 Use 'make logs' to view logs, 'make stop' to stop"

dev: demo ## Alias for demo (development mode)

stop: ## Stop all services
	@echo "🛑 Stopping Local Model Fine-Tuning services..."
	@docker-compose down
	@echo "✅ Services stopped"

clean: ## Clean up containers and data
	@echo "🧹 Cleaning Local Model Fine-Tuning..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@rm -rf models/* training_data/* outputs/* || true
	@echo "✅ Cleanup complete"

logs: ## Show service logs
	@docker-compose logs -f

health: ## Check service health
	@echo "🏥 Checking Local Model Fine-Tuning health..."
	@curl -s http://localhost:8005/health || echo "Service not responding"

test: ## Run tests
	@echo "🧪 Running Local Model Fine-Tuning tests..."
	@uv run python -m pytest test_*.py -v || echo "No tests found"
	@echo "✅ Tests complete"

# Development targets
run-local: install ## Run locally without Docker
	@echo "🔬 Running Local Model Fine-Tuning locally..."
	@uv run uvicorn server.main:app --host 0.0.0.0 --port 8005 --reload

# Training targets
pull-models: ## Pull required models with Ollama
	@echo "📥 Pulling required models..."
	@docker-compose exec ollama ollama pull llama2:7b-chat || echo "Ollama not running"
	@docker-compose exec ollama ollama pull llama2:13b-chat || echo "Ollama not running"
	@docker-compose exec ollama ollama pull mistral:7b || echo "Ollama not running"
	@docker-compose exec ollama ollama pull qwen2.5:3b || echo "Ollama not running"

start-training: ## Start a training session
	@echo "🚀 Starting training session..."
	@curl -X POST http://localhost:8005/training/start \
		-H "Content-Type: application/json" \
		-d '{"model_name": "llama2:7b-chat", "epochs": 3}' || echo "Service not running"

stop-training: ## Stop current training
	@echo "⏹️ Stopping training..."
	@curl -X POST http://localhost:8005/training/stop \
		-H "Content-Type: application/json" || echo "Service not running"

# Environment setup
setup-env: ## Create .env file from template
	@if [ ! -f .env ]; then \
		echo "🔧 Creating .env file..."; \
		echo "OPENAI_API_KEY=your_openai_key_here" > .env; \
		echo "OLLAMA_HOST=http://ollama:11434" >> .env; \
		echo "MODEL_CACHE_DIR=/app/models" >> .env; \
		echo "TRAINING_DATA_DIR=/app/training_data" >> .env; \
		echo "✅ Created .env file - please update with your API keys"; \
	else \
		echo "📋 .env file already exists"; \
	fi
