# -*- coding: utf-8 -*-
"""
优化分类结果 V3 - 应用用户最新修正
"""

import json
from pathlib import Path

base_path = Path(__file__).parent

with open(base_path / "分类结果_最终版.json", "r", encoding="utf-8") as f:
    result = json.load(f)

# ========== 用户最新修正 ==========
manual_corrections = {
    # 颜值/美女 全部合并到 生活/Vlog
    "-童锣烧_": "生活/Vlog",
    "伢伢gagako": "生活/Vlog",
    "十一的看脸日记": "生活/Vlog",
    "小鹿Lawrence": "生活/Vlog",
    "沛沛瑶呀爱吃糖呀": "生活/Vlog",
    "甜粥粥-": "生活/Vlog",

    # 其他修正
    "-欣小萌-": "生活/Vlog",
    "1350亿光年": "摄影/创作",
    "BloodyWilliam": "人工智能/AI",
    "Irene_yyy913": "生活/Vlog",
    "ModuliSpace": "数学",
    "PROJECT_蔡_重生": "效率工具",
}

# 要删除的UP主
to_delete = {"FOS-WAI"}

# ========== 处理逻辑 ==========

# 1. 提取所有UP主
all_ups = []
for cat, ups in result["categories"].items():
    for up in ups:
        up["category"] = cat
        all_ups.append(up)

print(f"原始UP主总数: {len(all_ups)}")

# 2. 删除指定的UP主
all_ups = [up for up in all_ups if up["name"] not in to_delete]
print(f"删除后UP主数: {len(all_ups)}")

# 3. 应用手动修正
for up in all_ups:
    if up["name"] in manual_corrections:
        up["category"] = manual_corrections[up["name"]]

# 4. 删除"颜值/美女"分类（已全部合并到生活/Vlog）
# 不需要特别处理，因为上面已经修正了

# 5. 重新组织分类
new_categories = {}
for up in all_ups:
    cat = up["category"]
    # 跳过颜值/美女分类（应该已经没有了）
    if cat == "颜值/美女":
        cat = "生活/Vlog"
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
    key=lambda x: (-len(x[1]), x[0])
))

# 7. 保存结果
new_result = {"categories": sorted_categories}

output_path = base_path / "分类结果_最终版.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(new_result, f, ensure_ascii=False, indent=2)

# 8. 生成Markdown
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
print(f"\n主要分类UP主数量:")
for cat, ups in list(sorted_categories.items())[:15]:
    print(f"  {cat}: {len(ups)}")
