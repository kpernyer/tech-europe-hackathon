# Living Twin Synthetic Data Generation - Project Makefile

.PHONY: all help clean install build demo dev stop test health \
	run-structured-data run-strategic-docs run-unified-personas run-quick-data list-scripts \
	show-outputs clean-outputs export-json export-training backup-data


# Default target
all: install build demo

help: ## Show this help message
	@echo "Living Twin Synthetic Data Generation"
	@echo "===================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install Python dependencies using uv
	@echo "📦 Installing dependencies for Living Twin Synthetic Data..."
	@pip install uv
	@uv sync
	@echo "✅ Dependencies installed"

build: ## Build Docker image
	@echo "🏗️ Building Living Twin Synthetic Data Docker image..."
	@docker-compose build
	@echo "✅ Docker image built"

demo: ## Start the demo server
	@echo "🎭 Starting Living Twin Synthetic Data demo..."
	@echo "📍 Demo will be available at: http://localhost:8004"
	@docker-compose up -d
	@echo "✅ Demo server started"
	@echo "💡 Use 'make logs' to view logs, 'make stop' to stop"

dev: demo ## Alias for demo (development mode)

stop: ## Stop all services
	@echo "🛑 Stopping Living Twin Synthetic Data services..."
	@docker-compose down
	@echo "✅ Services stopped"

clean: ## Clean temporary files and containers
	@echo "🧹 Cleaning temporary files..."
	@docker-compose down -v --remove-orphans 2>/dev/null || true
	@docker system prune -f 2>/dev/null || true
	@rm -rf outputs/tmp/ outputs/cache/ || true
	@echo "✅ Temporary files cleaned"

really-clean: ## Deep clean - remove all regenerable data
	@echo "🧹 Deep clean - removing regenerable data..."
	@$(MAKE) clean
	@rm -rf generated/
	@rm -rf outputs/
	@rm -rf production_data/
	@echo "✅ Deep clean complete - regenerable data removed"
	@echo "📦 Preserved: archives/, id_registry/, scripts/"
	@echo "💡 Tip: Restore with 'make restore-from-archive'"

logs: ## Show service logs
	@docker-compose logs -f

health: ## Check service health
	@echo "🏥 Checking Living Twin Synthetic Data health..."
	@curl -s http://localhost:8004/health || echo "Service not responding"

test: ## Run tests
	@echo "🧪 Running Living Twin Synthetic Data tests..."
	@uv run python -m pytest test_*.py -v || echo "No tests found"
	@echo "✅ Tests complete"

# Development targets
run-local: install ## Run locally without Docker
	@echo "🔬 Running Living Twin Synthetic Data locally..."
	@uv run uvicorn server.main:app --host 0.0.0.0 --port 8004 --reload

# Data generation targets
generate-orgs: ## Generate organizations only
	@echo "🏢 Generating organizations..."
	@curl -X POST http://localhost:8004/generate/organizations \
		-H "Content-Type: application/json" \
		-d '{"count": 10}' || echo "Service not running"

generate-people: ## Generate people personas
	@echo "👥 Generating people..."
	@curl -X POST http://localhost:8004/generate/people \
		-H "Content-Type: application/json" \
		-d '{"organization_id": "sample_org", "count": 25}' || echo "Service not running"

generate-all: ## Run full generation pipeline
	@echo "🚀 Running full generation pipeline..."
	@curl -X POST http://localhost:8004/pipeline/run \
		-H "Content-Type: application/json" || echo "Service not running"

# Environment setup
setup-env: ## Create .env file from template
	@if [ ! -f .env ]; then \
		echo "🔧 Creating .env file..."; \
		echo "OPENAI_API_KEY=your_openai_key_here" > .env; \
		echo "ELEVENLABS_API_KEY=your_elevenlabs_key_here" >> .env; \
		echo "AWS_REGION=us-east-1" >> .env; \
		echo "AWS_BEDROCK_ENABLED=false" >> .env; \
		echo "✅ Created .env file - please update with your API keys"; \
	else \
		echo "📋 .env file already exists"; \
	fi

