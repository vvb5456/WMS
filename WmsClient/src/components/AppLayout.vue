<template>
  <el-container class="layout">
    <el-aside width="220px" class="aside">
      <div class="logo">WMS 仓库管理</div>
      <el-menu :default-active="route.path" router>
        <el-menu-item index="/"><el-icon><Odometer /></el-icon>首页看板</el-menu-item>
        <el-menu-item v-if="auth.hasRole('admin')" index="/products"><el-icon><Goods /></el-icon>产品管理</el-menu-item>
        <el-menu-item v-if="auth.hasRole('admin')" index="/warehouses"><el-icon><OfficeBuilding /></el-icon>仓库库位</el-menu-item>
        <el-menu-item index="/inventory"><el-icon><Box /></el-icon>库存查询</el-menu-item>
        <el-menu-item v-if="auth.canOperateOrders()" index="/inbound"><el-icon><Download /></el-icon>入库单</el-menu-item>
        <el-menu-item v-if="auth.canOperateOrders()" index="/outbound"><el-icon><Upload /></el-icon>出库单</el-menu-item>
        <el-menu-item v-if="auth.canEdit()" index="/stocktake"><el-icon><DocumentChecked /></el-icon>盘点单</el-menu-item>
        <el-menu-item v-if="auth.hasRole('admin')" index="/users"><el-icon><User /></el-icon>增加新用户</el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>{{ auth.user?.name }}（{{ roleLabel }}）</span>
        <div class="header-actions">
          <el-button link @click="pwdDialog = true">修改密码</el-button>
          <el-button type="danger" link @click="onLogout">退出</el-button>
        </div>
      </el-header>
      <el-main><router-view /></el-main>
    </el-container>

    <el-dialog v-model="pwdDialog" title="修改密码" width="420px" @closed="resetPwdForm">
      <el-form :model="pwdForm" label-width="90px">
        <el-form-item label="原密码" required>
          <el-input v-model="pwdForm.oldPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="新密码" required>
          <el-input v-model="pwdForm.newPassword" type="password" show-password />
        </el-form-item>
        <el-form-item label="确认密码" required>
          <el-input v-model="pwdForm.confirmPassword" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialog = false">取消</el-button>
        <el-button type="primary" :loading="pwdSaving" @click="submitPassword">保存</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { changePassword } from '@/api/auth'
import { useAuthStore } from '@/state/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const pwdDialog = ref(false)
const pwdSaving = ref(false)
const pwdForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })

const roleLabel = computed(() => {
  const m: Record<string, string> = { admin: '管理员', warehouse_keeper: '仓管员', viewer: '查看员' }
  return m[auth.role || ''] || auth.role
})

function onLogout() {
  auth.logout()
  router.push('/login')
}

function resetPwdForm() {
  Object.assign(pwdForm, { oldPassword: '', newPassword: '', confirmPassword: '' })
}

async function submitPassword() {
  if (!pwdForm.oldPassword || !pwdForm.newPassword) {
    ElMessage.warning('请填写原密码和新密码')
    return
  }
  if (pwdForm.newPassword !== pwdForm.confirmPassword) {
    ElMessage.warning('两次输入的新密码不一致')
    return
  }
  pwdSaving.value = true
  try {
    await changePassword(pwdForm.oldPassword, pwdForm.newPassword)
    ElMessage.success('密码修改成功，请重新登录')
    pwdDialog.value = false
    onLogout()
  } finally {
    pwdSaving.value = false
  }
}
</script>

<style scoped>
.layout { height: 100vh; }
.aside { background: #1d2b3a; }
.logo { color: #fff; font-size: 18px; font-weight: 600; padding: 20px 16px; }
.aside :deep(.el-menu) { border-right: none; background: #1d2b3a; }
.aside :deep(.el-menu-item) { color: #bfcbd9; }
.aside :deep(.el-menu-item.is-active) { background: #409eff33; color: #fff; }
.header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; }
.header-actions { display: flex; align-items: center; gap: 8px; }
</style>
