import { API_PATHS } from './paths'
import { del, get, post } from './http'
import type { Paginated, User, UserRole } from './types'

export interface CreateUserPayload {
  username: string
  name: string
  password: string
  role: UserRole
}

export function listUsers(params?: Record<string, unknown>) {
  return get<Paginated<User>>(API_PATHS.users, params)
}

export function createUser(data: CreateUserPayload) {
  return post<User>(API_PATHS.users, data)
}

export function resetUserPassword(id: number) {
  return post(`${API_PATHS.users}/${id}/reset-password`)
}

export function deleteUser(id: number) {
  return del(`${API_PATHS.users}/${id}`)
}
