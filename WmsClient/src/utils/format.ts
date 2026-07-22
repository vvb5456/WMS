import type { OrderStatus } from '@/api/types'

export function formatQty(val: number | undefined | null): string {
  if (val == null) return '0'
  return Number(val).toLocaleString('zh-CN', { maximumFractionDigits: 3 })
}

/** 将后端 UTC 时间格式化为本地 YYYY-MM-DD HH:mm:ss */
export function formatDateTime(val: string | null | undefined): string {
  if (!val) return '-'
  const raw = val.trim()
  const hasTimezone = /(?:[zZ]|[+-]\d{2}:?\d{2})$/.test(raw)
  const normalized = hasTimezone ? raw : `${raw}Z`
  const date = new Date(normalized)
  if (Number.isNaN(date.getTime())) return val

  const pad = (n: number) => String(n).padStart(2, '0')
  return [
    date.getFullYear(),
    '-',
    pad(date.getMonth() + 1),
    '-',
    pad(date.getDate()),
    ' ',
    pad(date.getHours()),
    ':',
    pad(date.getMinutes()),
    ':',
    pad(date.getSeconds()),
  ].join('')
}

const STATUS_MAP: Record<OrderStatus, { label: string; type: string }> = {
  draft: { label: '草稿', type: 'info' },
  submitted: { label: '待审核', type: 'warning' },
  approved: { label: '已审核', type: 'primary' },
  completed: { label: '已完成', type: 'success' },
  cancelled: { label: '已取消', type: 'danger' },
}

export function orderStatusMeta(status: OrderStatus) {
  return STATUS_MAP[status] || { label: status, type: 'info' }
}
