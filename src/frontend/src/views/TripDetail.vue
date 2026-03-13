<template>
  <div class="flex h-screen overflow-hidden bg-white font-display text-slate-900">
    <!-- 侧边栏 -->
    <aside class="w-72 flex-shrink-0 bg-white/60 dark:bg-black/20 border-r border-primary/10 flex flex-col justify-between p-6 backdrop-blur-sm">
      <div class="flex flex-col gap-8">
        <div class="flex items-center gap-3 px-2">
          <div class="bg-primary p-2 rounded-lg flex items-center justify-center">
            <span class="material-symbols-outlined text-white text-2xl">travel_explore</span>
          </div>
          <div>
            <h1 class="text-xl font-bold tracking-tight">旅行规划</h1>
            <p class="text-xs text-primary/70">温润高端体验</p>
          </div>
        </div>
        <nav class="flex flex-col gap-2">
          <router-link to="/" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-primary/10 transition-colors">
            <span class="material-symbols-outlined text-primary">dashboard</span>
            <span class="font-medium">行程概览</span>
          </router-link>
          <router-link to="/trip" class="flex items-center gap-3 px-4 py-3 rounded-xl bg-primary text-white shadow-lg shadow-primary/20">
            <span class="material-symbols-outlined">calendar_month</span>
            <span class="font-medium">我的行程</span>
          </router-link>
          <router-link to="/packing" class="flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-primary/10 transition-colors">
            <span class="material-symbols-outlined text-primary">fact_check</span>
            <span class="font-medium">清单管理</span>
          </router-link>
        </nav>
      </div>
      <div class="mt-auto p-4 rounded-2xl bg-primary/5 border border-primary/10">
        <p class="text-xs font-semibold uppercase tracking-wider text-primary mb-2">当前目的地</p>
        <div class="flex items-center justify-between">
          <span class="text-xl font-bold">{{ tripSpec?.destination_city || '未设置' }}</span>
          <span class="material-symbols-outlined text-primary">trending_flat</span>
        </div>
      </div>
    </aside>

    <!-- 主内容 -->
    <main class="flex-1 overflow-y-auto p-8 flex flex-col gap-8 bg-white/40 dark:bg-black/10 backdrop-blur-sm">
      <!-- 头部 -->
      <header class="flex flex-col gap-2">
        <h2 class="text-5xl font-black tracking-tight text-slate-900 dark:text-white">行程详情</h2>
        <div class="flex items-center gap-2 text-primary font-medium">
          <span class="material-symbols-outlined text-sm">event</span>
          <span>{{ dateRange }}</span>
        </div>
      </header>

      <!-- 日历 -->
      <div class="bg-white dark:bg-primary/5 rounded-xl p-8 border border-slate-200 dark:border-primary/10 shadow-sm">
        <div class="flex items-center justify-between mb-8">
          <button class="p-2 rounded-full hover:bg-primary/10 transition-colors" @click="prevMonth">
            <span class="material-symbols-outlined">chevron_left</span>
          </button>
          <h3 class="text-2xl font-bold">{{ currentMonthYear }}</h3>
          <button class="p-2 rounded-full hover:bg-primary/10 transition-colors" @click="nextMonth">
            <span class="material-symbols-outlined">chevron_right</span>
          </button>
        </div>
        <div class="calendar-grid gap-1">
          <!-- 星期 -->
          <div v-for="day in weekDays" :key="day" class="h-12 flex items-center justify-center font-bold text-slate-400">
            {{ day }}
          </div>
          <!-- 日期格子 -->
          <div
            v-for="cell in calendarCells"
            :key="cell.key"
            :class="[
              'h-20 flex flex-col items-center justify-center rounded-xl transition-colors',
              cell.isTripDay ? 'bg-primary/20 border border-primary/30' : 'hover:bg-primary/5',
              cell.isTripStart ? 'rounded-l-xl' : '',
              cell.isTripEnd ? 'rounded-r-xl' : '',
            ]"
          >
            <span :class="['font-bold', cell.isTripDay ? 'text-primary' : '']">{{ cell.day }}</span>
            <span v-if="cell.isTripStart" class="text-[10px] uppercase font-bold text-primary">出发</span>
            <span v-if="cell.isTripEnd" class="text-[10px] uppercase font-bold text-primary">返程</span>
          </div>
        </div>
      </div>

      <!-- 底部卡片 -->
      <div class="grid grid-cols-2 gap-6">
        <div class="p-6 rounded-2xl bg-white dark:bg-primary/5 border border-slate-200 dark:border-primary/10">
          <h4 class="text-xl font-bold mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">attractions</span>
            推荐景点
            <span v-if="recommendationsLoading" class="text-sm text-slate-400 ml-2">加载中...</span>
          </h4>
          <div v-if="topAttraction" class="space-y-4">
            <div class="flex gap-4 items-start">
              <div class="w-20 h-20 rounded-lg overflow-hidden flex-shrink-0" :style="{ background: topAttraction.gradient }">
                <img v-if="topAttraction.image" :src="topAttraction.image" class="w-full h-full object-cover" @error="(e) => e.target.style.display = 'none'" />
              </div>
              <div class="flex-1">
                <p class="font-bold text-lg">{{ topAttraction.name }}</p>
                <p class="text-sm text-slate-500">{{ topAttraction.description }}</p>
                <div class="flex gap-2 mt-2">
                  <span class="px-2 py-0.5 rounded-full bg-primary/10 text-primary text-xs font-bold">{{ topAttraction.type === 'attraction' ? '景点' : '推荐' }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-slate-400 text-center py-4">
            请先在首页设置目的地
          </div>
        </div>
        <div class="p-6 rounded-2xl bg-white dark:bg-primary/5 border border-slate-200 dark:border-primary/10">
          <h4 class="text-xl font-bold mb-4 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary">cloud</span>
            目的地天气
            <span class="text-sm text-slate-400 font-normal">({{ todayDate }})</span>
            <span v-if="weatherLoading" class="text-sm text-slate-400 ml-2">加载中...</span>
          </h4>
          <div v-if="weather.city" class="flex items-center gap-6">
            <span class="material-symbols-outlined text-5xl text-primary">{{ weatherIcon }}</span>
            <div>
              <p class="text-lg font-bold text-slate-600">{{ weather.city }}</p>
              <p class="text-3xl font-black">{{ weather.temp }}°C</p>
              <p class="text-slate-500">{{ weather.description }}</p>
              <div class="flex gap-4 mt-1 text-xs text-slate-400">
                <span>体感: {{ weather.realFeel }}°C</span>
                <span>湿度: {{ weather.humidity }}%</span>
                <span>风力: {{ weather.wind }}</span>
              </div>
              <p v-if="weather.tips" class="text-xs text-primary mt-2">💡 {{ weather.tips }}</p>
            </div>
          </div>
          <div v-else class="text-slate-400 text-center py-4">
            请先设置目的地
          </div>
        </div>
      </div>

      <!-- Agent 智能推荐 -->
      <div class="mt-6 p-6 rounded-2xl bg-gradient-to-br from-primary/5 to-primary/10 border border-primary/20">
        <h4 class="text-xl font-bold mb-4 flex items-center gap-2">
          <span class="material-symbols-outlined text-primary">auto_awesome</span>
          AI 智能推荐
          <span class="text-xs font-normal text-slate-400 ml-2">Multi-Agent 生成</span>
        </h4>

        <div v-if="agentLoading" class="flex items-center justify-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-4 border-primary border-t-transparent"></div>
          <span class="ml-3 text-slate-500">AI 正在分析...</span>
        </div>

        <div v-else-if="agentRecommendations.length > 0" class="space-y-4">
          <div
            v-for="(rec, index) in agentRecommendations"
            :key="index"
            class="p-4 bg-white/50 dark:bg-white/5 rounded-xl border border-slate-200 dark:border-primary/10"
          >
            <div class="flex items-start gap-3">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
                   :class="{
                     'bg-blue-100 text-blue-600': rec.type === 'attraction',
                     'bg-orange-100 text-orange-600': rec.type === 'food',
                     'bg-green-100 text-green-600': rec.type === 'tip',
                     'bg-purple-100 text-purple-600': rec.type === 'transport'
                   }">
                <span class="material-symbols-outlined text-xl">
                  {{ rec.type === 'attraction' ? 'attractions' : rec.type === 'food' ? 'restaurant' : rec.type === 'tip' ? 'lightbulb' : 'train' }}
                </span>
              </div>
              <div class="flex-1">
                <p class="font-bold text-slate-800 dark:text-slate-200">{{ rec.title }}</p>
                <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">{{ rec.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-6">
          <p class="text-slate-400 mb-3">设置目的地后获取AI推荐</p>
          <button
            @click="fetchAgentRecommendations"
            :disabled="!tripSpec?.destination_city"
            class="px-4 py-2 bg-primary text-white rounded-lg font-medium hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            获取智能推荐
          </button>
        </div>

        <button
          v-if="agentRecommendations.length > 0"
          @click="fetchAgentRecommendations"
          class="w-full mt-4 px-4 py-2 border border-primary/30 text-primary rounded-lg font-medium hover:bg-primary/5 transition-colors flex items-center justify-center gap-2"
        >
          <span class="material-symbols-outlined text-lg">refresh</span>
          刷新推荐
        </button>
      </div>
    </main>

    <!-- 右侧面板 -->
    <aside class="w-96 flex-shrink-0 bg-white dark:bg-[#1a0c0c] border-l border-primary/10 p-8">
      <div class="flex flex-col gap-6">
        <!-- 美食推荐入口 -->
        <router-link to="/food" class="w-full text-left group relative overflow-hidden rounded-2xl aspect-[16/9] flex flex-col justify-end p-6 shadow-xl shadow-primary/20 transition-transform active:scale-95">
          <img
            v-if="foodCardImage"
            :src="foodCardImage"
            alt="美食推荐"
            class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            @error="(e) => e.target.style.display = 'none'"
          />
          <div v-else class="absolute inset-0 bg-gradient-to-br from-orange-500 to-red-600"></div>
          <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent"></div>
          <div class="absolute top-4 right-4 bg-white/20 backdrop-blur-md p-2 rounded-full">
            <span class="material-symbols-outlined text-white">restaurant</span>
          </div>
          <div class="relative z-10">
            <p class="text-white/80 text-sm font-medium uppercase tracking-widest">Gourmet Selection</p>
            <h3 class="text-white text-3xl font-black">地道美食推荐</h3>
          </div>
        </router-link>

        <!-- 景点推荐入口 -->
        <router-link to="/attractions" class="w-full text-left group relative overflow-hidden rounded-2xl aspect-[16/9] flex flex-col justify-end p-6 shadow-xl shadow-slate-900/20 transition-transform active:scale-95">
          <img
            v-if="attractionCardImage"
            :src="attractionCardImage"
            alt="景点推荐"
            class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
            @error="(e) => e.target.style.display = 'none'"
          />
          <div v-else class="absolute inset-0 bg-gradient-to-br from-blue-600 to-indigo-700"></div>
          <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent"></div>
          <div class="absolute top-4 right-4 bg-white/20 backdrop-blur-md p-2 rounded-full">
            <span class="material-symbols-outlined text-white">location_city</span>
          </div>
          <div class="relative z-10">
            <p class="text-white/80 text-sm font-medium uppercase tracking-widest">Urban Classics</p>
            <h3 class="text-white text-3xl font-black">城市经典推荐</h3>
          </div>
        </router-link>

        <!-- 票务查询入口 -->
        <router-link to="/monitor" class="w-full text-left group relative overflow-hidden rounded-2xl aspect-[16/9] flex flex-col justify-end p-6 shadow-xl transition-transform active:scale-95 overflow-hidden">
          <img src="/12306.png" alt="票务查询" class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
          <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent"></div>
          <div class="absolute top-4 right-4 bg-white/20 backdrop-blur-md p-2 rounded-full">
            <span class="material-symbols-outlined text-white">train</span>
          </div>
          <div class="relative z-10">
            <p class="text-white/80 text-sm font-medium uppercase tracking-widest">Train Tickets</p>
            <h3 class="text-white text-3xl font-black">票务查询</h3>
          </div>
        </router-link>

        <!-- 攻略推荐入口 -->
        <router-link to="/guide" class="w-full text-left group relative overflow-hidden rounded-2xl aspect-[16/9] flex flex-col justify-end p-6 shadow-xl transition-transform active:scale-95 overflow-hidden">
          <img src="/xiaohongshu.png" alt="小红书攻略笔记" class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" />
          <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent"></div>
          <div class="absolute top-4 right-4 bg-white/20 backdrop-blur-md p-2 rounded-full">
            <span class="material-symbols-outlined text-white">menu_book</span>
          </div>
          <div class="relative z-10">
            <p class="text-white/80 text-sm font-medium uppercase tracking-widest">Xiaohongshu Notes</p>
            <h3 class="text-white text-3xl font-black">小红书攻略笔记</h3>
          </div>
        </router-link>

        <!-- 作者信息 -->
        <div class="mt-4 p-4 rounded-xl bg-slate-100 dark:bg-slate-800/50 text-center">
          <p class="text-xs text-slate-500 dark:text-slate-400">
            作者：<span class="font-medium text-primary">ursuladuva-vibecoding</span> 全栈开发
          </p>
          <p class="text-xs text-slate-400 dark:text-slate-500 mt-1">
            技术栈：Vue 3 + FastAPI + MCP + Multi-Agent + LLM + LangChain + Pinia + Tailwind CSS
          </p>
        </div>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { weatherApi, attractionApi, foodApi } from '@/services/api'