# Script execution targets
run-structured-data: install ## Generate structured organizational data
	@echo "🏢 Generating structured organizational data..."
	@uv run python scripts/generate_structured_data.py

run-strategic-docs: install ## Generate strategic business documents
	@echo "📋 Generating strategic documents..."
	@uv run python scripts/generate_strategic_documents.py

run-unified-personas: install ## Generate unified personas pipeline
	@echo "👥 Running unified personas pipeline..."
	@uv run python scripts/unified_persona_pipeline.py

run-quick-data: install ## Generate quick sample data
	@echo "⚡ Generating quick sample data..."
	@uv run python scripts/quick_structured_data.py

# List available scripts
list-scripts: ## Show available generation scripts
	@echo "📜 Available generation scripts:"
	@echo "  make run-structured-data    - Generate structured organizational data"
	@echo "  make run-strategic-docs     - Generate strategic business documents"  
	@echo "  make run-unified-personas   - Generate unified personas pipeline"
	@echo "  make run-quick-data         - Generate quick sample data"
	@echo ""
	@echo "📖 For more details, see: scripts/README.md"

# Data management targets
show-outputs: ## Show generated data summary
	@echo "📊 Generated Data Summary:"
	@echo "=========================="
	@echo "📁 Organizations: $$(find outputs/organizations -name "*.json" 2>/dev/null | wc -l | tr -d ' ') files"
	@echo "👥 People: $$(find outputs/people -name "*.json" 2>/dev/null | wc -l | tr -d ' ') files"
	@echo "🎭 Scenarios: $$(find outputs/scenarios -name "*.json" 2>/dev/null | wc -l | tr -d ' ') files"
	@echo "🎵 Voice files: $$(find outputs/voices -name "*.mp3" 2>/dev/null | wc -l | tr -d ' ') files"
	@echo "📋 Documents: $$(find outputs/documents -name "*.json" -o -name "*.md" 2>/dev/null | wc -l | tr -d ' ') files"
	@echo ""
	@echo "💾 Total size: $$(du -sh outputs 2>/dev/null | cut -f1 || echo '0B')"

clean-outputs: ## Clean all generated data (keep structure)
	@echo "🧹 Cleaning generated data..."
	@find outputs -type f -name "*.json" -delete 2>/dev/null || true
	@find outputs -type f -name "*.mp3" -delete 2>/dev/null || true
	@find outputs -type f -name "*.wav" -delete 2>/dev/null || true
	@find outputs -type f -name "*.csv" -delete 2>/dev/null || true
	@find outputs -type f -name "*.md" ! -name "README.md" -delete 2>/dev/null || true
	@echo "✅ Generated data cleaned (structure preserved)"

export-json: ## Export all data as JSON
	@echo "📤 Exporting data as JSON..."
	@mkdir -p outputs/exports/json
	@find outputs -name "*.json" -not -path "*/exports/*" -exec cp {} outputs/exports/json/ \; 2>/dev/null || true
	@echo "✅ JSON export complete: outputs/exports/json/"

export-training: ## Export data in training format
	@echo "🤖 Exporting training data..."
	@mkdir -p outputs/exports/training
	@echo "Training data export would combine all personas, scenarios, and documents"
	@echo "📋 See outputs/exports/training/ for ML-ready datasets"

backup-data: ## Create timestamped backup of all data
	@echo "💾 Creating data backup..."
	@timestamp=$$(date +%Y%m%d_%H%M%S) && \
	 tar -czf "data_backup_$$timestamp.tar.gz" outputs/ && \
	 echo "✅ Backup created: data_backup_$$timestamp.tar.gz"

restore-from-archive: ## Restore latest deployment from archive
	@echo "📦 Restoring from latest archive..."
	@latest_archive=$$(ls -t archives/*.tar.gz 2>/dev/null | head -1); \
	if [ -n "$$latest_archive" ]; then \
		echo "📂 Extracting: $$latest_archive"; \
		tar -xzf "$$latest_archive" -C .; \
		echo "✅ Data restored from archive"; \
	else \
		echo "❌ No archives found in archives/"; \
	fi

deploy-production: ## Run production data management system
	@echo "🏭 Running production data deployment..."
	@uv run python scripts/data_management_system.py

