<template>
  <div>
    <el-tabs v-model="tab">
      <el-tab-pane label="现存量" name="stock">
        <el-table :data="inventory" v-loading="loading" border>
          <el-table-column prop="product.sku_code" label="编码" width="120" />
          <el-table-column prop="product.name" label="商品" />
          <el-table-column prop="location.code" label="库位" width="100" />
          <el-table-column label="数量" width="100">
            <template #default="{ row }">{{ formatQty(row.quantity) }} {{ row.product?.unit }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
      <el-tab-pane label="库存流水" name="tx">
        <el-table :data="transactions" v-loading="txLoading" border>
          <el-table-column label="时间" width="180">
            <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
          </el-table-column>
          <el-table-column prop="product.sku_code" label="编码" width="120" />
          <el-table-column prop="location.code" label="库位" width="100" />
          <el-table-column label="变动" width="100">
            <template #default="{ row }">
              <span :style="{ color: row.delta_qty >= 0 ? '#67c23a' : '#f56c6c' }">
                {{ row.delta_qty >= 0 ? '+' : '' }}{{ formatQty(row.delta_qty) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="余额" width="100">
            <template #default="{ row }">{{ formatQty(row.balance_after) }}</template>
          </el-table-column>
          <el-table-column prop="ref_type" label="来源" width="100" />
          <el-table-column prop="remark" label="备注" />
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { listInventory, listTransactions } from '@/api/inventory'
import { formatDateTime, formatQty } from '@/utils/format'
import type { InventoryItem, InventoryTransaction } from '@/api/types'

const tab = ref('stock')
const loading = ref(false)
const txLoading = ref(false)
const inventory = ref<InventoryItem[]>([])
const transactions = ref<InventoryTransaction[]>([])

async function loadInventory() {
  loading.value = true
  try {
    const res = await listInventory({ per_page: 100, in_stock: 1 })
    inventory.value = res.items
  } finally {
    loading.value = false
  }
}

async function loadTransactions() {
  txLoading.value = true
  try {
    const res = await listTransactions({ per_page: 100 })
    transactions.value = res.items
  } finally {
    txLoading.value = false
  }
}

watch(tab, (v) => { if (v === 'tx' && !transactions.value.length) loadTransactions() })
onMounted(loadInventory)
</script>
