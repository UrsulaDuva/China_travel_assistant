<template>
  <div class="min-h-screen bg-white font-display text-slate-900">
    <div class="max-w-2xl mx-auto min-h-screen flex flex-col p-4 md:p-8">
      <div class="shadow-2xl rounded-3xl p-6 md:p-8 bg-white/80 dark:bg-slate-900/50 backdrop-blur-xl border border-primary/10">
        <!-- 头部 -->
        <header class="flex items-center justify-between mb-8">
          <router-link to="/" class="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <div class="bg-primary p-2 rounded-lg flex items-center justify-center">
              <span class="material-symbols-outlined text-white text-2xl">travel_explore</span>
            </div>
            <h1 class="text-2xl font-bold tracking-tight text-slate-900">行李清单</h1>
          </router-link>
          <div class="flex gap-3">
            <router-link to="/trip" class="flex items-center gap-2 px-4 py-2 rounded-xl bg-primary text-white hover:bg-primary/90 transition-colors">
              <span class="material-symbols-outlined text-xl">calendar_today</span>
              <span class="text-sm font-medium">返回行程</span>
            </router-link>
            <router-link to="/" class="flex items-center gap-2 px-4 py-2 rounded-xl bg-black/5 hover:bg-black/10 transition-colors text-slate-900">
              <span class="material-symbols-outlined text-xl">home</span>
              <span class="text-sm font-medium">返回首页</span>
            </router-link>
            <button class="bg-black/5 p-2.5 rounded-xl hover:bg-black/10 transition-colors text-slate-900">
              <span class="material-symbols-outlined text-xl">ios_share</span>
            </button>
            <button class="bg-black/5 p-2.5 rounded-xl hover:bg-black/10 transition-colors text-slate-900">
              <span class="material-symbols-outlined text-xl">picture_as_pdf</span>
            </button>
          </div>
        </header>

        <!-- 进度追踪 -->
        <section class="bg-white/40 border border-black/5 rounded-xl p-6 mb-8 relative overflow-hidden">
          <div class="absolute top-0 left-0 w-1 h-full bg-primary"></div>
          <div class="flex justify-between items-end mb-4">
            <div>
              <p class="text-slate-500 text-sm uppercase tracking-wider mb-1">准备进度</p>
              <h2 class="text-3xl font-bold text-slate-900">
                {{ checkedCount }} <span class="text-slate-400 text-xl">/ {{ totalCount }}</span>
                <span class="text-base font-normal text-slate-500 ml-2">项目已就绪</span>
              </h2>
            </div>
            <div class="text-right">
              <span class="text-primary font-bold text-lg">{{ progressPercent }}%</span>
            </div>
          </div>
          <div class="w-full bg-black/5 h-3 rounded-full overflow-hidden">
            <div
              class="bg-primary h-full rounded-full transition-all duration-500"
              :style="{ width: `${progressPercent}%` }"
              style="box-shadow: 0 0 15px rgba(239, 67, 67, 0.4);"
            ></div>
          </div>
          <p class="mt-4 text-sm text-slate-500 flex items-center gap-2">
            <span class="material-symbols-outlined text-primary text-sm">info</span>
            <span v-if="remainingCount > 0">加油！只需再准备 {{ remainingCount }} 件物品即可出发。</span>
            <span v-else>太棒了！所有物品都已准备就绪，祝您旅途愉快！</span>
          </p>
        </section>

        <!-- 分类清单 -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 relative z-10">
          <!-- 旅行证件 -->
          <div class="bg-black/5 rounded-xl p-5 border border-black/5">
            <div class="flex items-center gap-2 mb-4">
              <span class="material-symbols-outlined text-primary">description</span>
              <h3 class="font-bold text-lg text-slate-900">旅行证件</h3>
            </div>
            <ul class="space-y-3">
              <li v-for="item in categories.documents" :key="item.id" class="flex items-center justify-between">
                <span :class="['text-slate-700', item.checked ? 'line-through text-slate-400' : '']">{{ item.name }}</span>
                <input
                  v-model="item.checked"
                  class="checkbox-custom h-5 w-5 rounded border-slate-300 bg-white text-primary focus:ring-primary accent-primary"
                  type="checkbox"
                />
              </li>
            </ul>
          </div>

          <!-- 衣物鞋帽 -->
          <div class="bg-black/5 rounded-xl p-5 border border-black/5">
            <div class="flex items-center gap-2 mb-4">
              <span class="material-symbols-outlined text-primary">apparel</span>
              <h3 class="font-bold text-lg text-slate-900">衣物鞋帽</h3>
            </div>
            <ul class="space-y-3">
              <li v-for="item in categories.clothing" :key="item.id" class="flex items-center justify-between">
                <span :class="['text-slate-700', item.checked ? 'line-through text-slate-400' : '']">{{ item.name }}</span>
                <input
                  v-model="item.checked"
                  class="checkbox-custom h-5 w-5 rounded border-slate-300 bg-white text-primary focus:ring-primary accent-primary"
                  type="checkbox"
                />
              </li>
            </ul>
          </div>

          <!-- 数码配件 -->
          <div class="bg-black/5 rounded-xl p-5 border border-black/5">
            <div class="flex items-center gap-2 mb-4">
              <span class="material-symbols-outlined text-primary">devices</span>
              <h3 class="font-bold text-lg text-slate-900">数码配件</h3>
            </div>
            <ul class="space-y-3">
              <li v-for="item in categories.electronics" :key="item.id" class="flex items-center justify-between">
                <span :class="['text-slate-700', item.checked ? 'line-through text-slate-400' : '']">{{ item.name }}</span>
                <input
                  v-model="item.checked"
                  class="checkbox-custom h-5 w-5 rounded border-slate-300 bg-white text-primary focus:ring-primary accent-primary"
                  type="checkbox"
                />
              </li>
            </ul>
          </div>

          <!-- 个人洗护 -->
          <div class="bg-black/5 rounded-xl p-5 border border-black/5">
            <div class="flex items-center gap-2 mb-4">
              <span class="material-symbols-outlined text-primary">sanitizer</span>
              <h3 class="font-bold text-lg text-slate-900">个人洗护</h3>
            </div>
            <ul class="space-y-3">
              <li v-for="item in categories.toiletries" :key="item.id" class="flex items-center justify-between">
                <span :class="['text-slate-700', item.checked ? 'line-through text-slate-400' : '']">{{ item.name }}</span>
                <input
                  v-model="item.checked"
                  class="checkbox-custom h-5 w-5 rounded border-slate-300 bg-white text-primary focus:ring-primary accent-primary"
                  type="checkbox"
                />
              </li>
            </ul>
          </div>

          <!-- 常用药品 -->
          <div class="bg-black/5 rounded-xl p-5 md:col-span-2 border border-black/5">
            <div class="flex items-center gap-2 mb-4">
              <span class="material-symbols-outlined text-primary">medication</span>
              <h3 class="font-bold text-lg text-slate-900">常用药品</h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-3">
              <li v-for="item in categories.medicine" :key="item.id" class="flex items-center justify-between list-none">
                <span :class="['text-slate-700', item.checked ? 'line-through text-slate-400' : '']">{{ item.name }}</span>
                <input
                  v-model="item.checked"
                  class="checkbox-custom h-5 w-5 rounded border-slate-300 bg-white text-primary focus:ring-primary accent-primary"
                  type="checkbox"
                />
              </li>
            </div>
          </div>

          <!-- 添加其他物品 -->
          <div class="bg-black/5 rounded-xl p-5 border border-black/5 md:col-span-2 mt-4">
            <div class="flex items-center gap-2 mb-4">
              <span class="material-symbols-outlined text-primary">add_task</span>
              <h3 class="font-bold text-lg text-slate-900">添加其他物品</h3>
            </div>
            <div class="relative flex items-center">
              <input
                v-model="newItemName"
                @keyup.enter="addCustomItem"
                class="w-full bg-white border-slate-200 rounded-lg py-2.5 px-4 text-slate-700 focus:ring-primary focus:border-primary placeholder:text-slate-400 transition-all shadow-sm"
                placeholder="输入你想添加的物品..."
                type="text"
              />
              <button
                @click="addCustomItem"
                class="absolute right-2 bg-primary text-white p-1.5 rounded-md hover:bg-primary/90 transition-colors flex items-center justify-center"
              >
                <span class="material-symbols-outlined text-xl">add</span>
              </button>
            </div>
            <p class="mt-3 text-xs text-slate-400 italic">您可以手动添加清单中未列出的个人物品</p>

            <!-- 自定义物品列表 -->
            <ul v-if="customItems.length > 0" class="mt-4 space-y-3">
              <li v-for="item in customItems" :key="item.id" class="flex items-center justify-between bg-white/50 rounded-lg px-4 py-2">
                <span :class="['text-slate-700', item.checked ? 'line-through text-slate-400' : '']">{{ item.name }}</span>
                <div class="flex items-center gap-2">
                  <input
                    v-model="item.checked"
                    class="checkbox-custom h-5 w-5 rounded border-slate-300 bg-white text-primary focus:ring-primary accent-primary"
                    type="checkbox"
                  />
                  <button @click="removeCustomItem(item.id)" class="text-slate-400 hover:text-primary transition-colors">
                    <span class="material-symbols-outlined text-lg">close</span>
                  </button>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'

