# -*- coding: utf-8 -*-
"""
优化分类结果 V8 - 按用户明确的分类规则重新整理

用户背景：
- 上海交大 AI专业 大三，准备考研清北
- 男生，喜欢看美女
- 关注医美/颜值提升
- 关注两性认知
- 关注地缘政治/国际形势

分类规则：
1. 数学 ≠ 考研（必须分开）
2. 美女 ≠ 形象提升/医美 ≠ 两性情感（三个不同）
3. 时政/地缘政治（含军事）≠ 历史/人文（不混淆）
4. 心理学 → 两性情感
5. 科普细分到具体学科
6. 生活类是大类：美女、Vlog、汽车、电影、娱乐、美食、游戏、音乐等
"""

import json
import re
from pathlib import Path

base_path = Path(__file__).parent

# 读取V2分类结果
with open(base_path / "分类结果_v2.json", "r", encoding="utf-8") as f:
    result = json.load(f)

# ========== 分类映射规则 ==========

# 关键词到目标分类的映射
CATEGORY_RULES = {
    # === 考研类（统一）===
    "考研": [
        "考研", "研究生", "保研", "上岸", "复试", "高等教育", "学习教师",
        "考研数学", "数学一", "考研高数", "考研线代", "考研概率",
        "考研英语", "英语一", "英语二",
        "考研政治", "肖秀荣", "徐涛", "腿姐",
        "408", "826", "考研数据结构", "考研操作系统", "考研计组", "考研计网",
        "王道", "天勤"
    ],

    # === 学科类（纯学科，非考研向）===
    "数学": [
        "数学", "高数", "线代", "线性代数", "概率", "统计", "微积分",
        "数学分析", "抽象代数", "数论", "几何", "3Blue1Brown"
    ],
    "编程/计算机": [
        "编程", "程序", "代码", "开发", "软件", "算法", "数据结构",
        "Python", "Java", "C++", "前端", "后端", "Web", "计算机",
        "Linux", "Git", "数据库"
    ],
    "人工智能/AI": [
        "人工智能", "AI", "机器学习", "深度学习", "神经网络",
        "大模型", "LLM", "GPT", "Claude", "ChatGPT", "Prompt",
        "计算机视觉", "CV", "NLP", "自然语言", "强化学习",
        "Agent", "RAG", "向量",
        "机器人", "ROS", "机械臂", "自动驾驶", "无人机", "具身智能"
    ],
    "电气/电子/自动化": [
        "嵌入式", "单片机", "Arduino", "树莓派",
        "电气", "电子", "电路", "电力", "通信", "信号", "控制", "PLC", "自动化"
    ],
    "物理": [
        "物理", "量子", "力学", "电磁", "光学", "热力学", "相对论"
    ],
    "化学": ["化学", "有机", "无机", "分子"],
    "生物": ["生物", "基因", "细胞", "医学", "神经科学"],
    "天文": ["天文", "宇宙", "星球", "太空", "航天"],

    # === 男性向精确分类 ===
    "形象提升/医美": [
        "医美", "整形", "穿搭", "形象", "颜值提升", "变帅", "护肤",
        "发型", "五官", "脸型", "审美", "时尚穿搭"
    ],
    "两性情感": [
        "两性", "情感", "恋爱", "婚姻", "婚恋", "感情", "捞女", "龟男",
        "相亲", "约会", "PUA", "心理学", "心理", "人性", "社交",
        "男女", "国男", "国女", "情感认知"
    ],

    # === 时政 vs 历史（不混淆）===
    "时政/地缘政治": [
        "时政", "政治", "地缘", "国际", "中美", "美国", "欧洲", "俄罗斯",
        "中东", "日本", "韩国", "台湾", "军事", "战争", "武器", "国防",
        "外交", "政策", "新闻", "时事", "局势", "观察者", "张维为"
    ],
    "历史/人文": [
        "历史", "古代", "近代", "朝代", "皇帝", "战国", "三国", "唐宋",
        "明清", "民国", "文化", "传统", "哲学", "思想", "人文", "文学",
        "考古", "文物", "纪录片"
    ],

    # === 其他精确分类 ===
    "财经/金融": [
        "财经", "金融", "投资", "理财", "股票", "基金", "经济", "商业",
        "创业", "房地产", "房价"
    ],
    "效率工具": [
        "Obsidian", "Notion", "笔记", "效率", "生产力", "工具", "GTD",
        "知识管理", "PKM"
    ],
    "数码/科技": [
        "数码", "手机", "电脑", "硬件", "测评", "评测", "科技产品",
        "苹果", "iPhone", "安卓", "显卡", "CPU", "华为", "小米",
        "硬科技", "产品", "3C", "电子产品"
    ],

    # === 生活大类（包含很多子内容）===
    "生活": [
        "美女", "颜值", "小姐姐", "好看",  # 美女
        "Vlog", "日常", "生活", "记录",  # Vlog
        "汽车", "车", "驾驶", "自驾",  # 汽车
        "电影", "影视", "剧", "动漫", "番剧",  # 影视
        "娱乐", "搞笑", "鬼畜", "整活",  # 娱乐
        "美食", "吃", "做饭", "烹饪", "探店",  # 美食
        "游戏", "MC", "原神", "王者", "电竞",  # 游戏
        "音乐", "唱歌", "乐器", "钢琴", "吉他",  # 音乐
        "旅行", "旅游", "户外", "露营",  # 旅行
        "摄影", "拍照", "视频制作",  # 摄影
        "宠物", "猫", "狗", "萌宠",  # 宠物
        "健身", "运动", "减肥", "健康", "营养",  # 运动健康
        "舞蹈", "跳舞",  # 舞蹈
        "成长", "感悟", "访谈",  # 成长
        "图书", "阅读", "读书",  # 阅读
        "美术", "绘画", "画画",  # 美术
        "官方", "B站", "平台", "运营",  # 官方账号
        "科普", "科学",  # 科普归生活
    ],
}

