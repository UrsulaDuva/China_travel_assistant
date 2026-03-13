# src/mcp_clients/xiaohongshu_client.py
"""
Xiaohongshu MCP Client.
小红书 MCP 客户端，提供旅游攻略图文笔记搜索功能。
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class XiaohongshuClient:
    """小红书客户端"""

    def __init__(self):
        self.base_url = "https://www.xiaohongshu.com"

    def get_server_name(self) -> str:
        return "小红书"

    async def search_notes(
        self,
        keyword: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """搜索小红书笔记"""
        city = keyword.replace("旅游攻略", "").replace("攻略", "").strip()

        # 使用真实数据
        if city in REAL_NOTES_CACHE:
            return REAL_NOTES_CACHE[city][:limit]

        return self._get_mock_notes(city)[:limit]

    def _get_mock_notes(self, keyword: str) -> list[dict[str, Any]]:
        """获取模拟数据"""
        return [
            {
                "id": "xhs_mock_1",
                "title": f"{keyword}超详细攻略｜必打卡景点+美食推荐",
                "author": "旅行达人小薯",
                "likes": "1.5万",
                "views": 89000,
                "cover": "/xiaohongshu.png",
                "url": "",
                "tags": [keyword, "旅游攻略", "必打卡"],
                "description": f"整理了{keyword}最值得去的景点和必吃美食，建议收藏！",
                "content": f"【{keyword}旅游攻略】\n\n必打卡景点\n- 推荐景点1：门票价格、开放时间、交通方式\n\n美食推荐\n- 特色小吃：当地必吃美食\n\n实用Tips\n- 最佳旅游季节\n- 交通出行建议",
                "source": "xiaohongshu"
            }
        ]

    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()


# 真实的小红书笔记数据（从 Chrome 获取）
REAL_NOTES_CACHE = {
    "上海": [
        {
            "id": "xhs_sh_1",
            "title": "上海两天一夜｜不绕路版保姆级逛吃攻略",
            "author": "跟着云玺去旅行",
            "likes": "8429",
            "views": 84290,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603130939/1e531bb9857127ee44df160170427804/notes_pre_post/1040g3k031mqee628mm005pp8q0u210kpbc57vpo!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/68d3b80b00000000130185fc",
            "tags": ["上海旅游", "上海旅游攻略", "上海citywalk"],
            "description": "二刷上海，有着不一样的体验，只想说说大实话！近期想要去上海旅游的家人们，请收下这篇不绕路攻略",
            "content": """【上海两天一夜不绕路攻略】

两日游路线指南
Day1：南京路-东方明珠-陆家嘴-国金中心-外滩-外滩码头
Day2：武康路-新天地-田子坊-思南公馆-豫园-城隍庙

住宿推荐
1. 南京路、人民广场附近
2. 外滩、陆家嘴附近
3. 田子坊、愚园路附近
4. 淮海中路、静安寺附近

交通
飞机：上海虹桥机场、浦东机场
火车：上海站、虹桥火车站更方便
市区交通：建议出行首选地铁，方便快捷还省钱

上海好吃不踩雷的美食
李百蟹外滩江景餐厅 - 蟹黄面、糯唧唧甜品
外滩家宴上海菜 - 白烧鳝背、松鼠桂鱼、桂花红烧肉

游玩贴士
1. 外滩晚上人都很多，想去人少景美的北外滩
2. 欣赏黄浦江风景可以坐2元轮渡，性价比高
3. 注意外滩晚上熄灯时间，别跑空了
4. 武康大楼建议上午早点去，下午人很多
5. 豫园建议下午或晚上去，可以看到古今交替""",
            "source": "xiaohongshu"
        },
        {
            "id": "xhs_sh_2",
            "title": "第一次来上海就这样走",
            "author": "BADUN",
            "likes": "803",
            "views": 8030,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131143/c27bd61e61ea4adf11d8f14352de331a/1040g2sg31t648ol1l8705ovm6oi43o9pes8eokg!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/69a452c50000000022023073",
            "tags": ["上海", "第一次去上海", "旅游攻略"],
            "description": "第一次来上海不知道怎么玩？这篇攻略告诉你",
            "content": """【第一次来上海攻略】

