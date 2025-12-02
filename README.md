# OpenPoke 🌴

OpenPoke is a simplified, open-source take on [Interaction Company’s](https://interaction.co/about) [Poke](https://poke.com/) assistant—built to show how a multi-agent orchestration stack can feel genuinely useful. It keeps the handful of things Poke is great at (email triage, reminders, and persistent agents) while staying easy to spin up locally.

- Multi-agent FastAPI backend that mirrors Poke's interaction/execution split, powered by [Ananas AI](https://anannas.ai/).
- Gmail tooling via [Composio](https://composio.dev/) for drafting/replying/forwarding without leaving chat.
- Trigger scheduler and background watchers for reminders and "important email" alerts.
- Next.js web UI that proxies everything through the shared `.env`, so plugging in API keys is the only setup.

## Requirements
- Python 3.10+
- Node.js 18+
- npm 9+

## Quick Start 🚀

### One Command Start (Recommended)
The easiest way to get started:

```bash
# Clone and enter the repo
git clone https://github.com/shlokkhemani/OpenPoke
cd OpenPoke

# Copy and configure environment
cp .env.example .env
# Edit .env and add your API keys

# Start everything with one command
npm start
# or
make start
# or (Linux/Mac)
./start.sh
# or (Windows)
start.bat
```

The startup script will automatically:
- Create a virtual environment if needed
- Install backend and frontend dependencies
- Start both servers concurrently

### Manual Setup (Alternative)
If you prefer step-by-step setup:

1. **Clone and enter the repo:**
   ```bash
   git clone https://github.com/shlokkhemani/OpenPoke
   cd OpenPoke
   ```

2. **Create a shared env file:**
   ```bash
   cp .env.example .env
   ```

3. **Get your API keys and add them to `.env`:**
   
   **Ananas AI (Required)**
   - Create an account at [anannas.ai](https://anannas.ai/)
   - Generate an API key
   - Replace `your_anannas_api_key_here` with your actual key in `.env`
   - Configure which models to use for each task (see `.env` for options)
   
   **Composio (Required for Gmail)**
   - Sign in at [composio.dev](https://composio.dev/)
   - Create an API key
   - Set up Gmail integration and get your auth config ID
   - Replace `your_composio_api_key_here` and `your_gmail_auth_config_id_here` in `.env`

4. **Install dependencies:**
   ```bash
   make install
   # or
   npm run install:all
   ```

5. **Start both servers:**
   ```bash
   make start
   # or
   npm start
   ```

6. **Connect Gmail for email workflows:** With both services running, open [http://localhost:3000](http://localhost:3000), head to *Settings → Gmail*, and complete the Composio OAuth flow.

### Available Commands

**Using npm:**
```bash
npm start          # Start both backend and frontend
npm run backend    # Start only backend
npm run frontend   # Start only frontend
npm run install:all # Install all dependencies
npm run stop       # Stop all services
```

**Using Makefile:**
```bash
make start         # Start both backend and frontend
make backend       # Start only backend
make frontend      # Start only frontend
make install       # Install all dependencies
make stop          # Stop all services
make clean         # Remove all generated files
make setup         # Initial setup (copy .env and install deps)
make help          # Show all available commands
```

## Service URLs

When running:
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8001
- **API Docs:** http://localhost:8001/docs

The web app proxies API calls to the Python server using the values in `.env`.

## Project Layout
- `server/` – FastAPI application and agents
- `web/` – Next.js app
- `server/data/` – runtime data (ignored by git)

## License
MIT — see [LICENSE](LICENSE).
# openpoke
# openpoke
