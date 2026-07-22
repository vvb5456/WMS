import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, UserRole } from '@/api/types'
import { login as apiLogin, fetchMe } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('wms_token') || '')
  const user = ref<User | null>(
    localStorage.getItem('wms_user') ? JSON.parse(localStorage.getItem('wms_user')!) : null
  )

  const isLoggedIn = computed(() => !!token.value)
  const role = computed(() => user.value?.role)

  function canEdit() {
    return role.value === 'admin' || role.value === 'warehouse_keeper'
  }

  function canOperateOrders() {
    return role.value === 'admin' || role.value === 'warehouse_keeper' || role.value === 'viewer'
  }

  function canApprove() {
    return role.value === 'admin' || role.value === 'warehouse_keeper'
  }

  function hasRole(...roles: UserRole[]) {
    return role.value ? roles.includes(role.value) || role.value === 'admin' : false
  }

  async function login(username: string, password: string) {
    const res = await apiLogin(username, password)
    token.value = res.token
    user.value = res.user
    localStorage.setItem('wms_token', res.token)
    localStorage.setItem('wms_user', JSON.stringify(res.user))
  }

  async function loadUser() {
    if (!token.value) return
    user.value = await fetchMe()
    localStorage.setItem('wms_user', JSON.stringify(user.value))
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('wms_token')
    localStorage.removeItem('wms_user')
  }

  return {
    token,
    user,
    isLoggedIn,
    role,
    canEdit,
    canOperateOrders,
    canApprove,
    hasRole,
    login,
    loadUser,
    logout,
  }
})
