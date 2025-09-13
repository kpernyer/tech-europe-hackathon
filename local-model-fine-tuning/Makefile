.PHONY: demo start-backend start-frontend stop install

demo:
	@echo "🚀 Starting Organizational AI Fine-Tuning Demo..."
	docker-compose up --build

start-backend:
	@echo "🐍 Starting backend..."
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

start-frontend:
	@echo "⚛️  Starting frontend..."
	cd frontend && npm run dev

stop:
	@echo "🛑 Stopping demo..."
	docker-compose down

install:
	@echo "📦 Installing dependencies..."
	cd backend && pip install -e .
	cd frontend && npm install

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down --volumes
	docker system prune -f
