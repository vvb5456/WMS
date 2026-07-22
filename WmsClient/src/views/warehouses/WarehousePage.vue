<template>
  <div>
    <h2>仓库 / 库位</h2>
    <el-row :gutter="16">
      <el-col :span="10">
        <el-card header="仓库列表">
          <el-button v-if="auth.hasRole('admin')" type="primary" size="small" @click="openWhDialog()" style="margin-bottom: 12px">新建仓库</el-button>
          <el-table :data="warehouses" highlight-current-row @current-change="onWhSelect" size="small">
            <el-table-column prop="code" label="编码" width="80" />
            <el-table-column prop="name" label="名称" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="14">
        <el-card :header="`库位列表 ${selectedWh ? '- ' + selectedWh.name : ''}`">
          <el-button v-if="auth.hasRole('admin') && selectedWh" type="primary" size="small" @click="openLocDialog()" style="margin-bottom: 12px">新建库位</el-button>
          <el-table :data="locations" size="small">
            <el-table-column prop="code" label="编码" />
            <el-table-column prop="name" label="名称" />
            <el-table-column v-if="auth.hasRole('admin')" label="操作" width="80">
              <template #default="{ row }">
                <el-button type="danger" link @click="removeLoc(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="whDialog" title="新建仓库" width="400px">
      <el-form :model="whForm" label-width="80px">
        <el-form-item label="编码"><el-input v-model="whForm.code" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="whForm.name" /></el-form-item>
        <el-form-item label="地址"><el-input v-model="whForm.address" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="whDialog = false">取消</el-button>
        <el-button type="primary" @click="saveWh">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="locDialog" title="新建库位" width="400px">
      <el-form :model="locForm" label-width="80px">
        <el-form-item label="编码"><el-input v-model="locForm.code" /></el-form-item>
        <el-form-item label="名称"><el-input v-model="locForm.name" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="locDialog = false">取消</el-button>
        <el-button type="primary" @click="saveLoc">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessageBox } from 'element-plus'
import { listWarehouses, createWarehouse } from '@/api/warehouses'
import { listLocations, createLocation, deleteLocation } from '@/api/locations'
import { useAuthStore } from '@/state/auth'
import type { Location, Warehouse } from '@/api/types'

const auth = useAuthStore()
const warehouses = ref<Warehouse[]>([])
const locations = ref<Location[]>([])
const selectedWh = ref<Warehouse | null>(null)
const whDialog = ref(false)
const locDialog = ref(false)
const whForm = reactive({ code: '', name: '', address: '' })
const locForm = reactive({ code: '', name: '' })

async function loadWarehouses() {
  const res = await listWarehouses({ per_page: 100 })
  warehouses.value = res.items
  if (res.items.length && !selectedWh.value) onWhSelect(res.items[0])
}

async function loadLocations() {
  if (!selectedWh.value) return
  const res = await listLocations({ warehouse_id: selectedWh.value.id, per_page: 100 })
  locations.value = res.items
}

function onWhSelect(row: Warehouse | null) {
  selectedWh.value = row
  loadLocations()
}

function openWhDialog() { Object.assign(whForm, { code: '', name: '', address: '' }); whDialog.value = true }
function openLocDialog() { Object.assign(locForm, { code: '', name: '' }); locDialog.value = true }

async function saveWh() {
  await createWarehouse(whForm)
  whDialog.value = false
  await loadWarehouses()
}

async function saveLoc() {
  if (!selectedWh.value) return
  await createLocation({ ...locForm, warehouse_id: selectedWh.value.id })
  locDialog.value = false
  await loadLocations()
}

async function removeLoc(row: Location) {
  await ElMessageBox.confirm(`确定删除库位「${row.code}」？`, '删除库位', { type: 'warning' })
  await deleteLocation(row.id)
  await loadLocations()
}

onMounted(loadWarehouses)
</script>
