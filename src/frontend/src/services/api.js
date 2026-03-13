import axios from 'axios'

const api = axios.create({
  baseURL: '',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// 聊天 API
export const chatApi = {
  // 发送消息
  async chat(message, sessionId = null) {
    return api.post('/chat', {
      message,
      session_id: sessionId,
    })
  },

  // 获取会话状态
  async getSession(sessionId) {
    return api.get(`/sessions/${sessionId}`)
  },

  // 发送工作流事件
  async sendEvent(sessionId, eventType, data = {}) {
    return api.post(`/sessions/${sessionId}/event`, {
      type: eventType,
      ...data,
    })
  },

  // 获取 Agent 列表
  async getAgents() {
    return api.get('/agents')
  },
}

// 监控 API
export const monitorApi = {
  // 获取监控列表
  async getList() {
    // 模拟数据
    return {
      flights: [
        {
          id: 1,
          from: '北京 (PEK)',
          to: '上海 (SHA)',
          currentPrice: 820,
          targetPrice: 750,
          status: 'monitoring',
          trend: 'down',
        },
      ],
      trains: [
        {
          id: 1,
          trainNo: 'G1',
          from: '北京南',
          to: '上海虹桥',
          seats: ['二等座', '一等座'],
          targetPrice: 553,
          status: 'monitoring',
        },
        {
          id: 2,
          trainNo: 'G108',
          from: '南京南',
          to: '杭州东',
          seats: ['二等座'],
          targetPrice: 120,
          status: 'stopped',
        },
      ],
    }
  },

  // 添加监控
  async addMonitor(data) {
    return { success: true, id: Date.now() }
  },

  // 删除监控
  async deleteMonitor(id) {
    return { success: true }
  },
}

// 景点 API
export const attractionApi = {
  // 获取景点列表 - 实时高德API数据
  async getList(city, category = null) {
    try {
      const params = category ? { category } : {}
      const response = await api.get(`/api/attractions/${city}`, { params })
      if (response.success && response.data && response.data.length > 0) {
        return response.data.map((item, index) => ({
          id: item.id || index + 1,
          name: item.name || '未知景点',
          rating: item.rating || 4.5,
          ticketPrice: item.cost || '请咨询',
          openTime: item.address || city,
          highlights: item.type || '热门景点',
          image: item.image || '',
          gradient: item.image ? '' : _getGradientByIndex(index),
          tags: _getTagsByType(item.type),
          address: item.address || '',
        }))
      }
    } catch (error) {
      console.error('获取景点失败:', error)
    }
    // 返回空数组，不使用模拟数据
    return []
  },
}

// 美食 API
export const foodApi = {
  // 获取餐厅列表 - 实时高德API数据
  async getList(city, cuisine = null) {
    try {
      const params = cuisine ? { cuisine } : {}
      const response = await api.get(`/api/food/${city}`, { params })
      if (response.success && response.data && response.data.length > 0) {
        return response.data.map((item, index) => ({
          id: item.id || index + 1,
          name: item.name || '未知餐厅',
          area: item.adname || item.cityname || city,
          rating: item.rating || 4.5,
          avgPrice: parseInt(item.cost) || 100,
          signatureDishes: item.type ? item.type.split(';').slice(0, 3) : ['招牌菜'],
          description: item.address || '特色美食',
          image: item.image || '',
          gradient: item.image ? '' : _getGradientByIndex(index),
          visitors: Math.floor(Math.random() * 500) + 100,
          tags: item.type ? [item.type.split(';')[0]] : ['推荐'],
        }))
      }
    } catch (error) {
      console.error('获取美食失败:', error)
    }
    // 返回空数组，不使用模拟数据
    return []
  },
}

// 天气 API
export const weatherApi = {
  // 获取城市天气 - MCP实时数据，支持指定日期
  async getWeather(city, date = null) {
    try {
      const params = date ? { date } : {}
      const response = await api.get(`/api/weather/${city}`, { params })
      if (response.success && response.data) {
        const data = response.data
        return {
          city: data.city || city,
          temp: data.temperature ?? data.temp ?? '--',
          description: data.weather || data.description || '晴',
          humidity: data.humidity ?? '--',
          wind: data.wind || '微风',
          tips: data.tips || '',
          realFeel: data.real_feel ?? data.realFeel ?? data.temperature ?? '--',
          updateTime: data.update_time || '',
          queryDate: data.query_date || data.date || '',
        }
      }
    } catch (error) {
      console.error('获取天气失败:', error)
    }
    // 返回空数据，不使用模拟数据
    return { city: '', temp: '--', description: '请设置目的地', humidity: '--', wind: '--', tips: '', realFeel: '--' }
  },
}

// 酒店 API
export const hotelApi = {
  async getList(city, area = null) {
    try {
      const params = area ? { area } : {}
      const response = await api.get(`/api/hotels/${city}`, { params })
      if (response.success && response.data) {
        return response.data.map((item, index) => ({
          id: item.id || index + 1,
          name: item.name || '未知酒店',
          rating: item.rating || 4.5,
          price: item.cost || '请咨询',
          address: item.address || '',
          type: item.type || '酒店',
        }))
      }
    } catch (error) {
      console.error('获取酒店失败:', error)
    }
    return []
  },
}

// 攻略 API
export const guideApi = {
  async getGuides(city, keywords = null) {
    try {
      const params = keywords ? { keywords } : {}
      const response = await api.get(`/api/guide/${city}`, { params })
      if (response.success && response.data && response.data.length > 0) {
        return response.data.map((item, index) => ({
          id: item.id || index + 1,
          title: item.title || '旅游攻略',
          author: item.author || '抖音博主',
          likes: item.likes || 0,
          views: item.views || 0,
          cover: item.cover || '',
          url: item.url || '',
          tags: item.tags || [city + '旅游'],
          description: item.description || '',
          content: item.content || '',  // 添加详细内容
        }))
      }
    } catch (error) {
      console.error('获取攻略失败:', error)
    }
    return []
  },
}

// 辅助函数
function _getGradientByIndex(index) {
  const gradients = [
    'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
    'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
    'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
    'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)',
    'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)',
    'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)',
  ]
  return gradients[index % gradients.length]
}

function _getTagsByType(type) {
  if (!type) return ['热门']
  if (type.includes('历史') || type.includes('博物馆')) return ['人文历史', '必游']
  if (type.includes('自然') || type.includes('公园')) return ['自然风光', '推荐']
  if (type.includes('夜') || type.includes('夜景')) return ['夜景地标', '推荐']
  return ['热门推荐']
}

// 热门目的地 API
export const destinationApi = {
  async getHotDestinations() {
    // 热门城市配置 - 使用可靠的图片URL
    const cities = [
      {
        name: '北京',
        tag: '推荐',
        duration: '5天4晚',
        description: '千年古都，现代京韵',
        image: 'https://images.unsplash.com/photo-1508804185872-d7badad00f7d?w=800&q=80'
      },
      {
        name: '上海',
        tag: '人气',
        duration: '3天2晚',
        description: '摩登都市，外滩风云',
        image: 'https://images.unsplash.com/photo-1538428494232-9c0d8a3ab403?w=800&q=80'
      },
      {
        name: '成都',
        tag: '美食',
        duration: '4天3晚',
        description: '巴蜀风味，慢生活之都',
        image: 'https://images.unsplash.com/photo-1590559899731-a382839e5549?w=800&q=80'
      },
      {
        name: '杭州',
        tag: '诗意',
        duration: '2天1晚',
        description: '人间天堂，西湖美景',
        image: 'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=800&q=80'
      },
    ]

    return cities.map((city, index) => ({
      id: index + 1,
      ...city,
      gradient: _getGradientByIndex(index),
    }))
  },
}

export default api