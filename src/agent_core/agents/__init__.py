"""
Specialist Agents for Travel Planning
======================================

Each agent specializes in a specific domain of travel planning.
"""

from typing import List, Dict, Any, Optional, Type
from langchain_core.tools import BaseTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.runnables import Runnable, RunnableConfig
from pydantic import BaseModel, Field
import os
import sys
import json
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Try to import DashScope LLM, fallback to mock
try:
    from langchain_community.llms import Tongyi
    DASHSCOPE_AVAILABLE = True
except ImportError:
    DASHSCOPE_AVAILABLE = False

from ..tools import ALL_TOOLS, TOOL_MAP
from ..memory import ConversationMemory


class AgentState(BaseModel):
    """State shared between agents."""
    session_id: str = ""
    messages: List[Dict[str, str]] = []
    current_task: str = ""
    trip_context: Dict[str, Any] = {}
    tool_results: Dict[str, Any] = {}
    final_response: str = ""


class BaseTravelAgent:
    """Base class for all travel planning agents."""

    name: str = "base_agent"
    description: str = "Base travel agent"
    system_prompt: str = "You are a helpful travel planning assistant."

    def __init__(
        self,
        tools: Optional[List[BaseTool]] = None,
        llm: Optional[Any] = None,
        memory: Optional[ConversationMemory] = None
    ):
        self.tools = tools or []
        self.tool_map = {t.name: t for t in self.tools}
        self.memory = memory

        # Initialize LLM
        if llm:
            self.llm = llm
        elif DASHSCOPE_AVAILABLE and os.getenv("DASHSCOPE_API_KEY"):
            self.llm = Tongyi(
                model_name="qwen-plus",
                dashscope_api_key=os.getenv("DASHSCOPE_API_KEY")
            )
        else:
            self.llm = None

    def get_system_prompt(self, context: str = "") -> str:
        """Get the system prompt with optional context."""
        prompt = self.system_prompt
        if context:
            prompt += f"\n\n当前上下文：\n{context}"
        return prompt

    async def process(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """Process user input and return response."""
        raise NotImplementedError


class CoordinatorAgent(BaseTravelAgent):
    """Main coordinator agent that routes to specialists."""

    name = "coordinator"
    description = "主协调器，分析用户意图并分配任务给专业Agent"

    # 意图识别 Prompt - 参考 SmartVoyage 的优秀模式
    INTENT_PROMPT = """你是一个专业的旅行需求分析专家。你的任务是分析用户的旅行需求，提取关键信息。

## 当前对话上下文
{context}

## 当前已收集的旅行信息
- 目的地：{current_destination}
- 出发日期：{current_start_date}
- 返程日期：{current_end_date}
- 出行人数：{current_travelers}

## 用户输入
{user_input}

## 任务
请分析用户输入，提取以下信息（如果能从上下文推断，也要包含）：

1. 目的地城市（destination）：用户想去哪个城市旅游
2. 出发日期（start_date）：格式为 YYYY-MM-DD，如果用户说"3月14号"，则根据当前日期推断年份
3. 行程天数（duration）：用户计划玩几天，支持"两天"、"三天"、"两三天"等中文表达
4. 出行人数（travelers）：几个人出行

## 中文数字转换
- "一"=1, "二"=2, "三"=3, "四"=4, "五"=5, "六"=6, "七"=7, "八"=8, "九"=9, "十"=10
- "两"=2, "俩"=2
- "十一"=11, "十二"=12 等

## 输出格式
请严格输出以下 JSON 格式，不要添加任何其他文字：
{{
    "destination": "城市名称或 null",
    "start_date": "YYYY-MM-DD 或 null",
    "end_date": "YYYY-MM-DD 或 null（根据出发日期+天数计算）",
    "duration": 数字或 null,
    "travelers": 数字或 null,
    "has_new_info": true/false,
    "missing_slots": ["缺失的信息项"],
    "follow_up_message": "追问用户缺失信息的友好话语"
}}

## 示例
用户输入："我3月14号出发"
输出：{{"destination": null, "start_date": "2026-03-14", "end_date": null, "duration": null, "travelers": null, "has_new_info": true, "missing_slots": ["目的地", "行程天数"], "follow_up_message": "好的，已记录您的出发日期是3月14日。请问您想去哪里旅游呢？计划玩几天？"}}

用户输入："上海"
输出：{{"destination": "上海", "start_date": null, "end_date": null, "duration": null, "travelers": null, "has_new_info": true, "missing_slots": ["出发日期", "行程天数"], "follow_up_message": "上海是个好地方！请问您计划什么时候出发？玩几天呢？"}}

用户输入："玩两天"
输出：{{"destination": null, "start_date": null, "end_date": null, "duration": 2, "travelers": null, "has_new_info": true, "missing_slots": ["目的地", "出发日期"], "follow_up_message": "好的，2天的行程。请问您想去哪里？什么时候出发？"}}

用户输入："三天"
输出：{{"destination": null, "start_date": null, "end_date": null, "duration": 3, "travelers": null, "has_new_info": true, "missing_slots": ["目的地", "出发日期"], "follow_up_message": "好的，3天的行程。请问您想去哪里？什么时候出发？"}}

用户输入："玩5天"
输出：{{"destination": null, "start_date": null, "end_date": null, "duration": 5, "travelers": null, "has_new_info": true, "missing_slots": ["目的地", "出发日期"], "follow_up_message": "好的，5天的行程。请问您想去哪里？什么时候出发？"}}"""

    def __init__(self, **kwargs):
        super().__init__(tools=ALL_TOOLS, **kwargs)

    async def analyze_intent(self, user_input: str, context: str = "") -> Dict[str, Any]:
        """Analyze user intent using LLM with structured prompt."""
        # 先尝试使用 LLM 分析
        if self.llm:
            try:
                # 解析当前上下文中的旅行信息
                current_destination = "未设置"
                current_start_date = "未设置"
                current_end_date = "未设置"
                current_travelers = "未设置"

                # 从上下文解析已有信息
                if context:
                    if "目的地：" in context:
                        match = re.search(r'目的地[：:]\s*(\S+)', context)
                        if match:
                            current_destination = match.group(1)
                    if "出发日期：" in context:
                        match = re.search(r'出发日期[：:]\s*(\S+)', context)
                        if match:
                            current_start_date = match.group(1)

                # 构建完整 prompt
                full_prompt = self.INTENT_PROMPT.format(
                    context=context or "（无）",
                    current_destination=current_destination,
                    current_start_date=current_start_date,
                    current_end_date=current_end_date,
                    current_travelers=current_travelers,
                    user_input=user_input
                )

                # 调用 LLM
                response = await self.llm.ainvoke(full_prompt)

                # 解析 JSON 响应
                json_match = re.search(r'\{[^{}]*\}', response, re.DOTALL)
                if json_match:
                    try:
                        result = json.loads(json_match.group())
                        # 转换为内部格式
                        return self._convert_llm_result(result)
                    except json.JSONDecodeError:
                        pass

            except Exception as e:
                print(f"LLM 意图分析失败: {e}")
                import traceback
                traceback.print_exc()

        # Fallback: 规则分析
        return self._rule_based_analysis(user_input)

    def _convert_llm_result(self, llm_result: Dict) -> Dict[str, Any]:
        """将 LLM 返回的结果转换为内部格式."""
        result = {
            "intent": "collect_info",
            "cities": [],
            "dates": [],
            "update_date": False,
            "update_duration": False,
            "update_travelers": False,
            "extracted_date": None,
            "extracted_duration": None,
            "extracted_travelers": None,
            "needs_info": llm_result.get("missing_slots", []),
            "response": llm_result.get("follow_up_message", ""),
            "has_new_info": llm_result.get("has_new_info", False)
        }

        # 处理目的地
        if llm_result.get("destination"):
            result["cities"] = [llm_result["destination"]]
            result["update_destination"] = True

        # 处理出发日期
        if llm_result.get("start_date"):
            date_str = llm_result["start_date"]
            try:
                from datetime import datetime
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                result["extracted_date"] = {"month": date_obj.month, "day": date_obj.day, "year": date_obj.year}
                result["update_date"] = True
            except:
                pass

        # 处理天数
        if llm_result.get("duration"):
            result["extracted_duration"] = llm_result["duration"]
            result["update_duration"] = True

        # 处理人数
        if llm_result.get("travelers"):
            result["extracted_travelers"] = llm_result["travelers"]
            result["update_travelers"] = True

        return result

    def _rule_based_analysis(self, user_input: str) -> Dict[str, Any]:
        """Rule-based intent analysis - 作为 LLM 的后备方案."""
        from datetime import datetime, timedelta

        result = {
            "intent": "collect_info",
            "cities": [],
            "dates": [],
            "update_date": False,
            "update_duration": False,
            "update_travelers": False,
            "extracted_date": None,
            "extracted_duration": None,
            "extracted_travelers": None,
            "needs_info": [],
            "response": "",
            "has_new_info": False
        }

        # City detection - 扩展城市列表（从城市信息表提取）
        cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '西安', '南京', '武汉', '重庆',
                  '苏州', '天津', '长沙', '郑州', '青岛', '大连', '厦门', '昆明', '三亚', '桂林',
                  '丽江', '大理', '张家界', '黄山', '珠海', '无锡', '宁波', '福州', '济南', '烟台',
                  '哈尔滨', '沈阳', '长春', '石家庄', '太原', '呼和浩特', '乌鲁木齐', '拉萨',
                  '银川', '西宁', '兰州', '贵阳', '南宁', '海口', '台北', '香港', '澳门',
                  # 新增热门城市
                  '东莞', '佛山', '惠州', '中山', '常州', '南通', '扬州', '镇江', '泰州',
                  '嘉兴', '绍兴', '金华', '台州', '温州', '湖州', '舟山', '芜湖', '泉州', '漳州',
                  '九江', '赣州', '威海', '日照', '洛阳', '开封', '南阳', '宜昌', '襄阳', '株洲',
                  '湘潭', '衡阳', '岳阳', '汕头', '湛江', '茂名', '北海', '柳州',
                  '绵阳', '宜宾', '泸州', '乐山', '南充', '遵义', '曲靖', '玉溪', '咸阳', '延安',
                  '宝鸡', '天水', '酒泉', '克拉玛依', '珠海', '汕头', '湛江', '茂名', '揭阳',
                  '潮州', '清远', '韶关', '梅州', '河源', '阳江', '云浮', '汕尾',
                  '湖州', '金华', '衢州', '丽水', '台州', '舟山', '嘉兴', '绍兴', '温州',
                  '泰安', '临沂', '潍坊', '济宁', '淄博', '德州', '聊城', '滨州', '菏泽',
                  '保定', '邯郸', '邢台', '张家口', '承德', '唐山', '廊坊', '沧州', '衡水',
                  '大同', '临汾', '运城', '晋中', '长治', '晋城', '朔州', '忻州', '吕梁',
                  '包头', '赤峰', '通辽', '鄂尔多斯', '呼伦贝尔', '巴彦淖尔', '乌兰察布',
                  '鞍山', '抚顺', '本溪', '丹东', '锦州', '营口', '阜新', '辽阳', '盘锦', '铁岭', '朝阳', '葫芦岛',
                  '吉林', '四平', '辽源', '通化', '白山', '松原', '白城',
                  '齐齐哈尔', '牡丹江', '佳木斯', '大庆', '鸡西', '双鸭山', '伊春', '七台河', '鹤岗', '黑河', '绥化',
                  '常州', '徐州', '连云港', '淮安', '盐城', '扬州', '镇江', '泰州', '宿迁',
                  '合肥', '芜湖', '蚌埠', '淮南', '马鞍山', '淮北', '铜陵', '安庆', '黄山', '滁州', '阜阳', '宿州', '六安', '亳州', '池州', '宣城',
                  '福州', '厦门', '莆田', '三明', '泉州', '漳州', '南平', '龙岩', '宁德',
                  '南昌', '景德镇', '萍乡', '九江', '新余', '鹰潭', '赣州', '吉安', '宜春', '抚州', '上饶',
                  '济南', '青岛', '淄博', '枣庄', '东营', '烟台', '潍坊', '济宁', '泰安', '威海', '日照', '临沂', '德州', '聊城', '滨州', '菏泽',
                  '开封', '洛阳', '平顶山', '安阳', '鹤壁', '新乡', '焦作', '濮阳', '许昌', '漯河', '三门峡', '南阳', '商丘', '信阳', '周口', '驻马店',
                  '黄石', '十堰', '宜昌', '襄阳', '鄂州', '荆门', '孝感', '荆州', '黄冈', '咸宁', '随州', '恩施',
                  '株洲', '湘潭', '衡阳', '邵阳', '岳阳', '常德', '张家界', '益阳', '郴州', '永州', '怀化', '娄底', '湘西',
                  '深圳', '珠海', '汕头', '佛山', '韶关', '湛江', '肇庆', '江门', '茂名', '惠州', '梅州', '汕尾', '河源', '阳江', '清远', '东莞', '中山', '潮州', '揭阳', '云浮',
                  '南宁', '柳州', '桂林', '梧州', '北海', '防城港', '钦州', '贵港', '玉林', '百色', '贺州', '河池', '来宾', '崇左',
                  '海口', '三亚', '三沙', '儋州',
                  '成都', '自贡', '攀枝花', '泸州', '德阳', '绵阳', '广元', '遂宁', '内江', '乐山', '南充', '眉山', '宜宾', '广安', '达州', '雅安', '巴中', '资阳', '阿坝', '甘孜', '凉山',
                  '贵阳', '六盘水', '遵义', '安顺', '毕节', '铜仁', '黔西南', '黔东南', '黔南',
                  '昆明', '曲靖', '玉溪', '保山', '昭通', '丽江', '普洱', '临沧', '楚雄', '红河', '文山', '西双版纳', '大理', '德宏', '怒江', '迪庆',
                  '拉萨', '昌都', '山南', '日喀则', '那曲', '阿里', '林芝',
                  '西安', '铜川', '宝鸡', '咸阳', '渭南', '延安', '汉中', '榆林', '安康', '商洛',
                  '兰州', '嘉峪关', '金昌', '白银', '天水', '武威', '张掖', '平凉', '酒泉', '庆阳', '定西', '陇南', '临夏', '甘南',
                  '西宁', '海东', '海北', '黄南', '海南', '果洛', '玉树', '海西',
                  '银川', '石嘴山', '吴忠', '固原', '中卫',
                  '乌鲁木齐', '克拉玛依', '吐鲁番', '哈密', '昌吉', '博尔塔拉', '巴音郭楞', '阿克苏', '克孜勒苏', '喀什', '和田', '伊犁', '塔城', '阿勒泰']

        for city in cities:
            if city in user_input:
                result["cities"].append(city)
                result["has_new_info"] = True

        # Province to city mapping
        provinces = {
            "四川": "成都", "广东": "广州", "浙江": "杭州", "江苏": "南京",
            "山东": "济南", "河南": "郑州", "湖北": "武汉", "湖南": "长沙",
            "福建": "福州", "云南": "昆明", "海南": "三亚", "贵州": "贵阳",
            "黑龙江": "哈尔滨", "辽宁": "沈阳", "吉林": "长春", "陕西": "西安",
        }
        for province, city in provinces.items():
            if province in user_input and city not in result["cities"]:
                result["cities"].append(city)
                result["has_new_info"] = True

        # Date extraction - 支持更多格式
        # 格式1: 3月14号, 3月14日, 03-14
        date_match1 = re.search(r'(\d{1,2})月(\d{1,2})[日号]?', user_input)
        # 格式2: 三月十四
        date_match2 = re.search(r'([一二三四五六七八九十]+)月([一二三四五六七八九十]+)[日号]?', user_input)
        # 格式3: 3-14, 3.14, 3/14
        date_match3 = re.search(r'(\d{1,2})[-./](\d{1,2})(?!\d)', user_input)
        # 格式4: 下周, 下个月
        if "下周" in user_input or "下星期" in user_input:
            next_week = datetime.now() + timedelta(days=7)
            result["extracted_date"] = {"month": next_week.month, "day": next_week.day, "year": next_week.year}
            result["update_date"] = True
            result["has_new_info"] = True
        elif date_match1:
            month = int(date_match1.group(1))
            day = int(date_match1.group(2))
            year = datetime.now().year
            if month < datetime.now().month:
                year += 1
            result["extracted_date"] = {"month": month, "day": day, "year": year}
            result["update_date"] = True
            result["has_new_info"] = True
        elif date_match2:
            chinese_nums = {'一':1,'二':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10, '十一':11, '十二':12}
            month = chinese_nums.get(date_match2.group(1), 0)
            day = chinese_nums.get(date_match2.group(2), 0)
            if month and day:
                year = datetime.now().year
                if month < datetime.now().month:
                    year += 1
                result["extracted_date"] = {"month": month, "day": day, "year": year}
                result["update_date"] = True
                result["has_new_info"] = True
        elif date_match3:
            month = int(date_match3.group(1))
            day = int(date_match3.group(2))
            if 1 <= month <= 12 and 1 <= day <= 31:
                year = datetime.now().year
                if month < datetime.now().month:
                    year += 1
                result["extracted_date"] = {"month": month, "day": day, "year": year}
                result["update_date"] = True
                result["has_new_info"] = True

        # Duration extraction - 支持更多表达
        duration_patterns = [
            r'(\d+)[天日]',
            r'玩(\d+)[天日]',
            r'(\d+)[天日]的行程',
            r'行程(\d+)[天日]',
            r'([一二三四五六七八九十两]+)[天日]',
            r'玩([一二三四五六七八九十两]+)[天日]',
            r'去([一二三四五六七八九十两]+)[天日]',
        ]
        # 扩展中文数字映射
        chinese_nums = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '两': 2, '俩': 2,
            '十一': 11, '十二': 12, '十三': 13, '十四': 14, '十五': 15,
            '十六': 16, '十七': 17, '十八': 18, '十九': 19, '二十': 20,
        }
        for pattern in duration_patterns:
            match = re.search(pattern, user_input)
            if match:
                val = match.group(1)
                if val.isdigit():
                    result["extracted_duration"] = int(val)
                else:
                    # 先尝试完整匹配
                    if val in chinese_nums:
                        result["extracted_duration"] = chinese_nums[val]
                    else:
                        # 尝试解析复合数字，如 "二十三"
                        try:
                            # 处理 "二十X" 格式
                            if val.startswith('二十'):
                                rest = val[2:]
                                if rest:
                                    result["extracted_duration"] = 20 + chinese_nums.get(rest, 0)
                                else:
                                    result["extracted_duration"] = 20
                            elif val.startswith('三十'):
                                rest = val[2:]
                                if rest:
                                    result["extracted_duration"] = 30 + chinese_nums.get(rest, 0)
                                else:
                                    result["extracted_duration"] = 30
                            else:
                                result["extracted_duration"] = chinese_nums.get(val, 3)
                        except:
                            result["extracted_duration"] = 3
                result["update_duration"] = True
                result["has_new_info"] = True
                break

        # Travelers extraction - 支持中文数字
        travelers_patterns = [
            r'(\d+)[人个位]',
            r'(\d+)[人个位]出行',
            r'我们(\d+)[人个]',
            r'([一二三四五六七八九十两]+)[人个位]',
            r'我们([一二三四五六七八九十两]+)[人个]',
            r'([一二三四五六七八九十两]+)个人',
            r'一家([一二三四五六七八九十两]+)口',
        ]
        # 中文数字映射
        travelers_chinese_nums = {
            '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
            '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
            '两': 2, '俩': 2,
        }
        for pattern in travelers_patterns:
            match = re.search(pattern, user_input)
            if match:
                val = match.group(1)
                if val.isdigit():
                    result["extracted_travelers"] = int(val)
                else:
                    result["extracted_travelers"] = travelers_chinese_nums.get(val, 1)
                result["update_travelers"] = True
                result["has_new_info"] = True
                break

        return result


