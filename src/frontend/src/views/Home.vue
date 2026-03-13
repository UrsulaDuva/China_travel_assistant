<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark">
    <!-- 顶部导航 -->
    <header class="sticky top-0 z-50 w-full border-b border-primary/30 backdrop-blur-xl bg-white/60">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <span class="material-symbols-outlined text-primary text-3xl">explore</span>
          <h1 class="text-3xl font-black tracking-tight text-primary">旅行智囊</h1>
          <span class="ml-2 px-2 py-1 bg-primary/10 text-primary text-xs font-bold rounded-full">Multi-Agent</span>
        </div>
        <nav class="hidden md:flex items-center gap-8">
          <router-link to="/" class="text-base font-bold hover:text-primary transition-colors text-slate-700">首页</router-link>
          <router-link to="/trip" class="text-base font-bold hover:text-primary transition-colors text-slate-700">行程规划</router-link>
          <router-link to="/monitor" class="text-base font-bold hover:text-primary transition-colors text-slate-700">票务查询</router-link>
          <router-link to="/food" class="text-base font-bold hover:text-primary transition-colors text-slate-700">美食推荐</router-link>
          <router-link to="/attractions" class="text-base font-bold hover:text-primary transition-colors text-slate-700">景点推荐</router-link>
        </nav>
        <div class="flex items-center gap-4">
          <router-link to="/profile" class="h-10 w-10 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center overflow-hidden">
            <span class="material-symbols-outlined text-primary">person</span>
          </router-link>
        </div>
      </div>
    </header>

    <!-- Hero 区域 -->
    <section class="relative py-16 px-4 overflow-hidden">
      <!-- 背景图片 -->
      <div class="absolute inset-0 z-0">
        <img src="/local.png" alt="背景" class="w-full h-full object-cover" />
        <div class="absolute inset-0 bg-gradient-to-b from-black/70 via-black/50 to-black/80"></div>
      </div>

      <div class="max-w-5xl mx-auto relative z-10">
        <!-- 标题区域 -->
        <div class="text-center mb-8">
          <h2 class="text-5xl md:text-7xl font-black text-white mb-4 leading-tight">
            AI 驱动的<br/>中国旅行规划专家
          </h2>
          <p class="text-lg md:text-xl text-slate-200 font-medium mb-2">
            智能行程规划 · 票务监控 · 美食推荐 · 一键搞定
          </p>
          <p class="text-sm text-slate-300">
            Powered by LangChain + Multi-Agent + MCP
          </p>
        </div>

        <!-- 对话区域 -->
        <div class="bg-white/20 backdrop-blur-xl rounded-3xl shadow-2xl overflow-hidden">
          <!-- 对话消息列表 -->
          <div ref="messageContainer" class="max-h-[450px] overflow-y-auto p-6 space-y-4">
            <div v-if="messages.length === 0" class="text-center py-8">
              <div class="w-20 h-20 mx-auto mb-4 bg-primary/10 rounded-full flex items-center justify-center">
                <span class="material-symbols-outlined text-primary text-4xl">travel_explore</span>
              </div>
              <p class="text-slate-500 font-medium">请告诉我您的旅行计划</p>
              <p class="text-slate-400 text-sm mt-2">例如：上海、北京、杭州...</p>
            </div>

            <div
              v-for="msg in messages"
              :key="msg.id"
              :class="['flex', msg.role === 'user' ? 'justify-end' : 'justify-start']"
            >
              <div
                :class="[
                  'max-w-[85%] rounded-2xl px-5 py-3',
                  msg.role === 'user'
                    ? 'bg-primary text-white rounded-br-md'
                    : 'bg-slate-100 text-slate-800 rounded-bl-md'
                ]"
              >
                <div class="whitespace-pre-wrap text-sm leading-relaxed">{{ msg.content }}</div>
              </div>
            </div>

            <!-- 加载动画 -->
            <div v-if="isLoading" class="flex justify-start">
              <div class="bg-slate-100 rounded-2xl px-5 py-3 rounded-bl-md">
                <div class="flex items-center gap-2">
                  <div class="flex gap-1">
                    <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 0ms"></div>
                    <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 150ms"></div>
                    <div class="w-2 h-2 bg-primary rounded-full animate-bounce" style="animation-delay: 300ms"></div>
                  </div>
                  <span class="text-sm text-slate-500">AI 正在思考...</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 输入框 -->
          <div class="border-t border-slate-200 p-4">
            <div class="flex items-center gap-3">
              <div class="flex-1 flex items-center bg-slate-100 rounded-full px-4">
                <span class="material-symbols-outlined text-slate-400 text-xl">chat</span>
                <input
                  v-model="searchQuery"
                  @keyup.enter="handleSearch"
                  class="w-full bg-transparent border-none focus:outline-none text-slate-900 placeholder:text-slate-400 text-sm py-3 caret-primary caret-2"
                  placeholder="输入目的地、日期、人数，如：上海3月15号出发玩5天"
                  type="text"
                />
              </div>
              <button
                @click="handleSearch"
                :disabled="isLoading"
                class="bg-primary hover:bg-primary/90 text-white px-6 py-3 rounded-full font-bold text-sm transition-all flex items-center gap-2"
              >
                <span v-if="isLoading">处理中</span>
                <span v-else>发送</span>
                <span class="material-symbols-outlined text-lg">send</span>
              </button>
              <button
                v-if="currentTripSpec?.destination_city && currentTripSpec?.start_date"
                @click="goToTrip"
                class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-full font-bold text-sm transition-all flex items-center gap-2"
              >
                <span class="material-symbols-outlined text-lg">calendar_month</span>
                查看行程
              </button>
            </div>

            <!-- 快捷推荐 -->
            <div class="flex flex-wrap gap-2 mt-3">
              <button @click="quickSearch('上海')" class="px-3 py-1 bg-slate-100 hover:bg-primary/10 text-slate-600 hover:text-primary rounded-full text-xs font-medium transition-colors">
                上海
              </button>
              <button @click="quickSearch('北京')" class="px-3 py-1 bg-slate-100 hover:bg-primary/10 text-slate-600 hover:text-primary rounded-full text-xs font-medium transition-colors">
                北京
              </button>
              <button @click="quickSearch('杭州')" class="px-3 py-1 bg-slate-100 hover:bg-primary/10 text-slate-600 hover:text-primary rounded-full text-xs font-medium transition-colors">
                杭州
              </button>
              <button @click="quickSearch('成都')" class="px-3 py-1 bg-slate-100 hover:bg-primary/10 text-slate-600 hover:text-primary rounded-full text-xs font-medium transition-colors">
                成都
              </button>
              <button @click="quickSearch('西安')" class="px-3 py-1 bg-slate-100 hover:bg-primary/10 text-slate-600 hover:text-primary rounded-full text-xs font-medium transition-colors">
                西安
              </button>
            </div>
          </div>
        </div>

        <!-- 当前行程信息 -->
        <div v-if="currentTripSpec?.destination_city" class="mt-4 bg-white/90 backdrop-blur-xl rounded-xl p-4 shadow-lg border border-primary/20 max-w-md mx-auto">
          <div class="flex items-center gap-4">
            <div class="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center">
              <span class="material-symbols-outlined text-primary text-2xl">location_on</span>
            </div>
            <div class="flex-1">
              <p class="text-xs text-slate-500">当前目的地</p>
              <p class="font-bold text-lg text-slate-800">{{ currentTripSpec.destination_city }}</p>
            </div>
            <div v-if="currentTripSpec.start_date" class="text-right">
              <p class="text-xs text-slate-500">{{ currentTripSpec.start_date }}</p>
              <p class="text-xs text-slate-400" v-if="currentTripSpec.end_date">至 {{ currentTripSpec.end_date }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 核心功能 -->
    <section class="py-16 px-4 max-w-7xl mx-auto">
      <div class="flex items-center gap-3 mb-10">
        <div class="h-8 w-1.5 bg-primary rounded-full"></div>
        <h3 class="text-3xl font-black text-slate-900">核心功能</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          v-for="feature in features"
          :key="feature.title"
          class="bg-white p-8 rounded-2xl border border-slate-200 hover:border-primary/40 transition-all group shadow-lg"
        >
          <div class="w-16 h-16 bg-primary/10 rounded-xl flex items-center justify-center text-primary mb-6 group-hover:scale-110 transition-transform">
            <span class="material-symbols-outlined text-4xl">{{ feature.icon }}</span>
          </div>
          <h4 class="text-xl font-bold mb-3 text-slate-800">{{ feature.title }}</h4>
          <p class="text-slate-600 text-sm leading-relaxed">{{ feature.description }}</p>
        </div>
      </div>
    </section>

    <!-- 热门目的地 -->
    <section class="py-16 bg-primary/5 px-4">
      <div class="max-w-7xl mx-auto">
        <div class="mb-10">
          <div class="flex items-center gap-3 mb-3">
            <div class="h-8 w-1.5 bg-primary rounded-full"></div>
            <h3 class="text-3xl font-black text-slate-900">热门目的地</h3>
          </div>
          <p class="text-slate-500 font-medium">挑选您心仪的城市，开启AI定制之旅</p>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div
            v-for="dest in destinations"
            :key="dest.name"
            class="group relative overflow-hidden rounded-2xl h-80 cursor-pointer"
            @click="quickSearch(dest.name)"
          >
            <img
              v-if="dest.image"
              :src="dest.image"
              :alt="dest.name"
              class="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              @error="(e) => e.target.style.display = 'none'"
            />
            <div
              v-if="!dest.image"
              class="absolute inset-0 transition-transform duration-500 group-hover:scale-110"
              :style="{ background: dest.gradient }"
            ></div>
            <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent"></div>
            <div class="absolute bottom-6 left-6 text-white">
              <span class="px-2 py-1 rounded-full bg-primary text-xs font-bold">{{ dest.tag }}</span>
              <h5 class="text-2xl font-bold mt-2">{{ dest.name }}</h5>
              <p class="text-slate-200 text-sm mt-1">{{ dest.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 底部 -->
    <footer class="bg-slate-900 text-white py-12 px-4">
      <div class="max-w-7xl mx-auto text-center">
        <div class="flex items-center justify-center gap-2 mb-4">
          <span class="material-symbols-outlined text-primary text-2xl">explore</span>
          <span class="text-xl font-bold">旅行智囊</span>
        </div>
        <p class="text-slate-400 text-sm mb-2">AI智行，懂中国，更懂你</p>
        <p class="text-xs text-slate-500">
          技术栈：Vue 3 + FastAPI + MCP + Multi-Agent + LLM + LangChain + Pinia + Tailwind CSS
        </p>
        <p class="text-xs text-slate-500 mt-2">
          作者：ursuladuva-vibecoding 全栈开发
        </p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useChatStore } from '@/stores/chat'
import { destinationApi } from '@/services/api'

const router = useRouter()
const chatStore = useChatStore()

const searchQuery = ref('')
const destinations = ref([])
const isLoading = ref(false)
const messageContainer = ref(null)

// 计算属性
const messages = computed(() => chatStore.messages)
const currentTripSpec = computed(() => chatStore.currentTripSpec)

const features = [
  {
    icon: 'auto_awesome',
    title: 'AI 智能规划',
    description: 'Multi-Agent 协作，智能分析需求，生成个性化行程方案。',
  },
  {
    icon: 'train',
    title: '票务监控',
    description: '12306 实时数据，高铁余票动态监控，自动提醒。',
  },
  {
    icon: 'restaurant',
    title: '美食推荐',
    description: '基于真实口碑，发掘地道美味，定制专属美食清单。',
  },
  {
    icon: 'attractions',
    title: '景点攻略',
    description: '抖音达人推荐，热门景点一键获取，出行无忧。',
  },
]

onMounted(async () => {
  destinations.value = await destinationApi.getHotDestinations()
})

// 自动滚动到底部
watch(messages, async () => {
  await nextTick()
  if (messageContainer.value) {
    messageContainer.value.scrollTop = messageContainer.value.scrollHeight
  }
}, { deep: true })

async function handleSearch() {
  if (!searchQuery.value.trim()) return
  isLoading.value = true
  const query = searchQuery.value
  searchQuery.value = ''

  try {
    await chatStore.sendMessage(query)
  } catch (error) {
    console.error('发送失败:', error)
  } finally {
    isLoading.value = false
  }
}

async function quickSearch(query) {
  searchQuery.value = query
  await handleSearch()
}

function goToTrip() {
  router.push('/trip')
}
</script>