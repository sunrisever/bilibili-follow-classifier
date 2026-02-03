# -*- coding: utf-8 -*-
"""
优化分类结果
1. 应用用户的手动修正
2. 合并相似分类
3. 考研和数学分开
"""

import json
from pathlib import Path

# 读取原始数据和分类结果
base_path = Path(__file__).parent
with open(base_path / "分类结果.json", "r", encoding="utf-8") as f:
    result = json.load(f)

with open(base_path / "up主原始数据.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# 创建 mid -> name 的映射
mid_to_name = {up["mid"]: up["name"] for up in raw_data}
name_to_mid = {up["name"]: up["mid"] for up in raw_data}

# ========== 用户手动修正 ==========
manual_corrections = {
    "沛沛瑶呀爱吃糖呀": "颜值/美女",
    "伢伢gagako": "颜值/美女",
    "甜粥粥": "颜值/美女",
    "小鹿Lawrence": "颜值/美女",
    "十三会魔法": "两性情感/自我提升",
    "峰哥亡命天涯": "两性情感/自我提升",
    "大沛沛沛吖": "两性情感/自我提升",
    "RM云汉交龙战队": "高校实验室/科研展示",
    "猫哥mao": "大学生/校园分享",
    "彭酱酱LINYA": "大学生/校园分享",
    "卓叔增重": "健康/医疗",
    "兔叭咯": "健康/医疗",
    "Cello纳多": "音乐",
    "Cuppix_": "音乐",
    "不想做实验的锦鲤仔": "评测/产品测评",
    "老爸评测": "评测/产品测评",
    "清华护肤学长王植": "评测/产品测评",
    "数学小呆瓜h": "数学",
    "电路通": "电气/电子学习",
    "鹏哥金融学考研": "金融/经济学",
    "哔哩哔哩课堂": "学习平台/官方",
}

# 要删除的UP主
to_delete = ["浮泽动漫协会", "hello刘小备", "Larry想做技术大佬"]

# ========== 分类合并映射 ==========
category_merge = {
    # 考研相关 -> 统一为"考研"
    "考研/数学": "考研",
    "教育/考研辅导": "考研",
    "考研/全程辅导": "考研",
    "教育/数学与学术": "数学",
    "数学/思辨": "数学",
    "学术/数学科普": "数学",

    # 编程/计算机
    "编程/计算机科学": "编程/计算机",
    "编程/IT技术": "编程/计算机",
    "编程/IT培训": "编程/计算机",
    "编程/算法与求职": "编程/计算机",
    "算法竞赛/ACM": "编程/计算机",
    "编程/个人学习": "编程/计算机",

    # 人工智能
    "人工智能/AI工具与应用": "人工智能/AI",
    "人工智能/教育与课程": "人工智能/AI",
    "人工智能/深度学习": "人工智能/AI",
    "人工智能/学术研究": "人工智能/AI",
    "人工智能/前沿科技": "人工智能/AI",
    "AI/科技/综合": "人工智能/AI",
    "AI/人工智能技术": "人工智能/AI",
    "机器人/ROS/智能控制": "人工智能/AI",

    # 科技数码
    "科技/数码评测": "科技/数码",
    "科技/硬件DIY与极客": "科技/数码",
    "科技/数码评测与行业分析": "科技/数码",
    "科技/硬件测评": "科技/数码",
    "消费电子/手机测评": "科技/数码",
    "消费Ƽ/产品测评": "科技/数码",

    # 生活/Vlog
    "生活/Vlog/日常": "生活/Vlog",
    "生活/Vlog与日常记录": "生活/Vlog",
    "生活/情感/泛日常": "生活/Vlog",
    "Vlog/生活记录": "生活/Vlog",
    "Vlog/个人成长": "生活/Vlog",

    # 财经
    "财经/投资与商业分析": "财经/商业",
    "财经/股票投资": "财经/商业",
    "财经/理财科普": "财经/商业",
    "投资理财/基金": "财经/商业",

    # 搞笑娱乐
    "搞笑/娱乐": "娱乐/搞笑",
    "搞笑/创意": "娱乐/搞笑",

    # 高校
    "高校实验室/科研展示": "高校/科研",
    "高校/官方账号": "高校/科研",
    "高校/学生组织": "高校/科研",

    # 未分类合并
    "未分类/信息不足": "未分类",
    "未明确分类/信息不足": "未分类",
    "综合内容/未明确分类": "未分类",
    "泛知识/未明确领域": "未分类",
    "综合知识/未明确分类": "未分类",
}

# ========== 处理逻辑 ==========

# 1. 先从所有分类中提取所有UP主
all_ups = []
for cat, ups in result["categories"].items():
    for up in ups:
        up["original_category"] = cat
        all_ups.append(up)

print(f"原始UP主总数: {len(all_ups)}")

# 2. 删除指定的UP主
all_ups = [up for up in all_ups if up["name"] not in to_delete]
print(f"删除后UP主数: {len(all_ups)}")

# 3. 应用手动修正
for up in all_ups:
    if up["name"] in manual_corrections:
        up["new_category"] = manual_corrections[up["name"]]
        up["reason"] = f"用户手动指定分类"
    else:
        # 应用分类合并
        orig_cat = up["original_category"]
        up["new_category"] = category_merge.get(orig_cat, orig_cat)

# 4. 特殊处理：将"考研/数学"中的UP主根据内容重新分类
for up in all_ups:
    name = up["name"].lower()
    reason = up.get("reason", "").lower()

    # 如果名字或理由中包含"考研"，归入考研
    if "考研" in up["name"] or "考研" in up.get("reason", ""):
        if up["new_category"] == "数学":
            up["new_category"] = "考研"

    # 纯数学内容（不涉及考研）归入数学
    if any(x in name for x in ["数学", "高数", "线代", "概率"]):
        if "考研" not in up["name"] and "考研" not in up.get("reason", ""):
            up["new_category"] = "数学"

# 5. 重新组织分类
new_categories = {}
for up in all_ups:
    cat = up["new_category"]
    if cat not in new_categories:
        new_categories[cat] = []
    new_categories[cat].append({
        "name": up["name"],
        "mid": up["mid"],
        "reason": up.get("reason", "")
    })

# 6. 按分类大小排序
sorted_categories = dict(sorted(
    new_categories.items(),
    key=lambda x: len(x[1]),
    reverse=True
))

# 7. 保存结果
new_result = {
    "categories": sorted_categories,
    "category_descriptions": {}
}

output_path = base_path / "分类结果_优化版.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(new_result, f, ensure_ascii=False, indent=2)

# 8. 生成Markdown
md_path = base_path / "分类结果_优化版.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# B站关注UP主分类结果（优化版）\n\n")
    f.write(f"总计: {len(all_ups)} 个UP主，{len(sorted_categories)} 个分类\n\n")
    f.write("---\n\n")

    for category, ups in sorted_categories.items():
        f.write(f"## {category} ({len(ups)}个)\n\n")
        for up in ups:
            mid = up.get('mid', '')
            f.write(f"- [{up['name']}](https://space.bilibili.com/{mid})\n")
        f.write("\n")

print(f"\n优化完成！")
print(f"总UP主数: {len(all_ups)}")
print(f"分类数量: {len(sorted_categories)}")
print(f"\n各分类UP主数量:")
for cat, ups in list(sorted_categories.items())[:20]:
    print(f"  {cat}: {len(ups)}")
print("  ...")
print(f"\n结果已保存到:")
print(f"  {output_path}")
print(f"  {md_path}")
