import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/trip',
    name: 'TripDetail',
    component: () => import('@/views/TripDetail.vue'),
    meta: { title: '行程详情' }
  },
  {
    path: '/monitor',
    name: 'Monitor',
    component: () => import('@/views/Monitor.vue'),
    meta: { title: '监控中心' }
  },
  {
    path: '/food',
    name: 'Food',
    component: () => import('@/views/Food.vue'),
    meta: { title: '美食推荐' }
  },
  {
    path: '/attractions',
    name: 'Attractions',
    component: () => import('@/views/Attractions.vue'),
    meta: { title: '景点推荐' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人中心' }
  },
  {
    path: '/packing',
    name: 'Packing',
    component: () => import('@/views/Packing.vue'),
    meta: { title: '行李清单' }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/History.vue'),
    meta: { title: '历史行程' }
  },
  {
    path: '/guide',
    name: 'Guide',
    component: () => import('@/views/Guide.vue'),
    meta: { title: '攻略推荐' }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || '页面'} - 旅行智囊`
  next()
})

export default router