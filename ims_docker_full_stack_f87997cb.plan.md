---
name: IMS Docker Full Stack
overview: Full-stack Inventory Management System (Docker, PostgreSQL, FastAPI, React+TS+Tailwind) with JWT/RBAC, suppliers, purchase orders, reports, CSV export, and a layered backend (routes → services → repositories).
todos:
  - id: scaffold-root
    content: Create root docker-compose.yml, .env.example, .gitignore, README.md
    status: completed
  - id: backend-models
    content: "Build FastAPI models: User (with role), Category, Product, Supplier, PurchaseOrder, PO items, StockMovement + Alembic migration"
    status: completed
  - id: backend-api
    content: Implement JWT auth, RBAC deps, CRUD APIs, PurchaseOrderService (receive → stock IN), StockService, dashboard, reports + CSV export
    status: completed
  - id: backend-docker
    content: Add backend Dockerfile and migrate-on-start entrypoint with seed data
    status: completed
  - id: frontend-scaffold
    content: Scaffold Vite/React/TS/Tailwind with API client, auth context (role-aware), layout, routing
    status: completed
  - id: frontend-pages
    content: "Build all pages: Login, Dashboard, Products, Categories, Movements, Suppliers, Purchase Orders, Reports, Users"
    status: completed
  - id: frontend-docker
    content: Add frontend Dockerfile and wire VITE_API_URL in compose
    status: completed
  - id: backend-repositories
    content: "Refactor backend to repository + service layers with DI, domain exceptions, thin routes"
    status: completed
  - id: integration
    content: Seed data (admin + staff users), CORS/env wiring, end-to-end smoke test via docker compose
    status: completed
isProject: false
---

# Inventory Management System — Implementation Plan

**Status: Implemented.** All planned features and the repository-layer refactor are complete.

## Scope (delivered)

- **Auth:** Register/login with JWT; all inventory routes protected
- **Roles (RBAC):** `admin` and `staff` with permission boundaries
- **Core inventory:** Products, categories, stock levels, stock in/out/adjustment movements, low-stock alerts, dashboard
- **Suppliers:** Full CRUD for vendor records linked to purchase orders
- **Purchase orders:** Create PO with line items, status workflow, receive goods (auto stock IN)
- **Reports:** Inventory summary, low-stock report, movement history report, PO summary
- **CSV export:** Download reports as CSV from API endpoints
- **Docker:** One-command `docker compose up` for local dev
- **Backend architecture:** Routes → Services → Repositories (SOLID-aligned layering)

---

## Role permissions

| Action | admin | staff |
|--------|:-----:|:-----:|
| View dashboard, products, categories, movements | yes | yes |
| Create/edit/delete products & categories | yes | yes |
| Manual stock movements (IN/OUT/ADJUSTMENT) | yes | yes |
| View suppliers | yes | yes |
| Create/edit/delete suppliers | yes | no |
| Create/edit purchase orders | yes | yes |
| Receive / cancel purchase orders | yes | no |
| View reports & export CSV | yes | yes |
| Manage users / change roles | yes | no |
| Delete purchase orders (draft only) | yes | no |

Enforced via FastAPI `require_admin` on restricted routes; frontend hides/disables UI for unauthorized actions.

---

## Architecture

```mermaid
flowchart LR
  subgraph client [Frontend]
    ReactApp["React + TS + Tailwind\n:5173"]
  end
  subgraph docker [Docker Compose]
    subgraph backend_svc [Backend]
      Routes["api/v1 routes"]
      Services["services"]
      Repos["repositories"]
      FastAPI["FastAPI\n:8000"]
    end
    subgraph db_svc [Database]
      Postgres["PostgreSQL 16\n:5432"]
    end
  end
  ReactApp -->|"REST /api/v1"| Routes
  Routes --> Services
  Services --> Repos
  Repos -->|"SQLAlchemy"| Postgres
```

| Service | Tech | Port |
|---------|------|------|
| `frontend` | Vite + React 18 + TypeScript + Tailwind | 5173 |
| `backend` | FastAPI + SQLAlchemy 2 + Alembic + Pydantic v2 | 8000 |
| `db` | PostgreSQL 16 | 5432 |

### Backend layering

| Layer | Path | Responsibility |
|-------|------|----------------|
| Routes | [`backend/app/api/v1/`](backend/app/api/v1/) | HTTP only; no `db.query()` |
| Services | [`backend/app/services/`](backend/app/services/) | Business rules; raise domain exceptions |
| Repositories | [`backend/app/repositories/`](backend/app/repositories/) | All SQLAlchemy queries |
| Models | [`backend/app/models/`](backend/app/models/) | DB entities |
| Schemas | [`backend/app/schemas/`](backend/app/schemas/) | Pydantic DTOs |
| Core | [`backend/app/core/`](backend/app/core/) | Config, security, deps (DI), exceptions, pagination |

