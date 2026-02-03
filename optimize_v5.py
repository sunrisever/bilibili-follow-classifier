# -*- coding: utf-8 -*-
"""
优化分类结果 V5 - 拆分"教育/学习"到具体学科
用户是人工智能学生，学科包括：数学、物理、计算机、人工智能、电气/电子、考研政治、考研英语
"""

import json
from pathlib import Path

base_path = Path(__file__).parent

with open(base_path / "分类结果_最终版.json", "r", encoding="utf-8") as f:
    result = json.load(f)

# ========== 将"教育/学习"中的UP主分到具体学科 ==========
education_to_specific = {
    # 数学相关
    "宋浩老师官方": "数学",
    "大鱼考研竞赛数学": "数学",

    # 英语学习
    "KerryDowdle": "英语",
    "GPT中英字幕课程资源": "英语",

    # 学习方法/效率
    "加州理工Amy_Wang": "效率工具",
    "Johnny学": "效率工具",
    "喵星考拉": "效率工具",
    "每天两升水": "生活/Vlog",  # 学习陪伴类归生活
    "星伊云同桌自习室": "生活/Vlog",  # 学习直播类归生活
    "龙须糖会很甜": "生活/Vlog",

    # 其他
    "Sophie潘潘": "财经/金融",  # 商业咨询背景
    "Evaa4sure26": "生活/Vlog",  # 高考/学习vlog
    "我是小小魏w": "生活/Vlog",
    "灿出品": "生活/Vlog",
}

# ========== 其他手动修正 ==========
other_corrections = {
    # 考研政治/英语 -> 考研
    "考研政治徐涛": "考研/政治",
    "考研政治陆寓丰老师": "考研/政治",
    "考研政治广智老师": "考研/政治",

    # 未分类中的明确分类
    "交大姚老师": "数学",
    "南江山人": "历史/人文",

    # 高校/科研 -> 具体学科
    "Science科学杂志": "知识科普",
    "张维为": "时政/新闻",
    "猴博士爱讲课": "数学",  # 高数、线代、概率
    "chbpku": "编程/计算机",  # 北大计算机老师
    "出出要按时毕业": "生活/Vlog",  # 博士生活
    "鸭大坑导": "生活/Vlog",  # 博士生活
    "小花醉猫": "生活/Vlog",
    "PiKaChu345": "编程/计算机",
    "harcon-ma": "人工智能/AI",
    "线代铜": "数学",  # 线性代数

    # 其他调整
    "Stat_DSX": "数学",  # 统计学归数学
    "fcieee": "知识科普",  # 哲学思辨归知识科普
}

# ========== 处理逻辑 ==========

all_ups = []
for cat, ups in result["categories"].items():
    for up in ups:
        up["category"] = cat
        all_ups.append(up)

print(f"原始UP主总数: {len(all_ups)}")

# 应用修正
for up in all_ups:
    name = up["name"]

    # 1. 教育/学习拆分
    if name in education_to_specific:
        up["category"] = education_to_specific[name]

    # 2. 其他修正
    if name in other_corrections:
        up["category"] = other_corrections[name]

# 重新组织
new_categories = {}
for up in all_ups:
    cat = up["category"]
    # 删除空的"教育/学习"分类（已拆分）
    if cat == "教育/学习" and up["name"] in education_to_specific:
        continue
    if cat not in new_categories:
        new_categories[cat] = []
    new_categories[cat].append({
        "name": up["name"],
        "mid": up["mid"],
        "reason": up.get("reason", "")
    })

# 合并考研/数学到考研（保留作为子分类）
# 合并小分类
categories_to_merge = {
    "考研/数学辅导": "考研/数学",
    "统计/数据分析": "数学",
    "哲学/思辨": "知识科普",
    "影视/影评": "生活/Vlog",
    "影视/文艺Vlog": "生活/Vlog",
    "影视/电影评论": "生活/Vlog",
    "社会热点/泛资讯": "时政/新闻",
    "人物纪录片/真实记录": "生活/Vlog",
    "艺术/美术创作": "生活/Vlog",
    "职场/社会观察": "生活/Vlog",
    "体育/足球": "生活/Vlog",
    "直播/虚拟主播": "生活/Vlog",
    "影视解说/剧情分析": "生活/Vlog",
}

# 应用合并
final_categories = {}
for cat, ups in new_categories.items():
    final_cat = categories_to_merge.get(cat, cat)
    if final_cat not in final_categories:
        final_categories[final_cat] = []
    final_categories[final_cat].extend(ups)

# 排序
sorted_categories = dict(sorted(
    final_categories.items(),
    key=lambda x: (-len(x[1]), x[0])
))

# 保存
output_path = base_path / "分类结果_最终版.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"categories": sorted_categories}, f, ensure_ascii=False, indent=2)

md_path = base_path / "分类结果_最终版.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# B站关注UP主分类结果（最终版）\n\n")
    f.write(f"总计: {sum(len(ups) for ups in sorted_categories.values())} 个UP主，{len(sorted_categories)} 个分类\n\n")
    f.write("---\n\n")

    for category, ups in sorted_categories.items():
        f.write(f"## {category} ({len(ups)}个)\n\n")
        for up in sorted(ups, key=lambda x: x["name"]):
            mid = up.get('mid', '')
            f.write(f"- [{up['name']}](https://space.bilibili.com/{mid})\n")
        f.write("\n")

print(f"\n优化完成！")
print(f"分类数量: {len(sorted_categories)}")
print(f"\n各分类UP主数量:")
for cat, ups in sorted_categories.items():
    print(f"  {cat}: {len(ups)}")
