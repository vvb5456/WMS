import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/state/auth'
import { pinia } from '@/plugins/pinia'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: () => import('@/views/LoginPage.vue') },
    {
      path: '/',
      component: () => import('@/components/AppLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'dashboard', component: () => import('@/views/DashboardPage.vue') },
        { path: 'products', name: 'products', component: () => import('@/views/products/ProductListPage.vue'), meta: { requiresAdmin: true } },
        { path: 'warehouses', name: 'warehouses', component: () => import('@/views/warehouses/WarehousePage.vue'), meta: { requiresAdmin: true } },
        { path: 'inventory', name: 'inventory', component: () => import('@/views/inventory/InventoryPage.vue') },
        { path: 'inbound', name: 'inbound', component: () => import('@/views/inbound/InboundListPage.vue') },
        { path: 'inbound/new', name: 'inbound-new', component: () => import('@/views/inbound/InboundFormPage.vue') },
        { path: 'inbound/:id', name: 'inbound-detail', component: () => import('@/views/inbound/InboundFormPage.vue') },
        { path: 'outbound', name: 'outbound', component: () => import('@/views/outbound/OutboundListPage.vue') },
        { path: 'outbound/new', name: 'outbound-new', component: () => import('@/views/outbound/OutboundFormPage.vue') },
        { path: 'outbound/:id', name: 'outbound-detail', component: () => import('@/views/outbound/OutboundFormPage.vue') },
        { path: 'stocktake', name: 'stocktake', component: () => import('@/views/stocktake/StocktakeListPage.vue') },
        { path: 'stocktake/new', name: 'stocktake-new', component: () => import('@/views/stocktake/StocktakeFormPage.vue') },
        { path: 'stocktake/:id', name: 'stocktake-detail', component: () => import('@/views/stocktake/StocktakeFormPage.vue') },
        { path: 'users', name: 'users', component: () => import('@/views/users/UserManagePage.vue'), meta: { requiresAdmin: true } },
      ],
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore(pinia)
  if (to.matched.some((record) => record.meta.requiresAuth) && !auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.name === 'login' && auth.isLoggedIn) {
    return { name: 'dashboard' }
  }
  if (to.matched.some((record) => record.meta.requiresAdmin) && !auth.hasRole('admin')) {
    return { name: 'dashboard' }
  }
})

export default router
