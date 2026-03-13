<template>
  <div class="min-h-screen bg-background-light dark:bg-background-dark font-display text-slate-900">
    <!-- Sticky Navigation -->
    <nav class="glass-header sticky top-0 z-50 border-b border-primary/20 px-4 py-3">
      <div class="max-w-4xl mx-auto flex items-center justify-between">
        <router-link to="/trip" class="flex items-center gap-2 text-slate-100 hover:text-primary transition-colors">
          <span class="material-symbols-outlined">arrow_back</span>
          <span class="font-medium">返回行程详情</span>
        </router-link>
        <div class="flex items-center gap-4">
          <button class="flex items-center justify-center p-2 rounded-xl bg-primary/10 text-primary hover:bg-primary/20 transition-all">
            <span class="material-symbols-outlined">bookmark</span>
          </button>
          <button class="flex items-center justify-center p-2 rounded-xl bg-primary/10 text-primary hover:bg-primary/20 transition-all">
            <span class="material-symbols-outlined">share</span>
          </button>
        </div>
      </div>
    </nav>

    <main class="golden-gradient min-h-screen pb-20 pt-6 px-4">
      <div class="max-w-4xl mx-auto">
        <!-- Main Content Card -->
        <article class="bg-background-light dark:bg-[#2d1616] rounded-2xl overflow-hidden shadow-2xl border border-primary/10">
          <!-- Hero Image Container -->
          <div class="relative h-[400px] w-full overflow-hidden">
            <img
              :src="heroImage"
              :alt="city + '旅游攻略'"
              class="w-full h-full object-cover"
              @error="(e) => e.target.src = 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=800&q=80'"
            />
            <div class="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-8">
              <div>
                <span class="inline-block px-3 py-1 bg-primary text-white text-xs font-bold rounded-full mb-4 uppercase tracking-wider">深度指南</span>
                <h1 class="text-4xl md:text-5xl font-bold text-white leading-tight">{{ city }}旅游全攻略</h1>
              </div>
            </div>
          </div>

          <!-- Article Content -->
          <div class="p-8 md:p-12 space-y-8">
            <!-- Meta Info -->
            <div class="flex flex-wrap items-center gap-6 text-slate-500 dark:text-slate-400 border-b border-primary/10 pb-6">
              <div class="flex items-center gap-2">
                <div class="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary overflow-hidden">
                  <span class="material-symbols-outlined">person</span>
                </div>
                <span class="font-medium text-slate-900 dark:text-slate-100">小红书攻略笔记</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">calendar_today</span>
                <span>{{ todayDate }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="material-symbols-outlined text-sm">visibility</span>
                <span>{{ totalViews }} 次阅读</span>
              </div>
            </div>

            <!-- Intro Section -->
            <section class="prose dark:prose-invert max-w-none">
              <p class="text-xl leading-relaxed text-slate-700 dark:text-slate-300">
                为您精选{{ city }}最热门的旅游攻略，来自小红书博主的亲身体验分享。从必游景点到地道美食，从交通出行到住宿推荐，一站式解决您的旅行规划需求。
              </p>
            </section>

            <!-- Loading State -->
            <div v-if="loading" class="flex flex-col items-center justify-center py-16">
              <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent"></div>
              <p class="mt-4 text-slate-500">正在加载攻略...</p>
            </div>

            <!-- Empty State -->
            <div v-else-if="guides.length === 0" class="text-center py-16 text-slate-400">
              <span class="material-symbols-outlined text-5xl mb-4 block">explore_off</span>
              <p>请先在首页设置目的地</p>
              <router-link to="/" class="mt-4 inline-block px-6 py-2 bg-primary text-white rounded-xl">
                前往首页
              </router-link>
            </div>

            <!-- Guide List -->
            <div v-else class="space-y-8">
              <section v-for="(guide, index) in guides" :key="guide.id" class="space-y-4 border-b border-slate-200 dark:border-slate-700 pb-8 last:border-b-0">
                <!-- 标题和封面 -->
                <div class="flex gap-4">
                  <img
                    :src="guide.cover || '/xiaohongshu.png'"
                    :alt="guide.title"
                    class="w-32 h-24 rounded-xl object-cover flex-shrink-0"
                    @error="(e) => e.target.src = '/xiaohongshu.png'"
                  />
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2">
                      <span class="w-8 h-8 rounded-lg bg-primary flex items-center justify-center text-white text-sm font-bold">{{ index + 1 }}</span>
                      <h2 class="text-xl font-bold text-slate-900 dark:text-slate-100">{{ guide.title }}</h2>
                    </div>
                    <p class="text-slate-600 dark:text-slate-400">{{ guide.description }}</p>
                  </div>
                </div>

                <!-- 作者信息 -->
                <div class="flex items-center gap-4 text-sm text-slate-500">
                  <div class="flex items-center gap-2">
                    <div class="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
                      <span class="material-symbols-outlined text-primary text-sm">person</span>
                    </div>
                    <span class="text-primary font-medium">@{{ guide.author }}</span>
                  </div>
                  <span class="flex items-center gap-1">
                    <span class="material-symbols-outlined text-primary text-base">favorite</span>
                    {{ formatNumber(guide.likes) }}
                  </span>
                  <span class="flex items-center gap-1">
                    <span class="material-symbols-outlined text-primary text-base">visibility</span>
                    {{ formatNumber(guide.views) }}
                  </span>
                </div>

                <!-- 标签 -->
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="tag in guide.tags"
                    :key="tag"
                    class="px-3 py-1 bg-primary/10 text-primary text-xs rounded-full font-medium"
                  >
                    #{{ tag }}
                  </span>
                </div>

                <!-- 详细内容 - 美化显示 -->
                <div v-if="guide.content" class="mt-4 p-6 bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-800/50 dark:to-slate-700/50 rounded-2xl border border-slate-200 dark:border-slate-600">
                  <div class="prose prose-slate dark:prose-invert max-w-none">
                    <div class="whitespace-pre-wrap text-sm text-slate-700 dark:text-slate-300 leading-relaxed font-sans" v-html="formatContent(guide.content)"></div>
                  </div>
                </div>
              </section>
            </div>

            <!-- Interactive Footer -->
            <div class="pt-10 border-t border-primary/10 flex flex-col md:flex-row items-center justify-between gap-6">
              <div class="flex items-center gap-4">
                <router-link to="/" class="px-8 py-3 bg-primary text-white font-bold rounded-xl flex items-center gap-2 hover:bg-primary/90 transition-all shadow-lg shadow-primary/20">
                  <span class="material-symbols-outlined">home</span>
                  返回首页规划
                </router-link>
                <router-link to="/trip" class="px-8 py-3 border border-primary/30 rounded-xl flex items-center gap-2 text-primary hover:bg-primary/5 transition-all">
                  <span class="material-symbols-outlined">calendar_today</span>
                  查看行程
                </router-link>
              </div>
            </div>
          </div>
        </article>

        <!-- Related Guides -->
        <div class="mt-12 space-y-6" v-if="relatedCities.length > 0">
          <h3 class="text-2xl font-bold text-white">相关目的地攻略</h3>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <router-link
              v-for="related in relatedCities"
              :key="related.name"
              :to="'/guide'"
              @click="refreshGuides(related.name)"
              class="bg-background-light dark:bg-[#2d1616] rounded-xl overflow-hidden border border-primary/10 group cursor-pointer"
            >
              <div class="h-40 overflow-hidden">
                <img
                  :src="related.image"
                  :alt="related.name"
                  class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  @error="(e) => e.target.style.display = 'none'"
                />
              </div>
              <div class="p-4">
                <h4 class="font-bold text-slate-900 dark:text-slate-100 line-clamp-1">{{ related.name }}旅游攻略</h4>
                <p class="text-xs text-slate-500 mt-2">{{ related.views }} 次阅读</p>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useChatStore } from '@/stores/chat'