class TripPlanningAgent(BaseTravelAgent):
    """Agent specialized in overall trip planning."""

    name = "trip_planning"
    description = "行程规划专家，负责整体旅行方案的制定"
    system_prompt = """你是一个专业的旅行规划师。你的职责是：

1. 根据用户的目的地、日期、人数等信息制定合理的行程
2. 推荐最佳游览路线和景点组合
3. 考虑交通、住宿、餐饮的合理安排
4. 提供实用的旅行建议和注意事项

请根据用户提供的信息，给出详细的行程规划建议。"""

    def __init__(self, **kwargs):
        super().__init__(tools=[TOOL_MAP["attractions"], TOOL_MAP["guides"]], **kwargs)


class AttractionAgent(BaseTravelAgent):
    """Agent specialized in attraction recommendations."""

    name = "attraction"
    description = "景点推荐专家，提供热门景点信息和游玩建议"
    system_prompt = """你是一个景点推荐专家。你的职责是：

1. 推荐目的地的热门景点和隐藏宝地
2. 提供景点的详细信息（开放时间、门票、交通等）
3. 根据用户的兴趣和偏好定制推荐
4. 给出游玩路线和时间安排建议

请根据用户的需求，推荐最合适的景点。"""

    def __init__(self, **kwargs):
        super().__init__(tools=[TOOL_MAP["attractions"], TOOL_MAP["amap_search"]], **kwargs)


