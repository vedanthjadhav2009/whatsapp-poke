# Repository Guidelines

## Project Structure & Module Organization
- Backend FastAPI service lives in `server/` with domain logic under `agents/`, API routes in `routes/` (e.g., `chat.py`, `gmail.py`, `whatsapp.py`), and shared helpers in `services/` and `utils/`. Runtime artifacts land in `server/data/` (gitignored).
- Frontend Next.js app sits in `web/`, with the app router in `web/app/`, shared UI in `web/components/`, and global styles in `web/app/globals.css`.
- Root scripts (`start.sh`, `start.bat`, `Makefile`) orchestrate both apps. Environment configuration is shared from `.env` at the repo root.

## Build, Test, and Development Commands
- Install deps: `make install` or `npm run install:all` (creates `.venv`, installs `server/requirements.txt`, then `web/package.json`).
- Run everything: `make start` or `npm start` (spawns backend and `next dev` together). Stop with `make stop` or `npm run stop`.
- Focused dev: `make backend` (FastAPI with reload) or `make frontend` / `npm run frontend` (Next.js dev server). Frontend lint: `npm run lint --prefix web`.
- Clean workspace: `make clean` (removes `.venv`, `web/node_modules`, `.next`, and `server/__pycache__`).

## Coding Style & Naming Conventions
- Python: 4-space indents, type hints for public functions, snake_case for modules/functions, PascalCase for Pydantic models. Keep FastAPI route handlers thin; push logic into `services/` or `agents/`.
- TypeScript/React: use functional components and hooks; PascalCase components in `web/components/`, camelCase props; co-locate UI-specific helpers with components. Run `npm run lint --prefix web` before opening a PR.
- Config and secret keys stay in `.env`; never commit credentials or files under `server/data/`.

## Testing Guidelines
- No automated suite is bundled yet; add targeted tests when changing behavior. Backend: prefer `pytest` with FastAPI `TestClient` (declare deps in `server/requirements.txt`). Frontend: use React Testing Library/Jest aligned with Next 14 (declare deps in `web/package.json`).
- Name tests after the unit under test (e.g., `test_chat_routes.py`, `SettingsModal.test.tsx`) and keep fixtures small.
- Before merging, run `npm run lint --prefix web` and any new tests you add; note results in the PR.

## Commit & Pull Request Guidelines
- Follow concise, imperative commit messages (e.g., `Add Gmail webhook route`); group related changes; include issue/PR references (`#123`) when applicable. Current history is inconsistent—please tighten conventions going forward.
- PRs should describe scope, motivation, and user impact; link issues; call out env/config changes; attach screenshots for UI tweaks and sample requests/responses for API changes.
- Ensure docs stay accurate (update `README.md`, `DEPLOYMENT.md`, or inline docstrings) when behavior changes.

## Security & Configuration Tips
- Keep `.env` in sync with `.env.example`; required keys include Ananas and Composio tokens used by agents.
- Avoid logging secrets; prefer structured logs via `server/logging_config.py`. Scrub user data from debug traces before sharing.
