import { API_PATHS } from './paths'
import { get } from './http'
import type { InventoryItem, InventoryTransaction, Paginated } from './types'

export function listInventory(params?: Record<string, unknown>) {
  return get<Paginated<InventoryItem>>(API_PATHS.inventory, params)
}

export function listTransactions(params?: Record<string, unknown>) {
  return get<Paginated<InventoryTransaction>>(API_PATHS.inventoryTransactions, params)
}

export function listAlerts() {
  return get<InventoryItem[]>(API_PATHS.inventoryAlerts)
}
