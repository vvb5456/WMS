<template>
  <div v-loading="loading">
    <div class="toolbar">
      <h2>{{ isNew ? '新建盘点单' : `盘点单 ${order?.order_no}` }}</h2>
      <OrderStatusTag v-if="order" :status="order.status" />
    </div>
    <el-form label-width="90px" style="max-width: 600px">
      <el-form-item label="仓库">
        <el-select v-model="form.warehouse_id" :disabled="!editable" style="width: 100%" @change="onWarehouseChange">
          <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" :disabled="!editable" type="textarea" />
      </el-form-item>
    </el-form>

    <div v-if="editable" class="line-toolbar">
      <el-button type="primary" plain :disabled="!form.warehouse_id" @click="generateFromInventory">
        按库存生成明细
      </el-button>
      <span class="hint">按当前仓库有库存的「商品 + 库位」生成盘点行，实盘默认等于账面，按实盘结果改即可</span>
    </div>

    <OrderLineTable
      :lines="form.lines"
      :products="[]"
      :locations="[]"
      :inventory-items="inventoryItems"
      :editable="editable"
      mode="stocktake"
    />

    <div class="actions">
      <el-button @click="$router.back()">返回</el-button>
      <template v-if="editable">
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
        <el-button v-if="!isNew" type="success" @click="doSubmit">提交</el-button>
        <el-button v-if="!isNew" type="danger" @click="doDelete">删除</el-button>
      </template>
      <template v-if="order?.status === 'submitted' && auth.canApprove()">
        <el-button type="success" @click="doApprove">审核过账</el-button>
        <el-button @click="doReject">驳回</el-button>
        <el-button type="warning" @click="doCancel">取消</el-button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getStocktakeOrder, createStocktakeOrder, updateStocktakeOrder,
  submitStocktakeOrder, approveStocktakeOrder, rejectStocktakeOrder,
  cancelStocktakeOrder, deleteStocktakeOrder,
} from '@/api/stocktakeOrders'
import { listWarehouses } from '@/api/warehouses'
import { listInventory } from '@/api/inventory'
import { useAuthStore } from '@/state/auth'
import OrderStatusTag from '@/components/OrderStatusTag.vue'
import OrderLineTable from '@/components/OrderLineTable.vue'
import type { StocktakeOrder, OrderLine, Warehouse, InventoryItem } from '@/api/types'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const isNew = computed(() => route.name === 'stocktake-new')
const order = ref<StocktakeOrder | null>(null)
const loading = ref(false)
const saving = ref(false)
const warehouses = ref<Warehouse[]>([])
const inventoryItems = ref<InventoryItem[]>([])
const form = reactive({ warehouse_id: 0, remark: '', lines: [] as OrderLine[] })
const editable = computed(() => isNew.value || order.value?.status === 'draft')

onMounted(async () => {
  loading.value = true
  try {
    const w = await listWarehouses({ per_page: 100 })
    warehouses.value = w.items
    if (!isNew.value) {
      order.value = await getStocktakeOrder(Number(route.params.id))
      form.warehouse_id = order.value.warehouse_id
      form.remark = order.value.remark || ''
      form.lines = order.value.lines || []
      await loadInventory()
    } else {
      if (w.items.length) form.warehouse_id = w.items[0].id
      await loadInventory()
      fillLinesFromInventory()
    }
  } finally {
    loading.value = false
  }
})

async function loadInventory() {
  if (!form.warehouse_id) {
    inventoryItems.value = []
    return
  }
  const items: InventoryItem[] = []
  let page = 1
  while (true) {
    const res = await listInventory({
      warehouse_id: form.warehouse_id,
      in_stock: 1,
      per_page: 100,
      page,
    })
    items.push(...res.items)
    if (items.length >= res.total || res.items.length === 0) break
    page += 1
  }
  inventoryItems.value = items
}

function fillLinesFromInventory() {
  form.lines = inventoryItems.value.map((item) => ({
    product_id: item.product_id,
    location_id: item.location_id,
    book_qty: item.quantity,
    counted_qty: item.quantity,
    product: item.product,
    location: item.location,
  }))
}

async function generateFromInventory() {
  if (!form.warehouse_id) {
    ElMessage.warning('请先选择仓库')
    return
  }
  if (form.lines.length) {
    await ElMessageBox.confirm('将用当前库存覆盖已有明细，是否继续？', '按库存生成', {
      type: 'warning',
    })
  }
  await loadInventory()
  fillLinesFromInventory()
  if (!form.lines.length) {
    ElMessage.warning('该仓库暂无库存可盘点')
  } else {
    ElMessage.success(`已生成 ${form.lines.length} 条盘点明细`)
  }
}

async function onWarehouseChange() {
  if (!editable.value) return
  form.lines = []
  await loadInventory()
  fillLinesFromInventory()
}

async function save() {
  saving.value = true
  try {
    if (isNew.value) {
      const created = await createStocktakeOrder(form)
      router.replace(`/stocktake/${created.id}`)
    } else {
      await updateStocktakeOrder(Number(route.params.id), form)
      order.value = await getStocktakeOrder(Number(route.params.id))
    }
  } finally {
    saving.value = false
  }
}

async function doSubmit() {
  await submitStocktakeOrder(Number(route.params.id))
  order.value = await getStocktakeOrder(Number(route.params.id))
}
async function doApprove() {
  await approveStocktakeOrder(Number(route.params.id))
  order.value = await getStocktakeOrder(Number(route.params.id))
}
async function doReject() {
  await rejectStocktakeOrder(Number(route.params.id))
  order.value = await getStocktakeOrder(Number(route.params.id))
}
async function doCancel() {
  await cancelStocktakeOrder(Number(route.params.id))
  order.value = await getStocktakeOrder(Number(route.params.id))
}
async function doDelete() {
  await deleteStocktakeOrder(Number(route.params.id))
  router.push('/stocktake')
}
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.line-toolbar { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; flex-wrap: wrap; }
.hint { color: #909399; font-size: 13px; }
.actions { margin-top: 20px; display: flex; gap: 8px; }
</style>
