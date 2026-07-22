<template>
  <div>
    <div class="toolbar">
      <h2>产品管理</h2>
      <el-button v-if="auth.hasRole('admin')" type="primary" @click="openDialog()">新建商品</el-button>
    </div>
    <el-table :data="items" v-loading="loading" border>
      <el-table-column prop="sku_code" label="编码" width="140" />
      <el-table-column prop="name" label="名称" />
      <el-table-column prop="spec" label="规格" />
      <el-table-column prop="unit" label="单位" width="80" />
      <el-table-column label="安全库存" width="100">
        <template #default="{ row }">{{ formatQty(row.safe_stock) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="auth.hasRole('admin')" label="操作" width="140">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="removeProduct(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑商品' : '新建商品'" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="编码" required>
          <el-input v-model="form.sku_code" :disabled="!!form.id" placeholder="新建时自动生成，可修改" />
        </el-form-item>
        <el-form-item label="名称" required><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="规格"><el-input v-model="form.spec" /></el-form-item>
        <el-form-item label="单位"><el-input v-model="form.unit" /></el-form-item>
        <el-form-item label="安全库存">
          <div class="field-with-hint">
            <el-input-number v-model="form.safe_stock" :min="0" :precision="3" />
            <span class="field-hint">低于此数量时首页预警，0 表示不预警</span>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { listProducts, suggestProductCode, createProduct, updateProduct, deleteProduct } from '@/api/products'
import { useAuthStore } from '@/state/auth'
import { formatQty } from '@/utils/format'
import type { Product } from '@/api/types'

const auth = useAuthStore()
const items = ref<Product[]>([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const form = reactive<Partial<Product>>({})

async function load() {
  loading.value = true
  try {
    const res = await listProducts({ per_page: 100 })
    items.value = res.items
  } finally {
    loading.value = false
  }
}

async function openDialog(row?: Product) {
  if (row) {
    Object.assign(form, row)
  } else {
    const { sku_code } = await suggestProductCode()
    Object.assign(form, { sku_code, name: '', spec: '', unit: '件', safe_stock: 0 })
  }
  dialogVisible.value = true
}

async function save() {
  saving.value = true
  try {
    if (form.id) await updateProduct(form.id, form)
    else await createProduct(form)
    dialogVisible.value = false
    await load()
  } finally {
    saving.value = false
  }
}

async function removeProduct(row: Product) {
  await ElMessageBox.confirm(`确定删除商品「${row.sku_code} - ${row.name}」？`, '删除商品', { type: 'warning' })
  await deleteProduct(row.id)
  await load()
}

onMounted(load)
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
.field-with-hint { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.field-hint { font-size: 12px; color: var(--el-text-color-secondary); line-height: 1.4; }
</style>
