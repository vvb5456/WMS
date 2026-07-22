import { API_PATHS } from './paths'
import { get, post } from './http'
import type { User } from './types'

export function login(username: string, password: string) {
  return post<{ token: string; user: User }>(API_PATHS.login, { username, password })
}

export function fetchMe() {
  return get<User>(API_PATHS.me)
}

export function changePassword(oldPassword: string, newPassword: string) {
  return post(`${API_PATHS.me}/change-password`, {
    old_password: oldPassword,
    new_password: newPassword,
  })
}
