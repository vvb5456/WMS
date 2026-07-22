import { API_PATHS } from './paths'
import { get, post, put } from './http'
import type { Paginated, Warehouse } from './types'

export function listWarehouses(params?: Record<string, unknown>) {
  return get<Paginated<Warehouse>>(API_PATHS.warehouses, params)
}

export function createWarehouse(data: Partial<Warehouse>) {
  return post<Warehouse>(API_PATHS.warehouses, data)
}

export function updateWarehouse(id: number, data: Partial<Warehouse>) {
  return put<Warehouse>(`${API_PATHS.warehouses}/${id}`, data)
}
