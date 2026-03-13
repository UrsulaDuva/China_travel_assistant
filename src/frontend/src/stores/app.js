import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAppStore = defineStore('app', () => {
  // 状态
  const isDark = ref(false)
  const sessionId = ref(null)
  const user = ref(null)
  const notifications = ref([])

  // 计算属性
  const isAuthenticated = computed(() => !!user.value)

  // 初始化
  function init() {
    // 从 localStorage 恢复状态
    const savedSessionId = localStorage.getItem('sessionId')
    if (savedSessionId) {
      sessionId.value = savedSessionId
    }

    // 检测系统主题
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      isDark.value = true
      document.documentElement.classList.add('dark')
    }
  }

  // 切换主题
  function toggleDark() {
    isDark.value = !isDark.value
    if (isDark.value) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  // 设置会话ID
  function setSessionId(id) {
    sessionId.value = id
    localStorage.setItem('sessionId', id)
  }

  // 获取或创建会话ID
  function getOrCreateSessionId() {
    if (!sessionId.value) {
      sessionId.value = 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
      localStorage.setItem('sessionId', sessionId.value)
    }
    return sessionId.value
  }

  // 添加通知
  function addNotification(notification) {
    notifications.value.push({
      id: Date.now(),
      ...notification,
    })
  }

  // 移除通知
  function removeNotification(id) {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  return {
    isDark,
    sessionId,
    user,
    notifications,
    isAuthenticated,
    init,
    toggleDark,
    setSessionId,
    getOrCreateSessionId,
    addNotification,
    removeNotification,
  }
})