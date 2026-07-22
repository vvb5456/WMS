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

    <el-card class="trend-card" v-loading="trendLoading">
      <template #header>
        <div class="trend-header">
          <div class="trend-title">
            <span>出入库数量趋势</span>
            <span v-if="selectedProduct" class="trend-subtitle">
              {{ selectedProduct.sku_code }} · {{ selectedProduct.name }}
            </span>
          </div>
          <el-form inline class="trend-filters">
            <el-form-item label="日期">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                value-format="YYYY-MM-DD"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                :clearable="false"
                @change="loadTrend"
              />
            </el-form-item>
            <el-form-item label="仓库">
              <el-select
                v-model="warehouseId"
                clearable
                placeholder="全部仓库"
                style="width: 180px"
                @change="onWarehouseChange"
              >
                <el-option
                  v-for="warehouse in warehouses"
                  :key="warehouse.id"
                  :label="warehouse.name"
                  :value="warehouse.id"
                />
              </el-select>
            </el-form-item>
            <el-form-item label="产品" required>
              <el-select
                v-model="productId"
                filterable
                :loading="productLoading"
                placeholder="请选择产品"
                style="width: 220px"
                @change="loadTrend"
              >
                <el-option
                  v-for="product in products"
                  :key="product.id"
                  :label="`${product.sku_code} - ${product.name}`"
                  :value="product.id"
                />
              </el-select>
            </el-form-item>
          </el-form>
        </div>
      </template>

      <div v-if="!productId" class="trend-empty">请选择产品后查看出入库数量趋势</div>
      <template v-else>
        <div class="trend-summary">
          <span>入库合计：{{ formatQty(chart.inboundTotal) }}</span>
          <span>出库合计：{{ formatQty(chart.outboundTotal) }}</span>
        </div>
        <div class="trend-chart">
          <svg
            viewBox="0 0 1000 320"
            role="img"
            :aria-label="`${selectedProductLabel}出入库数量趋势图`"
            preserveAspectRatio="none"
          >
            <g class="chart-legend">
              <circle cx="410" cy="14" r="5" class="inbound-fill" />
              <text x="422" y="19">入库数量</text>
              <circle cx="510" cy="14" r="5" class="outbound-fill" />
              <text x="522" y="19">出库数量</text>
            </g>
            <g v-for="tick in chart.yTicks" :key="tick.value">
              <line x1="64" :y1="tick.y" x2="976" :y2="tick.y" class="grid-line" />
              <text x="56" :y="tick.y + 4" text-anchor="end" class="axis-label">
                {{ formatQty(tick.value) }}
              </text>
            </g>
            <polyline :points="chart.inboundPoints" class="trend-line inbound-line" />
            <polyline :points="chart.outboundPoints" class="trend-line outbound-line" />
            <template v-if="chart.showPoints">
              <circle
                v-for="point in chart.inboundDots"
                :key="`in-${point.date}`"
                :cx="point.x"
                :cy="point.y"
                r="4"
                class="inbound-fill"
              >
                <title>{{ point.date }} 入库：{{ formatQty(point.value) }}</title>
              </circle>
              <circle
                v-for="point in chart.outboundDots"
                :key="`out-${point.date}`"
                :cx="point.x"
                :cy="point.y"
                r="4"
                class="outbound-fill"
              >
                <title>{{ point.date }} 出库：{{ formatQty(point.value) }}</title>
              </circle>
            </template>
            <text
              v-for="label in chart.xLabels"
              :key="label.date"
              :x="label.x"
              y="304"
              text-anchor="middle"
              class="axis-label"
            >
              {{ label.date.slice(5) }}
            </text>
          </svg>
        </div>
        <div v-if="!chart.hasData" class="trend-empty soft">当前筛选条件下暂无出入库流水</div>
      </template>
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
import { computed, onMounted, ref } from 'vue'
import { getInventoryTrend, type InventoryTrendItem } from '@/api/dashboard'
import { listInventory, listAlerts } from '@/api/inventory'
import { listInboundOrders } from '@/api/inboundOrders'
import { listProducts } from '@/api/products'
import { listWarehouses } from '@/api/warehouses'
import { formatQty } from '@/utils/format'
import type { InventoryItem, Product, Warehouse } from '@/api/types'

const loading = ref(false)
const trendLoading = ref(false)
const inventoryCount = ref(0)
const pendingInbound = ref(0)
const alertCount = ref(0)
const alerts = ref<InventoryItem[]>([])
const warehouses = ref<Warehouse[]>([])
const products = ref<Product[]>([])
const warehouseId = ref<number>()
const productId = ref<number>()
const productLoading = ref(false)
const trendItems = ref<InventoryTrendItem[]>([])

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

