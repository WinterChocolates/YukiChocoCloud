# CLAUDE.md
请使用使用简体中文与我对话，并在回答时保持专业、简介。

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What is YukiChocoCloud

A private cloud storage web app (personal NAS-style file manager) built with FastAPI + Vue 3 + PostgreSQL. Targets deployment on home servers via Docker.

## Development Commands

### Backend (Python / FastAPI)
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # then edit secrets
uvicorn app.main:app --reload          # dev server at :8000
```
- API docs auto-generated at http://localhost:8000/docs
- Requires a running PostgreSQL instance (see Docker section below)
- Uses conda as the default Python env manager (per VS Code settings)

### Frontend (Vue 3 / Vite)
```bash
cd frontend
npm install
npm run dev        # dev server at :3000, proxies /api → localhost:8000
npm run build      # type-check (vue-tsc) + vite build → dist/
npm run preview    # preview production build locally
```

### Docker (full stack)
```bash
cp .env.example .env  # edit DATABASE_URL, SECRET_KEY, POSTGRES_* vars
docker-compose up -d  # starts postgres + app on :8000
```
The Dockerfile uses multi-stage build: frontend `dist/` is copied into the Python image as `/app/static`, served by FastAPI as a SPA catch-all.

### Database
No Alembic yet — models are created directly via SQLAlchemy. The `DATABASE_URL` env var uses `postgresql+asyncpg://` scheme.

## Architecture

### Backend — `backend/app/`

Layered structure: **routers → services → models**, with **schemas** for request/response validation.

| Layer | Purpose |
|-------|---------|
| `main.py` | FastAPI app, mounts routers, serves SPA static files in production |
| `config.py` | Pydantic `Settings` loaded from `.env` (DATABASE_URL, SECRET_KEY, UPLOAD_DIR, STORAGE_LIMIT) |
| `database.py` | Async engine + session factory via SQLAlchemy 2.0 + asyncpg; `get_db` dependency |
| `models/` | SQLAlchemy ORM models: `User`, `File`, `Share` — all use `Mapped[]` style |
| `schemas/` | Pydantic v2 models. All API responses wrap in `ResponseModel[T]` (code/message/data) |
| `routers/` | FastAPI routers with prefix `/api/...`. Auth uses `HTTPBearer` + JWT |
| `services/` | Business logic (no HTTP concerns). `auth.py` handles JWT + bcrypt, `files.py` handles CRUD, `storage.py` handles disk I/O, `share.py` handles share links |

**Key patterns:**
- All API responses follow `ResponseModel[T]` format: `{"code": 0, "message": "ok", "data": ...}`
- Auth: `python-jose` JWT + `passlib` bcrypt. `get_current_user` dependency extracts user from Bearer token
- File storage: local disk at `UPLOAD_DIR`, path pattern `{user_id}/{YYYY}/{MM}/{filename}`
- Files model is a tree structure via `parent_id` self-referential FK; `is_dir` distinguishes folders from files
- Soft delete: `is_deleted` boolean flag on files (recycle bin pattern)
- Shares: token-based with optional bcrypt-hashed password and expiry

### Frontend — `frontend/src/`

Vue 3 Composition API + TypeScript + Element Plus + Pinia + Vue Router.

| Path | Purpose |
|------|---------|
| `api/index.ts` | Axios instance with JWT interceptor (auto-attach token, 401 → redirect login). All API functions exported here |
| `stores/user.ts` | Pinia store: token/username in localStorage, login/logout actions |
| `router/index.ts` | Two routes: `/login` and `/` (auth-guarded). History mode |
| `views/Login.vue` | Login page |
| `views/Home.vue` | Main file manager: sidebar + file grid + upload + preview. All file operations orchestrated here |
| `components/` | `Topbar`, `Sidebar`, `FileCard`, `UploadFloatButton`, `SnowBackground` |
| `assets/styles/` | SCSS with variables (`variables.scss`), global styles, animations |

**Key patterns:**
- Dev proxy: Vite proxies `/api/*` to `http://localhost:8000` (avoids CORS)
- File preview: fetched as blob, displayed via `URL.createObjectURL`
- Design theme: dark winter/chocolate aesthetic with glass-morphism, defined in SCSS variables

### Routers overview

| Router | Prefix | Endpoints |
|--------|--------|-----------|
| `auth` | `/api/auth` | POST `/register`, POST `/login` |
| `files` | `/api/files` | GET `""` (list), POST `""` (create folder), DELETE `/{id}`, GET `/storage` |
| `upload` | — | POST `/api/upload`, GET `/api/download/{id}`, GET `/api/preview/{id}` |
| `share` | — | POST `/api/shares`, POST `/api/public/share/{token}` |

## Environment Variables

Defined in `backend/.env` (see `.env.example`):
- `DATABASE_URL` — PostgreSQL async connection string
- `SECRET_KEY` — JWT signing key
- `UPLOAD_DIR` — File storage root (default: `uploads`)
- `STORAGE_LIMIT` — Per-user quota, supports human-readable sizes (e.g. `10GB`)
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` — Used by docker-compose
