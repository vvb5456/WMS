<template>
  <div>
    <div class="toolbar">
      <h2>出库单</h2>
      <el-button v-if="auth.canOperateOrders()" type="primary" @click="$router.push('/outbound/new')">新建出库单</el-button>
    </div>
    <el-table :data="items" v-loading="loading" border @row-click="(row: OutboundOrder) => $router.push(`/outbound/${row.id}`)">
      <el-table-column prop="order_no" label="单号" width="160" />
      <el-table-column prop="warehouse.name" label="仓库" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }"><OrderStatusTag :status="row.status" /></template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { listOutboundOrders } from '@/api/outboundOrders'
import { useAuthStore } from '@/state/auth'
import OrderStatusTag from '@/components/OrderStatusTag.vue'
import { formatDateTime } from '@/utils/format'
import type { OutboundOrder } from '@/api/types'

const auth = useAuthStore()
const items = ref<OutboundOrder[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await listOutboundOrders({ per_page: 100 })
    items.value = res.items
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
:deep(.el-table__row) { cursor: pointer; }
</style>