const chatStore = useChatStore()

const currentMonth = ref(new Date().getMonth())
const currentYear = ref(new Date().getFullYear())

const weekDays = ['日', '一', '二', '三', '四', '五', '六']

const tripSpec = computed(() => chatStore.currentTripSpec)
const itinerary = computed(() => chatStore.itinerary)

const dateRange = computed(() => {
  if (tripSpec.value?.start_date && tripSpec.value?.end_date) {
    return `${tripSpec.value.start_date} - ${tripSpec.value.end_date}`
  }
  return '请先在首页设置行程'
})

const currentMonthYear = computed(() => {
  return `${currentYear.value}年${currentMonth.value + 1}月`
})

const todayDate = computed(() => {
  const today = new Date()
  return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
})

const weather = ref({
  city: '',
  temp: '--',
  description: '加载中...',
  realFeel: '--',
  humidity: '--',
  wind: '--',
  tips: '',
})

const weatherLoading = ref(false)
const recommendationsLoading = ref(false)
const foodCardImage = ref('')
const attractionCardImage = ref('')

// Agent 智能推荐
const agentLoading = ref(false)
const agentRecommendations = ref([])

const weatherIcon = computed(() => {
  const desc = weather.value.description
  if (desc.includes('雨')) return 'rainy'
  if (desc.includes('云') || desc.includes('阴')) return 'cloud'
  if (desc.includes('雪')) return 'ac_unit'
  if (desc.includes('雾') || desc.includes('霾')) return 'foggy'
  return 'sunny'
})