import { guideApi } from '@/services/api'

const chatStore = useChatStore()
const tripSpec = computed(() => chatStore.currentTripSpec)

const guides = ref([])
const loading = ref(false)
const city = computed(() => tripSpec.value?.destination_city || '中国')

const heroImages = {
  '北京': 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&q=80',
  '上海': 'https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?w=800&q=80',
  '成都': 'https://images.unsplash.com/photo-1590559899731-a382839e5549?w=800&q=80',
  '杭州': 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800&q=80',
}

const heroImage = computed(() => {
  return heroImages[city.value] || '/xiaohongshu.png'
})

const todayDate = computed(() => {
  const today = new Date()
  return `${today.getFullYear()}年${today.getMonth() + 1}月${today.getDate()}日`
})

const totalViews = computed(() => {
  return guides.value.reduce((sum, g) => sum + (g.views || 0), 0)
})

const relatedCities = computed(() => {
  const allCities = [
    { name: '北京', image: 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=400&q=80', views: '32.5k' },
    { name: '上海', image: 'https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?w=400&q=80', views: '28.3k' },
    { name: '成都', image: 'https://images.unsplash.com/photo-1590559899731-a382839e5549?w=400&q=80', views: '45.2k' },
    { name: '杭州', image: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400&q=80', views: '18.7k' },
    { name: '西安', image: '', views: '15.3k' },
    { name: '广州', image: '', views: '22.1k' },
  ]
  return allCities.filter(c => c.name !== city.value).slice(0, 3)
})

function formatNumber(num) {
  if (!num) return '0'
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'k'
  }
  return num.toString()
}

function formatContent(content) {
  if (!content) return ''
  return content
    .replace(/\n/g, '<br>')
    .replace(/【(.+?)】/g, '<strong class="text-primary text-lg">$1</strong>')
    .replace(/([🎫🚶📸💡🚇🏮🍜⏰🌅🗺️🏛️🏖️🎢⚡🎆💰🥟🍢🔥📍♨️🏛️🏞️🚲])/g, '<span class="text-xl">$1</span>')
}

async function fetchGuides() {
  const targetCity = city.value
  if (!targetCity || targetCity === '中国') {
    guides.value = []
    return
  }

  loading.value = true
  try {
    const data = await guideApi.getGuides(targetCity)
    guides.value = data
  } catch (error) {
    console.error('获取攻略失败:', error)
    guides.value = []
  } finally {
    loading.value = false
  }
}

function refreshGuides(newCity) {
  // This would refresh the page with a new city
  // For now, we'll just trigger a re-fetch
  if (newCity) {
    fetchGuides()
  }
}

watch(() => tripSpec.value?.destination_city, (newCity) => {
  if (newCity) {
    fetchGuides()
  }
}, { immediate: true })

onMounted(() => {
  chatStore.init()
  if (city.value && city.value !== '中国') {
    fetchGuides()
  }
})
</script>

<style scoped>
.glass-header {
  background: rgba(34, 16, 16, 0.8);
  backdrop-filter: blur(12px);
}
.golden-gradient {
  background: radial-gradient(circle at top right, #482323, #221010);
}
</style>