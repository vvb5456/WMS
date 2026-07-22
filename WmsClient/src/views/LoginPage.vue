<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>仓库管理系统</h2>
      <form class="login-form" @submit.prevent="onSubmit">
        <el-form-item label="用户名">
          <el-input v-model="username" placeholder="admin" @keyup.enter="onSubmit" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="password"
            type="password"
            placeholder="admin123"
            show-password
            @keyup.enter="onSubmit"
          />
        </el-form-item>
        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          style="width: 100%"
        >
          登录
        </el-button>
      </form>
      <p class="hint">默认账号: admin / keeper / viewer，密码均为 admin123</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/state/auth'
import { pinia } from '@/plugins/pinia'

const username = ref('admin')
const password = ref('admin123')
const loading = ref(false)
const auth = useAuthStore(pinia)
const router = useRouter()
const route = useRoute()

async function onSubmit() {
  if (loading.value) return
  if (!username.value.trim() || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    await nextTick()
    const redirect = route.query.redirect as string | undefined
    if (redirect && redirect !== '/login') {
      await router.replace(redirect)
    } else {
      await router.replace({ name: 'dashboard' })
    }
  } catch (e: unknown) {
    const err = e as { message?: string }
    ElMessage.error(err?.message || '登录失败，请检查后端是否已启动')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1d2b3a, #409eff);
}
.login-card { width: 400px; }
.login-form { display: block; }
.hint { margin-top: 16px; color: #999; font-size: 12px; text-align: center; }
</style>
