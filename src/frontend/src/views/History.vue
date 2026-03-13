<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark font-display text-slate-900 dark:text-slate-100">
    <div class="flex h-screen overflow-hidden">
      <!-- 侧边栏 -->
      <aside class="w-72 flex-shrink-0 bg-background-light dark:bg-background-dark border-r border-primary/10 flex flex-col justify-between p-6">
        <div class="flex flex-col gap-8">
          <div class="flex items-center gap-3 px-2">
            <div class="bg-primary p-2 rounded-lg flex items-center justify-center">
              <span class="material-symbols-outlined text-white text-2xl">explore</span>
            </div>
            <div>
              <h1 class="text-xl font-bold tracking-tight text-slate-900">TravelAI</h1>
              <p class="text-xs text-primary font-semibold uppercase tracking-widest">Assistant</p>
            </div>
          </div>
          <nav class="flex flex-col gap-2">
            <router-link to="/" class="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-primary/10 dark:hover:bg-primary/20 transition-all">
              <span class="material-symbols-outlined">home</span>
              <span class="font-medium">返回首页</span>
            </router-link>
            <router-link to="/trip" class="flex items-center gap-3 px-4 py-3 rounded-xl bg-primary text-white shadow-lg shadow-primary/20 transition-all">
              <span class="material-symbols-outlined">calendar_today</span>
              <span class="font-medium">行程详情</span>
            </router-link>
            <router-link to="/profile" class="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-primary/10 dark:hover:bg-primary/20 transition-all">
              <span class="material-symbols-outlined">person</span>
              <span class="font-medium">个人资料</span>
            </router-link>
            <router-link to="/monitor" class="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-primary/10 dark:hover:bg-primary/20 transition-all">
              <span class="material-symbols-outlined">monitoring</span>
              <span class="font-medium">我的监控</span>
            </router-link>
            <router-link to="/history" class="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-primary/10 dark:hover:bg-primary/20 transition-all">
              <span class="material-symbols-outlined">chat_bubble</span>
              <span class="font-medium">消息通知</span>
            </router-link>
            <router-link to="/" class="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-primary/10 dark:hover:bg-primary/20 transition-all">
              <span class="material-symbols-outlined">shopping_bag</span>
              <span class="font-medium">我的订单</span>
            </router-link>
            <router-link to="/packing" class="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-primary/10 dark:hover:bg-primary/20 transition-all">
              <span class="material-symbols-outlined">favorite</span>
              <span class="font-medium">收藏列表</span>
            </router-link>
            <router-link to="/" class="flex items-center gap-3 px-4 py-3 rounded-xl text-slate-600 dark:text-slate-400 hover:bg-primary/10 dark:hover:bg-primary/20 transition-all">
              <span class="material-symbols-outlined">settings</span>
              <span class="font-medium">设置</span>
            </router-link>
          </nav>
        </div>
        <div class="bg-gradient-to-br from-amber-400/20 to-amber-600/20 p-4 rounded-xl border border-amber-500/30">
          <p class="text-xs font-bold text-amber-500 mb-2 uppercase">专业版会员</p>
          <p class="text-sm text-slate-600 dark:text-slate-300 mb-4 leading-relaxed">Unlock unlimited flight monitors and concierge AI support.</p>
          <button class="w-full bg-primary text-white font-bold py-2 rounded-lg text-sm hover:opacity-90 transition-opacity">升级计划</button>
        </div>
      </aside>

      <!-- 主内容 -->
      <main class="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark p-8 space-y-6">
        <!-- 标题 -->
        <div class="flex items-center justify-between mb-8">
          <div>
            <h2 class="text-3xl font-bold tracking-tight">消息通知</h2>
            <p class="text-slate-500 mt-1">共有 {{ unreadCount }} 条未读消息</p>
          </div>
          <button @click="markAllRead" class="px-4 py-2 text-sm font-medium text-primary hover:bg-primary/10 rounded-lg transition-colors">
            全部标记已读
          </button>
        </div>

        <!-- 分类标签 -->
        <div class="flex gap-2 mb-6">
          <button
            v-for="tab in tabs"
            :key="tab.value"
            @click="currentTab = tab.value"
            :class="[
              'px-4 py-2 rounded-full text-sm font-bold transition-all',
              currentTab === tab.value
                ? 'bg-primary text-white shadow-lg shadow-primary/20'
                : 'bg-slate-100 dark:bg-primary/10 text-slate-600 dark:text-slate-400 hover:bg-primary/10'
            ]"
          >
            {{ tab.label }}
            <span v-if="tab.count > 0" :class="['ml-2 px-2 py-0.5 rounded-full text-xs', currentTab === tab.value ? 'bg-white/20' : 'bg-primary/20 text-primary']">
              {{ tab.count }}
            </span>
          </button>
        </div>

        <!-- 消息列表 -->
        <div class="space-y-4">
          <div
            v-for="notification in filteredNotifications"
            :key="notification.id"
            :class="[
              'p-6 rounded-xl border transition-all cursor-pointer hover:shadow-lg',
              notification.read
                ? 'bg-white dark:bg-primary/5 border-slate-200 dark:border-primary/10'
                : 'bg-primary/5 border-primary/30 shadow-md'
            ]"
          >
            <div class="flex gap-4">
              <!-- 图标 -->
              <div :class="['p-3 rounded-xl shrink-0', getIconBgClass(notification.type)]">
                <span :class="['material-symbols-outlined text-2xl', getIconColorClass(notification.type)]">
                  {{ getIcon(notification.type) }}
                </span>
              </div>

              <!-- 内容 -->
              <div class="flex-1 min-w-0">
                <div class="flex items-start justify-between gap-4 mb-2">
                  <h3 class="font-bold text-lg text-slate-900 dark:text-slate-100">{{ notification.title }}</h3>
                  <span class="text-xs text-slate-400 shrink-0">{{ notification.time }}</span>
                </div>
                <p class="text-slate-600 dark:text-slate-400 text-sm leading-relaxed">{{ notification.content }}</p>

                <!-- 操作按钮 -->
                <div v-if="notification.actions" class="flex gap-3 mt-4">
                  <button
                    v-for="action in notification.actions"
                    :key="action.label"
                    @click.stop="handleAction(action)"
                    :class="[
                      'px-4 py-2 rounded-lg text-sm font-bold transition-colors',
                      action.primary
                        ? 'bg-primary text-white hover:bg-primary/90'
                        : 'bg-slate-100 dark:bg-primary/10 text-slate-600 dark:text-slate-400 hover:bg-primary/10'
                    ]"
                  >
                    {{ action.label }}
                  </button>
                </div>
              </div>

              <!-- 未读标记 -->
              <div v-if="!notification.read" class="w-2 h-2 rounded-full bg-primary shrink-0 mt-2"></div>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="filteredNotifications.length === 0" class="text-center py-16">
            <div class="inline-flex items-center justify-center w-20 h-20 bg-slate-100 dark:bg-primary/10 rounded-full mb-4">
              <span class="material-symbols-outlined text-4xl text-slate-400">notifications_off</span>
            </div>
            <p class="text-slate-500 text-lg">暂无消息</p>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const currentTab = ref('all')