class FoodAgent(BaseTravelAgent):
    """Agent specialized in food recommendations."""

    name = "food"
    description = "美食推荐专家，介绍当地特色美食和餐厅"
    system_prompt = """你是一个美食推荐专家。你的职责是：

1. 介绍目的地的特色美食和名小吃
2. 推荐高评分的餐厅和美食街
3. 根据用户的口味偏好提供个性化推荐
4. 分享美食文化和用餐建议

请根据用户的需求，推荐最值得一试的美食。"""

    def __init__(self, **kwargs):
        super().__init__(tools=[TOOL_MAP["food"], TOOL_MAP["amap_search"]], **kwargs)


class TransportAgent(BaseTravelAgent):
    """Agent specialized in transportation."""

    name = "transport"
    description = "交通出行专家，提供火车、航班等交通信息"
    system_prompt = """你是一个交通出行专家。你的职责是：

1. 查询火车、高铁、航班等交通信息
2. 比较不同出行方式的优缺点
3. 推荐最便捷和经济的选择
4. 提供购票建议和出行提示

请根据用户的需求，提供最佳的交通方案。"""

    def __init__(self, **kwargs):
        super().__init__(tools=[TOOL_MAP["railway"], TOOL_MAP["amap_search"]], **kwargs)


class BudgetAgent(BaseTravelAgent):
    """Agent specialized in budget planning."""

    name = "budget"
    description = "预算规划专家，帮助用户合理安排旅行预算"
    system_prompt = """你是一个预算规划专家。你的职责是：

1. 根据行程估算各项费用（交通、住宿、餐饮、门票等）
2. 提供省钱技巧和优惠信息
3. 帮助用户合理分配预算
4. 推荐性价比高的选择

请根据用户的预算和需求，给出合理的费用建议。"""

    def __init__(self, **kwargs):
        super().__init__(tools=ALL_TOOLS, **kwargs)


# Agent registry
AGENTS = {
    "coordinator": CoordinatorAgent,
    "trip_planning": TripPlanningAgent,
    "attraction": AttractionAgent,
    "food": FoodAgent,
    "transport": TransportAgent,
    "budget": BudgetAgent,
}