import { API_PATHS } from './paths'
import { get } from './http'

export interface ProductMovementItem {
  product_id: number
  sku_code: string
  name: string
  spec: string
  unit: string
  inbound_quantity: number
  outbound_quantity: number
  net_consumption: number
  current_quantity: number
  safe_stock: number
  suggested_purchase: number
}

export interface ProductMovement {
  start_date: string
  end_date: string
  warehouse_id: number | null
  formula: string
  items: ProductMovementItem[]
}

export function getProductMovement(params?: Record<string, unknown>) {
  return get<ProductMovement>(API_PATHS.productMovement, params)
}