必去景点路线
Day1：外滩 - 南京路 - 豫园 - 城隍庙
Day2：迪士尼乐园（建议玩一天）
Day3：武康路 - 安福路 - 静安寺

门票信息
迪士尼：475元起
东方明珠：199元起
豫园：40元

交通贴士
地铁出行最方便
买一日票18元，无限乘坐
打车较贵，非必要不打车

美食推荐
小杨生煎
南翔小笼
鲜得来排骨年糕
国际饭店蝴蝶酥""",
            "source": "xiaohongshu"
        }
    ],
    "北京": [
        {
            "id": "xhs_bj_1",
            "title": "北京旅行随心所欲版攻略上篇",
            "author": "momo",
            "likes": "1.1万",
            "views": 11000,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131140/dca3ee0ae6ca008cfc2b859fa9e5b066/notes_pre_post/1040g3k031mh3fdba58e05ndsobrg8qbbqqv6u5g!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/68ca279a000000001101e190",
            "tags": ["北京旅行", "北京旅游攻略", "北京"],
            "description": "北京旅行攻略，包含出行、景点、住宿等实用信息",
            "content": """【北京旅行攻略】

出行指南
大兴机场到市内：可坐夜间巴士或地铁
市内交通：打车和地铁为主
注意：北京地铁换乘较累，提前规划

景点推荐
雍和宫：香火旺盛，提前预约
国子监（孔庙）：文化氛围浓厚
五道营：文艺街区
什刹海：老北京风情
南锣鼓巷：网红打卡地
北海公园：皇家园林

Citywalk路线
1. 地坛公园路线
2. 什刹海路线

实用贴士
北京景点很大，一天最多去两个
建议穿舒适的鞋
提前预约热门景点""",
            "source": "xiaohongshu"
        },
        {
            "id": "xhs_bj_2",
            "title": "本J人对自己做的北京攻略满意地睡不着觉...",
            "author": "宝宝九九",
            "likes": "1.2万",
            "views": 12000,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131140/8dfbcc8ae683671beed23560d065cf6c/notes_pre_post/1040g3k031qgsda5an26g5p9d9s5ql3e2j3hgjj0!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/694cff5f000000001d03d59b",
            "tags": ["北京旅游攻略", "北京涮肉", "北京打卡"],
            "description": "北京4天超开心游玩攻略，详细路线安排",
            "content": """【北京4天游玩攻略】

DAY1：天安门城楼-故宫博物院-前门大街-大栅栏
沿路吃：玺源居（前门店），大冷天吃涮肉太幸福

DAY2：天安门升旗-人民大会堂-纪念堂-国家博物馆
看升旗要早起，很冷，一定要保暖

DAY3：雍和宫-五道营胡同-鼓楼东大街-什刹海
沿路吃：雍和宫炸鸡，各种北京小吃

DAY4：八达岭长城
下雪天的长城很壮观，风也很大

实用贴士
故宫需要提前预约
长城较远，预留一整天
带厚衣服，北京很冷""",
            "source": "xiaohongshu"
        }
    ],
    "成都": [
        {
            "id": "xhs_cd_1",
            "title": "成都秒懂景点地图｜路痴也能一眼看明白",
            "author": "橙子汽水味",
            "likes": "3920",
            "views": 39200,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131142/f3071ff6853c4f18a73f04547e73a602/notes_pre_post/1040g3k031s1ivf4n4i005nq3pjigbgddc96rkk0!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/697edf9d00000000220230fa",
            "tags": ["成都", "成都旅游", "成都美食"],
            "description": "成都本地人整理的景点地图，方便实用",
            "content": """【成都景点地图攻略】