const recommendations = ref([])

// 获取第一个景点推荐
const topAttraction = computed(() => {
  return recommendations.value.find(item => item.type === 'attraction') || recommendations.value[0] || null
})

const calendarCells = computed(() => {
  const cells = []
  const firstDay = new Date(currentYear.value, currentMonth.value, 1)
  const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
  const startOffset = firstDay.getDay()

  // 解析行程日期
  let tripStart = null
  let tripEnd = null
  if (tripSpec.value?.start_date && tripSpec.value?.end_date) {
    const startDate = new Date(tripSpec.value.start_date)
    const endDate = new Date(tripSpec.value.end_date)
    if (startDate.getMonth() === currentMonth.value) {
      tripStart = startDate.getDate()
    }
    if (endDate.getMonth() === currentMonth.value) {
      tripEnd = endDate.getDate()
    }
  }

  // 空白格子
  for (let i = 0; i < startOffset; i++) {
    cells.push({ key: `empty-${i}`, day: '', isTripDay: false })
  }

  // 日期格子
  for (let day = 1; day <= lastDay.getDate(); day++) {
    const isTripDay = tripStart !== null && tripEnd !== null && day >= tripStart && day <= tripEnd
    cells.push({
      key: `day-${day}`,
      day,
      isTripDay,
      isTripStart: day === tripStart,
      isTripEnd: day === tripEnd,
    })
  }

  return cells
})

