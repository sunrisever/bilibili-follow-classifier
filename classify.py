# -*- coding: utf-8 -*-
"""
B站关注UP主分类优化脚本
基于用户明确的分类规则

用户背景：上海交大AI专业大三，准备考研清北
"""

import json
from pathlib import Path
from collections import Counter

base_path = Path(__file__).parent

# 读取V2分类结果（包含合集信息）
with open(base_path / "分类结果_v2.json", "r", encoding="utf-8") as f:
    result = json.load(f)

# ========== 已取关，需要删除 ==========
TO_DELETE = {
    "Larry想做技术大佬",
}

# ========== 手动指定分类（优先级最高）==========
MANUAL = {
    # ===== 美女UP主 → 生活 =====
    "王六堡": "生活",
    "小鹿Lawrence": "生活",
    "沛沛瑶呀爱吃糖呀": "生活",
    "伢伢gagako": "生活",
    "-童锣烧_": "生活",
    "甜粥粥-": "生活",
    "米老师呀": "生活",  # 演员，vlog

    # ===== 纯数学（非考研向）=====
    "分析学爱好者": "数学",
    "3Blue1Brown": "数学",
    "交大姚老师": "数学",
    "SJTU抽象代数": "数学",
    "线代铜": "数学",
    "无尽沙砾": "数学",  # 近世代数、常微分方程

    # ===== 考研 =====
    "宋浩老师官方": "考研",
    "猴博士爱讲课": "考研",
    "没咋了": "考研",
    "大鱼考研竞赛数学": "考研",
    "考研政治徐涛": "考研",
    "考研政治陆寓丰老师": "考研",
    "考研政治广智老师": "考研",
    "澄潇宇": "考研",
    "星伊云同桌自习室": "考研",
    "是知识呀": "考研",

    # ===== 人工智能/AI（含机器人、ROS）=====
    "同济子豪兄": "人工智能/AI",
    "古月居GYH": "人工智能/AI",
    "U航-首形科技": "人工智能/AI",
    "Unitree宇树科技": "人工智能/AI",
    "稚晖君": "人工智能/AI",
    "上交大DAI实验室": "人工智能/AI",
    "上海交大ViSYS实验室": "人工智能/AI",
    "上海交大CIUS实验室": "人工智能/AI",
    "上海交通大学IPADS": "人工智能/AI",

    # ===== 编程/计算机 =====
    "上海交大计算机学院": "编程/计算机",
    "慕课网官方账号": "编程/计算机",
    "边亮_网络安全": "编程/计算机",

    # ===== 两性情感 =====
    "十三会魔法": "两性情感",

    # ===== 形象提升/医美 =====
    "十一的看脸日记": "形象提升/医美",

    # ===== 时政/地缘政治 =====
    "张维为": "时政/地缘政治",
    "观察者网": "时政/地缘政治",
    "小羊在鲜花舍": "生活",  # 新华社记者张扬，做访谈纪录片《扬声》

    # ===== 电气/电子/自动化 =====
    "电路通": "电气/电子/自动化",
    "郭天祥老师": "电气/电子/自动化",
    "工科男孙老师": "电气/电子/自动化",

    # ===== 数码/科技 =====
    "喵星考拉": "数码/科技",

    # ===== 生活（其他）=====
    "我是范志毅": "生活",
    "Michael范同学": "生活",
    "水论文的程序猿-水导": "生活",
    "卡布叻_周深": "生活",
    "猫哥mao": "生活",
    "加州理工Amy_Wang": "生活",
}

# ========== 关键词规则（按优先级排序）==========
# 注意：先匹配的优先级高