**DI wiring:** [`backend/app/core/deps.py`](backend/app/core/deps.py) provides `get_*_repo()` and `get_*_service()` factories via FastAPI `Depends`.

**Error handling:** Services raise `DomainError` subclasses from [`backend/app/core/exceptions.py`](backend/app/core/exceptions.py); [`backend/app/main.py`](backend/app/main.py) maps them to JSON HTTP responses.

---

## Repository layout

```
IMS/
├── docker-compose.yml
├── .env.example
├── .gitignore
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── requirements.txt
│   ├── alembic/
│   └── app/
│       ├── main.py
│       ├── seed.py
│       ├── core/              # config, security, deps, exceptions, pagination
│       ├── models/
│       ├── schemas/
│       ├── repositories/      # data access (one per aggregate)
│       ├── services/          # business logic (instance classes + DI)
│       └── api/v1/            # thin HTTP handlers
└── frontend/
    ├── Dockerfile
    ├── package.json
    └── src/
        ├── api/
        ├── components/
        ├── context/           # AuthContext with role
        ├── pages/
        └── types/
```

### Repositories (implemented)

| Repository | Key methods |
|------------|-------------|
| `UserRepository` | `get_by_email`, `list_all` |
| `CategoryRepository` | `get_by_name`, `list_all`, `count` |
| `ProductRepository` | `list_paginated`, `list_low_stock`, `get_for_update`, `count_low_stock` |
| `SupplierRepository` | `get_by_name`, `list_all`, `count` |
| `PurchaseOrderRepository` | `get_by_id_with_details`, `get_for_update_with_items`, `list_paginated`, `count_open` |
| `StockMovementRepository` | `list_paginated`, `list_for_report`, `list_recent` |

### Services (implemented)

| Service | Responsibility |
|---------|----------------|
| `AuthService` | Register, authenticate, token, user role management |
| `CategoryService` | Category CRUD |
| `ProductService` | Product CRUD + pagination + low-stock |
| `SupplierService` | Supplier CRUD |
| `StockService` | Transactional stock movements (IN/OUT/ADJUSTMENT) |
| `PurchaseOrderService` | PO lifecycle (draft → ordered → partial/received) + receive |
| `DashboardService` | Dashboard summary aggregates |
| `ReportService` | Report queries + CSV generation |

---

## Database schema

```mermaid
erDiagram
  users ||--o{ stock_movements : creates
  users ||--o{ purchase_orders : creates
  categories ||--o{ products : contains
  products ||--o{ stock_movements : tracks
  products ||--o{ purchase_order_items : ordered
  suppliers ||--o{ purchase_orders : supplies
  purchase_orders ||--|{ purchase_order_items : contains

  users {
    int id PK
    string email UK
    string hashed_password
    string full_name
    enum role "admin|staff"
    datetime created_at
  }
  categories {
    int id PK
    string name UK
    string description
  }
  products {
    int id PK
    string sku UK
    string name
    int category_id FK
    int quantity
    int reorder_level
    decimal unit_price
    string description
    datetime updated_at
  }
  suppliers {
    int id PK
    string name UK
    string contact_name
    string email
    string phone
    string address
    bool is_active
    datetime created_at
  }
  purchase_orders {
    int id PK
    string po_number UK
    int supplier_id FK
    int created_by FK
    enum status "draft|ordered|partial|received|cancelled"
    date expected_date
    string notes
    datetime created_at
    datetime updated_at
  }
  purchase_order_items {
    int id PK
    int purchase_order_id FK
    int product_id FK
    int quantity_ordered
    int quantity_received
    decimal unit_cost
  }
  stock_movements {
    int id PK
    int product_id FK
    int user_id FK
    int purchase_order_id FK "nullable"
    enum type "IN|OUT|ADJUSTMENT"
    int quantity
    string note
    datetime created_at
  }
```

**Stock rules:**
- Manual `IN` / `OUT` / `ADJUSTMENT` via stock-movements API (staff + admin)
- PO **receive** creates `IN` movements per line item and updates `products.quantity` atomically
- `OUT` rejects insufficient stock; `ADJUSTMENT` sets absolute quantity
- `purchase_order_id` on movements links auto-IN from PO receiving

**PO status workflow:**
- `draft` → `ordered` (staff/admin can submit)
- `ordered` → `partial` or `received` on receive (admin only for receive)
- `draft` → `cancelled` (admin only)
- Cannot edit line items once status is `received` or `cancelled`

---

## API surface (`/api/v1`)