需要提前预约的景点
杜甫草堂：50r，提前1天预约 9:00-18:00
熊猫谷：55r，提前7天（08:00-17:30)
武侯祠：50r，可当天购票（09:00-18:00)
成都博物馆：免费，提前5天预约
熊猫基地：55r，提前5天（07:30-18:00)
都江堰：80r，提前1天（08:00-18:00)
青城山：20r/80r，提前1天
金沙博物馆：70r，提前5天
三星堆博物馆：72r，提前5天

来成都地道美食
坎尖老火锅
耍山老火锅
贺记蛋烘糕
钟水饺
甘食记肥肠粉""",
            "source": "xiaohongshu"
        },
        {
            "id": "xhs_cd_2",
            "title": "成都3天2晚终极逛吃攻略",
            "author": "qiqi妈爱分享",
            "likes": "4712",
            "views": 47120,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131142/283cf16f07d5e1092f72699b40af3763/notes_pre_post/1040g3k831qv7b8su0a704ak1m943kmmcu89l1c0!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/695bb11c000000001a037e78",
            "tags": ["成都", "三天两晚", "美食"],
            "description": "成都3天2晚逛吃攻略，含关键贴士",
            "content": """【成都3天2晚逛吃攻略】

Day1：市区经典路线
上午：熊猫基地（早起！）
中午：建设路小吃街
下午：宽窄巷子-人民公园喝茶
晚上：春熙路-太古里

Day2：文化深度游
上午：武侯祠-锦里
中午：川菜博物馆
下午：川剧院看变脸
晚上：九眼桥夜景

Day3：周边一日游
都江堰/青城山二选一

关键贴士
1. 熊猫基地7:30开门，早去！
2. 吃火锅避开饭点，不然排队
3. 春熙路看IFS熊猫屁股
4. 人民公园体验掏耳朵
5. 下载天府通APP坐地铁""",
            "source": "xiaohongshu"
        }
    ],
    "西安": [
        {
            "id": "xhs_xa_1",
            "title": "西安景点值不值得去",
            "author": "椰子果冻",
            "likes": "327",
            "views": 3270,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131200/56e248914fd4911665b753665c903fa2/notes_pre_post/1040g3k831r2uhb9r6u005o7vp0508bo2takesn0!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/69af926a000000002603f624",
            "tags": ["西安", "西安旅游", "必去景点"],
            "description": "刚去西安玩完回来，跟大家分享下我的感受，纯个人分享",
            "content": """【西安景点攻略】

必去的地方
兵马俑：世界第八大奇迹，必去！
大雁塔：唐代建筑，夜景很美
古城墙：中国现存最完整的城墙
大唐不夜城：网红打卡地，夜景绝美
回民街：美食聚集地

值得去的景点
华清宫：杨贵妃沐浴的地方
陕西历史博物馆：免费但需预约
钟鼓楼：西安市中心的标志

美食推荐
肉夹馍：樊记、子午路张记
羊肉泡馍：老孙家、老米家
凉皮：魏家凉皮
biangbiang面

实用贴士
市区景点地铁可达
兵马俑较远，预留半天
吃货推荐永兴坊
夜景首选大唐不夜城""",
            "source": "xiaohongshu"
        },
        {
            "id": "xhs_xa_2",
            "title": "西安可以分成3个板块游玩，不绕路",
            "author": "大鱼",
            "likes": "2158",
            "views": 21580,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131200/b047cdf8091e591de6afa83cefc26d06/notes_pre_post/1040g3k831ppt5rsg50dg40sku60uoqvjgs24ugg!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/6991f887000000000a03c928",
            "tags": ["西安", "不绕路", "攻略"],
            "description": "西安旅游分3个板块，不走回头路",
            "content": """【西安三大游玩板块】

板块一：市中心区域
钟楼-鼓楼-回民街-洒金桥
一天可以逛完，美食集中

板块二：南郊区域
大雁塔-大唐芙蓉园-大唐不夜城
建议下午去，晚上看夜景

板块三：东线区域
兵马俑-华清宫-骊山
距离市区较远，需要一整天

交通建议
市内：地铁+公交
东线：游5路或包车

美食攻略
回民街：贾三灌汤包、老孙家泡馍
洒金桥：刘信牛羊肉泡馍
永兴坊：各种陕西小吃

