.PHONY: help install start dev stop clean backend frontend

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "🌴 OpenPoke - Available Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
	@echo ""

install: ## Install all dependencies (backend + frontend)
	@echo "📦 Installing backend dependencies..."
	@python3 -m venv .venv
	@. .venv/bin/activate && pip install -r server/requirements.txt
	@echo "📦 Installing frontend dependencies..."
	@npm install --prefix web
	@echo "✅ All dependencies installed!"

start: ## Start both backend and frontend servers
	@chmod +x start.sh
	@./start.sh

dev: start ## Alias for 'start' command

backend: ## Start only the backend server
	@echo "🚀 Starting FastAPI backend..."
	@. .venv/bin/activate && python -m server.server --reload

frontend: ## Start only the frontend server
	@echo "🚀 Starting Next.js frontend..."
	@npm run dev --prefix web

stop: ## Stop all running services
	@echo "⏹️  Stopping services..."
	@pkill -f "python -m server.server" || true
	@pkill -f "next dev" || true
	@echo "✅ All services stopped"

clean: ## Remove all generated files and dependencies
	@echo "🧹 Cleaning up..."
	@rm -rf .venv
	@rm -rf web/node_modules
	@rm -rf web/.next
	@rm -rf server/__pycache__
	@rm -rf server/**/__pycache__
	@rm -rf server/data
	@echo "✅ Cleanup complete"

check: ## Check if .env file exists and dependencies are installed
	@if [ ! -f .env ]; then \
		echo "❌ .env file not found. Run: cp .env.example .env"; \
		exit 1; \
	fi
	@if [ ! -d .venv ]; then \
		echo "❌ Virtual environment not found. Run: make install"; \
		exit 1; \
	fi
	@if [ ! -d web/node_modules ]; then \
		echo "❌ Frontend dependencies not found. Run: make install"; \
		exit 1; \
	fi
	@echo "✅ All checks passed"

setup: ## Initial setup - copy .env.example and install dependencies
	@if [ ! -f .env ]; then \
		echo "📝 Creating .env file..."; \
		cp .env.example .env; \
		echo "⚠️  Please edit .env and add your API keys!"; \
	else \
		echo "✓ .env file already exists"; \
	fi
	@$(MAKE) install
