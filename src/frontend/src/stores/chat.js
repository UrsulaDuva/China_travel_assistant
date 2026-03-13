import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { chatApi } from '@/services/api'

export const useChatStore = defineStore('chat', () => {
  // 状态
  const messages = ref([])
  const isLoading = ref(false)
  const currentTripSpec = ref(null)
  const itinerary = ref(null)

  // 初始化 - 从localStorage恢复数据
  function init() {
    const savedTripSpec = localStorage.getItem('tripSpec')
    if (savedTripSpec) {
      try {
        const parsed = JSON.parse(savedTripSpec)
        currentTripSpec.value = parsed
        console.log('从 localStorage 恢复 tripSpec:', parsed)
      } catch (e) {
        console.error('Failed to parse saved trip spec:', e)
      }
    }
  }

  // 保存tripSpec到localStorage
  function saveTripSpec(tripSpec) {
    if (tripSpec) {
      currentTripSpec.value = tripSpec
      localStorage.setItem('tripSpec', JSON.stringify(tripSpec))
      console.log('保存 tripSpec 到 localStorage:', tripSpec)
    }
  }

  // 添加消息
  function addMessage(role, content, data = null) {
    messages.value.push({
      id: Date.now(),
      role,
      content,
      data,
      timestamp: new Date().toISOString(),
    })
  }

  // 发送消息
  async function sendMessage(content) {
    const { getOrCreateSessionId } = useAppStore()
    const sessionId = getOrCreateSessionId()

    // 添加用户消息
    addMessage('user', content)

    isLoading.value = true

    try {
      const response = await chatApi.chat(content, sessionId)
      console.log('API 响应:', response)

      // 添加助手消息
      addMessage('assistant', response.message, response.data)

      // 更新行程数据并保存到localStorage
      if (response.data?.trip_spec) {
        console.log('从响应中获取 trip_spec:', response.data.trip_spec)
        saveTripSpec(response.data.trip_spec)
      }
      if (response.data?.itinerary) {
        itinerary.value = response.data.itinerary
      }

      // 如果响应中没有 trip_spec，尝试从消息中提取城市和日期
      if (!currentTripSpec.value?.destination_city && content) {
        // 省份映射到省会
        const provinces = {
          "四川": "成都", "四川": "成都",
          "广东": "广州", "浙江": "杭州", "江苏": "南京",
          "山东": "济南", "河南": "郑州", "湖北": "武汉",
          "湖南": "长沙", "福建": "福州", "云南": "昆明",
          "海南": "三亚", "贵州": "贵阳", "安徽": "合肥",
          "江西": "南昌", "山西": "太原", "河北": "石家庄",
          "陕西": "西安", "甘肃": "兰州", "青海": "西宁",
          "辽宁": "沈阳", "吉林": "长春", "黑龙江": "哈尔滨",
          "广西": "桂林", "内蒙古": "呼和浩特", "新疆": "乌鲁木齐",
          "西藏": "拉萨", "宁夏": "银川",
        }

        // 提取天数（如"3日游"、"5天"、"三日游"）
        const chineseToNumber = (chinese) => {
          const chineseNums = {
            '零': 0, '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4,
            '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10
          }
          if (chinese in chineseNums) return chineseNums[chinese]
          if (!isNaN(parseInt(chinese))) return parseInt(chinese)
          return 3
        }

        // 尝试阿拉伯数字
        const daysMatch = content.match(/(\d+)[天日](?:游)?/)
        // 尝试中文数字
        const chineseDaysMatch = content.match(/([一二三四五六七八九十])[天日](?:游)?/)
        const days = daysMatch ? parseInt(daysMatch[1]) :
                     chineseDaysMatch ? chineseToNumber(chineseDaysMatch[1]) : 3

        // 提取具体日期（如 "3月15日"、"03-15"、"3.14"、"2024-03-15"）
        let startDate = null
        let endDate = null

        // 匹配 "明天"、"后天"
        if (content.includes('明天')) {
          const today = new Date()
          startDate = new Date(today.getTime() + 1 * 24 * 60 * 60 * 1000)
          endDate = new Date(today.getTime() + days * 24 * 60 * 60 * 1000)
        } else if (content.includes('后天')) {
          const today = new Date()
          startDate = new Date(today.getTime() + 2 * 24 * 60 * 60 * 1000)
          endDate = new Date(today.getTime() + (2 + days - 1) * 24 * 60 * 60 * 1000)
        } else if (content.includes('下周') || content.includes('下个星期')) {
          const today = new Date()
          const dayOfWeek = today.getDay()
          const daysUntilNextWeek = 7 - dayOfWeek + 1
          startDate = new Date(today.getTime() + daysUntilNextWeek * 24 * 60 * 60 * 1000)
          endDate = new Date(startDate.getTime() + (days - 1) * 24 * 60 * 60 * 1000)
        } else {
          // 匹配 "X月X日" 格式
          const dateMatch = content.match(/(\d{1,2})月(\d{1,2})[日号]?/)
          if (dateMatch) {
            const month = parseInt(dateMatch[1]) - 1
            const day = parseInt(dateMatch[2])
            const today = new Date()
            let year = today.getFullYear()
            // 如果月份已经过去，则为明年
            if (month < today.getMonth()) {
              year++
            }
            startDate = new Date(year, month, day)
            endDate = new Date(startDate.getTime() + (days - 1) * 24 * 60 * 60 * 1000)
          }
          // 匹配 "YYYY-MM-DD" 或 "YYYY/MM/DD" 格式
          const isoDateMatch = content.match(/(\d{4})[-/](\d{1,2})[-/](\d{1,2})/)
          if (isoDateMatch) {
            startDate = new Date(parseInt(isoDateMatch[1]), parseInt(isoDateMatch[2]) - 1, parseInt(isoDateMatch[3]))
            endDate = new Date(startDate.getTime() + (days - 1) * 24 * 60 * 60 * 1000)
          }
          // 匹配 "M.D" 或 "M-D" 格式（如 "3.14"、"3-15"）
          const shortDateMatch = content.match(/(?<!\d)(\d{1,2})[.-](\d{1,2})(?!\d)/)
          if (shortDateMatch && !isoDateMatch) {
            const month = parseInt(shortDateMatch[1]) - 1
            const day = parseInt(shortDateMatch[2])
            const today = new Date()
            let year = today.getFullYear()
            // 如果月份已经过去，则为明年
            if (month < today.getMonth()) {
              year++
            }
            startDate = new Date(year, month, day)
            endDate = new Date(startDate.getTime() + (days - 1) * 24 * 60 * 60 * 1000)
          }
        }

        // 如果没有提取到日期，使用默认（7天后）
        if (!startDate) {
          const today = new Date()
          startDate = new Date(today.getTime() + 7 * 24 * 60 * 60 * 1000)
          endDate = new Date(today.getTime() + (7 + days - 1) * 24 * 60 * 60 * 1000)
        }

        const formatDate = (d) => {
          const year = d.getFullYear()
          const month = String(d.getMonth() + 1).padStart(2, '0')
          const day = String(d.getDate()).padStart(2, '0')
          return `${year}-${month}-${day}`
        }

        // 先检查省份
        for (const [province, city] of Object.entries(provinces)) {
          if (content.includes(province)) {
            saveTripSpec({
              destination_city: city,
              origin_city: '出发地',
              start_date: formatDate(startDate),
              end_date: formatDate(endDate),
              num_travelers: 1,
            })
            return response
          }
        }

        // 检查城市
        const cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '西安', '南京', '武汉', '重庆',
                       '苏州', '天津', '长沙', '郑州', '青岛', '大连', '厦门', '昆明', '三亚', '桂林',
                       '丽江', '大理', '张家界', '黄山', '珠海', '无锡', '宁波', '福州', '济南', '烟台',
                       '沈阳', '哈尔滨', '长春', '呼和浩特', '乌鲁木齐', '拉萨', '西宁', '兰州', '银川',
                       '贵阳', '南宁', '北海', '阳朔', '汕头', '佛山', '东莞', '常州', '南通', '扬州']

        for (const city of cities) {
          if (content.includes(city)) {
            saveTripSpec({
              destination_city: city,
              origin_city: '出发地',
              start_date: formatDate(startDate),
              end_date: formatDate(endDate),
              num_travelers: 1,
            })
            break
          }
        }
      }

      return response
    } catch (error) {
      addMessage('assistant', '抱歉，服务暂时不可用，请稍后再试。')
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 清空消息
  function clearMessages() {
    messages.value = []
  }

  // 清空行程数据
  function clearTripSpec() {
    currentTripSpec.value = null
    localStorage.removeItem('tripSpec')
  }

  // 获取会话状态
  async function fetchSessionState() {
    const { sessionId } = useAppStore()
    if (!sessionId.value) return

    try {
      const state = await chatApi.getSession(sessionId.value)
      if (state.trip_spec) {
        saveTripSpec(state.trip_spec)
      }
      if (state.itinerary) {
        itinerary.value = state.itinerary
      }
    } catch (error) {
      console.error('获取会话状态失败:', error)
    }
  }

  // 初始化
  init()

  return {
    messages,
    isLoading,
    currentTripSpec,
    itinerary,
    addMessage,
    sendMessage,
    clearMessages,
    clearTripSpec,
    fetchSessionState,
    saveTripSpec,
    init,
  }
})

// 避免循环引用
import { useAppStore } from './app'