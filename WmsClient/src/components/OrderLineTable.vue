<template>
  <el-table :data="lines" border size="small">
    <el-table-column label="编码" min-width="120">
      <template #default="{ row }">
        <el-select
          v-if="editable && mode !== 'stocktake'"
          :model-value="row.product_id || undefined"
          filterable
          clearable
          :placeholder="fromStock ? '选择有库存商品' : '选择商品'"
          style="width: 100%"
          @update:model-value="(v: number | undefined) => onProductChange(row, v)"
        >
          <el-option
            v-for="p in productOptions(row)"
            :key="p.id"
            :label="`${p.sku_code} - ${p.name}`"
            :value="p.id"
          />
        </el-select>
        <span v-else>{{ productCode(row) }}</span>
      </template>
    </el-table-column>
    <el-table-column label="名称" min-width="140">
      <template #default="{ row }">{{ productName(row) }}</template>
    </el-table-column>
    <el-table-column label="库位" min-width="140">
      <template #default="{ row }">
        <el-select
          v-if="editable && mode !== 'stocktake'"
          :model-value="row.location_id || undefined"
          filterable
          clearable
          :placeholder="fromStock ? '选择有库存库位' : '选择库位'"
          :disabled="fromStock && !row.product_id"
          style="width: 100%"
          @update:model-value="(v: number | undefined) => onLocationChange(row, v)"
        >
          <el-option
            v-for="l in locationOptions(row)"
            :key="l.id"
            :label="locationLabel(l, row)"
            :value="l.id"
          />
        </el-select>
        <span v-else>{{ locationCode(row) }}</span>
      </template>
    </el-table-column>
    <el-table-column v-if="mode === 'inbound' || mode === 'outbound'" label="数量" width="120">
      <template #default="{ row }">
        <el-input-number
          v-if="editable"
          :model-value="qtyValue(row)"
          :min="0"
          :max="maxQty(row)"
          :precision="0"
          :step="1"
          controls-position="right"
          @update:model-value="(v: number | undefined) => setQty(row, Math.round(v ?? 0))"
        />
        <span v-else>{{ formatQty(displayQty(row)) }}</span>
      </template>
    </el-table-column>
    <el-table-column v-if="mode === 'stocktake' && editable" label="账面数量" width="100">
      <template #default="{ row }">{{ formatQty(bookQty(row)) }}</template>
    </el-table-column>
    <el-table-column v-if="mode === 'stocktake'" label="实盘数量" width="120">
      <template #default="{ row }">
        <el-input-number
          v-if="editable"
          v-model="row.counted_qty"
          :min="0"
          :precision="0"
          :step="1"
          controls-position="right"
          @change="emitChange"
        />
        <span v-else>{{ formatQty(row.counted_qty) }}</span>
      </template>
    </el-table-column>
    <el-table-column v-if="mode === 'stocktake' && !editable" label="账面" width="100">
      <template #default="{ row }">{{ formatQty(row.book_qty) }}</template>
    </el-table-column>
    <el-table-column v-if="mode === 'stocktake' && !editable" label="差异" width="100">
      <template #default="{ row }">{{ formatQty(row.diff_qty) }}</template>
    </el-table-column>
    <el-table-column v-if="editable" label="操作" width="80">
      <template #default="{ $index }">
        <el-button type="danger" link @click="removeLine($index)">删除</el-button>
      </template>
    </el-table-column>
  </el-table>
  <el-button v-if="editable && mode !== 'stocktake'" style="margin-top: 8px" @click="addLine">添加明细</el-button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { InventoryItem, Location, OrderLine, Product } from '@/api/types'
import { formatQty } from '@/utils/format'

const props = defineProps<{
  lines: OrderLine[]
  products: Product[]
  locations: Location[]
  inventoryItems?: InventoryItem[]
  editable?: boolean
  mode: 'inbound' | 'outbound' | 'stocktake'
  showActual?: boolean
}>()

const fromStock = computed(
  () =>
    (props.mode === 'outbound' || props.mode === 'stocktake') &&
    (props.inventoryItems?.length ?? 0) > 0,
)

const stockProducts = computed(() => {
  const map = new Map<number, Product>()
  for (const item of props.inventoryItems ?? []) {
    if (item.product && !map.has(item.product_id)) map.set(item.product_id, item.product)
  }
  return [...map.values()]
})

