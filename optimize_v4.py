# -*- coding: utf-8 -*-
"""
优化分类结果 V4 - 应用更多合并规则
1. 颜值/美女、娱乐/搞笑、摄影/创作、旅行/户外 -> 生活/Vlog
2. 高校实验室按具体内容分到对应分区（大多是AI/计算机）
"""

import json
from pathlib import Path

base_path = Path(__file__).parent

with open(base_path / "分类结果_最终版.json", "r", encoding="utf-8") as f:
    result = json.load(f)

# ========== 用户修正 ==========
manual_corrections = {
    # 生活区合并
    "-欣小萌-": "生活/Vlog",
    "Irene_yyy913": "生活/Vlog",
    "-童锣烧_": "生活/Vlog",
    "伢伢gagako": "生活/Vlog",
    "十一的看脸日记": "生活/Vlog",
    "小鹿Lawrence": "生活/Vlog",
    "沛沛瑶呀爱吃糖呀": "生活/Vlog",
    "甜粥粥-": "生活/Vlog",

    # 其他
    "1350亿光年": "生活/Vlog",  # 摄影也归入生活
    "BloodyWilliam": "人工智能/AI",
    "ModuliSpace": "数学",
    "PROJECT_蔡_重生": "效率工具",

    # 高校实验室 -> 按具体内容分类
    "上交CyPhy实验室": "人工智能/AI",
    "上交大DAI实验室": "人工智能/AI",
    "上海交大CIUS实验室": "人工智能/AI",
    "上海交大ViSYS实验室": "人工智能/AI",
    "上海交通大学IPADS": "编程/计算机",
    "X-LANCE实验室": "人工智能/AI",
    "华南理工大学MetaEvo": "人工智能/AI",
    "南京大学NLP研究组": "人工智能/AI",
    "THUDBGroup": "编程/计算机",
    "上交IWIN-FINS实验室": "编程/计算机",
    "张伟楠SJTU": "人工智能/AI",
    "RM云汉交龙战队": "编程/计算机",  # RoboMaster是机器人/嵌入式

    # 一些明确的分类
    "SJTU抽象代数": "数学",
}

# 要删除的UP主
to_delete = {"FOS-WAI"}

# 整个分类合并到生活/Vlog
categories_to_merge_to_life = {
    "颜值/美女",
    "娱乐/搞笑",
    "摄影/创作",
    "旅行/户外",
}

# ========== 处理逻辑 ==========

all_ups = []
for cat, ups in result["categories"].items():
    for up in ups:
        up["category"] = cat
        all_ups.append(up)

print(f"原始UP主总数: {len(all_ups)}")

# 删除
all_ups = [up for up in all_ups if up["name"] not in to_delete]
print(f"删除后UP主数: {len(all_ups)}")

# 应用修正
for up in all_ups:
    name = up["name"]

    # 1. 手动修正优先
    if name in manual_corrections:
        up["category"] = manual_corrections[name]
    # 2. 整个分类合并
    elif up["category"] in categories_to_merge_to_life:
        up["category"] = "生活/Vlog"

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

# 保存
new_result = {"categories": sorted_categories}

output_path = base_path / "分类结果_最终版.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(new_result, f, ensure_ascii=False, indent=2)

md_path = base_path / "分类结果_最终版.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# B站关注UP主分类结果（最终版）\n\n")
    f.write(f"总计: {len(all_ups)} 个UP主，{len(sorted_categories)} 个分类\n\n")
    f.write("---\n\n")

    for category, ups in sorted_categories.items():
        f.write(f"## {category} ({len(ups)}个)\n\n")
        for up in sorted(ups, key=lambda x: x["name"]):
            mid = up.get('mid', '')
            f.write(f"- [{up['name']}](https://space.bilibili.com/{mid})\n")
        f.write("\n")

print(f"\n优化完成！")
print(f"总UP主数: {len(all_ups)}")
print(f"分类数量: {len(sorted_categories)}")
print(f"\n各分类UP主数量:")
for cat, ups in sorted_categories.items():
    print(f"  {cat}: {len(ups)}")
