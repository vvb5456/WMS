<template>
  <div v-loading="loading">
    <div class="toolbar">
      <h2>{{ isNew ? '新建出库单' : (order?.order_no ? `出库单 ${order.order_no}` : '出库单') }}</h2>
      <OrderStatusTag v-if="order" :status="order.status" />
    </div>
    <el-form label-width="90px" style="max-width: 600px">
      <el-form-item label="仓库">
        <el-select
          v-model="form.warehouse_id"
          :disabled="!editable"
          style="width: 100%"
          @change="onWarehouseChange"
        >
          <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="order" label="提出人">
        <span>{{ order.creator?.name || order.creator?.username || '-' }}</span>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" :disabled="!editable" type="textarea" />
      </el-form-item>
    </el-form>

    <OrderLineTable
      :lines="form.lines"
      :products="[]"
      :locations="[]"
      :inventory-items="inventoryItems"
      :editable="editable"
      mode="outbound"
      :show-actual="order?.status === 'submitted'"
    />

    <div class="actions">
      <el-button @click="$router.back()">返回</el-button>
      <template v-if="editable">
        <el-button type="primary" :loading="saving" @click="save">
          {{ isNew ? '提交' : '保存' }}
        </el-button>
        <el-button v-if="!isNew" type="success" @click="doSubmit">提交</el-button>
        <el-button v-if="!isNew" type="danger" @click="doDelete">删除</el-button>
      </template>
      <template v-if="order?.status === 'submitted' && auth.canApprove()">
        <el-button type="success" @click="doApprove">审核通过</el-button>
        <el-button @click="doReject">驳回</el-button>
        <el-button type="warning" @click="doCancel">取消</el-button>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  getOutboundOrder, createOutboundOrder, updateOutboundOrder,
  submitOutboundOrder, approveOutboundOrder, rejectOutboundOrder,
  cancelOutboundOrder, deleteOutboundOrder,
} from '@/api/outboundOrders'
import { listInventory } from '@/api/inventory'
import { listWarehouses } from '@/api/warehouses'
import { useAuthStore } from '@/state/auth'
import OrderStatusTag from '@/components/OrderStatusTag.vue'
import OrderLineTable from '@/components/OrderLineTable.vue'
import type { OutboundOrder, OrderLine, InventoryItem, Warehouse } from '@/api/types'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const isNew = computed(() => route.name === 'outbound-new')
const order = ref<OutboundOrder | null>(null)
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
      order.value = await getOutboundOrder(Number(route.params.id))
      form.warehouse_id = order.value.warehouse_id
      form.remark = order.value.remark || ''
      form.lines = order.value.lines || []
    } else {
      if (w.items.length) form.warehouse_id = w.items[0].id
      form.lines = []
    }
    await loadInventory()
  } finally {
    loading.value = false
  }
})

async function loadInventory() {
  if (!form.warehouse_id) {
    inventoryItems.value = []
    return
  }
  const res = await listInventory({
    warehouse_id: form.warehouse_id,
    in_stock: 1,
    per_page: 100,
  })
  inventoryItems.value = res.items
}

function onWarehouseChange() {
  if (editable.value) form.lines = []
  loadInventory()
}

async function save() {
  saving.value = true
  try {
    if (isNew.value) {
      const created = await createOutboundOrder(form)
      await submitOutboundOrder(created.id)
      router.replace(`/outbound/${created.id}`)
    } else {
      await updateOutboundOrder(Number(route.params.id), form)
      order.value = await getOutboundOrder(Number(route.params.id))
    }
  } finally {
    saving.value = false
  }
}

async function doSubmit() {
  await submitOutboundOrder(Number(route.params.id))
  order.value = await getOutboundOrder(Number(route.params.id))
}
async function doApprove() {
  await approveOutboundOrder(Number(route.params.id))
  order.value = await getOutboundOrder(Number(route.params.id))
}
async function doReject() {
  await rejectOutboundOrder(Number(route.params.id))
  order.value = await getOutboundOrder(Number(route.params.id))
}
async function doCancel() {
  await cancelOutboundOrder(Number(route.params.id))
  order.value = await getOutboundOrder(Number(route.params.id))
}
async function doDelete() {
  await deleteOutboundOrder(Number(route.params.id))
  router.push('/outbound')
}
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.actions { margin-top: 20px; display: flex; gap: 8px; }
</style>
