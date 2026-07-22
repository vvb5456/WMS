import { API_PATHS } from './paths'
import { get, post, del } from './http'
import type { Location, Paginated } from './types'

export function listLocations(params?: Record<string, unknown>) {
  return get<Paginated<Location>>(API_PATHS.locations, params)
}

export function createLocation(data: Partial<Location>) {
  return post<Location>(API_PATHS.locations, data)
}

export function deleteLocation(id: number) {
  return del(`${API_PATHS.locations}/${id}`)
}
