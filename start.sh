#!/bin/bash

# OpenPoke Startup Script
# Starts both backend and frontend services concurrently

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🌴 OpenPoke Startup Script${NC}"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and configure your API keys:${NC}"
    echo "  cp .env.example .env"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Check if backend dependencies are installed
if [ ! -f ".venv/bin/uvicorn" ] && [ ! -f ".venv/Scripts/uvicorn.exe" ]; then
    echo -e "${YELLOW}⚠️  Backend dependencies not installed. Installing...${NC}"
    source .venv/bin/activate 2>/dev/null || . .venv/Scripts/activate 2>/dev/null
    pip install -r server/requirements.txt
    echo -e "${GREEN}✓ Backend dependencies installed${NC}"
fi

# Check if frontend dependencies are installed
if [ ! -d "web/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not installed. Installing...${NC}"
    npm install --prefix web
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
fi

echo ""
echo -e "${GREEN}Starting services...${NC}"
echo ""

# Trap to kill all background processes on exit
trap 'kill $(jobs -p) 2>/dev/null' EXIT

# Start backend server
echo -e "${BLUE}🚀 Starting FastAPI backend on http://localhost:8001${NC}"
source .venv/bin/activate 2>/dev/null || . .venv/Scripts/activate 2>/dev/null
python -m server.server --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend server
echo -e "${BLUE}🚀 Starting Next.js frontend on http://localhost:3000${NC}"
npm run dev --prefix web &
FRONTEND_PID=$!

echo ""
echo -e "${GREEN}✓ Both services are starting...${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🌴 OpenPoke is running!${NC}"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}📱 Frontend:${NC} http://localhost:3000"
echo -e "${BLUE}🔧 Backend API:${NC} http://localhost:8001"
echo -e "${BLUE}📚 API Docs:${NC} http://localhost:8001/docs"
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo ""

# Wait for both processes
wait
