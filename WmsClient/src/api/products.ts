import { API_PATHS } from './paths'
import { get, post, put, del } from './http'
import type { Paginated, Product } from './types'

export function listProducts(params?: Record<string, unknown>) {
  return get<Paginated<Product>>(API_PATHS.products, params)
}

export function suggestProductCode() {
  return get<{ sku_code: string }>(`${API_PATHS.products}/suggest-code`)
}

export function createProduct(data: Partial<Product>) {
  return post<Product>(API_PATHS.products, data)
}

export function updateProduct(id: number, data: Partial<Product>) {
  return put<Product>(`${API_PATHS.products}/${id}`, data)
}

export function deleteProduct(id: number) {
  return del(`${API_PATHS.products}/${id}`)
}
