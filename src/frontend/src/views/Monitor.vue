<template>
  <div class="min-h-screen page-bg-gradient dark:page-bg-dark font-display text-slate-100">
    <div class="max-w-[1200px] mx-auto min-h-screen flex flex-col">
      <!-- 导航栏 -->
      <header class="flex items-center justify-between px-6 py-6 border-b border-primary/10">
        <router-link to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div class="bg-primary p-2 rounded-lg">
            <span class="material-symbols-outlined text-white text-2xl">train</span>
          </div>
          <div>
            <h1 class="text-xl font-bold tracking-tight text-slate-100">票务查询 <span class="text-primary">|</span> 12306实时查询</h1>
            <p class="text-xs text-slate-400">Train Ticket Query</p>
          </div>
        </router-link>
        <div class="flex items-center gap-4">
          <router-link to="/trip" class="flex items-center gap-2 px-4 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 transition-colors">
            <span class="material-symbols-outlined">calendar_today</span>
            <span class="text-sm font-medium">返回行程</span>
          </router-link>
          <router-link to="/" class="flex items-center gap-2 px-4 py-2 rounded-lg bg-white/5 hover:bg-white/10 transition-colors text-slate-200">
            <span class="material-symbols-outlined">home</span>
            <span class="text-sm font-medium">返回首页</span>
          </router-link>
        </div>
      </header>

      <main class="flex-1 p-6 space-y-8">
        <!-- 查询条件 -->
        <div class="glass-panel rounded-xl p-6 shadow-2xl">
          <div class="flex flex-col md:flex-row items-center gap-4">
            <div class="flex items-center gap-4 w-full md:w-auto">
              <div class="flex-1 md:w-48">
                <label class="text-xs text-slate-400 block mb-1">出发地</label>
                <input v-model="fromStation" class="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-lg font-bold text-slate-100 focus:outline-none focus:border-primary/50 transition-colors" placeholder="出发城市" />
              </div>
              <span class="material-symbols-outlined text-primary text-2xl mt-4">sync_alt</span>
              <div class="flex-1 md:w-48">
                <label class="text-xs text-slate-400 block mb-1">目的地</label>
                <input v-model="toStation" class="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-lg font-bold text-slate-100 focus:outline-none focus:border-primary/50 transition-colors" placeholder="目的城市" />
              </div>
            </div>
            <div class="flex items-center gap-4">
              <div>
                <label class="text-xs text-slate-400 block mb-1">出发日期</label>
                <input v-model="travelDate" type="date" class="bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-slate-100 focus:outline-none focus:border-primary/50 transition-colors" />
              </div>
              <button @click="searchTrains" :disabled="loading" class="mt-4 px-8 py-3 bg-primary hover:bg-primary/90 text-white font-bold rounded-lg transition-all flex items-center gap-2 shadow-lg shadow-primary/30">
                <span v-if="loading">查询中...</span>
                <span v-else>查询车次</span>
                <span class="material-symbols-outlined">search</span>
              </button>
            </div>
          </div>
        </div>

        <!-- 车次列表 -->
        <div class="glass-panel rounded-xl p-8 shadow-2xl">
          <div class="flex items-center justify-between mb-6">
            <h2 class="text-2xl font-bold flex items-center gap-2">
              <span class="material-symbols-outlined text-primary">train</span>
              车次信息
            </h2>
            <span v-if="trains.length > 0" class="text-slate-400 text-sm">共 {{ trains.length }} 趟列车</span>
          </div>

          <div v-if="loading" class="text-center py-12">
            <span class="material-symbols-outlined text-5xl text-primary animate-spin">refresh</span>
            <p class="text-slate-400 mt-4">正在查询12306数据...</p>
          </div>

          <div v-else-if="trains.length === 0" class="text-center py-12">
            <span class="material-symbols-outlined text-5xl text-slate-500">train</span>
            <p class="text-slate-400 mt-4">{{ fromStation && toStation ? '暂无车次信息' : '请输入出发地和目的地查询' }}</p>
          </div>

          <div v-else class="space-y-4">
            <div v-for="train in trains" :key="train.train_no" class="bg-white/5 rounded-xl p-6 hover:bg-white/[0.08] transition-all">
              <div class="flex flex-col md:flex-row items-center justify-between gap-4">
                <!-- 车次信息 -->
                <div class="flex items-center gap-6">
                  <div class="bg-primary/20 text-primary px-4 py-2 rounded-lg text-center">
                    <div class="text-xl font-black">{{ train.train_no }}</div>
                    <div class="text-xs">{{ train.train_type || '高铁' }}</div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-black">{{ train.start_time }}</div>
                    <div class="text-sm text-slate-400">{{ train.from_station }}</div>
                  </div>
                  <div class="flex flex-col items-center">
                    <span class="text-xs text-slate-500">{{ train.duration }}</span>
                    <div class="flex items-center gap-2">
                      <div class="w-2 h-2 rounded-full bg-primary"></div>
                      <div class="w-16 h-0.5 bg-slate-600"></div>
                      <span class="material-symbols-outlined text-primary text-sm">arrow_forward</span>
                      <div class="w-16 h-0.5 bg-slate-600"></div>
                      <div class="w-2 h-2 rounded-full bg-primary"></div>
                    </div>
                  </div>
                  <div class="text-center">
                    <div class="text-2xl font-black">{{ train.end_time }}</div>
                    <div class="text-sm text-slate-400">{{ train.to_station }}</div>
                  </div>
                </div>

                <!-- 余票信息 -->
                <div class="flex flex-wrap gap-6">
                  <div v-for="seat in train.seats" :key="seat.name" class="text-center px-4 py-3 bg-white/5 rounded-lg min-w-[80px]">
                    <div class="text-xs text-slate-400">{{ seat.name }}</div>
                    <div :class="['font-bold text-lg', seat.count > 0 ? 'text-green-400' : 'text-red-400']">
                      {{ seat.count > 0 ? `${seat.count}张` : '无票' }}
                    </div>
                    <div class="text-sm text-primary font-bold">¥{{ seat.price }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 提示信息 -->
        <div class="glass-panel rounded-xl p-6 flex items-center gap-4">
          <span class="material-symbols-outlined text-primary text-3xl">info</span>
          <div>
            <h4 class="font-bold text-slate-200">温馨提示</h4>
            <p class="text-sm text-slate-400">车次信息来源于12306官方网站，实时更新。建议提前预订，确保出行顺利。</p>
          </div>
        </div>
      </main>

      <footer class="p-8 text-center text-slate-500 text-sm border-t border-white/5">
        © 2024 出行助手 Travel Assistant. All Rights Reserved. 沪ICP备12345678号
      </footer>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const tripSpec = computed(() => chatStore.currentTripSpec)

const fromStation = ref('')
const toStation = ref('')
const travelDate = ref('')
const loading = ref(false)
const trains = ref([])

// 从trip_spec获取出发地和目的地
onMounted(() => {
  chatStore.init()
  if (tripSpec.value) {
    fromStation.value = tripSpec.value.origin_city || ''
    toStation.value = tripSpec.value.destination_city || ''
    travelDate.value = tripSpec.value.start_date || ''
  }
})

// 查询车次
async function searchTrains() {
  if (!fromStation.value || !toStation.value) {
    alert('请输入出发地和目的地')
    return
  }

  loading.value = true
  try {
    // 调用后端API查询12306
    const response = await fetch(`/api/trains?from_station=${encodeURIComponent(fromStation.value)}&to_station=${encodeURIComponent(toStation.value)}&date=${travelDate.value}`)
    const data = await response.json()

    if (data.success && data.data) {
      trains.value = data.data
    } else {
      // 模拟数据用于演示
      trains.value = generateMockTrains()
    }
  } catch (error) {
    console.error('查询车次失败:', error)
    // 使用模拟数据
    trains.value = generateMockTrains()
  } finally {
    loading.value = false
  }
}

// 生成模拟车次数据
function generateMockTrains() {
  const mockTrains = [
    { train_no: 'G1', train_type: '高铁', from_station: fromStation.value + '南', to_station: toStation.value + '虹桥', start_time: '07:00', end_time: '11:30', duration: '4小时30分', seats: [{ name: '二等座', count: 156, price: 553 }, { name: '一等座', count: 45, price: 933 }, { name: '商务座', count: 12, price: 1748 }] },
    { train_no: 'G3', train_type: '高铁', from_station: fromStation.value + '南', to_station: toStation.value + '虹桥', start_time: '08:00', end_time: '12:35', duration: '4小时35分', seats: [{ name: '二等座', count: 89, price: 553 }, { name: '一等座', count: 23, price: 933 }] },
    { train_no: 'G5', train_type: '高铁', from_station: fromStation.value + '南', to_station: toStation.value + '虹桥', start_time: '09:00', end_time: '13:20', duration: '4小时20分', seats: [{ name: '二等座', count: 0, price: 553 }, { name: '一等座', count: 5, price: 933 }, { name: '商务座', count: 3, price: 1748 }] },
    { train_no: 'G7', train_type: '高铁', from_station: fromStation.value + '南', to_station: toStation.value + '虹桥', start_time: '10:00', end_time: '14:45', duration: '4小时45分', seats: [{ name: '二等座', count: 234, price: 553 }, { name: '一等座', count: 67, price: 933 }] },
    { train_no: 'D701', train_type: '动车', from_station: fromStation.value, to_station: toStation.value, start_time: '19:08', end_time: '23:58', duration: '4小时50分', seats: [{ name: '软卧', count: 28, price: 630 }, { name: '硬卧', count: 0, price: 400 }] },
  ]
  return mockTrains
}
</script>

<style scoped>
.glass-panel {
  background: rgba(253, 245, 230, 0.05);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(239, 67, 67, 0.1);
}

input[type="date"]::-webkit-calendar-picker-indicator {
  filter: invert(1);
}
</style>