function prevMonth() {
  if (currentMonth.value === 0) {
    currentMonth.value = 11
    currentYear.value--
  } else {
    currentMonth.value--
  }
}

function nextMonth() {
  if (currentMonth.value === 11) {
    currentMonth.value = 0
    currentYear.value++
  } else {
    currentMonth.value++
  }
}

// 获取天气数据 - 获取当天实时天气
async function fetchWeather(city) {
  if (!city) return
  weatherLoading.value = true
  try {
    const data = await weatherApi.getWeather(city)
    console.log('天气数据:', data)
    if (data && data.city) {
      weather.value = {
        city: data.city,
        temp: data.temp ?? '--',
        description: data.description || '未知',
        realFeel: data.realFeel ?? data.temp ?? '--',
        humidity: data.humidity ?? '--',
        wind: data.wind || '微风',
        tips: data.tips || '',
      }
    } else {
      weather.value = {
        city: city,
        temp: '--',
        description: '暂无数据',
        realFeel: '--',
        humidity: '--',
        wind: '--',
        tips: '',
      }
    }
  } catch (error) {
    console.error('获取天气失败:', error)
    weather.value = {
      city: city,
      temp: '--',
      description: '获取失败',
      realFeel: '--',
      humidity: '--',
      wind: '--',
      tips: '',
    }
  } finally {
    weatherLoading.value = false
  }
}

