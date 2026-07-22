import { API_PATHS } from './paths'
import { get, post, put, del } from './http'
import type { InboundOrder, Paginated } from './types'

const base = API_PATHS.inboundOrders

export function listInboundOrders(params?: Record<string, unknown>) {
  return get<Paginated<InboundOrder>>(base, params)
}

export function getInboundOrder(id: number) {
  return get<InboundOrder>(`${base}/${id}`)
}

export function createInboundOrder(data: unknown) {
  return post<InboundOrder>(base, data)
}

export function updateInboundOrder(id: number, data: unknown) {
  return put<InboundOrder>(`${base}/${id}`, data)
}

export function submitInboundOrder(id: number) {
  return post<InboundOrder>(`${base}/${id}/submit`)
}

export function approveInboundOrder(id: number) {
  return post<InboundOrder>(`${base}/${id}/approve`)
}

export function rejectInboundOrder(id: number) {
  return post<InboundOrder>(`${base}/${id}/reject`)
}

export function cancelInboundOrder(id: number) {
  return post<InboundOrder>(`${base}/${id}/cancel`)
}

export function deleteInboundOrder(id: number) {
  return del(`${base}/${id}`)
}