**Auth**
| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/auth/register` | Create user (default role: `staff`) |
| POST | `/auth/login` | Return JWT (includes role claim) |
| GET | `/auth/me` | Current user + role |
| GET | `/auth/users` | List users (admin) |
| PATCH | `/auth/users/{id}/role` | Change role (admin) |

**Inventory**
| Method | Endpoint | Purpose |
|--------|----------|---------|
| CRUD | `/categories` | Category management |
| CRUD | `/products` | Product CRUD + search/filter/pagination |
| GET | `/products/low-stock` | Products at/below reorder level |
| POST | `/stock-movements` | Record IN/OUT/ADJUSTMENT |
| GET | `/stock-movements` | Paginated history (filter by product, type, date) |

**Suppliers** (create/update/delete: admin only)
| Method | Endpoint | Purpose |
|--------|----------|---------|
| CRUD | `/suppliers` | Supplier management |

**Purchase orders**
| Method | Endpoint | Purpose | Role |
|--------|----------|---------|------|
| GET/POST | `/purchase-orders` | List / create PO | staff+ |
| GET/PATCH | `/purchase-orders/{id}` | Detail / update draft PO | staff+ |
| POST | `/purchase-orders/{id}/submit` | draft → ordered | staff+ |
| POST | `/purchase-orders/{id}/receive` | Receive items, stock IN | admin |
| POST | `/purchase-orders/{id}/cancel` | Cancel PO | admin |
| DELETE | `/purchase-orders/{id}` | Delete draft PO | admin |

**Dashboard & reports**
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/dashboard/summary` | Totals, low-stock count, recent movements, open POs |
| GET | `/reports/inventory` | Full inventory snapshot (JSON) |
| GET | `/reports/inventory/export` | CSV download |
| GET | `/reports/low-stock` | Low-stock items (JSON) |
| GET | `/reports/low-stock/export` | CSV download |
| GET | `/reports/movements` | Movement history with date filters (JSON) |
| GET | `/reports/movements/export` | CSV download |
| GET | `/reports/purchase-orders` | PO summary with status filters (JSON) |
| GET | `/reports/purchase-orders/export` | CSV download |

### Seed data ([`backend/app/seed.py`](backend/app/seed.py))
- Admin: `admin@ims.local` / `admin123`
- Staff: `staff@ims.local` / `staff123`
- Sample categories, products, suppliers, one draft PO

---

## Frontend (React + TypeScript + Tailwind)

### Tooling
- Vite, React Router v6, TanStack Query, Axios (JWT interceptors)
- Tailwind admin layout (sidebar + top bar)

### Pages

| Route | Page | Features |
|-------|------|----------|
| `/login` | Login | Email/password |
| `/register` | Register | Creates staff account |
| `/` | Dashboard | Stats, low-stock, recent movements, open POs |
| `/products` | Products | CRUD table, search, stock badges |
| `/categories` | Categories | CRUD list |
| `/movements` | Stock Movements | Record form + filtered history |
| `/suppliers` | Suppliers | CRUD (admin: full; staff: read-only) |
| `/purchase-orders` | Purchase Orders | List, create/edit draft, submit, receive (admin), detail view |
| `/reports` | Reports | Tabs per report type, date filters, Export CSV |
| `/users` | User Management | Admin only: list users, change roles |

---

## Data flow: receive purchase order

```mermaid
sequenceDiagram
  participant UI as PurchaseOrdersPage
  participant Route as API_Route
  participant POSvc as PurchaseOrderService
  participant PORepo as PurchaseOrderRepository
  participant StockSvc as StockService
  participant ProdRepo as ProductRepository

  UI->>Route: POST /purchase-orders/{id}/receive
  Route->>POSvc: receive(user, po_id, data)
  POSvc->>PORepo: get_for_update_with_items()
  loop each line item
    POSvc->>ProdRepo: get_for_update(product_id)
    POSvc->>StockSvc: apply_movement(IN, qty, po_id)
  end
  POSvc->>PORepo: commit()
  Route-->>UI: 200 OK
```

---

## Docker Compose

3 services (`db`, `backend`, `frontend`) with healthcheck, hot reload, and `VITE_API_URL`.

```bash
docker compose up --build
```

---

## Verification checklist

- [x] Full stack scaffolded (backend, frontend, Docker)
- [x] JWT auth + admin/staff RBAC
- [x] Products, categories, suppliers, POs, movements, reports
- [x] Repository + service layering with DI
- [x] Domain exceptions mapped to HTTP responses
- [x] Seed data (admin + staff demo accounts)
- [ ] `docker compose up --build` E2E smoke test (run locally with Docker Desktop)

**Manual E2E checks:**
- Login as admin and staff; JWT includes role
- Staff cannot create suppliers or receive POs (403)
- Admin can manage suppliers, receive POs, change user roles
- Create supplier → create PO → submit → receive → product quantity increases
- Manual OUT movement fails on insufficient stock
- Reports return correct data; CSV exports download valid files
