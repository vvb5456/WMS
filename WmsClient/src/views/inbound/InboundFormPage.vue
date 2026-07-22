<template>
  <div v-loading="loading">
    <div class="toolbar">
      <h2>{{ isNew ? '新建入库单' : (order?.order_no ? `入库单 ${order.order_no}` : '入库单') }}</h2>
      <OrderStatusTag v-if="order" :status="order.status" />
    </div>
    <el-form label-width="90px" style="max-width: 600px">
      <el-form-item label="仓库">
        <el-select v-model="form.warehouse_id" :disabled="!editable" style="width: 100%">
          <el-option v-for="w in warehouses" :key="w.id" :label="w.name" :value="w.id" />
        </el-select>
      </el-form-item>
      <el-form-item v-if="order" label="提出人">
        <span>{{ order.creator?.name || order.creator?.username || '-' }}</span>
      </el-form-item>
      <el-form-item v-if="order?.approver" label="审核人">
        <span>{{ order.approver.name || order.approver.username }}</span>
      </el-form-item>
      <el-form-item label="备注">
        <el-input v-model="form.remark" :disabled="!editable" type="textarea" />
      </el-form-item>
    </el-form>

    <OrderLineTable
      :lines="form.lines"
      :products="products"
      :locations="locations"
      :editable="editable"
      mode="inbound"
      :show-actual="order?.status === 'submitted'"
    />

    <div class="actions">
      <el-button @click="$router.back()">返回</el-button>
      <template v-if="editable">
        <el-button v-if="isNew" type="primary" :loading="saving" @click="save">
          提交
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
  getInboundOrder, createInboundOrder, updateInboundOrder,
  submitInboundOrder, approveInboundOrder, rejectInboundOrder,
  cancelInboundOrder, deleteInboundOrder,
} from '@/api/inboundOrders'
import { listProducts } from '@/api/products'
import { listWarehouses } from '@/api/warehouses'
import { listLocations } from '@/api/locations'
import { useAuthStore } from '@/state/auth'
import OrderStatusTag from '@/components/OrderStatusTag.vue'
import OrderLineTable from '@/components/OrderLineTable.vue'
import type { InboundOrder, OrderLine, Product, Warehouse, Location } from '@/api/types'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const isNew = computed(() => route.name === 'inbound-new')
const order = ref<InboundOrder | null>(null)
const loading = ref(false)
const saving = ref(false)
const products = ref<Product[]>([])
const warehouses = ref<Warehouse[]>([])
const locations = ref<Location[]>([])
const form = reactive({ warehouse_id: 0, remark: '', lines: [] as OrderLine[] })
const editable = computed(() => isNew.value || order.value?.status === 'draft')

onMounted(async () => {
  loading.value = true
  try {
    const [p, w] = await Promise.all([listProducts({ per_page: 100 }), listWarehouses({ per_page: 100 })])
    products.value = p.items
    warehouses.value = w.items
    if (w.items.length) form.warehouse_id = w.items[0].id
    await loadLocations()
    if (!isNew.value) {
      order.value = await getInboundOrder(Number(route.params.id))
      form.warehouse_id = order.value.warehouse_id
      form.remark = order.value.remark || ''
      form.lines = order.value.lines || []
      await loadLocations()
    } else {
      form.lines = []
    }
  } finally {
    loading.value = false
  }
})

async function loadLocations() {
  if (!form.warehouse_id) return
  const res = await listLocations({ warehouse_id: form.warehouse_id, per_page: 100 })
  locations.value = res.items
}

async function save() {
  saving.value = true
  try {
    if (isNew.value) {
      const created = await createInboundOrder(form)
      await submitInboundOrder(created.id)
      router.replace(`/inbound/${created.id}`)
    } else {
      await updateInboundOrder(Number(route.params.id), form)
      order.value = await getInboundOrder(Number(route.params.id))
    }
  } finally {
    saving.value = false
  }
}

async function doSubmit() {
  const orderId = Number(route.params.id)
  saving.value = true
  try {
    await updateInboundOrder(orderId, form)
    await submitInboundOrder(orderId)
    order.value = await getInboundOrder(orderId)
  } finally {
    saving.value = false
  }
}
async function doApprove() {
  await approveInboundOrder(Number(route.params.id))
  order.value = await getInboundOrder(Number(route.params.id))
}
async function doReject() {
  await rejectInboundOrder(Number(route.params.id))
  order.value = await getInboundOrder(Number(route.params.id))
}
async function doCancel() {
  await cancelInboundOrder(Number(route.params.id))
  order.value = await getInboundOrder(Number(route.params.id))
}
async function doDelete() {
  await deleteInboundOrder(Number(route.params.id))
  router.push('/inbound')
}
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.actions { margin-top: 20px; display: flex; gap: 8px; }
</style>