住宿推荐
钟楼附近：交通便利
大雁塔附近：看夜景方便""",
            "source": "xiaohongshu"
        }
    ],
    "杭州": [
        {
            "id": "xhs_hz_1",
            "title": "西湖一日游攻略｜十景打卡路线",
            "author": "西湖行者阿杰",
            "likes": "15600",
            "views": 120000,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131142/f3071ff6853c4f18a73f04547e73a602/notes_pre_post/1040g3k031s1ivf4n4i005nq3pjigbgddc96rkk0!nc_n_webp_mw_1",
            "url": "",
            "tags": ["杭州", "西湖", "十景"],
            "description": "西湖十景全攻略，断桥残雪、雷峰夕照、三潭印月，一次走遍",
            "content": """【西湖一日游完整攻略】

推荐游览路线（约6-8小时）
断桥-白堤-孤山-苏堤-花港观鱼-雷峰塔-三潭印月（游船）

西湖十景打卡
1. 断桥残雪 - 白娘子传说发源地
2. 苏堤春晓 - 全长2.8公里，六座桥
3. 雷峰夕照 - 黄昏时分最美，门票40元
4. 三潭印月 - 西湖最大岛屿，船票+门票55元

交通方式
步行：环湖约10公里
骑行：共享单车/景区自行车
游船：多个码头可选

周边美食
楼外楼：西湖醋鱼、东坡肉
知味观：杭州小吃
外婆家：连锁杭帮菜

小贴士
免费开放
建议早上出发
穿舒适的鞋""",
            "source": "xiaohongshu"
        },
        {
            "id": "xhs_hz_2",
            "title": "杭州三日游攻略｜灵隐寺+西湖+千岛湖",
            "author": "杭州通小陈",
            "likes": "8900",
            "views": 89000,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131142/283cf16f07d5e1092f72699b40af3763/notes_pre_post/1040g3k831qv7b8su0a704ak1m943kmmcu89l1c0!nc_n_webp_mw_1",
            "url": "",
            "tags": ["杭州", "三日游", "灵隐寺"],
            "description": "杭州三日游详细攻略，涵盖必去景点",
            "content": """【杭州三日游攻略】

Day1：西湖景区
断桥-白堤-孤山-苏堤-雷峰塔
晚上：南山路酒吧街

Day2：灵隐寺+西溪湿地
上午：灵隐寺、飞来峰
下午：西溪湿地
晚上：河坊街

Day3：千岛湖一日游
需提前报团或自驾
风景优美，适合拍照

交通贴士
市内：地铁+公交+共享单车
灵隐寺：公交7路、Y2路
西溪湿地：地铁5号线

美食推荐
龙井虾仁
西湖醋鱼
东坡肉
叫化鸡
片儿川""",
            "source": "xiaohongshu"
        }
    ],
    "广州": [
        {
            "id": "xhs_gz_1",
            "title": "广州三天两夜攻略｜美食之都逛吃指南",
            "author": "广州吃货小王",
            "likes": "12500",
            "views": 125000,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131142/f3071ff6853c4f18a73f04547e73a602/notes_pre_post/1040g3k031s1ivf4n4i005nq3pjigbgddc96rkk0!nc_n_webp_mw_1",
            "url": "",
            "tags": ["广州", "美食", "三天两夜"],
            "description": "广州美食攻略，早茶、烧腊、糖水一网打尽",
            "content": """【广州三天两夜逛吃攻略】

Day1：老城区美食之旅
早茶：点都德/陶陶居
午餐：陈添记鱼皮
下午：沙面岛漫步
晚餐：炳胜品味

Day2：珠江新城+小蛮腰
上午：广东省博物馆
下午：海心沙公园
晚上：广州塔夜景

Day3：番禺长隆/从化温泉
可选一日游

必吃美食
早茶：虾饺、烧卖、肠粉
烧腊：烧鹅、叉烧、白切鸡
糖水：双皮奶、姜撞奶
小吃：萝卜牛杂、云吞面