# 特殊UP主手动指定分类
MANUAL_OVERRIDE = {
    # 美女UP主 → 生活
    "王六堡": "生活",
    "小鹿Lawrence": "生活",
    "沛沛瑶呀爱吃糖呀": "生活",
    "伢伢gagako": "生活",
    "-童锣烧_": "生活",
    "甜粥粥-": "生活",

    # 纯数学（非考研向）
    "分析学爱好者": "数学",
    "3Blue1Brown": "数学",
    "交大姚老师": "数学",
    "SJTU抽象代数": "数学",
    "线代铜": "数学",

    # 考研（统一分类）
    "宋浩老师官方": "考研",
    "猴博士爱讲课": "考研",
    "没咋了": "考研",
    "大鱼考研竞赛数学": "考研",
    "考研政治徐涛": "考研",
    "考研政治陆寓丰老师": "考研",
    "考研政治广智老师": "考研",
    "澄潇宇": "考研",
    "星伊云同桌自习室": "考研",

    # 两性情感
    "十三会魔法": "两性情感",

    # 形象提升/医美
    "十一的看脸日记": "形象提升/医美",

    # 时政/地缘政治
    "张维为": "时政/地缘政治",
    "观察者网": "时政/地缘政治",

    # 额外手动归类（其他类）
    "我是范志毅": "生活",  # 图书/阅读
    "边亮_网络安全": "编程/计算机",  # 网络安全
    "Michael范同学": "生活",  # 交大大学生活
    "水论文的程序猿-水导": "生活",  # 学生圈动态
    "喵星考拉": "数码/科技",  # 汽车/机械科普
    "卡布叻_周深": "生活",  # 音乐
    "是知识呀": "考研",  # 保研挑战
    "无尽沙砾": "数学",  # 近世代数、常微分方程等数学教学
    "电路通": "电气/电子/自动化",  # 电路学习
    "猫哥mao": "生活",  # 法学学习经验
    "加州理工Amy_Wang": "生活",  # 留学经验

    # 机器人区分：决策感知→AI，控制硬件→自动化
    "同济子豪兄": "人工智能/AI",  # 深度学习、CV
    "古月居GYH": "人工智能/AI",  # 具身智能
    "U航-首形科技": "人工智能/AI",  # 具身智能
    "Unitree宇树科技": "人工智能/AI",  # 机器人公司，感知决策
    "稚晖君": "人工智能/AI",  # 智元机器人创始人
}

def get_target_category(original_cat, up_name):
    """根据规则判断目标分类"""

    # 1. 先检查手动指定
    if up_name in MANUAL_OVERRIDE:
        return MANUAL_OVERRIDE[up_name]

    # 2. 考研类优先判断（所有考研相关都归到"考研"）
    original_lower = original_cat.lower()

    if "考研" in original_cat or "研究生" in original_cat or "保研" in original_cat:
        return "考研"

    # 3. 根据原分类名称中的关键词判断（按顺序匹配）
    # 先匹配更具体的分类
    priority_order = [
        "考研",
        "人工智能/AI", "电气/电子/自动化", "编程/计算机",
        "时政/地缘政治", "历史/人文",
        "形象提升/医美", "两性情感",
        "数学", "物理", "化学", "生物", "天文",
        "财经/金融", "效率工具", "数码/科技",
        "生活"
    ]

    for target_cat in priority_order:
        if target_cat in CATEGORY_RULES:
            for kw in CATEGORY_RULES[target_cat]:
                if kw.lower() in original_lower:
                    return target_cat

    # 4. 无法匹配的归到"其他"
    return "其他"


# ========== 处理逻辑 ==========

all_ups = []
for cat, ups in result["categories"].items():
    for up in ups:
        up["original_category"] = cat
        all_ups.append(up)

print(f"原始UP主总数: {len(all_ups)}")
print(f"原始分类数: {len(result['categories'])}")

# 重新分类
for up in all_ups:
    up["category"] = get_target_category(up["original_category"], up["name"])

# 统计
from collections import Counter
cat_counter = Counter(up["category"] for up in all_ups)
print(f"\n新分类统计:")
for cat, count in cat_counter.most_common():
    print(f"  {cat}: {count}")

# 重新组织
new_categories = {}
for up in all_ups:
    cat = up["category"]
    if cat not in new_categories:
        new_categories[cat] = []
    new_categories[cat].append({
        "name": up["name"],
        "mid": up["mid"],
        "reason": up.get("reason", ""),
        "original": up["original_category"]
    })

# 排序（按数量）
sorted_categories = dict(sorted(
    new_categories.items(),
    key=lambda x: (-len(x[1]), x[0])
))

# 保存JSON
output_path = base_path / "分类结果_v3.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"categories": sorted_categories}, f, ensure_ascii=False, indent=2)

# 保存Markdown
md_path = base_path / "分类结果_v3.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# B站关注UP主分类结果（V3 - 优化版）\n\n")
    total = sum(len(ups) for ups in sorted_categories.values())
    f.write(f"总计: {total} 个UP主，{len(sorted_categories)} 个分类\n\n")
    f.write("---\n\n")

    for category, ups in sorted_categories.items():
        f.write(f"## {category} ({len(ups)}个)\n\n")
        for up in sorted(ups, key=lambda x: x["name"]):
            mid = up.get('mid', '')
            f.write(f"- [{up['name']}](https://space.bilibili.com/{mid})\n")
        f.write("\n")

print(f"\n优化完成！")
print(f"新分类数量: {len(sorted_categories)}")
print(f"结果已保存到: {output_path}")
print(f"Markdown: {md_path}")