RULES = [
    # 考研（优先于数学、计算机等）
    ("考研", ["考研", "研究生", "保研", "上岸", "复试", "408", "826", "王道", "天勤"]),

    # AI（含机器人、ROS）
    ("人工智能/AI", [
        "人工智能", "AI", "机器学习", "深度学习", "神经网络",
        "大模型", "LLM", "GPT", "Claude", "ChatGPT", "Prompt",
        "计算机视觉", "CV", "NLP", "强化学习", "Agent", "RAG",
        "机器人", "ROS", "机械臂", "自动驾驶", "无人机", "具身智能", "SLAM"
    ]),

    # 编程/计算机
    ("编程/计算机", [
        "编程", "程序", "代码", "开发", "软件", "算法", "数据结构",
        "Python", "Java", "C++", "前端", "后端", "Web", "计算机",
        "Linux", "Git", "数据库", "网络安全", "黑客"
    ]),

    # 时政/地缘政治（含军事）
    ("时政/地缘政治", [
        "时政", "政治", "地缘", "国际", "中美", "美国", "欧洲", "俄罗斯",
        "中东", "日本", "韩国", "台湾", "军事", "战争", "武器", "国防",
        "外交", "政策", "新闻", "时事", "局势"
    ]),

    # 历史/人文（不要和时政混）
    ("历史/人文", [
        "历史", "古代", "近代", "朝代", "皇帝", "战国", "三国", "唐宋",
        "明清", "民国", "文化", "传统", "哲学", "人文", "文学", "考古"
    ]),

    # 数学
    ("数学", [
        "数学", "高数", "线代", "线性代数", "概率", "统计", "微积分",
        "数学分析", "抽象代数", "数论", "几何"
    ]),

    # 物理
    ("物理", ["物理", "量子", "力学", "电磁", "光学", "热力学", "相对论"]),

    # 电气/电子/自动化
    ("电气/电子/自动化", [
        "电气", "电子", "电路", "电力", "通信", "信号", "控制", "PLC",
        "嵌入式", "单片机", "Arduino", "树莓派", "自动化"
    ]),

    # 财经/金融
    ("财经/金融", [
        "财经", "金融", "投资", "理财", "股票", "基金", "经济", "商业", "创业"
    ]),

    # 效率工具
    ("效率工具", [
        "Obsidian", "Notion", "笔记", "效率", "生产力", "工具", "知识管理"
    ]),

    # 数码/科技
    ("数码/科技", [
        "数码", "手机", "电脑", "硬件", "测评", "评测", "科技产品",
        "苹果", "iPhone", "华为", "小米", "显卡"
    ]),

    # 形象提升/医美
    ("形象提升/医美", [
        "医美", "整形", "穿搭", "形象", "变帅", "护肤", "发型", "五官", "脸型"
    ]),

    # 两性情感（含心理学）
    ("两性情感", [
        "两性", "情感", "恋爱", "婚姻", "婚恋", "感情", "捞女", "龟男",
        "相亲", "约会", "心理学", "心理", "人性", "男女"
    ]),

    # 化学
    ("化学", ["化学", "有机", "无机", "分子"]),

    # 生活（最后匹配，包含很多子内容）
    ("生活", [
        "美女", "颜值", "小姐姐",
        "Vlog", "日常", "生活", "记录",
        "汽车", "车", "驾驶",
        "电影", "影视", "剧", "动漫",
        "娱乐", "搞笑", "鬼畜",
        "美食", "吃", "做饭", "探店",
        "游戏", "原神", "王者",
        "音乐", "唱歌", "乐器", "钢琴",
        "旅行", "旅游", "户外",
        "摄影", "拍照",
        "宠物", "猫", "狗",
        "健身", "运动",
        "舞蹈",
        "成长", "感悟",
        "科普", "科学"
    ]),
]


def classify(original_cat, up_name):
    """分类逻辑"""
    # 1. 手动指定优先
    if up_name in MANUAL:
        return MANUAL[up_name]

    # 2. 考研优先判断
    if "考研" in original_cat or "研究生" in original_cat or "保研" in original_cat:
        return "考研"

    # 3. 按规则匹配
    original_lower = original_cat.lower()
    for target_cat, keywords in RULES:
        for kw in keywords:
            if kw.lower() in original_lower:
                return target_cat

    # 4. 默认归生活
    return "生活"


# ========== 执行分类 ==========

all_ups = []
for cat, ups in result["categories"].items():
    for up in ups:
        # 跳过已取关的
        if up["name"] in TO_DELETE:
            continue
        up["original_category"] = cat
        all_ups.append(up)

print(f"原始UP主: {len(all_ups)}")
print(f"原始分类: {len(result['categories'])}")

# 重新分类
for up in all_ups:
    up["category"] = classify(up["original_category"], up["name"])

# 统计
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
        "reason": up.get("reason", "")
    })

# 排序
sorted_categories = dict(sorted(
    new_categories.items(),
    key=lambda x: (-len(x[1]), x[0])
))

# 保存JSON
output_path = base_path / "分类结果.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"categories": sorted_categories}, f, ensure_ascii=False, indent=2)

# 保存Markdown
md_path = base_path / "分类结果.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# B站关注UP主分类结果\n\n")
    total = sum(len(ups) for ups in sorted_categories.values())
    f.write(f"总计: {total} 个UP主，{len(sorted_categories)} 个分类\n\n")
    f.write("---\n\n")

    for category, ups in sorted_categories.items():
        f.write(f"## {category} ({len(ups)}个)\n\n")
        for up in sorted(ups, key=lambda x: x["name"]):
            mid = up.get('mid', '')
            f.write(f"- [{up['name']}](https://space.bilibili.com/{mid})\n")
        f.write("\n")

print(f"\n完成！分类数: {len(sorted_categories)}")
print(f"结果: {output_path}")
