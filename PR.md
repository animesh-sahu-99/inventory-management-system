# PR — API Test Plan (All Endpoints & Conditions)

Manual API verification checklist for the Inventory Management System. Run after `docker compose up --build` with a fresh or seeded database.

**Base URL:** `http://localhost:8000/api/v1`  
**Interactive docs:** `http://localhost:8000/docs`  
**Health:** `GET http://localhost:8000/health` → `200 {"status":"ok"}`

---

## Setup

### 1. Start services

```bash
docker compose up --build
```

### 2. Seed accounts (auto on first boot)

| Role  | Email             | Password  |
|-------|-------------------|-----------|
| Admin | admin@ims.local   | admin123  |
| Staff | staff@ims.local   | staff123  |

### 3. Obtain JWT tokens

```bash
# Admin token
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@ims.local&password=admin123"

# Staff token
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=staff@ims.local&password=staff123"
```

Set environment variables for convenience:

```bash
export ADMIN_TOKEN="<access_token from admin login>"
export STAFF_TOKEN="<access_token from staff login>"
export AUTH_ADMIN="Authorization: Bearer $ADMIN_TOKEN"
export AUTH_STAFF="Authorization: Bearer $STAFF_TOKEN"
```

### 4. Seeded reference IDs (after fresh seed)

Use `GET` list endpoints to confirm IDs if they differ:

| Resource   | Example values |
|------------|----------------|
| Categories | Electronics (id=1), Office Supplies (id=2) |
| Products   | ELEC-001 (qty=50), ELEC-002 (qty=8, low stock), OFF-002 (qty=5, low stock) |
| Suppliers  | TechParts Inc (id=1), Office Depot Wholesale (id=2) |
| Draft PO   | PO-DEMO0001 (status=draft, 1 line item for ELEC-002) |

---

## Global / Cross-cutting tests

| # | Condition | Request | Expected |
|---|-----------|---------|----------|
| G1 | No auth token on protected route | `GET /products` (no header) | `401` |
| G2 | Invalid / expired token | `GET /products` with `Bearer invalid` | `401` |
| G3 | Staff on admin-only route | `POST /suppliers` with staff token | `403` |
| G4 | Staff receive PO | `POST /purchase-orders/{id}/receive` with staff token | `403` |
| G5 | Staff list users | `GET /auth/users` with staff token | `403` |
| G6 | Invalid JSON body | `POST /products` with `{}` | `422` validation error |
| G7 | Non-existent resource ID | `GET /products/99999` | `404` |

---

## Auth — `/auth`

### `POST /auth/register`

| # | Condition | Body | Expected |
|---|-----------|------|----------|
| A1 | Happy path | `{"email":"new@ims.local","password":"pass123","full_name":"New User"}` | `201`, `role=staff` |
| A2 | Duplicate email | Same email as A1 again | `400` "Email already registered" |
| A3 | Password too short | `password: "12345"` (5 chars) | `422` |
| A4 | Invalid email format | `email: "not-an-email"` | `422` |
| A5 | Missing full_name | Omit `full_name` | `422` |

### `POST /auth/login`

| # | Condition | Body (form-urlencoded) | Expected |
|---|-----------|------------------------|----------|
| A6 | Admin happy path | `username=admin@ims.local&password=admin123` | `200`, `access_token` present |
| A7 | Staff happy path | `username=staff@ims.local&password=staff123` | `200` |
| A8 | Wrong password | Correct email, wrong password | `401` |
| A9 | Unknown email | `username=nobody@ims.local&password=admin123` | `401` |
| A10 | Missing fields | Empty body | `422` |

### `GET /auth/me`

| # | Condition | Auth | Expected |
|---|-----------|------|----------|
| A11 | Valid token | Admin or staff token | `200`, email + role returned |
| A12 | No token | — | `401` |

### `GET /auth/users` (admin only)

| # | Condition | Auth | Expected |
|---|-----------|------|----------|
| A13 | Admin lists users | Admin | `200`, array includes admin + staff |
| A14 | Staff denied | Staff | `403` |

