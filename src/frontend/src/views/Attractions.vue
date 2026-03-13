<template>
  <div class="min-h-screen bg-white font-display text-slate-900">
    <div class="relative flex flex-col min-h-screen w-full overflow-x-hidden">
      <div class="layout-container flex h-full grow flex-col">
        <div class="px-4 md:px-20 lg:px-40 flex flex-1 justify-center py-5">
          <div class="layout-content-container flex flex-col max-w-[960px] flex-1">
            <!-- 顶部导航 -->
            <header class="flex items-center justify-between whitespace-nowrap border-b border-solid border-primary/20 px-4 py-4 mb-6">
              <router-link to="/" class="flex items-center gap-4 hover:opacity-80 transition-opacity">
                <div class="size-8 bg-primary rounded-lg flex items-center justify-center text-white">
                  <span class="material-symbols-outlined">explore</span>
                </div>
                <h2 class="text-slate-900 dark:text-slate-100 text-xl font-bold leading-tight tracking-tight">景点推荐</h2>
              </router-link>
              <div class="flex gap-3">
                <router-link to="/trip" class="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-white hover:bg-primary/90 transition-colors">
                  <span class="material-symbols-outlined">calendar_today</span>
                  <span class="text-sm font-medium">返回行程</span>
                </router-link>
                <router-link to="/" class="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary/10 dark:bg-primary/20 text-primary hover:bg-primary/20 dark:hover:bg-primary/30 transition-colors">
                  <span class="material-symbols-outlined">home</span>
                  <span class="text-sm font-medium">返回首页</span>
                </router-link>
                <button class="flex items-center justify-center rounded-xl size-10 bg-primary/10 dark:bg-primary/20 text-primary hover:bg-primary/20 transition-colors">
                  <span class="material-symbols-outlined">search</span>
                </button>
              </div>
            </header>

            <!-- 标题区 -->
            <div class="flex flex-col gap-6 mb-8 px-4">
              <div class="flex flex-col gap-2">
                <h1 class="text-slate-900 dark:text-slate-100 text-4xl font-black leading-tight tracking-tight">城市经典推荐</h1>
                <p class="text-slate-600 dark:text-primary/70 text-lg font-normal">为您精选的必游之地，领略城市底蕴</p>
              </div>
            </div>

            <!-- 景点卡片 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6 px-4 pb-24">
              <div v-if="attractions.length === 0 && !loading" class="col-span-2 text-center py-16 text-slate-400">
                <span class="material-symbols-outlined text-5xl mb-4 block">explore_off</span>
                <p>请先在首页设置目的地</p>
              </div>
              <div
                v-for="attraction in attractions"
                :key="attraction.id"
                class="group flex flex-col bg-white dark:bg-primary/5 rounded-xl overflow-hidden border border-slate-200 dark:border-primary/10 hover:border-primary/50 transition-all shadow-sm"
              >
                <div class="h-56 w-full overflow-hidden relative">
                  <img
                    v-if="attraction.image"
                    :src="attraction.image"
                    :alt="attraction.name"
                    class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                    @error="(e) => e.target.style.display = 'none'"
                  />
                  <div
                    v-else
                    class="w-full h-full transition-transform duration-500 group-hover:scale-105"
                    :style="{ background: attraction.gradient }"
                  ></div>
                  <div class="absolute top-4 left-4 bg-primary text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                    {{ attraction.tags?.[0] || '景点' }}
                  </div>
                </div>
                <div class="p-6 flex flex-col gap-4">
                  <div class="flex justify-between items-start">
                    <h3 class="text-2xl font-bold text-slate-900 dark:text-slate-100">{{ attraction.name }}</h3>
                    <span class="flex items-center text-amber-500 font-bold">
                      <span class="material-symbols-outlined fill-icon text-sm mr-1">star</span>{{ attraction.rating }}
                    </span>
                  </div>
                  <div class="flex flex-col gap-3">
                    <div class="flex items-center gap-2 text-slate-600 dark:text-slate-400 text-sm">
                      <span class="material-symbols-outlined text-lg text-primary">location_on</span>
                      <span>{{ attraction.address || attraction.openTime }}</span>
                    </div>
                    <div class="flex items-center gap-2 text-slate-600 dark:text-slate-400 text-sm">
                      <span class="material-symbols-outlined text-lg text-primary">sell</span>
                      <span>{{ attraction.ticketPrice || '请咨询' }}</span>
                    </div>
                  </div>
                  <button class="mt-2 w-full bg-primary hover:bg-primary/90 text-white font-bold py-3 rounded-lg transition-colors flex items-center justify-center gap-2">
                    查看详情 <span class="material-symbols-outlined text-lg">arrow_forward</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <nav class="fixed bottom-6 left-1/2 -translate-x-1/2 w-[90%] max-w-md bg-white/80 dark:bg-background-dark/80 backdrop-blur-lg border border-slate-200 dark:border-primary/20 rounded-full shadow-2xl px-8 py-4 flex justify-between items-center z-50">
      <router-link to="/" class="flex flex-col items-center gap-1 group cursor-pointer">
        <span class="material-symbols-outlined text-slate-400 group-hover:text-primary transition-colors">home</span>
        <span class="text-[10px] font-bold text-slate-400 group-hover:text-primary uppercase tracking-tighter">首页</span>
      </router-link>
      <router-link to="/trip" class="flex flex-col items-center gap-1 group cursor-pointer">
        <span class="material-symbols-outlined text-primary fill-icon">calendar_today</span>
        <span class="text-[10px] font-bold text-primary uppercase tracking-tighter">行程</span>
      </router-link>
      <router-link to="/profile" class="flex flex-col items-center gap-1 group cursor-pointer">
        <span class="material-symbols-outlined text-slate-400 group-hover:text-primary transition-colors">person</span>
        <span class="text-[10px] font-bold text-slate-400 group-hover:text-primary uppercase tracking-tighter">我的</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { attractionApi } from '@/services/api'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const tripSpec = computed(() => chatStore.currentTripSpec)

const attractions = ref([])
const loading = ref(false)

// 根据目的地获取景点数据
async function fetchAttractions() {
  const city = tripSpec.value?.destination_city
  if (!city) return

  loading.value = true
  try {
    const data = await attractionApi.getList(city)
    attractions.value = data
  } catch (error) {
    console.error('获取景点失败:', error)
    attractions.value = []
  } finally {
    loading.value = false
  }
}

// 监听目的地变化
import { watch } from 'vue'
watch(() => tripSpec.value?.destination_city, (newCity) => {
  if (newCity) {
    fetchAttractions()
  }
}, { immediate: true })

onMounted(() => {
  if (tripSpec.value?.destination_city) {
    fetchAttractions()
  }
})
</script>