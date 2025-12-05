# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

OpenPoke is a multi-agent email and messaging assistant inspired by Interaction Company's Poke. It uses a FastAPI backend with two types of agents (interaction and execution) powered by Ananas AI, along with a Next.js frontend. The system handles email triage via Composio/Gmail integration, manages reminders through a trigger scheduler, monitors important emails via background watchers, and supports WhatsApp messaging via YCloud.

## Development Commands

### Starting the Application

```bash
# Start both backend and frontend (recommended)
npm start
# or
make start
# or
./start.sh  # Linux/Mac
# or
start.bat   # Windows

# Start only backend (runs on port 8001)
make backend
# or
npm run backend

# Start only frontend (runs on port 3000)
make frontend
# or
npm run frontend
```

### Installation and Setup

```bash
# Initial setup with .env creation
make setup

# Install all dependencies
make install
# or
npm run install:all

# Stop all services
make stop
# or
npm run stop

# Clean all generated files
make clean
```

### Backend Development

```bash
# Run backend with hot reload
python -m server.server --reload

# Backend runs on http://localhost:8001
# API docs at http://localhost:8001/docs
```

### Frontend Development

```bash
# Run frontend dev server
npm run dev --prefix web

# Frontend runs on http://localhost:3000
```

## Architecture

### Multi-Agent System

The application uses a two-agent orchestration pattern:

**Interaction Agent** (`server/agents/interaction_agent/`)
- Handles user conversations and interprets user intent
- Maintains conversation state and decides when to delegate tasks
- Routes to execution agents via `send_message_to_agent` tool
- Runtime in `runtime.py` manages LLM calls and tool execution loops (max 8 iterations)
- Tools defined in `tools.py` include conversation management and agent delegation

**Execution Agent** (`server/agents/execution_agent/`)
- Executes specific tasks using Gmail and trigger tools
- Each execution agent instance has a unique name (e.g., "draft reply to Keith")
- Maintains persistent history in `server/data/execution_agents/{agent_name}.txt`
- Runtime in `runtime.py` handles tool execution loops (max 8 iterations)
- Tools registry in `tools/registry.py` provides Gmail operations and trigger management

### Agent Communication Flow

1. User sends message → Interaction Agent processes it
2. Interaction Agent uses tools or delegates to Execution Agent via `send_message_to_agent`
3. Execution Agent runs in `batch_manager.py` → uses Gmail/trigger tools
4. Results flow back: Execution Agent → Batch Manager → Interaction Agent → User

### LLM Integration (Ananas AI)

All LLM calls go through `server/openrouter_client/client.py` which interfaces with Ananas AI:
- API base URL: `https://api.anannas.ai/v1`
- Supports tool calling (function calling) via OpenAI-compatible format
- Model selection per agent type via `.env` configuration:
  - `INTERACTION_AGENT_MODEL` - user conversation handling
  - `EXECUTION_AGENT_MODEL` - task execution
  - `EXECUTION_AGENT_SEARCH_MODEL` - email search operations
  - `SUMMARIZER_MODEL` - conversation summarization
  - `EMAIL_CLASSIFIER_MODEL` - important email detection

### Background Services

**Trigger Scheduler** (`server/services/trigger_scheduler.py`)
- Polls triggers from SQLite database (`server/data/triggers.db`) every 10 seconds
- Dispatches execution agents when triggers are due
- Handles one-time and recurring triggers with timezone support
- Manages trigger failures and rescheduling

**Important Email Watcher** (`server/services/gmail/watcher.py`)
- Polls Gmail for new messages every 60 seconds
- Uses LLM-based classification (`server/services/gmail/importance_classifier.py`)
- Creates execution agents for important emails to notify user
- Tracks seen messages in `server/data/gmail_seen.json` to prevent duplicates

**WhatsApp Integration** (`server/services/whatsapp/`)
- YCloud webhook handler for incoming WhatsApp messages
- `client.py` - sends text messages via YCloud API
- `signature.py` - HMAC-SHA256 signature verification for webhooks
- `context.py` - manages per-request WhatsApp context (user phone, message tracking)
- Messages processed asynchronously through the Interaction Agent

### Data Storage

All runtime data stored in `server/data/` (gitignored):
- `conversation/chat_log.txt` - main conversation transcript
- `conversation/working_memory.txt` - summarized conversation state
- `execution_agents/{agent_name}.txt` - per-agent execution history
- `triggers.db` - SQLite database for scheduled triggers
- `gmail_seen.json` - tracking processed emails
- `timezone.txt` - user timezone preference

### Conversation Summarization

Configured via `server/config.py`:
- `conversation_summary_threshold: 100` - messages before summarization triggers
- `conversation_summary_tail_size: 10` - recent messages kept outside summary
- Summarizer in `server/services/conversation/summarization/summarizer.py`
- Working memory maintained in `working_memory_log.py`

### Gmail Integration