const tabs = computed(() => [
  { value: 'all', label: '全部', count: notifications.value.filter(n => !n.read).length },
  { value: 'price', label: '价格提醒', count: notifications.value.filter(n => !n.read && n.type === 'price').length },
  { value: 'trip', label: '行程提醒', count: notifications.value.filter(n => !n.read && n.type === 'trip').length },
  { value: 'ai', label: 'AI 规划', count: notifications.value.filter(n => !n.read && n.type === 'ai').length },
])

const notifications = ref([
  {
    id: 1,
    type: 'price',
    title: '机票降价提醒',
    content: '您监控的北京→上海航线今日票价降至 ¥680，低于您的目标价 ¥750。建议尽快预订！',
    time: '5分钟前',
    read: false,
    actions: [
      { label: '立即预订', primary: true, action: 'book' },
      { label: '继续监控', primary: false, action: 'continue' },
    ],
  },
  {
    id: 2,
    type: 'trip',
    title: '行程出发提醒',
    content: '您的杭州3日游将于明天出发！请确认行李准备情况，查看完整行程详情。',
    time: '1小时前',
    read: false,
    actions: [
      { label: '查看行程', primary: true, action: 'view' },
      { label: '行李清单', primary: false, action: 'packing' },
    ],
  },
  {
    id: 3,
    type: 'ai',
    title: 'AI 行程规划完成',
    content: '您的"成都美食4日深度游"行程已生成完毕。包含12个精选景点和8家地道餐厅推荐。',
    time: '2小时前',
    read: false,
    actions: [
      { label: '查看详情', primary: true, action: 'view' },
      { label: '调整偏好', primary: false, action: 'adjust' },
    ],
  },
  {
    id: 4,
    type: 'price',
    title: '高铁余票提醒',
    content: 'G1234次列车（北京南→杭州东）出现二等座余票，发车时间 09:30，票价 ¥531。',
    time: '3小时前',
    read: true,
    actions: [
      { label: '立即抢票', primary: true, action: 'book' },
    ],
  },
  {
    id: 5,
    type: 'trip',
    title: '酒店入住提醒',
    content: '您预订的"西湖精品酒店"将于明天14:00可办理入住。酒店地址：西湖区北山街88号。',
    time: '昨天',
    read: true,
    actions: [],
  },
  {
    id: 6,
    type: 'ai',
    title: '个性化推荐已更新',
    content: '根据您的浏览历史和偏好，我们为您更新了上海美食推荐列表，新增3家高分餐厅。',
    time: '2天前',
    read: true,
    actions: [
      { label: '查看推荐', primary: true, action: 'view' },
    ],
  },
])

const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

const filteredNotifications = computed(() => {
  if (currentTab.value === 'all') {
    return notifications.value
  }
  return notifications.value.filter(n => n.type === currentTab.value)
})

function getIcon(type) {
  const icons = {
    price: 'trending_down',
    trip: 'flight_takeoff',
    ai: 'auto_awesome',
  }
  return icons[type] || 'notifications'
}

function getIconBgClass(type) {
  const classes = {
    price: 'bg-emerald-100 dark:bg-emerald-500/20',
    trip: 'bg-blue-100 dark:bg-blue-500/20',
    ai: 'bg-amber-100 dark:bg-amber-500/20',
  }
  return classes[type] || 'bg-slate-100'
}

function getIconColorClass(type) {
  const classes = {
    price: 'text-emerald-600 dark:text-emerald-400',
    trip: 'text-blue-600 dark:text-blue-400',
    ai: 'text-amber-600 dark:text-amber-400',
  }
  return classes[type] || 'text-slate-600'
}

function markAllRead() {
  notifications.value.forEach(n => n.read = true)
}

function handleAction(action) {
  console.log('Action:', action.action)
  // 根据action执行相应操作
}
</script>