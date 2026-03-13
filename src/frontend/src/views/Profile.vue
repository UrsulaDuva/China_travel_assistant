<template>
  <div class="min-h-screen bg-white font-display text-slate-900">
    <div class="flex h-screen overflow-hidden">
      <!-- 侧边栏 -->
      <aside class="w-72 flex-shrink-0 bg-white/50 dark:bg-black/20 border-r border-primary/10 flex flex-col justify-between p-6 backdrop-blur-sm">
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
              <span class="ml-auto bg-primary text-white text-[10px] px-2 py-0.5 rounded-full italic font-bold">3</span>
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
      <main class="flex-1 overflow-y-auto bg-background-light dark:bg-background-dark p-8 space-y-8">
        <!-- 用户资料卡片 -->
        <section class="red-gradient-bg rounded-xl p-8 text-white relative overflow-hidden shadow-2xl">
          <div class="absolute right-0 top-0 h-full w-1/3 opacity-10 pointer-events-none" style="background-image: radial-gradient(circle, white 1px, transparent 1px); background-size: 20px 20px;"></div>
          <div class="flex flex-col md:flex-row items-center gap-8 relative z-10">
            <div class="relative">
              <div class="w-32 h-32 rounded-full border-4 border-white/20 overflow-hidden shadow-xl bg-slate-200">
                <img alt="Profile" class="w-full h-full object-cover" src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=200&h=200&fit=crop" />
              </div>
              <div class="absolute bottom-1 right-1 bg-amber-400 p-1.5 rounded-full border-2 border-primary">
                <span class="material-symbols-outlined text-[16px] text-primary-900 font-bold">verified</span>
              </div>
            </div>
            <div class="flex-1 text-center md:text-left">
              <h2 class="text-4xl font-bold mb-1 tracking-tight">{{ user.name }}</h2>
              <div class="flex flex-wrap justify-center md:justify-start items-center gap-3">
                <span class="bg-amber-400/90 text-background-dark text-xs font-bold px-3 py-1 rounded-full uppercase tracking-tighter">{{ user.level }}</span>
                <span class="text-white/80 text-sm flex items-center gap-1 italic">
                  <span class="material-symbols-outlined text-[18px]">calendar_today</span>
                  Since {{ user.since }}
                </span>
              </div>
            </div>
            <div class="flex gap-3">
              <button class="px-6 py-2.5 bg-white text-primary font-bold rounded-xl hover:bg-slate-100 transition-colors">编辑资料</button>
              <button class="p-2.5 bg-white/10 border border-white/20 rounded-xl hover:bg-white/20 transition-colors">
                <span class="material-symbols-outlined">share</span>
              </button>
            </div>
          </div>
        </section>

        <!-- 统计卡片 -->
        <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div class="glass-card p-6 rounded-xl border-l-4 border-primary">
            <div class="flex items-center justify-between mb-4">
              <p class="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-widest">已完成行程</p>
              <span class="material-symbols-outlined text-primary">flight_takeoff</span>
            </div>
            <div class="flex items-baseline gap-2">
              <h3 class="text-3xl font-bold">{{ stats.trips }}</h3>
              <span class="text-emerald-500 text-sm font-bold flex items-center">
                <span class="material-symbols-outlined text-sm">trending_up</span>
                +2%
              </span>
            </div>
          </div>
          <div class="glass-card p-6 rounded-xl border-l-4 border-amber-400">
            <div class="flex items-center justify-between mb-4">
              <p class="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-widest">已节省金额</p>
              <span class="material-symbols-outlined text-amber-500">payments</span>
            </div>
            <div class="flex items-baseline gap-2">
              <h3 class="text-3xl font-bold">¥{{ stats.saved }}</h3>
              <span class="text-emerald-500 text-sm font-bold flex items-center">
                <span class="material-symbols-outlined text-sm">trending_up</span>
                +15%
              </span>
            </div>
          </div>
          <div class="glass-card p-6 rounded-xl border-l-4 border-primary">
            <div class="flex items-center justify-between mb-4">
              <p class="text-sm font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-widest">旅行积分</p>
              <span class="material-symbols-outlined text-primary">stars</span>
            </div>
            <div class="flex items-baseline gap-2">
              <h3 class="text-3xl font-bold">{{ stats.points }}</h3>
              <span class="text-emerald-500 text-sm font-bold flex items-center">
                <span class="material-symbols-outlined text-sm">expand_less</span>
                +500
              </span>
            </div>
          </div>
        </section>

        <!-- 最近旅程 -->
        <section class="space-y-4">
          <h2 class="text-2xl font-bold tracking-tight">最近旅程</h2>
          <div class="p-8 rounded-xl border border-amber-200/50 shadow-sm" style="background-color: #fdf5e6;">
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-8">
              <div>
                <h3 class="text-3xl font-bold text-slate-900 mb-2">上海 - 杭州 4日深度游</h3>
                <div class="flex items-center gap-2 text-slate-600">
                  <span class="material-symbols-outlined text-sm">calendar_today</span>
                  <span class="text-sm font-medium">2024年3月15日 - 3月18日</span>
                </div>
              </div>
              <div class="text-right">
                <p class="text-sm text-slate-500 font-bold uppercase tracking-wider mb-1">总消费金额</p>
                <p class="text-4xl font-bold text-primary">¥4,500</p>
              </div>
            </div>
            <div class="bg-white/60 rounded-xl p-6">
              <h4 class="font-bold text-lg mb-4 flex items-center gap-2">
                <span class="material-symbols-outlined text-primary">map</span>
                行程概览
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <ul class="space-y-3">
                  <li class="flex gap-3">
                    <span class="w-6 h-6 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center font-bold shrink-0">D1</span>
                    <p class="text-slate-700">抵达上海，入住外滩精品酒店，夜游黄浦江。</p>
                  </li>
                  <li class="flex gap-3">
                    <span class="w-6 h-6 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center font-bold shrink-0">D2</span>
                    <p class="text-slate-700">参观武康路历史街区，下午体验法租界艺术展。</p>
                  </li>
                </ul>
                <ul class="space-y-3">
                  <li class="flex gap-3">
                    <span class="w-6 h-6 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center font-bold shrink-0">D3</span>
                    <p class="text-slate-700">乘高铁前往杭州，游览西湖，品尝龙井春茶。</p>
                  </li>
                  <li class="flex gap-3">
                    <span class="w-6 h-6 rounded-full bg-primary/10 text-primary text-xs flex items-center justify-center font-bold shrink-0">D4</span>
                    <p class="text-slate-700">灵隐寺祈福，漫步南宋御街，结束旅程返回。</p>
                  </li>
                </ul>
              </div>
            </div>
            <div class="mt-8 flex justify-end gap-4">
              <button class="px-6 py-2.5 bg-white text-slate-700 font-bold rounded-xl border border-slate-200 hover:bg-slate-50 transition-colors">查看完整行程</button>
              <button class="px-6 py-2.5 bg-primary text-white font-bold rounded-xl shadow-lg shadow-primary/20 hover:opacity-90 transition-opacity">账单详情</button>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const user = ref({
  name: 'Alex Wanderer',
  level: '黄金会员',
  since: 'Aug 2023',
})

const stats = ref({
  trips: 24,
  saved: '1,240',
  points: '8,500',
})
</script>

<style scoped>
.glass-card {
  background: rgba(239, 67, 67, 0.05);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(239, 67, 67, 0.1);
}
</style>