// 获取热门推荐
async function fetchRecommendations(city) {
  if (!city) return
  recommendationsLoading.value = true
  try {
    // 并行获取景点和美食
    const [attractions, foods] = await Promise.all([
      attractionApi.getList(city).catch(() => []),
      foodApi.getList(city).catch(() => []),
    ])

    // 设置卡片图片
    if (foods.length > 0 && foods[0].image) {
      foodCardImage.value = foods[0].image
    }
    if (attractions.length > 0 && attractions[0].image) {
      attractionCardImage.value = attractions[0].image
    }

    // 合并推荐 - 景点排在前面
    const recs = []
    if (attractions.length > 0) {
      recs.push({
        type: 'attraction',
        name: attractions[0].name,
        description: attractions[0].highlights || attractions[0].openTime || '热门景点',
        gradient: attractions[0].gradient,
        image: attractions[0].image,
      })
    }
    if (foods.length > 0) {
      recs.push({
        type: 'food',
        name: foods[0].name,
        description: foods[0].signatureDishes?.join('、') || foods[0].description,
        gradient: foods[0].gradient,
        image: foods[0].image,
      })
    }
    recommendations.value = recs
  } catch (error) {
    console.error('获取推荐失败:', error)
  } finally {
    recommendationsLoading.value = false
  }
}

