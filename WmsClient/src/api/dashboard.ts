import { API_PATHS } from './paths'
import { get } from './http'

export interface InventoryTrendItem {
  date: string
  inbound_quantity: number
  outbound_quantity: number
}

export interface InventoryTrend {
  start_date: string
  end_date: string
  warehouse_id: number | null
  product_id: number | null
  items: InventoryTrendItem[]
}

export function getInventoryTrend(params?: Record<string, unknown>) {
  return get<InventoryTrend>(API_PATHS.inventoryTrend, params)
}