function productOptions(row: OrderLine) {
  if (!fromStock.value) return props.products
  const options = stockProducts.value
  if (row.product_id && !options.some((p) => p.id === row.product_id) && row.product) {
    return [...options, row.product]
  }
  return options
}

function locationOptions(row: OrderLine) {
  if (!fromStock.value) return props.locations
  if (!row.product_id) return []
  const fromInv = (props.inventoryItems ?? [])
    .filter((item) => item.product_id === row.product_id && item.location)
    .map((item) => item.location!)
  const unique = new Map<number, Location>()
  for (const loc of fromInv) unique.set(loc.id, loc)
  if (row.location_id && !unique.has(row.location_id) && row.location) {
    unique.set(row.location_id, row.location)
  }
  return [...unique.values()]
}

function stockQty(productId?: number, locationId?: number) {
  if (!productId || !locationId) return undefined
  const item = (props.inventoryItems ?? []).find(
    (inv) => inv.product_id === productId && inv.location_id === locationId,
  )
  return item?.quantity
}

function locationLabel(loc: Location, row: OrderLine) {
  const qty = stockQty(row.product_id, loc.id)
  if (qty == null) return loc.code
  const prefix = props.mode === 'stocktake' ? '账面' : '可用'
  return `${loc.code}（${prefix} ${formatQty(qty)}）`
}

function maxQty(row: OrderLine) {
  if (props.mode !== 'outbound' || !fromStock.value) return undefined
  return stockQty(row.product_id, row.location_id)
}

function findProduct(row: OrderLine) {
  if (row.product) return row.product
  if (row.product_id) return props.products.find((p) => p.id === row.product_id)
  return undefined
}

function findLocation(row: OrderLine) {
  if (row.location) return row.location
  if (row.location_id) return props.locations.find((l) => l.id === row.location_id)
  return undefined
}

function productCode(row: OrderLine) {
  return findProduct(row)?.sku_code || (row.product_id ? String(row.product_id) : '-')
}

function productName(row: OrderLine) {
  return findProduct(row)?.name || '-'
}

function locationCode(row: OrderLine) {
  return findLocation(row)?.code || (row.location_id ? String(row.location_id) : '-')
}

function bookQty(row: OrderLine) {
  if (props.mode === 'stocktake' && row.product_id && row.location_id) {
    return stockQty(row.product_id, row.location_id) ?? 0
  }
  return row.book_qty ?? 0
}

function onLocationChange(row: OrderLine, locationId: number | undefined) {
  row.location_id = locationId
  if (props.mode === 'stocktake' && locationId && row.product_id) {
    const qty = stockQty(row.product_id, locationId) ?? 0
    row.book_qty = qty
    row.counted_qty = qty
  }
  emitChange()
}

function onProductChange(row: OrderLine, productId: number | undefined) {
  row.product_id = productId
  if (fromStock.value && productId) {
    const validLocationIds = new Set(
      (props.inventoryItems ?? [])
        .filter((item) => item.product_id === productId)
        .map((item) => item.location_id),
    )
    if (row.location_id && !validLocationIds.has(row.location_id)) row.location_id = undefined
  }
  if (props.mode === 'stocktake') {
    if (row.location_id && productId) {
      const qty = stockQty(productId, row.location_id) ?? 0
      row.book_qty = qty
      row.counted_qty = qty
    } else {
      row.book_qty = 0
      row.counted_qty = 0
    }
  }
  emitChange()
}

const emit = defineEmits<{ change: [] }>()

function emitChange() { emit('change') }

function qtyValue(row: OrderLine) {
  return props.showActual ? (row.actual_qty ?? 0) : (row.planned_qty ?? 0)
}

function setQty(row: OrderLine, value: number) {
  if (props.showActual) row.actual_qty = value
  else row.planned_qty = value
  emitChange()
}

function displayQty(row: OrderLine) {
  if (row.actual_qty && row.actual_qty > 0) return row.actual_qty
  return row.planned_qty ?? 0
}

function addLine() {
  const line: OrderLine = {}
  if (props.mode === 'stocktake') line.counted_qty = 0
  else line.planned_qty = 0
  props.lines.push(line)
  emitChange()
}

function removeLine(index: number) {
  props.lines.splice(index, 1)
  emitChange()
}
</script>
