/**
 * LM Studio 本地大模型服务
 * 使用 OpenAI 兼容 API 进行旅行槽位识别（意图理解）
 *
 * LM Studio 默认地址: http://127.0.0.1:1234
 * 模型: qwen/qwen3-vl-4b（或 LM Studio 中加载的任意模型）
 */

const LM_STUDIO_BASE = '/lmstudio/v1'  // 通过 Vite 代理解决 CORS 问题
const LM_STUDIO_MODEL = 'qwen/qwen3-vl-4b'  // 与 LM Studio 中加载的模型名一致

/**
 * 调用 LM Studio Chat Completions API
 */
async function lmStudioChat(messages, { maxTokens = 512, temperature = 0.1 } = {}) {
  const resp = await fetch(`${LM_STUDIO_BASE}/chat/completions`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: LM_STUDIO_MODEL,
      messages,
      max_tokens: maxTokens,
      temperature,         // 低温度保证输出更稳定、更结构化
      stream: false,
    }),
  })

  if (!resp.ok) {
    throw new Error(`LM Studio API error: ${resp.status} ${resp.statusText}`)
  }

  const data = await resp.json()
  return data.choices?.[0]?.message?.content ?? ''
}

/**
 * 检测 LM Studio 是否可用
 */
export async function checkLMStudioAvailable() {
  try {
    const resp = await fetch(`${LM_STUDIO_BASE}/models`, { signal: AbortSignal.timeout(2000) })
    return resp.ok
  } catch {
    return false
  }
}

/**
 * 旅行槽位识别
 * 从用户自然语言输入中抽取结构化旅行信息
 *
 * @param {string} userInput - 用户原始输入，如 "我想去成都玩3天，下周五出发"
 * @param {string} [today]   - 当前日期 YYYY-MM-DD，用于相对日期计算
 * @returns {Object|null} tripSpec 结构，或 null（识别失败时）
 *   {
 *     destination_city: string,   // 目的地城市
 *     origin_city: string,        // 出发地（可选）
 *     start_date: string,         // YYYY-MM-DD
 *     end_date: string,           // YYYY-MM-DD
 *     num_travelers: number,      // 出行人数
 *     budget: string,             // 预算描述（可选）
 *   }
 */
export async function extractTravelSlots(userInput, today) {
  if (!today) {
    const d = new Date()
    today = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }

  const systemPrompt = `你是一个旅行意图识别助手，专门从用户输入中提取旅行信息。
今天的日期是 ${today}。

请从用户输入中提取以下信息，并以 JSON 格式返回，不要有任何额外文字：
{
  "destination_city": "目的地城市名（中文，仅城市名，如 '成都'、'北京'）",
  "origin_city": "出发地城市名（如未提及则为 '未知'）",
  "start_date": "出发日期，格式 YYYY-MM-DD（如未提及则从今天起7天后）",
  "end_date": "返回日期，格式 YYYY-MM-DD",
  "num_travelers": 出行人数（整数，未提及默认为1）,
  "budget": "预算描述（如未提及则为空字符串）"
}

规则：
- 如果用户说"明天"，则 start_date 为 ${today} 的下一天
- 如果用户说"后天"，则 start_date 为 ${today} 的两天后
- 如果用户说"下周X"，请根据今天星期几计算
- "3天游"、"玩5天"等表示行程天数，end_date = start_date + 天数 - 1
- 如果无法识别目的地，destination_city 为空字符串 ""
- 只返回 JSON，不要说其他任何话`

  const userMessage = `用户输入：${userInput}`

  try {
    const raw = await lmStudioChat([
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userMessage },
    ])

    console.log('[LM Studio] 原始槽位响应:', raw)

    // 提取 JSON（模型可能包裹在 ```json ... ``` 中）
    const jsonMatch = raw.match(/\{[\s\S]*\}/)
    if (!jsonMatch) {
      console.warn('[LM Studio] 无法提取 JSON，原始响应:', raw)
      return null
    }

    const slots = JSON.parse(jsonMatch[0])

    // 校验必要字段
    if (!slots.destination_city) {
      console.warn('[LM Studio] 未能识别目的地')
      return null
    }

    return {
      destination_city: slots.destination_city,
      origin_city: slots.origin_city || '未知',
      start_date: slots.start_date || '',
      end_date: slots.end_date || '',
      num_travelers: Number(slots.num_travelers) || 1,
      budget: slots.budget || '',
    }
  } catch (err) {
    console.error('[LM Studio] 槽位识别失败:', err)
    return null
  }
}

/**
 * 意图二分类：判断是「闲聊」还是「旅游咨询」
 *
 * @param {string} userInput - 用户输入
 * @returns {{ type: 'chat'|'travel', confidence: number }|null}
 *   - type: 'chat' 表示闲聊，'travel' 表示旅游业务咨询
 *   - null 表示 LM Studio 不可用或解析失败（调用方降级到旅游模式）
 */
export async function classifyIntent(userInput) {
  try {
    const raw = await lmStudioChat([
      {
        role: 'system',
        content: `你是一个意图分类器，判断用户输入属于哪种类型。

类型说明：
- "travel"：与旅游相关的咨询，包括目的地推荐、行程规划、景点/美食/酒店/交通/天气查询、攻略等
- "chat"：与旅游无关的闲聊、问候、闲话、其他话题

只返回 JSON，不要任何其他文字：
{"type": "travel" 或 "chat", "confidence": 0.0到1.0之间的数字}`,
      },
      {
        role: 'user',
        content: userInput,
      },
    ], { maxTokens: 64, temperature: 0.1 })

    const match = raw.match(/\{[\s\S]*?\}/)
    if (!match) return null

    const result = JSON.parse(match[0])
    if (!['chat', 'travel'].includes(result.type)) return null

    console.log(`[LM Studio 意图分类] "${userInput.slice(0, 30)}..." → ${result.type} (置信度 ${result.confidence})`)
    return { type: result.type, confidence: Number(result.confidence) || 0.8 }
  } catch (err) {
    console.warn('[LM Studio 意图分类] 失败，降级为旅游模式:', err.message)
    return null
  }
}

/**
 * 闲聊直接回复（不走后端，完全由 LM Studio 处理）
 *
 * @param {string} userInput - 用户输入
 * @param {Array}  history   - 历史消息 [{role, content}]（可选）
 * @returns {string|null} 回复文本，null 表示失败
 */
export async function chatDirectly(userInput, history = []) {
  try {
    const systemMsg = {
      role: 'system',
      content: `你是旅行智囊助手，一个友好、专业的中国旅游助手。对于与旅游无关的闲聊，你可以简短友好地回应，并适时引导用户聊旅游话题。回复要简洁自然，不超过100字。\n当前系统时间：${new Date().toLocaleDateString('zh-CN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}。`,
    }

    const messages = [
      systemMsg,
      // 最近5轮历史
      ...history.slice(-10).map(m => ({ role: m.role === 'user' ? 'user' : 'assistant', content: m.content })),
      { role: 'user', content: userInput },
    ]

    const reply = await lmStudioChat(messages, { maxTokens: 256, temperature: 0.7 })
    return reply.trim() || null
  } catch (err) {
    console.warn('[LM Studio 闲聊] 失败:', err.message)
    return null
  }
}
