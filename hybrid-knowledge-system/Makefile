.PHONY: install install-dev setup docker-up docker-down test demo init-system load-sample-data clean format lint help

# Python and environment setup
PYTHON := .venv/bin/python
UV := uv

help:
	@echo "🧠 Hybrid Knowledge System - Neo4j + Weaviate"
	@echo "=============================================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup           Complete setup (dependencies + docker + init)"  
	@echo "  install         Install dependencies with uv"
	@echo "  install-dev     Install with dev dependencies"
	@echo ""
	@echo "Docker Commands:"
	@echo "  docker-up       Start Neo4j, Weaviate, Redis containers"
	@echo "  docker-down     Stop all containers"
	@echo "  docker-clean    Stop containers and remove volumes"
	@echo ""
	@echo "System Commands:"
	@echo "  init-system     Initialize Neo4j indexes and Weaviate schema"
	@echo "  load-sample     Load sample business data"
	@echo "  test-system     Run system functionality tests"
	@echo ""
	@echo "Demo Commands:"
	@echo "  demo            Full demo setup and test"
	@echo "  quick-demo      Demo without Docker restart"
	@echo ""
	@echo "Development:"
	@echo "  test            Run all tests"
	@echo "  format          Format code with black and isort"
	@echo "  lint            Run linters"
	@echo "  clean           Clean up caches and temp files"

# Complete setup
setup: install docker-up init-system load-sample-data
	@echo "✅ Hybrid Knowledge System ready!"
	@echo "   Run 'make demo' to test the system"

# Dependencies
install:
	@echo "📦 Installing dependencies with uv..."
	test -d .venv || $(UV) venv
	$(UV) pip install --python .venv/bin/python -e .

install-dev:
	@echo "📦 Installing dev dependencies with uv..."
	test -d .venv || $(UV) venv
	$(UV) pip install --python .venv/bin/python -e .[dev]

# Docker services
docker-up:
	@echo "🐳 Starting Docker services..."
	cp .env.example .env 2>/dev/null || true
	docker-compose up -d
	@echo "⏳ Waiting for services to be ready..."
	sleep 10

docker-down:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

docker-clean:
	@echo "🧹 Cleaning Docker services and volumes..."
	docker-compose down --volumes --remove-orphans
	docker system prune -f

# System initialization
init-system:
	@echo "🔧 Initializing Neo4j indexes and Weaviate schema..."
	$(PYTHON) scripts/init_system.py

load-sample-data:
	@echo "📊 Loading sample business data..."
	$(PYTHON) scripts/load_sample_data.py

test-system:
	@echo "🧪 Testing system functionality..."
	$(PYTHON) scripts/test_system.py

# Demo commands
demo: docker-down docker-up init-system load-sample-data test-system
	@echo "🎯 Demo complete! System is ready for hackathon."

quick-demo: test-system
	@echo "⚡ Quick demo complete!"

# Development
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v

format:
	@echo "🎨 Formatting code..."
	black src/ scripts/ tests/
	isort src/ scripts/ tests/

lint:
	@echo "🔍 Running linters..."
	black --check src/ scripts/ tests/
	isort --check-only src/ scripts/ tests/
	mypy src/

clean:
	@echo "🧹 Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true

# Status and info
status:
	@echo "🔍 Docker services status:"
	docker-compose ps
	@echo ""
	@echo "🔗 Service URLs:"
	@echo "  Neo4j Browser: http://localhost:7474"
	@echo "  Weaviate:      http://localhost:8080"
	@echo "  Redis:         localhost:6379"

logs:
	@echo "📋 Service logs:"
	docker-compose logs --tail=50