const categories = reactive({
  documents: [
    { id: 1, name: '护照 / 签证', checked: true },
    { id: 2, name: '飞行行程单', checked: true },
    { id: 3, name: '酒店确认函', checked: false },
  ],
  clothing: [
    { id: 4, name: '内衣裤 (5套)', checked: true },
    { id: 5, name: '外套 / 夹克', checked: true },
    { id: 6, name: '舒适步行鞋', checked: true },
  ],
  electronics: [
    { id: 7, name: '万能转换插头', checked: true },
    { id: 8, name: '移动电源', checked: true },
    { id: 9, name: '降噪耳机', checked: false },
  ],
  toiletries: [
    { id: 10, name: '旅行套装 (洗发/沐浴)', checked: true },
    { id: 11, name: '牙刷牙膏', checked: true },
    { id: 12, name: '防晒霜', checked: false },
  ],
  medicine: [
    { id: 13, name: '感冒/退烧药', checked: true },
    { id: 14, name: '止泻/肠胃药', checked: true },
    { id: 15, name: '创口贴', checked: false },
    { id: 16, name: '晕车药', checked: false },
  ],
})

const customItems = ref([])
const newItemName = ref('')
let customItemId = 100

const allItems = computed(() => {
  const items = [
    ...categories.documents,
    ...categories.clothing,
    ...categories.electronics,
    ...categories.toiletries,
    ...categories.medicine,
    ...customItems.value,
  ]
  return items
})

const totalCount = computed(() => allItems.value.length)
const checkedCount = computed(() => allItems.value.filter(item => item.checked).length)
const remainingCount = computed(() => totalCount.value - checkedCount.value)
const progressPercent = computed(() => {
  if (totalCount.value === 0) return 0
  return Math.round((checkedCount.value / totalCount.value) * 100)
})

function addCustomItem() {
  if (newItemName.value.trim()) {
    customItems.value.push({
      id: customItemId++,
      name: newItemName.value.trim(),
      checked: false,
    })
    newItemName.value = ''
  }
}

function removeCustomItem(id) {
  customItems.value = customItems.value.filter(item => item.id !== id)
}
</script>

<style scoped>
.checkbox-custom:checked {
  background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='white' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3e%3c/svg%3e");
}
</style>