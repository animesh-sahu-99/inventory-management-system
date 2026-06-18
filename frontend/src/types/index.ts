export type UserRole = 'admin' | 'staff'

export interface User {
  id: number
  email: string
  full_name: string
  role: UserRole
  created_at: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface Paginated<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface Category {
  id: number
  name: string
  description: string | null
}

export interface Product {
  id: number
  sku: string
  name: string
  category_id: number
  quantity: number
  reorder_level: number
  unit_price: string
  description: string | null
  updated_at: string
  category?: { id: number; name: string }
}

export interface Supplier {
  id: number
  name: string
  contact_name: string | null
  email: string | null
  phone: string | null
  address: string | null
  is_active: boolean
  created_at: string
}

export type POStatus = 'draft' | 'ordered' | 'partial' | 'received' | 'cancelled'
export type MovementType = 'IN' | 'OUT' | 'ADJUSTMENT'

export interface POItem {
  id: number
  product_id: number
  quantity_ordered: number
  quantity_received: number
  unit_cost: string
  product_name?: string
  product_sku?: string
}

export interface PurchaseOrder {
  id: number
  po_number: string
  supplier_id: number
  created_by: number
  status: POStatus
  expected_date: string | null
  notes: string | null
  created_at: string
  updated_at: string
  supplier?: { id: number; name: string }
  items: POItem[]
}

export interface StockMovement {
  id: number
  product_id: number
  user_id: number
  purchase_order_id: number | null
  type: MovementType
  quantity: number
  note: string | null
  created_at: string
  product?: { id: number; sku: string; name: string }
  user?: { id: number; full_name: string }
}

export interface DashboardSummary {
  total_products: number
  total_categories: number
  total_suppliers: number
  low_stock_count: number
  open_po_count: number
  total_inventory_value: string
  recent_movements: StockMovement[]
}
