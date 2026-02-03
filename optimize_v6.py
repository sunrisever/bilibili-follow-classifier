# -*- coding: utf-8 -*-
"""
优化分类结果 V6 - 形象/穿搭/颜值分析 -> 两性情感
"""

import json
from pathlib import Path

base_path = Path(__file__).parent

with open(base_path / "分类结果_最终版.json", "r", encoding="utf-8") as f:
    result = json.load(f)

# ========== 形象/穿搭/颜值 -> 两性情感 ==========
to_relationship = {
    "十一的看脸日记": "两性情感",  # 形象设计
    "小鹿Lawrence": "两性情感",  # 颜值类
    "沛沛瑶呀爱吃糖呀": "两性情感",
    "伢伢gagako": "两性情感",
    "-童锣烧_": "两性情感",
    "甜粥粥-": "两性情感",
}

# ========== 其他小调整 ==========
other_fixes = {
    # 考研政治单独标注
    "考研政治徐涛": "考研/政治",
    "考研政治陆寓丰老师": "考研/政治",
    "考研政治广智老师": "考研/政治",
}

# ========== 处理逻辑 ==========

all_ups = []
for cat, ups in result["categories"].items():
    for up in ups:
        up["category"] = cat
        all_ups.append(up)

# 应用修正
for up in all_ups:
    name = up["name"]
    if name in to_relationship:
        up["category"] = to_relationship[name]
    if name in other_fixes:
        up["category"] = other_fixes[name]

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
output_path = base_path / "分类结果_最终版.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({"categories": sorted_categories}, f, ensure_ascii=False, indent=2)

md_path = base_path / "分类结果_最终版.md"
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# B站关注UP主分类结果（最终版）\n\n")
    total = sum(len(ups) for ups in sorted_categories.values())
    f.write(f"总计: {total} 个UP主，{len(sorted_categories)} 个分类\n\n")
    f.write("---\n\n")

    for category, ups in sorted_categories.items():
        f.write(f"## {category} ({len(ups)}个)\n\n")
        for up in sorted(ups, key=lambda x: x["name"]):
            mid = up.get('mid', '')
            f.write(f"- [{up['name']}](https://space.bilibili.com/{mid})\n")
        f.write("\n")

print(f"优化完成！分类数量: {len(sorted_categories)}")
print(f"\n各分类UP主数量:")
for cat, ups in sorted_categories.items():
    print(f"  {cat}: {len(ups)}")
