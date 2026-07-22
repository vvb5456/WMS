export type OrderStatus = 'draft' | 'submitted' | 'approved' | 'completed' | 'cancelled'
export type UserRole = 'admin' | 'warehouse_keeper' | 'viewer'

export interface ApiResponse<T = unknown> {
  success: boolean
  code: string
  message: string
  data: T
  errors?: Record<string, string[]>
}

export interface Paginated<T> {
  items: T[]
  page: number
  per_page: number
  total: number
}

export interface User {
  id: number
  username: string
  name: string
  role: UserRole
  is_active: boolean
  last_login_at?: string | null
}

export interface Product {
  id: number
  sku_code: string
  name: string
  spec: string
  unit: string
  barcode?: string
  safe_stock: number
  is_active: boolean
}

export interface Warehouse {
  id: number
  code: string
  name: string
  address?: string
  is_active: boolean
}

export interface Location {
  id: number
  warehouse_id: number
  code: string
  name?: string
  is_active: boolean
}

export interface InventoryItem {
  id: number
  product_id: number
  warehouse_id: number
  location_id: number
  quantity: number
  product?: Product
  warehouse?: Warehouse
  location?: Location
  safe_stock?: number
}

export interface InventoryTransaction {
  id: number
  product_id: number
  delta_qty: number
  balance_after: number
  ref_type: string
  ref_id: number
  created_at: string
  product?: Product
  warehouse?: Warehouse
  location?: Location
}

export interface OrderLine {
  id?: number
  product_id?: number
  location_id?: number
  planned_qty?: number
  actual_qty?: number
  counted_qty?: number
  book_qty?: number
  diff_qty?: number
  product?: Product
  location?: Location
}

export interface BaseOrder {
  id: number
  order_no: string
  warehouse_id: number
  status: OrderStatus
  remark?: string
  created_at: string
  warehouse?: Warehouse
  creator?: User
  approver?: User
  lines?: OrderLine[]
}

export interface InboundOrder extends BaseOrder {
  supplier_name?: string
}

export interface OutboundOrder extends BaseOrder {
  customer_name?: string
}

export interface StocktakeOrder extends BaseOrder {}