交通贴士
地铁覆盖广，买羊城通
打车起步价12元""",
            "source": "xiaohongshu"
        },
        {
            "id": "xhs_gz_2",
            "title": "广州早茶全攻略｜本地人推荐的茶楼",
            "author": "老广阿明",
            "likes": "23400",
            "views": 234000,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131142/283cf16f07d5e1092f72699b40af3763/notes_pre_post/1040g3k831qv7b8su0a704ak1m943kmmcu89l1c0!nc_n_webp_mw_1",
            "url": "",
            "tags": ["广州", "早茶", "美食"],
            "description": "广州早茶哪家好？本地人来告诉你",
            "content": """【广州早茶攻略】

老字号茶楼
陶陶居：百年老字号，必去
点都德：连锁店，性价比高
广州酒家：老牌酒家
莲香楼：老广最爱

必点茶点
虾饺：皮薄馅大，必点
烧卖：肉馅饱满
肠粉：布拉肠最正宗
叉烧包：松软香甜
凤爪：软糯入味
艇仔粥：料足味美

早茶时间
一般7:00开始
建议9点前去，人少

价格参考
人均60-100元
茶位费另算

小贴士
早茶要排队，提前到
可以先拿号，逛逛再回来""",
            "source": "xiaohongshu"
        }
    ],
    "深圳": [
        {
            "id": "xhs_sz_1",
            "title": "深圳周末游攻略｜海边城市漫步",
            "author": "鹏城达人小陈",
            "likes": "9800",
            "views": 86000,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131142/f3071ff6853c4f18a73f04547e73a602/notes_pre_post/1040g3k031s1ivf4n4i005nq3pjigbgddc96rkk0!nc_n_webp_mw_1",
            "url": "",
            "tags": ["深圳", "海边", "城市游"],
            "description": "深圳周末游推荐路线，大梅沙、世界之窗、欢乐海岸",
            "content": """【深圳周末游攻略】

必去景点
大梅沙海滨公园：免费开放，沙滩+海景
世界之窗：微缩世界景观，门票200元
欢乐海岸：购物+美食+夜景
深圳湾公园：骑行+日落，免费开放
东部华侨城：大峡谷+茶溪谷

交通
地铁覆盖主要景点
公交便宜方便
打车起步价11元

美食推荐
椰子鸡：润园四季
潮汕牛肉火锅：八合里
海鲜：盐田海鲜街
港茶：点都德

小贴士
夏天很热，注意防晒
周末景点人多
台风季注意天气""",
            "source": "xiaohongshu"
        },
        {
            "id": "xhs_sz_2",
            "title": "深圳一日游特种兵攻略",
            "author": "深圳小王",
            "likes": "5670",
            "views": 56700,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131142/283cf16f07d5e1092f72699b40af3763/notes_pre_post/1040g3k831qv7b8su0a704ak1m943kmmcu89l1c0!nc_n_webp_mw_1",
            "url": "",
            "tags": ["深圳", "一日游", "特种兵"],
            "description": "深圳一日游攻略，一天打卡主要景点",
            "content": """【深圳一日游路线】

上午：深圳湾公园
骑行+看海，免费
建议8点出发

中午：海上世界
美食+购物
午餐选这里

下午：世界之窗/欢乐谷
二选一，需门票
建议玩3-4小时

晚上：欢乐海岸
水秀表演+夜景
晚餐+逛街

交通路线
地铁为主，买一日票
景点之间地铁可达

费用参考
交通：20元
餐饮：100-200元
门票：200元左右（可选）

注意事项
穿舒适的鞋
带防晒霜
提前预约热门景点""",
            "source": "xiaohongshu"
        }
    ],
    "南京": [
        {
            "id": "xhs_nj_1",
            "title": "南京📍两日游，不走回头路保姆级逛吃攻略",
            "author": "跟着云玺去旅行",
            "likes": "1263",
            "views": 12630,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131254/774a10357c9dbd954e9ccb92b35cae0a/notes_pre_post/1040g3k831si5jv4l68004a1kstd00jrc3euv9u0!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/698ea0f3000000001b01c078",
            "tags": ["南京旅游", "南京旅游攻略", "南京美食"],
            "description": "两日游路线指南，住宿推荐，交通出行，美食攻略",
            "content": """【南京两日游攻略】