// 获取 Agent 智能推荐
async function fetchAgentRecommendations() {
  const city = tripSpec.value?.destination_city
  if (!city) return

  agentLoading.value = true
  agentRecommendations.value = []

  try {
    // 并行获取景点、美食、攻略和火车票
    const [attractions, foods, guides, trains] = await Promise.all([
      attractionApi.getList(city).catch(() => []),
      foodApi.getList(city).catch(() => []),
      fetch(`http://localhost:10000/api/guide/${city}`).then(r => r.json()).then(d => d.data || []).catch(() => []),
      // 获取火车票 - 从深圳出发到目的地
      fetch(`http://localhost:10000/api/trains?from_station=深圳&to_station=${city}&date=${tripSpec.value?.start_date || ''}`).then(r => r.json()).then(d => d.data || []).catch(() => []),
    ])

    const recs = []

    // 添加景点推荐 - 增加到5个
    if (attractions.length > 0) {
      const top5 = attractions.slice(0, 5)
      top5.forEach((a, i) => {
        recs.push({
          type: 'attraction',
          title: a.name || `推荐景点 ${i + 1}`,
          description: a.highlights || a.address || '值得游览的热门景点'
        })
      })
    }

    // 添加美食推荐 - 增加到3个
    if (foods.length > 0) {
      const top3 = foods.slice(0, 3)
      top3.forEach((f, i) => {
        recs.push({
          type: 'food',
          title: f.name || `推荐美食 ${i + 1}`,
          description: f.signatureDishes?.join('、') || f.description || '当地特色美食'
        })
      })
    }

    // 添加攻略推荐
    if (guides.length > 0) {
      guides.slice(0, 2).forEach(g => {
        recs.push({
          type: 'tip',
          title: g.title || '旅游攻略',
          description: g.description || g.content?.substring(0, 50) || '精选旅游攻略'
        })
      })
    }

    // 添加火车票推荐 - 推荐上午10点左右的车次
    if (trains.length > 0) {
      // 筛选上午9-11点的车次
      const morningTrains = trains.filter(t => {
        const hour = parseInt(t.start_time?.split(':')[0] || '0')
        return hour >= 9 && hour <= 11
      })

      // 如果没有上午车次，找最接近10点的
      let recommendedTrain = morningTrains[0]
      if (!recommendedTrain) {
        // 找最接近10点的车次
        let minDiff = 24
        trains.forEach(t => {
          const hour = parseInt(t.start_time?.split(':')[0] || '0')
          const diff = Math.abs(hour - 10)
          if (diff < minDiff) {
            minDiff = diff
            recommendedTrain = t
          }
        })
      }

      if (recommendedTrain) {
        const seatInfo = recommendedTrain.seats?.slice(0, 2).map(s => `${s.name}: ${s.count_display || s.count + '张'}`).join('、') || '有票'
        recs.push({
          type: 'transport',
          title: `推荐车次 ${recommendedTrain.train_no}`,
          description: `${recommendedTrain.from_station}→${recommendedTrain.to_station} ${recommendedTrain.start_time}出发 ${recommendedTrain.duration} | ${seatInfo}`
        })
      }

      // 再推荐一个备选车次
      const afternoonTrains = trains.filter(t => {
        const hour = parseInt(t.start_time?.split(':')[0] || '0')
        return hour >= 13 && hour <= 15
      })
      if (afternoonTrains[0] && afternoonTrains[0] !== recommendedTrain) {
        const seatInfo = afternoonTrains[0].seats?.slice(0, 2).map(s => `${s.name}: ${s.count_display || s.count + '张'}`).join('、') || '有票'
        recs.push({
          type: 'transport',
          title: `备选车次 ${afternoonTrains[0].train_no}`,
          description: `${afternoonTrains[0].from_station}→${afternoonTrains[0].to_station} ${afternoonTrains[0].start_time}出发 | ${seatInfo}`
        })
      }
    }

    // 添加旅行贴士
    if (tripSpec.value?.start_date) {
      const startDate = new Date(tripSpec.value.start_date)
      const month = startDate.getMonth() + 1
      let tip = ''
      if (month >= 3 && month <= 5) {
        tip = '春季出行，建议携带轻薄外套，注意花粉过敏'
      } else if (month >= 6 && month <= 8) {
        tip = '夏季出行，注意防晒防暑，建议携带遮阳伞'
      } else if (month >= 9 && month <= 11) {
        tip = '秋季出行，天气宜人，是旅游的好季节'
      } else {
        tip = '冬季出行，注意保暖，建议携带厚外套'
      }
      recs.push({
        type: 'tip',
        title: '出行贴士',
        description: tip
      })
    }

    agentRecommendations.value = recs
  } catch (error) {
    console.error('获取Agent推荐失败:', error)
    agentRecommendations.value = [
      { type: 'tip', title: '出行建议', description: '建议提前规划行程，预订酒店和交通' },
      { type: 'tip', title: '注意事项', description: '出行前检查天气，携带必要物品' }
    ]
  } finally {
    agentLoading.value = false
  }
}

// 监听目的地变化
watch(
  () => tripSpec.value?.destination_city,
  (newCity, oldCity) => {
    if (newCity && newCity !== oldCity) {
      console.log('目的地变化:', newCity)  // 调试日志
      fetchWeather(newCity)
      fetchRecommendations(newCity)
    }
  },
  { immediate: true }
)

onMounted(() => {
  // 显式初始化 store 从 localStorage
  chatStore.init()
  console.log('当前 tripSpec:', chatStore.currentTripSpec)  // 调试日志

  // 直接检查目的地并获取数据
  const city = chatStore.currentTripSpec?.destination_city
  if (city) {
    console.log('加载城市数据:', city)
    fetchWeather(city)
    fetchRecommendations(city)
  }
})
</script>