### `PATCH /auth/users/{user_id}/role` (admin only)

| # | Condition | Body | Expected |
|---|-----------|------|----------|
| A15 | Promote staff → admin | `{"role":"admin"}` on staff user id | `200`, role updated |
| A16 | Demote admin → staff | `{"role":"staff"}` on same user | `200` |
| A17 | Invalid user id | `user_id=99999` | `404` |
| A18 | Staff attempts change | Staff token | `403` |
| A19 | Invalid role value | `{"role":"superuser"}` | `422` |

---

## Categories — `/categories`

### `GET /categories`

| # | Condition | Expected |
|---|-----------|----------|
| C1 | List all (authenticated) | `200`, seeded categories present |
| C2 | No auth | `401` |

### `POST /categories`

| # | Condition | Body | Expected |
|---|-----------|------|----------|
| C3 | Create category | `{"name":"Test Cat","description":"desc"}` | `201` |
| C4 | Duplicate name | Same name as C3 | `400` "Category already exists" |
| C5 | Empty name | `{"name":""}` | `422` |

### `GET /categories/{id}`

| # | Condition | Expected |
|---|-----------|----------|
| C6 | Valid id | `200` |
| C7 | Invalid id | `404` |

### `PATCH /categories/{id}`

| # | Condition | Body | Expected |
|---|-----------|------|----------|
| C8 | Update description | `{"description":"updated"}` | `200` |
| C9 | Invalid id | — | `404` |

### `DELETE /categories/{id}`

| # | Condition | Expected |
|---|-----------|----------|
| C10 | Delete empty category | `204` |
| C11 | Delete category with products | `400` "Cannot delete category with products" |
| C12 | Invalid id | `404` |

---

## Products — `/products`

### `GET /products`

| # | Condition | Query params | Expected |
|---|-----------|--------------|----------|
| P1 | List paginated | `page=1&page_size=20` | `200`, `items`, `total`, `page` |
| P2 | Search by name | `search=Mouse` | `200`, ELEC-002 in results |
| P3 | Search by SKU | `search=ELEC-001` | `200`, match found |
| P4 | Filter by category | `category_id=1` | `200`, only electronics |
| P5 | Empty search results | `search=ZZZNOTFOUND` | `200`, `items=[]` |
| P6 | Invalid page | `page=0` | `422` |

### `GET /products/low-stock`

| # | Condition | Expected |
|---|-----------|----------|
| P7 | Low stock list | `200`, ELEC-002 and OFF-002 (qty ≤ reorder_level) |

### `POST /products`

| # | Condition | Body | Expected |
|---|-----------|------|----------|
| P8 | Create product | `{"sku":"TEST-001","name":"Test Item","category_id":1,"quantity":10,"reorder_level":5,"unit_price":9.99}` | `201` |
| P9 | Duplicate SKU | Same SKU as P8 | `400` "SKU already exists" |
| P10 | Invalid category_id | `category_id=99999` | `500` or FK error (DB constraint) |
| P11 | Negative quantity | `quantity: -1` | `422` |
| P12 | Missing required fields | `{}` | `422` |

### `GET /products/{id}`

| # | Condition | Expected |
|---|-----------|----------|
| P13 | Valid id | `200`, includes `category` nested object |
| P14 | Invalid id | `404` |

### `PATCH /products/{id}`

| # | Condition | Body | Expected |
|---|-----------|------|----------|
| P15 | Update name/price | `{"name":"Updated Name","unit_price":19.99}` | `200` |
| P16 | Invalid id | — | `404` |

### `DELETE /products/{id}`

| # | Condition | Expected |
|---|-----------|----------|
| P17 | Delete product | `204` |
| P18 | Invalid id | `404` |

---

## Stock Movements — `/stock-movements`

### `GET /stock-movements`