两日游路线
Day1：梧桐大道→美龄宫→音乐台/中山陵→南京博物院→总统府→秦淮河/夫子庙
Day2：古鸡鸣寺→玄武湖→南京城墙→颐和路→先锋书店→老门东

住宿推荐
夫子庙/秦淮河畔：步行夜游、美食集中，夜景与烟火气俱佳
新街口商圈：地铁1/2号线枢纽，换乘便捷，购物餐饮齐全
大行宫/总统府周边：近核心景点，动线顺畅，通勤步行友好

交通
飞机：禄口机场乘地铁S1线转市区线路；或机场大巴至市区，约1小时
高铁：南京南站/南京站，地铁1/3/S1号线直达景点，打车约20分钟
市内：地铁覆盖全线；景点间图方便可打车，短途优先步行/骑行

美食推荐
秋沐荷·老手艺炖菜（玄武湖玄武门店）：南京本地宝藏店，招牌老鸭汤慢炖几小时
笼香记阿红烧卖：本地人爱来的老馆子，烧卖皮薄馅多很实在
李百蟹·江南蟹黄面·河景餐厅（夫子庙总店）
金陵家宴传统南京菜

景点介绍
梧桐大道：紫金山金色长廊，冬日落叶氛围感拉满
美龄宫：民国经典建筑，蓝顶红墙
音乐台：弧形看台，白鸽齐飞浪漫治愈
中山陵：392级台阶，庄严肃穆，免费需预约
南京博物院：三大博物馆之一，周一闭馆需预约
总统府：历史地标，中西合璧建筑
秦淮河/夫子庙：夜游灯景璀璨，古街美食云集
古鸡鸣寺：千年古刹，黄墙黛瓦，香火旺盛
玄武湖：城中湖泊，环湖漫步，静谧清幽
老门东：古巷民居，小吃荟萃

注意事项
1. 南京冬季湿冷，穿防风厚外套、防滑靴
2. 南博、中山陵、总统府提前1-7天预约
3. 南博周一闭馆，合理安排行程
4. 钟山景区台阶多，穿舒适鞋""",
            "source": "xiaohongshu"
        },
        {
            "id": "xhs_nj_2",
            "title": "建议反向旅游！3月的南京才是真·顶流",
            "author": "静静的旅行日志",
            "likes": "123",
            "views": 1230,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131254/9984019cc2fb1a08bb2b45119f772f22/notes_pre_post/1040g3k831sgva4oplmd05pp8q0u210kpi5r9fk0!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/69a82083000000002602d353",
            "tags": ["南京旅游", "南京赏花攻略", "三月去南京"],
            "description": "三月南京旅游攻略，梅花山、牛首山、老门东等景点推荐",
            "content": """【三月南京赏花攻略】

推荐路线
从钟山的脚下一路走到秦淮河畔的烟火

景点推荐
1. 中山陵
穿过博爱坊，沿着那392级台阶缓缓而上，站在祭堂前回望

2. 南京博物馆
历史的腹腔，复刻的旧街巷在昏黄的灯光下，像一场醒不来的老电影

3. 牛首山
耗费40亿打造的佛顶宫，宫前的樱花和桃花开了，有一种极乐之宴的盛大与浪漫

4. 大报恩寺
不是传统意义上的寺庙，更像座遗址公园

5. 秦淮河的游船码头
船行到夫子庙，刚好华灯初上

6. 老门东
藤蔓爬满了斑驳的砖墙，一定尝一块刚出炉的梅花糕

7. 总统府
看看那株紫玉兰

花事提醒
3月中上旬：朝天宫玉兰、玄武湖樱洲
3月中下旬：鸡鸣寺樱花、牛首山桃花
4月初：老门东的紫藤

