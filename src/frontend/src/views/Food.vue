<template>
  <div class="min-h-screen bg-white font-display text-slate-900">
    <div class="relative flex min-h-screen flex-col overflow-x-hidden">
      <div class="layout-container flex h-full grow flex-col">
        <div class="px-4 md:px-20 lg:px-40 flex flex-1 justify-center py-5">
          <div class="layout-content-container flex flex-col max-w-[960px] flex-1">
            <!-- 顶部导航 -->
            <header class="flex items-center justify-between whitespace-nowrap border-b border-solid border-primary/20 px-4 py-4 mb-6">
              <router-link to="/" class="flex items-center gap-4 hover:opacity-80 transition-opacity">
                <div class="size-8 bg-primary rounded-lg flex items-center justify-center text-white">
                  <span class="material-symbols-outlined">restaurant_menu</span>
                </div>
                <h2 class="text-slate-900 dark:text-slate-100 text-xl font-bold leading-tight tracking-tight">美食推荐</h2>
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
                <h1 class="text-slate-900 dark:text-slate-100 text-4xl font-black leading-tight tracking-tight">地道美食推荐</h1>
                <p class="text-slate-600 dark:text-primary/70 text-lg font-normal">探索城市深处的至臻美味，品味非遗文化</p>
              </div>
            </div>

            <!-- 餐厅卡片 -->
            <div class="flex flex-col gap-8 px-4 pb-12">
              <div v-if="restaurants.length === 0 && !loading" class="text-center py-16 text-slate-400">
                <span class="material-symbols-outlined text-5xl mb-4 block">restaurant_menu</span>
                <p>请先在首页设置目的地</p>
              </div>
              <div
                v-for="restaurant in restaurants"
                :key="restaurant.id"
                class="group flex flex-col @container overflow-hidden rounded-xl border border-primary/10 bg-white dark:bg-primary/5 shadow-xl hover:shadow-primary/10 transition-all duration-300"
              >
                <div class="flex flex-col @[800px]:flex-row">
                  <div class="w-full @[800px]:w-2/5 aspect-[4/3] @[800px]:aspect-auto overflow-hidden">
                    <img
                      v-if="restaurant.image"
                      :src="restaurant.image"
                      :alt="restaurant.name"
                      class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                      @error="(e) => e.target.style.display = 'none'"
                    />
                    <div
                      v-else
                      class="w-full h-full transition-transform duration-500 group-hover:scale-105"
                      :style="{ background: restaurant.gradient }"
                    ></div>
                  </div>
                  <div class="flex-1 p-6 md:p-8 flex flex-col justify-between">
                    <div>
                      <div class="flex items-center gap-2 mb-3">
                        <span class="px-2 py-1 rounded bg-primary/10 text-primary text-xs font-bold uppercase tracking-widest">{{ restaurant.tags?.[0] || '推荐' }}</span>
                        <span class="text-primary/60 text-sm flex items-center gap-1">
                          <span class="material-symbols-outlined text-sm">location_on</span> {{ restaurant.area }}
                        </span>
                      </div>
                      <h3 class="text-slate-900 dark:text-slate-100 text-3xl font-black leading-tight mb-4">{{ restaurant.name }}</h3>
                      <div class="flex items-center gap-4 mb-6">
                        <div class="flex items-center gap-1 bg-primary text-white px-2 py-1 rounded-lg">
                          <span class="material-symbols-outlined text-sm fill-icon">star</span>
                          <span class="text-sm font-bold">{{ restaurant.rating }}</span>
                        </div>
                        <p class="text-primary/70 text-sm font-medium border-l border-primary/20 pl-4">
                          人均 ¥{{ restaurant.avgPrice }}
                        </p>
                      </div>
                      <div class="space-y-4">
                        <div>
                          <p class="text-slate-500 dark:text-slate-400 text-xs font-bold uppercase tracking-wider mb-2">特色</p>
                          <div class="flex flex-wrap gap-2">
                            <span v-for="dish in restaurant.signatureDishes?.slice(0, 3)" :key="dish" class="px-3 py-1 rounded-full border border-primary/20 bg-primary/5 text-sm font-medium">
                              {{ dish }}
                            </span>
                          </div>
                        </div>
                        <p class="text-slate-600 dark:text-slate-300 leading-relaxed">
                          {{ restaurant.description }}
                        </p>
                      </div>
                    </div>
                    <div class="mt-8 pt-6 border-t border-primary/10 flex items-center justify-between">
                      <div class="flex items-center gap-4">
                        <div class="flex -space-x-2">
                          <div class="size-8 rounded-full border-2 border-white dark:border-background-dark bg-slate-200"></div>
                          <div class="size-8 rounded-full border-2 border-white dark:border-background-dark bg-slate-300"></div>
                          <div class="size-8 rounded-full border-2 border-white dark:border-background-dark bg-slate-400 flex items-center justify-center text-[10px] font-bold">+{{ restaurant.visitors }}</div>
                        </div>
                        <p class="text-xs text-slate-500 font-medium">本月去过</p>
                      </div>
                      <button class="flex items-center gap-2 px-6 py-3 rounded-xl bg-primary text-white font-bold hover:bg-primary/90 transition-all shadow-lg shadow-primary/30">
                        <span>查看详情</span>
                        <span class="material-symbols-outlined text-sm">arrow_forward</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { foodApi } from '@/services/api'
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()
const tripSpec = computed(() => chatStore.currentTripSpec)

const restaurants = ref([])
const loading = ref(false)

// 根据目的地获取美食数据
async function fetchRestaurants() {
  const city = tripSpec.value?.destination_city
  if (!city) return

  loading.value = true
  try {
    const data = await foodApi.getList(city)
    restaurants.value = data
  } catch (error) {
    console.error('获取美食失败:', error)
    restaurants.value = []
  } finally {
    loading.value = false
  }
}

// 监听目的地变化
watch(() => tripSpec.value?.destination_city, (newCity) => {
  if (newCity) {
    fetchRestaurants()
  }
}, { immediate: true })

onMounted(() => {
  if (tripSpec.value?.destination_city) {
    fetchRestaurants()
  }
})
</script>