| # | Condition | Query params | Expected |
|---|-----------|--------------|----------|
| M1 | List paginated | `page=1&page_size=20` | `200`, paginated movements |
| M2 | Filter by product | `product_id=1` | `200`, only product 1 |
| M3 | Filter by type | `movement_type=IN` | `200` |
| M4 | Filter by date range | `start_date=2026-01-01&end_date=2026-12-31` | `200` |
| M5 | Invalid movement_type | `movement_type=INVALID` | `500` or error |

### `POST /stock-movements`

| # | Condition | Body | Expected |
|---|-----------|------|----------|
| M6 | Stock IN | `{"product_id":1,"type":"IN","quantity":5,"note":"restock"}` | `201`, product qty +5 |
| M7 | Stock OUT (sufficient) | `{"product_id":1,"type":"OUT","quantity":2}` | `201`, product qty -2 |
| M8 | Stock OUT (insufficient) | OUT qty > current stock | `400` "Insufficient stock" |
| M9 | ADJUSTMENT | `{"product_id":1,"type":"ADJUSTMENT","quantity":100}` | `201`, qty set to 100 |
| M10 | Invalid product_id | `product_id=99999` | `404` |
| M11 | Zero quantity | `quantity: 0` | `422` |
| M12 | Missing type | omit `type` | `422` |
| M13 | Verify audit trail | After M6, `GET /stock-movements` | New row with user + timestamp |

---

## Suppliers — `/suppliers`

### `GET /suppliers`

| # | Condition | Auth | Expected |
|---|-----------|------|----------|
| S1 | List (staff) | Staff | `200`, seeded suppliers |
| S2 | List (admin) | Admin | `200` |

### `POST /suppliers` (admin only)

| # | Condition | Body | Auth | Expected |
|---|-----------|------|------|----------|
| S3 | Create supplier | `{"name":"New Supplier","contact_name":"Bob","email":"bob@test.com","phone":"555","is_active":true}` | Admin | `201` |
| S4 | Staff denied | Same body | Staff | `403` |
| S5 | Duplicate name | Same name as S3 | Admin | `400` |
| S6 | Invalid email | `email: "bad"` | Admin | `422` |

### `GET /suppliers/{id}`

| # | Condition | Expected |
|---|-----------|----------|
| S7 | Valid id | `200` |
| S8 | Invalid id | `404` |

### `PATCH /suppliers/{id}` (admin only)

| # | Condition | Auth | Expected |
|---|-----------|------|----------|
| S9 | Update supplier | Admin | `200` |
| S10 | Staff denied | Staff | `403` |

### `DELETE /suppliers/{id}` (admin only)

| # | Condition | Expected |
|---|-----------|----------|
| S11 | Delete supplier with no POs | `204` |
| S12 | Delete supplier with POs | `400` "Cannot delete supplier with purchase orders" |
| S13 | Staff denied | `403` |

---

## Purchase Orders — `/purchase-orders`

### `GET /purchase-orders`

| # | Condition | Query | Expected |
|---|-----------|-------|----------|
| PO1 | List paginated | `page=1&page_size=20` | `200`, includes PO-DEMO0001 |
| PO2 | Filter by status | `status=draft` | `200`, only drafts |
| PO3 | Filter ordered | `status=ordered` | `200` (after submit test) |

### `POST /purchase-orders`

| # | Condition | Body | Auth | Expected |
|---|-----------|------|------|----------|
| PO4 | Create draft PO | See sample below | Staff or Admin | `201`, `status=draft` |
| PO5 | Empty items array | `items: []` | — | `422` |
| PO6 | Invalid product_id in item | `product_id=99999` | — | `404` |
| PO7 | Zero quantity_ordered | `quantity_ordered: 0` | — | `422` |
| PO8 | Invalid supplier_id | `supplier_id=99999` | — | FK/DB error |

**Sample create body:**

```json
{
  "supplier_id": 1,
  "expected_date": "2026-07-01",
  "notes": "Test PO",
  "items": [
    { "product_id": 1, "quantity_ordered": 10, "unit_cost": 12.00 }
  ]
}
```

### `GET /purchase-orders/{id}`

