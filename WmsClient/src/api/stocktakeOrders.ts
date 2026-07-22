import { API_PATHS } from './paths'
import { get, post, put, del } from './http'
import type { Paginated, StocktakeOrder } from './types'

const base = API_PATHS.stocktakeOrders

export function listStocktakeOrders(params?: Record<string, unknown>) {
  return get<Paginated<StocktakeOrder>>(base, params)
}

export function getStocktakeOrder(id: number) {
  return get<StocktakeOrder>(`${base}/${id}`)
}

export function createStocktakeOrder(data: unknown) {
  return post<StocktakeOrder>(base, data)
}

export function updateStocktakeOrder(id: number, data: unknown) {
  return put<StocktakeOrder>(`${base}/${id}`, data)
}

export function submitStocktakeOrder(id: number) {
  return post<StocktakeOrder>(`${base}/${id}/submit`)
}

export function approveStocktakeOrder(id: number) {
  return post<StocktakeOrder>(`${base}/${id}/approve`)
}

export function rejectStocktakeOrder(id: number) {
  return post<StocktakeOrder>(`${base}/${id}/reject`)
}

export function cancelStocktakeOrder(id: number) {
  return post<StocktakeOrder>(`${base}/${id}/cancel`)
}

export function deleteStocktakeOrder(id: number) {
  return del(`${base}/${id}`)
}
