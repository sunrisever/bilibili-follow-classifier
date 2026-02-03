# -*- coding: utf-8 -*-
"""
优化分类结果 V7 - 删除已取关的UP主 + 检查分类问题
"""

import json
from pathlib import Path

base_path = Path(__file__).parent

with open(base_path / "分类结果_最终版.json", "r", encoding="utf-8") as f:
    result = json.load(f)

# ========== 要删除的UP主（已取关）==========
to_delete = {
    "大一的吃货生活",  # 用户已删除
}

# ========== 需要重新分类的UP主（名字和内容不符）==========
# 这些UP主的名字可能误导分类，需要根据实际内容重新归类
reclassify = {
    # 美食区检查 - 很多可能是生活/vlog类
    "特厨隋卞": "生活/Vlog",  # 可能是生活类
    "特厨隋坡": "生活/Vlog",  # 可能是生活类
    "真探唐仁杰": "生活/Vlog",  # 探店类属于生活消遣

    # 其他可能需要调整的
    "盗月社食遇记": "生活/Vlog",  # 已经在生活区了，确认
}

# ========== 处理逻辑 ==========

all_ups = []
for cat, ups in result["categories"].items():
    for up in ups:
        up["category"] = cat
        all_ups.append(up)

print(f"原始UP主总数: {len(all_ups)}")

# 1. 删除已取关的
all_ups = [up for up in all_ups if up["name"] not in to_delete]
print(f"删除后UP主数: {len(all_ups)}")

# 2. 重新分类
for up in all_ups:
    if up["name"] in reclassify:
        up["category"] = reclassify[up["name"]]

# 3. 重新组织
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

# 4. 删除空分类
new_categories = {k: v for k, v in new_categories.items() if v}

# 5. 排序
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

print(f"\n优化完成！")
print(f"总UP主数: {total}")
print(f"分类数量: {len(sorted_categories)}")

# 列出小分类，方便检查
print("\n=== 小分类检查（可能需要合并或重新分类）===")
for cat, ups in sorted_categories.items():
    if len(ups) <= 5:
        print(f"\n【{cat}】({len(ups)}个)")
        for up in ups:
            print(f"  - {up['name']}")
