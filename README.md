# Inventory Management System (IMS)

A full-stack inventory management application with JWT authentication, role-based access control, suppliers, purchase orders, stock tracking, reports, and CSV export.

## Stack

- **Frontend:** React 18, TypeScript, Tailwind CSS, Vite, TanStack Query, Axios
- **Backend:** Python FastAPI, SQLAlchemy 2, Alembic, Pydantic v2
- **Database:** PostgreSQL 16
- **Infrastructure:** Docker Compose

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Run

**Linux / macOS:**

```bash
cp .env.example .env
docker compose up --build
```

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
docker compose up --build
```

| Service  | URL |
|----------|-----|
| Frontend | http://localhost:5173 |
| API Docs | http://localhost:8000/docs |
| API      | http://localhost:8000/api/v1 |

### Demo Accounts

| Role  | Email              | Password  |
|-------|--------------------|-----------|
| Admin | admin@ims.local    | admin123  |
| Staff | staff@ims.local    | staff123  |

## Features

- **Auth:** Register/login with JWT tokens
- **Roles:** Admin vs Staff with permission boundaries
- **Products & Categories:** Full CRUD with search and pagination
- **Stock Movements:** Record IN, OUT, and ADJUSTMENT with audit trail
- **Suppliers:** Vendor management (admin write, staff read)
- **Purchase Orders:** Draft → Ordered → Partial/Received workflow with auto stock-in on receive
- **Dashboard:** Inventory stats, low-stock alerts, recent movements, open POs
- **Reports:** Inventory, low-stock, movements, and PO summaries with CSV export

## Backend Architecture

The backend follows a layered design aligned with SOLID principles:

```
Route (HTTP)  →  Service (business logic)  →  Repository (DB access)  →  Model
```

| Layer | Location | Responsibility |
|-------|----------|----------------|
| **Routes** | `backend/app/api/v1/` | Parse requests, enforce auth deps, call services |
| **Services** | `backend/app/services/` | Business rules, workflows, domain exceptions |
| **Repositories** | `backend/app/repositories/` | SQLAlchemy queries, pagination, locking |
| **Models** | `backend/app/models/` | Database entities |
| **Schemas** | `backend/app/schemas/` | Pydantic request/response DTOs |

Services raise domain exceptions (`NotFoundError`, `BadRequestError`, etc.) defined in `core/exceptions.py`. FastAPI maps these to HTTP responses in `main.py`. Dependencies are wired via `core/deps.py` using FastAPI `Depends`.

## Project Structure

```
IMS/
├── docker-compose.yml
├── .env.example
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh          # migrate + seed + uvicorn
│   ├── requirements.txt
│   ├── alembic/
│   └── app/
│       ├── main.py
│       ├── seed.py
│       ├── core/              # config, security, deps, exceptions, pagination
│       ├── models/            # SQLAlchemy entities
│       ├── schemas/           # Pydantic DTOs
│       ├── repositories/      # Data access layer
│       ├── services/          # Business logic layer
│       └── api/v1/            # HTTP route handlers
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── api/               # Axios client
        ├── components/        # Shared UI
        ├── context/           # AuthContext (role-aware)
        ├── pages/             # Route pages
        └── types/             # TypeScript interfaces
```

## Common Commands

```bash
# View logs
docker compose logs -f

# Stop services
docker compose down

# Stop and remove database volume (fresh DB)
docker compose down -v

# Rebuild after dependency changes
docker compose up --build
```

## Role Permissions

| Action | Admin | Staff |
|--------|:-----:|:-----:|
| View inventory data | Yes | Yes |
| Manage products/categories | Yes | Yes |
| Manual stock movements | Yes | Yes |
| View suppliers | Yes | Yes |
| Manage suppliers | Yes | No |
| Create/submit POs | Yes | Yes |
| Receive/cancel POs | Yes | No |
| Reports & CSV export | Yes | Yes |
| User role management | Yes | No |

## Local Development (without Docker)

**Frontend** (requires Node 20+):

```bash
cd frontend
npm install
npm run dev
```

**Backend** (requires Python 3.12+ and a running PostgreSQL instance):

```bash
cd backend
pip install -r requirements.txt
# Set DATABASE_URL in .env to point at your local Postgres
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

Set `VITE_API_URL=http://localhost:8000/api/v1` in the frontend environment.