| # | Condition | Expected |
|---|-----------|----------|
| PO9 | Valid id | `200`, items + supplier nested |
| PO10 | Invalid id | `404` |

### `PATCH /purchase-orders/{id}`

| # | Condition | Expected |
|---|-----------|----------|
| PO11 | Update draft PO | `200`, notes/items updated |
| PO12 | Update non-draft PO | `400` "Only draft POs can be edited" |
| PO13 | Invalid id | `404` |

### `POST /purchase-orders/{id}/submit`

| # | Condition | Expected |
|---|-----------|----------|
| PO14 | Submit draft | `200`, `status=ordered` |
| PO15 | Submit again | `400` "Only draft POs can be submitted" |
| PO16 | Submit PO with no items | `400` (if items removed) |

### `POST /purchase-orders/{id}/receive` (admin only)

| # | Condition | Body | Auth | Expected |
|---|-----------|------|------|----------|
| PO17 | Staff denied | — | Staff | `403` |
| PO18 | Full receive | `{"items":[{"item_id":<id>,"quantity":20}]}` | Admin | `200`, `status=received`, product qty +20 |
| PO19 | Partial receive | Receive qty < ordered | Admin | `200`, `status=partial` |
| PO20 | Over-receive | qty > remaining | `400` |
| PO21 | Receive on draft PO | — | Admin | `400` "must be ordered or partial" |
| PO22 | Invalid item_id | `item_id=99999` | Admin | `404` |
| PO23 | Verify stock movement | After PO18, `GET /stock-movements?product_id=X` | IN movement linked to PO |

### `POST /purchase-orders/{id}/cancel` (admin only)

| # | Condition | Auth | Expected |
|---|-----------|------|----------|
| PO24 | Cancel ordered PO | Admin | `200`, `status=cancelled` |
| PO25 | Cancel received PO | Admin | `400` "Cannot cancel" |
| PO26 | Staff denied | Staff | `403` |

### `DELETE /purchase-orders/{id}` (admin only)

| # | Condition | Auth | Expected |
|---|-----------|------|----------|
| PO27 | Delete draft PO | Admin | `204` |
| PO28 | Delete non-draft | Admin | `400` "Only draft POs can be deleted" |
| PO29 | Staff denied | Staff | `403` |

---

## Dashboard — `/dashboard/summary`

| # | Condition | Expected |
|---|-----------|----------|
| D1 | Get summary | `200`, fields: `total_products`, `total_categories`, `total_suppliers`, `low_stock_count`, `open_po_count`, `total_inventory_value`, `recent_movements` |
| D2 | Counts match data | After creating product, `total_products` increments |
| D3 | Low stock count | Matches `GET /products/low-stock` length |
| D4 | No auth | `401` |

---

## Reports — `/reports/*`

### `GET /reports/inventory`

| # | Condition | Expected |
|---|-----------|----------|
| R1 | JSON report | `200`, array with `sku`, `name`, `category`, `quantity`, `status` (OK/Low/Out) |

### `GET /reports/inventory/export`

| # | Condition | Expected |
|---|-----------|----------|
| R2 | CSV download | `200`, `Content-Type: text/csv`, file downloads |

### `GET /reports/low-stock`

| # | Condition | Expected |
|---|-----------|----------|
| R3 | JSON report | `200`, only low/out items, includes `deficit` |

### `GET /reports/low-stock/export`

| # | Condition | Expected |
|---|-----------|----------|
| R4 | CSV download | `200`, valid CSV |

### `GET /reports/movements`

| # | Condition | Query | Expected |
|---|-----------|-------|----------|
| R5 | All movements | — | `200` |
| R6 | Date filter | `start_date=2026-01-01&end_date=2026-12-31` | `200`, filtered |

### `GET /reports/movements/export`

| # | Condition | Expected |
|---|-----------|----------|
| R7 | CSV download | `200`, headers: ID, Date, SKU, Product, Type, Quantity, User, Note |

### `GET /reports/purchase-orders`

