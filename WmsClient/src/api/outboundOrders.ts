import { API_PATHS } from './paths'
import { get, post, put, del } from './http'
import type { OutboundOrder, Paginated } from './types'

const base = API_PATHS.outboundOrders

export function listOutboundOrders(params?: Record<string, unknown>) {
  return get<Paginated<OutboundOrder>>(base, params)
}

export function getOutboundOrder(id: number) {
  return get<OutboundOrder>(`${base}/${id}`)
}

export function createOutboundOrder(data: unknown) {
  return post<OutboundOrder>(base, data)
}

export function updateOutboundOrder(id: number, data: unknown) {
  return put<OutboundOrder>(`${base}/${id}`, data)
}

export function submitOutboundOrder(id: number) {
  return post<OutboundOrder>(`${base}/${id}/submit`)
}

export function approveOutboundOrder(id: number) {
  return post<OutboundOrder>(`${base}/${id}/approve`)
}

export function rejectOutboundOrder(id: number) {
  return post<OutboundOrder>(`${base}/${id}/reject`)
}

export function cancelOutboundOrder(id: number) {
  return post<OutboundOrder>(`${base}/${id}/cancel`)
}

export function deleteOutboundOrder(id: number) {
  return del(`${base}/${id}`)
}
