<template>
  <div>
    <h2>首页看板</h2>
    <el-row :gutter="16" style="margin-bottom: 20px">
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-title">库存编码数</div>
          <div class="stat-value">{{ inventoryCount }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-title">待审入库单</div>
          <div class="stat-value">{{ pendingInbound }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card shadow="hover">
          <div class="stat-title">安全库存预警</div>
          <div class="stat-value warn">{{ alertCount }}</div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="movement-card" v-loading="movementLoading">
      <template #header>
        <div class="movement-header">
          <div class="movement-title">
            <span>周期出入库汇总</span>
            <span class="movement-subtitle">
              入/出库合计按所选日期统计；当前库存、安全库存为实时值
            </span>
          </div>
          <div class="movement-actions">
            <el-form inline class="movement-filters">
              <el-form-item label="日期">
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  value-format="YYYY-MM-DD"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  :clearable="false"
                />
              </el-form-item>
              <el-form-item label="仓库">
                <el-select
                  v-model="warehouseId"
                  clearable
                  placeholder="全部仓库"
                  style="width: 180px"
                >
                  <el-option
                    v-for="warehouse in warehouses"
                    :key="warehouse.id"
                    :label="warehouse.name"
                    :value="warehouse.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="movementLoading" @click="loadMovement">
                  查询
                </el-button>
              </el-form-item>
            </el-form>
            <el-dropdown :disabled="!items.length" @command="onExport">
              <el-button :disabled="!items.length">
                导出
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="csv">导出 CSV</el-dropdown-item>
                  <el-dropdown-item command="excel">导出 Excel</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>

      <el-table :data="items" size="small" empty-text="当前筛选条件下暂无出入库流水">
        <el-table-column prop="sku_code" label="编码" min-width="120" />
        <el-table-column prop="name" label="产品" min-width="160" />
        <el-table-column prop="unit" label="单位" width="70" />
        <el-table-column label="入库合计" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.inbound_quantity) }}</template>
        </el-table-column>
        <el-table-column label="出库合计" width="100" align="right" sortable :sort-method="sortByOutbound">
          <template #default="{ row }">{{ formatQty(row.outbound_quantity) }}</template>
        </el-table-column>
        <el-table-column label="当前库存" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.current_quantity) }}</template>
        </el-table-column>
        <el-table-column label="安全库存" width="100" align="right">
          <template #default="{ row }">{{ formatQty(row.safe_stock) }}</template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card header="库存预警">
      <el-table :data="alerts" size="small" v-loading="loading">
        <el-table-column prop="product.sku_code" label="编码" />
        <el-table-column prop="product.name" label="商品" />
        <el-table-column prop="warehouse.name" label="仓库" />
        <el-table-column prop="location.code" label="库位" />
        <el-table-column label="现存量" width="100">
          <template #default="{ row }">
            <span>{{ formatQty(row.quantity) }}</span>
            <el-tag v-if="row.quantity <= 0" type="danger" size="small" style="margin-left: 4px">缺货</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="安全库存">
          <template #default="{ row }">{{ formatQty(row.safe_stock) }}</template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { getProductMovement, type ProductMovementItem } from '@/api/dashboard'
import { listInventory, listAlerts } from '@/api/inventory'
import { listInboundOrders } from '@/api/inboundOrders'
import { listWarehouses } from '@/api/warehouses'
import { exportCsv, exportExcel, type ExportColumn } from '@/utils/exportTable'
import { formatQty } from '@/utils/format'
import type { InventoryItem, Warehouse } from '@/api/types'

const loading = ref(false)
const movementLoading = ref(false)
const inventoryCount = ref(0)
const pendingInbound = ref(0)
const alertCount = ref(0)
const alerts = ref<InventoryItem[]>([])
const warehouses = ref<Warehouse[]>([])
const warehouseId = ref<number>()
const items = ref<ProductMovementItem[]>([])

function formatDate(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const today = new Date()
const sevenDaysAgo = new Date(today)
sevenDaysAgo.setDate(today.getDate() - 6)
const dateRange = ref<[string, string]>([formatDate(sevenDaysAgo), formatDate(today)])

function sortByOutbound(a: ProductMovementItem, b: ProductMovementItem) {
  return a.outbound_quantity - b.outbound_quantity
}

const exportColumns: ExportColumn<ProductMovementItem>[] = [
  { key: 'sku_code', label: '编码' },
  { key: 'name', label: '产品' },
  { key: 'unit', label: '单位' },
  { key: 'inbound_quantity', label: '入库合计' },
  { key: 'outbound_quantity', label: '出库合计' },
  { key: 'current_quantity', label: '当前库存' },
  { key: 'safe_stock', label: '安全库存' },
]

function exportFilename(ext: string) {
  const [start, end] = dateRange.value
  const warehouse = warehouses.value.find((item) => item.id === warehouseId.value)
  const whPart = warehouse ? `_${warehouse.name}` : '_全部仓库'
  return `周期出入库汇总_${start}_${end}${whPart}.${ext}`
}

function onExport(command: string) {
  if (!items.value.length) return
  if (command === 'csv') {
    exportCsv(exportFilename('csv'), exportColumns, items.value)
    return
  }
  if (command === 'excel') {
    exportExcel(exportFilename('xls'), exportColumns, items.value)
  }
}

async function loadMovement() {
  if (!dateRange.value || dateRange.value.length !== 2) {
    items.value = []
    return
  }
  movementLoading.value = true
  try {
    const params: Record<string, unknown> = {
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
    }
    if (warehouseId.value) {
      params.warehouse_id = warehouseId.value
    }
    const result = await getProductMovement(params)
    items.value = result.items
  } finally {
    movementLoading.value = false
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const [inv, inbound, alertList, warehouseList] = await Promise.all([
      listInventory({ per_page: 1, in_stock: 1 }),
      listInboundOrders({ status: 'submitted', per_page: 1 }),
      listAlerts(),
      listWarehouses({ per_page: 100 }),
    ])
    inventoryCount.value = inv.total
    pendingInbound.value = inbound.total
    alerts.value = alertList
    alertCount.value = alertList.length
    warehouses.value = warehouseList.items.filter((warehouse) => warehouse.is_active)
  } finally {
    loading.value = false
  }
  await loadMovement()
})
</script>

<style scoped>
.stat-title { color: #666; font-size: 14px; }
.stat-value { font-size: 28px; font-weight: 600; margin-top: 8px; }
.stat-value.warn { color: #e6a23c; }
.movement-card { margin-bottom: 20px; }
.movement-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}
.movement-title { display: flex; flex-direction: column; gap: 4px; }
.movement-subtitle { color: #909399; font-size: 13px; }
.movement-actions {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}
.movement-filters { margin-bottom: -18px; }
@media (max-width: 1000px) {
  .movement-header { flex-direction: column; }
}
</style>
