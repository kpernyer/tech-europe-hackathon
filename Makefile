# Tech Europe Hackathon - Root Makefile
# Orchestrates all project builds and demos

.PHONY: all help clean dev stop install status check-deps \
	openai-voice weaviate-recall hybrid-knowledge living-twin local-model \
	demo-all build-all test-all setup-env quick-start logs

# Default target
all: check-deps install build-all demo-all

help: ## Show this help message
	@echo "Tech Europe Hackathon - AI Research Projects"
	@echo "=============================================="
	@echo ""
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'
	@echo ""
	@echo "Project-specific targets:"
	@echo "  openai-voice        Build and run OpenAI Voice project"
	@echo "  weaviate-recall     Build and run Weaviate Recall project"  
	@echo "  hybrid-knowledge    Build and run Hybrid Knowledge project"
	@echo "  living-twin         Build and run Living Twin project"
	@echo "  local-model         Build and run Local Model project"

check-deps: ## Check system dependencies
	@echo "🔍 Checking system dependencies..."
	@which docker >/dev/null || (echo "❌ Docker not found. Please install Docker." && exit 1)
	@which docker-compose >/dev/null || which docker compose >/dev/null || (echo "❌ Docker Compose not found. Please install Docker Compose." && exit 1)
	@which make >/dev/null || (echo "❌ Make not found. Please install make." && exit 1)
	@echo "✅ All system dependencies found"

install: ## Install dependencies for all projects
	@echo "📦 Installing dependencies for all projects..."
	@$(MAKE) -C openai-voice install
	@$(MAKE) -C weaviate-recall-knowledge install  
	@$(MAKE) -C hybrid-knowledge-system install
	@$(MAKE) -C living-twin-synthetic-data install
	@$(MAKE) -C local-model-fine-tuning install
	@echo "✅ All dependencies installed"

build-all: ## Build all projects
	@echo "🏗️ Building all projects..."
	@$(MAKE) -C openai-voice build
	@$(MAKE) -C weaviate-recall-knowledge build
	@$(MAKE) -C hybrid-knowledge-system build
	@$(MAKE) -C living-twin-synthetic-data build
	@$(MAKE) -C local-model-fine-tuning build
	@echo "✅ All projects built"

demo-all: ## Start demo servers for all projects (different ports)
	@echo "🎭 Starting all demo servers..."
	@echo "📍 Demo URLs will be:"
	@echo "   • OpenAI Voice:        http://localhost:8001"
	@echo "   • Weaviate Recall:     http://localhost:8002"
	@echo "   • Hybrid Knowledge:    http://localhost:8003"
	@echo "   • Living Twin:         http://localhost:8004"  
	@echo "   • Local Model:         http://localhost:8005"
	@echo ""
	@$(MAKE) -C openai-voice demo &
	@$(MAKE) -C weaviate-recall-knowledge demo &
	@$(MAKE) -C hybrid-knowledge-system demo &
	@$(MAKE) -C living-twin-synthetic-data demo &
	@$(MAKE) -C local-model-fine-tuning demo &
	@echo "✅ All demos started in background"
	@echo "💡 Use 'make stop' to stop all services"

dev: demo-all ## Alias for demo-all (development mode)

test-all: ## Run tests for all projects
	@echo "🧪 Running tests for all projects..."
	@$(MAKE) -C openai-voice test || true
	@$(MAKE) -C weaviate-recall-knowledge test || true
	@$(MAKE) -C hybrid-knowledge-system test || true
	@$(MAKE) -C living-twin-synthetic-data test || true
	@$(MAKE) -C local-model-fine-tuning test || true

stop: ## Stop all running services
	@echo "🛑 Stopping all services..."
	@$(MAKE) -C openai-voice stop || true
	@$(MAKE) -C weaviate-recall-knowledge stop || true
	@$(MAKE) -C hybrid-knowledge-system stop || true
	@$(MAKE) -C living-twin-synthetic-data stop || true
	@$(MAKE) -C local-model-fine-tuning stop || true
	@echo "✅ All services stopped"

clean: ## Clean all build artifacts
	@echo "🧹 Cleaning all projects..."
	@$(MAKE) -C openai-voice clean || true
	@$(MAKE) -C weaviate-recall-knowledge clean || true
	@$(MAKE) -C hybrid-knowledge-system clean || true
	@$(MAKE) -C living-twin-synthetic-data clean || true
	@$(MAKE) -C local-model-fine-tuning clean || true
	@echo "✅ All projects cleaned"

status: ## Show status of all services
	@echo "📊 Service Status:"
	@echo "=================="
	@echo ""
	@echo "🎤 OpenAI Voice (port 8001):"
	@curl -s http://localhost:8001/health 2>/dev/null && echo "  ✅ Running" || echo "  ❌ Not running"
	@echo ""
	@echo "🧠 Weaviate Recall (port 8002):"
	@curl -s http://localhost:8002/health 2>/dev/null && echo "  ✅ Running" || echo "  ❌ Not running"
	@echo ""
	@echo "🔗 Hybrid Knowledge (port 8003):"
	@curl -s http://localhost:8003/health 2>/dev/null && echo "  ✅ Running" || echo "  ❌ Not running"
	@echo ""
	@echo "🧬 Living Twin (port 8004):"
	@curl -s http://localhost:8004/health 2>/dev/null && echo "  ✅ Running" || echo "  ❌ Not running"
	@echo ""
	@echo "🤖 Local Model (port 8005):"
	@curl -s http://localhost:8005/health 2>/dev/null && echo "  ✅ Running" || echo "  ❌ Not running"

# Individual project targets
openai-voice: ## Build and run OpenAI Voice project
	@$(MAKE) -C openai-voice all

weaviate-recall: ## Build and run Weaviate Recall project  
	@$(MAKE) -C weaviate-recall-knowledge all

hybrid-knowledge: ## Build and run Hybrid Knowledge project
	@$(MAKE) -C hybrid-knowledge-system all

living-twin: ## Build and run Living Twin project
	@$(MAKE) -C living-twin-synthetic-data all

local-model: ## Build and run Local Model project
	@$(MAKE) -C local-model-fine-tuning all

# Environment setup
setup-env: ## Copy environment templates
	@echo "🔧 Setting up environment files..."
	@for dir in openai-voice weaviate-recall-knowledge hybrid-knowledge-system living-twin-synthetic-data local-model-fine-tuning; do \
		if [ -f "$$dir/.env.example" ]; then \
			cp "$$dir/.env.example" "$$dir/.env" 2>/dev/null || true; \
			echo "  ✅ Created $$dir/.env from template"; \
		fi; \
	done
	@echo "⚠️  Remember to update API keys in .env files!"

# Quick development shortcuts
quick-start: check-deps setup-env install demo-all ## Complete setup and start all demos

logs: ## Show logs from all services
	@echo "📋 Showing logs from all services..."
	@docker-compose -f openai-voice/docker-compose.yml logs --tail=10 || true
	@docker-compose -f weaviate-recall-knowledge/docker-compose.yml logs --tail=10 || true  
	@docker-compose -f hybrid-knowledge-system/docker-compose.yml logs --tail=10 || true
	@docker-compose -f living-twin-synthetic-data/docker-compose.yml logs --tail=10 || true
	@docker-compose -f local-model-fine-tuning/docker-compose.yml logs --tail=10 || true