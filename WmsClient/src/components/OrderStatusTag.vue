<template>
  <el-tag :type="meta.type as any">{{ meta.label }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { OrderStatus } from '@/api/types'
import { orderStatusMeta } from '@/utils/format'

const props = defineProps<{ status: OrderStatus }>()
const meta = computed(() => orderStatusMeta(props.status))
</script>