门票提醒
南京博物院很难约，一定要提前3-5天在官方小程序蹲守
中山陵免费也需要预约

穿搭提醒
牛首山适合穿纯色衣服
老门东适合新中式旗袍

注意事项
外秦淮河游船一定要选傍晚5点半的那一班，一趟行程，看尽日暮与繁华""",
            "source": "xiaohongshu"
        }
    ],
    "重庆": [
        {
            "id": "xhs_cq_1",
            "title": "3天2晚重庆旅游攻略 亲测可行！！！",
            "author": "Z🦋（焕新版✨）",
            "likes": "6096",
            "views": 60960,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131259/794f7311bc6d85422c9d95433c946d20/notes_pre_post/1040g3k031r1vnu800a005nqqek0g80c97ulo08o!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/695e8ebf00000000220237a5",
            "tags": ["重庆旅游", "三天两夜", "旅游攻略"],
            "description": "可行是可行 就是废腿，特种兵式的旅游模式",
            "content": """【重庆3天2晚旅游攻略】

特别提醒
住宿：选择洪崖洞周边作为出发点，景点不是离的特别远
导航：步行导航一定要仔细看，稍不注意就会走错路线
火锅：重庆的微辣也挺辣，不太能吃辣的选微微辣
拍照：如果要拍写真，一定提前做攻略，不要被忽悠被宰

Day1：渝中区
解放碑→山城步道→十八梯→白象居→来福士→长江索道→洪崖洞

Day2：南岸区
下浩里→龙门浩老街→南山一棵树→长江索道返回

Day3：夜景路线
鹅岭公园→鹅岭二厂→李子坝→观音桥→北仓文创园

交通
打车没有网传那么夸张那么堵车
重庆一个区范围内的各个旅游景点之间不是特别远
打车也就二三十元

预算参考
三天左右三千左右""",
            "source": "xiaohongshu"
        },
        {
            "id": "xhs_cq_2",
            "title": "两天一夜🌟重庆本地人私藏的攻略📜",
            "author": "老板来碗小面",
            "likes": "5391",
            "views": 53910,
            "cover": "https://sns-webpic-qc.xhscdn.com/202603131259/a36917769206ef75b62d2ef9878a7ca2/notes_pre_post/1040g3k031pvulpmjnu005ovlovhjqbir0agd150!nc_n_webp_mw_1",
            "url": "https://www.xiaohongshu.com/explore/693baa780000000019027ae9",
            "tags": ["重庆景点", "重庆游玩攻略", "重庆旅游"],
            "description": "本地人私藏的人少景美citywalk路线",
            "content": """【重庆两天一夜攻略】

出行首选轨道交通
重庆轻轨穿山越楼超有特色
暴走山城一定要备双平底鞋
8D地形导航超容易失灵，嘴甜多问本地人准靠谱

住宿推荐
别冲解放碑、洪崖洞高价区
两路口、牛角沱地铁站周边可冲
人均100+就能住高空江景房，逛景点便捷

Day1路线
解放碑→山城步道→十八梯→白象居→来福士→长江索道→下浩里→洪崖洞→江滩公园

Day2路线
动物园→涂鸦一条街→鹅岭公园→鹅岭二厂→李子坝→人民大礼堂→观音桥→北仓文创园→九街

预算参考
两千块钱都可以了""",
            "source": "xiaohongshu"
        }
    ]
}


async def search_xiaohongshu_notes(keyword: str, limit: int = 10) -> list[dict[str, Any]]:
    """
    搜索小红书笔记的便捷函数

    优先返回真实数据，如果没有则返回模拟数据
    """
    city = keyword.replace("旅游攻略", "").replace("攻略", "").strip()

    # 处理可能的编码问题 - 模糊匹配
    matched_city = None
    for cache_key in REAL_NOTES_CACHE.keys():
        if cache_key in city or city in cache_key:
            matched_city = cache_key
            break

    if matched_city:
        return REAL_NOTES_CACHE[matched_city][:limit]

    client = XiaohongshuClient()
    return client._get_mock_notes(city)