| # | Condition | Query | Expected |
|---|-----------|-------|----------|
| R8 | All POs | — | `200` |
| R9 | Status filter | `status=draft` | `200`, filtered |

### `GET /reports/purchase-orders/export`

| # | Condition | Expected |
|---|-----------|----------|
| R10 | CSV download | `200`, valid CSV |

### Reports auth

| # | Condition | Expected |
|---|-----------|----------|
| R11 | Staff can access reports | `200` on all report endpoints |
| R12 | No auth | `401` |

---

## End-to-end workflows

Run these flows in order to validate cross-module behavior.

### Workflow 1 — Full inventory cycle

- [ ] Login as staff
- [ ] `GET /categories` → pick category id
- [ ] `POST /products` → create product (qty=0)
- [ ] `POST /stock-movements` type `IN` qty=50
- [ ] `GET /products/{id}` → qty=50
- [ ] `POST /stock-movements` type `OUT` qty=10
- [ ] `GET /products/{id}` → qty=40
- [ ] `GET /dashboard/summary` → reflects changes
- [ ] `GET /reports/inventory` → product appears

### Workflow 2 — Purchase order lifecycle (admin)

- [ ] Login as admin
- [ ] `POST /suppliers` → create supplier
- [ ] `POST /purchase-orders` → draft with 2 line items
- [ ] `PATCH /purchase-orders/{id}` → update notes
- [ ] `POST /purchase-orders/{id}/submit` → status=ordered
- [ ] `POST /purchase-orders/{id}/receive` → partial qty on item 1
- [ ] Verify `status=partial`, product qty increased
- [ ] `POST /purchase-orders/{id}/receive` → remaining qty
- [ ] Verify `status=received`, full qty received
- [ ] `GET /reports/purchase-orders` → PO shows received

### Workflow 3 — RBAC enforcement

- [ ] Login as staff
- [ ] `POST /suppliers` → `403`
- [ ] `POST /purchase-orders/{id}/receive` → `403`
- [ ] `GET /auth/users` → `403`
- [ ] `POST /purchase-orders` → `201` (allowed)
- [ ] `POST /purchase-orders/{id}/submit` → `200` (allowed)

### Workflow 4 — Error boundaries

- [ ] `POST /stock-movements` OUT with qty > stock → `400`
- [ ] `DELETE /categories/{id}` with products → `400`
- [ ] `PATCH /purchase-orders/{id}` on ordered PO → `400`
- [ ] `POST /auth/register` duplicate email → `400`

---

## Sample curl commands

### Create product

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "$AUTH_ADMIN" -H "Content-Type: application/json" \
  -d '{"sku":"CURL-001","name":"Curl Test","category_id":1,"quantity":0,"reorder_level":5,"unit_price":1.99}'
```

### Stock IN

```bash
curl -X POST http://localhost:8000/api/v1/stock-movements \
  -H "$AUTH_ADMIN" -H "Content-Type: application/json" \
  -d '{"product_id":1,"type":"IN","quantity":10,"note":"curl test"}'
```

### Submit PO

```bash
curl -X POST http://localhost:8000/api/v1/purchase-orders/1/submit \
  -H "$AUTH_STAFF"
```

### Export inventory CSV

```bash
curl -o inventory.csv http://localhost:8000/api/v1/reports/inventory/export \
  -H "$AUTH_STAFF"
```

---

## PR sign-off checklist

| Area | Tests | Pass |
|------|-------|------|
| Auth (A1–A19) | | ☐ |
| Global (G1–G7) | | ☐ |
| Categories (C1–C12) | | ☐ |
| Products (P1–P18) | | ☐ |
| Stock movements (M1–M13) | | ☐ |
| Suppliers (S1–S13) | | ☐ |
| Purchase orders (PO1–PO29) | | ☐ |
| Dashboard (D1–D4) | | ☐ |
| Reports (R1–R12) | | ☐ |
| E2E workflows (1–4) | | ☐ |

**Tester:** _______________  
**Date:** _______________  
**Build / commit:** _______________
