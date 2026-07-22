<template>
  <div>
    <div class="toolbar">
      <h2>用户管理</h2>
      <el-button type="primary" @click="openDialog">增加新用户</el-button>
    </div>
    <el-table :data="items" v-loading="loading" border>
      <el-table-column prop="username" label="用户名" width="140" />
      <el-table-column prop="name" label="姓名" width="140" />
      <el-table-column label="角色" width="120">
        <template #default="{ row }">{{ roleLabel(row.role) }}</template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'">{{ row.is_active ? '启用' : '停用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="最近登录" min-width="180">
        <template #default="{ row }">{{ formatDateTime(row.last_login_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button link type="warning" @click="resetPassword(row)">重置密码</el-button>
          <el-button
            link
            type="danger"
            :loading="deletingId === row.id"
            @click="removeUser(row)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" title="增加新用户" width="480px">
      <el-form :model="form" label-width="90px">
        <el-form-item label="用户名" required>
          <el-input v-model="form.username" placeholder="登录账号" />
        </el-form-item>
        <el-form-item label="姓名" required>
          <el-input v-model="form.name" placeholder="显示名称" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" show-password placeholder="默认 888888" />
        </el-form-item>
        <el-form-item label="角色" required>
          <el-select v-model="form.role" style="width: 100%">
            <el-option label="管理员" value="admin" />
            <el-option label="仓管员" value="warehouse_keeper" />
            <el-option label="查看员" value="viewer" />
          </el-select>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { createUser, deleteUser, listUsers, resetUserPassword } from '@/api/users'
import { formatDateTime } from '@/utils/format'
import type { User, UserRole } from '@/api/types'

const items = ref<User[]>([])
const loading = ref(false)
const saving = ref(false)
const deletingId = ref<number | null>(null)
const dialogVisible = ref(false)
const DEFAULT_PASSWORD = '888888'
const form = reactive({
  username: '',
  name: '',
  password: DEFAULT_PASSWORD,
  role: 'warehouse_keeper' as UserRole,
})

const roleLabels: Record<UserRole, string> = {
  admin: '管理员',
  warehouse_keeper: '仓管员',
  viewer: '查看员',
}

function roleLabel(role: UserRole) {
  return roleLabels[role] || role
}

async function load() {
  loading.value = true
  try {
    const res = await listUsers({ per_page: 100 })
    items.value = res.items
  } finally {
    loading.value = false
  }
}

function openDialog() {
  Object.assign(form, { username: '', name: '', password: DEFAULT_PASSWORD, role: 'warehouse_keeper' })
  dialogVisible.value = true
}

async function save() {
  saving.value = true
  try {
    const password = form.password.trim() || DEFAULT_PASSWORD
    await createUser({ ...form, password })
    dialogVisible.value = false
    await load()
  } finally {
    saving.value = false
  }
}

async function resetPassword(row: User) {
  await ElMessageBox.confirm(
    `确定将用户「${row.username}」的密码重置为 ${DEFAULT_PASSWORD}？`,
    '重置密码',
    { type: 'warning' },
  )
  await resetUserPassword(row.id)
  ElMessage.success(`密码已重置为 ${DEFAULT_PASSWORD}`)
}

async function removeUser(row: User) {
  await ElMessageBox.confirm(
    `确定删除用户「${row.username}」？删除后该用户将无法登录。`,
    '删除用户',
    {
      type: 'warning',
      confirmButtonText: '删除',
      confirmButtonClass: 'el-button--danger',
    },
  )
  deletingId.value = row.id
  try {
    await deleteUser(row.id)
    ElMessage.success('用户已删除')
    await load()
  } finally {
    deletingId.value = null
  }
}

onMounted(load)
</script>

<style scoped>
.toolbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
</style>