Composio SDK used for Gmail operations (`server/agents/execution_agent/tools/gmail.py`):
- Draft creation, reply, forward, send
- Email search with custom implementation (`tasks/search_email/`)
- Authentication via Composio OAuth flow (configured in frontend settings)
- Entity ID format: `{composio_auth_config_id}_{user_email_address}`

Search email task uses specialized model and custom processing:
- `tool.py` - main search interface
- `gmail_internal.py` - Gmail API wrapper
- `email_cleaner.py` - HTML cleaning and text extraction
- Uses `EXECUTION_AGENT_SEARCH_MODEL` for better search result processing

### API Routes

Routes defined in `server/routes/`:
- `chat.py` - POST /api/chat/send, GET /api/chat/history, DELETE /api/chat/history
- `gmail.py` - GET /api/gmail/connected, GET /api/gmail/entity-id, POST /api/gmail/connect
- `meta.py` - GET /api/meta/timezone, POST /api/meta/timezone
- `whatsapp.py` - POST /api/whatsapp/webhook (YCloud webhook), GET /api/whatsapp/health

### Frontend Structure

Next.js app in `web/`:
- `app/page.tsx` - main chat interface
- `app/api/` - API proxy endpoints that add `.env` values to backend requests
- Uses Tailwind CSS for styling
- Proxies all API calls to backend at `http://localhost:8001`

## Configuration

Environment variables in `.env` (copy from `.env.example`):

**Required:**
- `ANANNAS_API_KEY` - Ananas AI API key
- `COMPOSIO_API_KEY` - Composio API key
- `COMPOSIO_GMAIL_AUTH_CONFIG_ID` - Gmail auth config from Composio
- `YCLOUD_API_KEY` - YCloud API key for WhatsApp
- `YCLOUD_PHONE_NUMBER` - WhatsApp Business phone number
- `YCLOUD_WEBHOOK_SECRET` - secret for webhook signature verification

**Optional:**
- `OPENPOKE_HOST` - server host (default: 0.0.0.0)
- `OPENPOKE_PORT` - server port (default: 8001)
- `OPENPOKE_CORS_ALLOW_ORIGINS` - CORS origins (default: *)
- `OPENPOKE_ENABLE_DOCS` - enable API docs (default: 1)
- Model selection variables (see LLM Integration section above)

## Common Development Patterns

### Adding a New Tool for Interaction Agent

1. Define tool schema in `server/agents/interaction_agent/tools.py` (`get_tool_schemas()`)
2. Implement handler in `handle_tool_call()` in same file
3. Return `ToolResult(success=True/False, payload={...}, user_message=optional_string)`

### Adding a New Tool for Execution Agent

1. Create tool function in `server/agents/execution_agent/tools/` (e.g., in `gmail.py`)
2. Register in `server/agents/execution_agent/tools/registry.py` (`get_tool_schemas()` and `get_tool_registry()`)
3. Tool functions receive kwargs matching schema parameters, return dict or raise exception

### Working with Agent History

Interaction agent uses conversation log (`server/services/conversation/conversation_log.py`):
- `record_user_message()` - log user input
- `record_reply()` - log assistant response
- `record_agent_message()` - log execution agent results

Execution agent maintains per-instance history:
- `agent.record_tool_execution(tool, args, result)` - log tool calls
- `agent.record_response(text)` - log final response
- History included in system prompt via `build_system_prompt_with_history()`

### Testing Agent Changes

No test suite currently in the repository. Manual testing workflow:
1. Start both servers with `npm start`
2. Connect Gmail via Settings → Gmail in frontend
3. Test conversation flows through chat interface at http://localhost:3000
4. Monitor backend logs for agent execution details
5. Check `server/data/` for persisted state

### Debugging

Logging configured in `server/logging_config.py`:
- Structured JSON logging with `extra` fields
- Agent-specific context (tool names, execution stages, errors)
- Reduced noise from uvicorn and watchfiles during development
- Key log points: tool execution start/done/error, LLM calls, trigger dispatches

### WhatsApp Message Flow

1. YCloud sends POST to `/api/whatsapp/webhook` when user messages the WhatsApp number
2. Signature verified using `YCLOUD_WEBHOOK_SECRET`
3. Message parsed and `WhatsAppContext` set for the request
4. `InteractionAgentRuntime` processes the message asynchronously
5. Response sent back via `WhatsAppClient.send_text_message()`
6. Context cleared after processing

Key files:
- `server/routes/whatsapp.py` - webhook endpoint
- `server/services/whatsapp/client.py` - YCloud API client
- `server/services/whatsapp/context.py` - per-request context management

## Important Notes

- Backend must be run as `python -m server.server` (not `python server/server.py`)
- Virtual environment expected at `.venv/` (created by install commands)
- Frontend proxies `.env` values to backend, so API keys only need to be in root `.env`
- Gmail entity ID format includes auth config ID + email address (underscore-separated)
- Tool iteration limits (8) prevent infinite loops in both agent types
- Trigger scheduler and email watcher start automatically with FastAPI server lifecycle
- Conversation summarization activates when message count exceeds threshold (default: 100)
- Health check endpoint at `GET /` for deployment platforms (Railway)
