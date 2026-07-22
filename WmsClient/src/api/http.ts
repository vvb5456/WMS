import axios, { type AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from './types'

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api/v1',
  timeout: 30000,
})

http.interceptors.request.use((config) => {
  const url = config.url || ''
  const isLogin = url.endsWith('/login')
  const token = localStorage.getItem('wms_token')
  if (token && !isLogin) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (res) => {
    const body = res.data as ApiResponse
    if (body && body.success === false) {
      ElMessage.error(body.message || '请求失败')
      return Promise.reject(body)
    }
    return res
  },
  (err: AxiosError<ApiResponse>) => {
    const body = err.response?.data
    const msg = body?.message || err.message || '网络错误'
    if (err.response?.status === 401) {
      localStorage.removeItem('wms_token')
      localStorage.removeItem('wms_user')
      if (location.pathname.includes('/login')) {
        ElMessage.error(msg)
      } else {
        location.href = '/login'
      }
    } else {
      ElMessage.error(msg)
    }
    return Promise.reject(body || err)
  }
)

export async function get<T>(url: string, params?: Record<string, unknown>) {
  const res = await http.get<ApiResponse<T>>(url, { params })
  return res.data.data
}

export async function post<T>(url: string, data?: unknown) {
  const res = await http.post<ApiResponse<T>>(url, data)
  const body = res.data
  if (body.message && body.message !== '操作成功') {
    ElMessage.success(body.message)
  }
  return body.data
}

export async function put<T>(url: string, data?: unknown) {
  const res = await http.put<ApiResponse<T>>(url, data)
  return res.data.data
}

export async function del<T>(url: string) {
  const res = await http.delete<ApiResponse<T>>(url)
  return res.data.data
}

export default http