const selectedProduct = computed(() => products.value.find((item) => item.id === productId.value))
const selectedProductLabel = computed(() => {
  if (!selectedProduct.value) return ''
  return `${selectedProduct.value.sku_code} ${selectedProduct.value.name}`
})

async function loadProducts(preferProductId?: number) {
  productLoading.value = true
  try {
    const result = await listProducts({
      per_page: 100,
      warehouse_id: warehouseId.value,
    })
    products.value = result.items
    const preferred = preferProductId && result.items.some((item) => item.id === preferProductId)
      ? preferProductId
      : result.items[0]?.id
    productId.value = preferred
  } finally {
    productLoading.value = false
  }
}

async function onWarehouseChange() {
  await loadProducts()
  await loadTrend()
}

const chart = computed(() => {
  const items = trendItems.value
  const left = 64
  const right = 976
  const top = 30
  const bottom = 276
  const inboundTotal = items.reduce((sum, item) => sum + item.inbound_quantity, 0)
  const outboundTotal = items.reduce((sum, item) => sum + item.outbound_quantity, 0)
  const maxQuantity = Math.max(
    1,
    ...items.flatMap((item) => [item.inbound_quantity, item.outbound_quantity]),
  )
  const niceMax = Math.max(4, Math.ceil(maxQuantity / 4) * 4)
  const x = (index: number) => {
    if (items.length <= 1) return (left + right) / 2
    return left + (index / (items.length - 1)) * (right - left)
  }
  const y = (value: number) => bottom - (value / niceMax) * (bottom - top)
  const inboundDots = items.map((item, index) => ({
    x: x(index),
    y: y(item.inbound_quantity),
    date: item.date,
    value: item.inbound_quantity,
  }))
  const outboundDots = items.map((item, index) => ({
    x: x(index),
    y: y(item.outbound_quantity),
    date: item.date,
    value: item.outbound_quantity,
  }))
  const labelStep = Math.max(1, Math.ceil(items.length / 10))

  return {
    inboundTotal,
    outboundTotal,
    hasData: inboundTotal > 0 || outboundTotal > 0,
    yTicks: Array.from({ length: 5 }, (_, index) => {
      const value = (niceMax / 4) * index
      return { value, y: y(value) }
    }),
    inboundPoints: inboundDots.map((point) => `${point.x},${point.y}`).join(' '),
    outboundPoints: outboundDots.map((point) => `${point.x},${point.y}`).join(' '),
    inboundDots,
    outboundDots,
    showPoints: items.length <= 31,
    xLabels: items
      .map((item, index) => ({ date: item.date, x: x(index), index }))
      .filter((item, index) => index % labelStep === 0 || index === items.length - 1),
  }
})

async function loadTrend() {
  if (!productId.value || dateRange.value.length !== 2) {
    trendItems.value = []
    return
  }
  trendLoading.value = true
  try {
    const trend = await getInventoryTrend({
      start_date: dateRange.value[0],
      end_date: dateRange.value[1],
      warehouse_id: warehouseId.value,
      product_id: productId.value,
    })
    trendItems.value = trend.items
  } finally {
    trendLoading.value = false
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
    await loadProducts()
  } finally {
    loading.value = false
  }
  await loadTrend()
})
</script>

<style scoped>
.stat-title { color: #666; font-size: 14px; }
.stat-value { font-size: 28px; font-weight: 600; margin-top: 8px; }
.stat-value.warn { color: #e6a23c; }
.trend-card { margin-bottom: 20px; }
.trend-header { display: flex; justify-content: space-between; align-items: center; gap: 16px; }
.trend-title { display: flex; flex-direction: column; gap: 4px; }
.trend-subtitle { color: #909399; font-size: 13px; }
.trend-filters { margin-bottom: -18px; }
.trend-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 8px;
  color: #606266;
  font-size: 14px;
}
.trend-chart { width: 100%; height: 360px; }
.trend-chart svg { width: 100%; height: 100%; overflow: visible; }
.trend-empty {
  padding: 48px 0;
  text-align: center;
  color: #909399;
}
.trend-empty.soft {
  padding: 0 0 12px;
}
.grid-line { stroke: #e5e7eb; stroke-width: 1; }
.axis-label, .chart-legend { fill: #606266; font-size: 12px; }
.trend-line { fill: none; stroke-width: 3; stroke-linejoin: round; stroke-linecap: round; }
.inbound-line { stroke: #67c23a; }
.outbound-line { stroke: #409eff; }
.inbound-fill { fill: #67c23a; }
.outbound-fill { fill: #409eff; }

@media (max-width: 1000px) {
  .trend-header { align-items: flex-start; flex-direction: column; }
}
</style>
