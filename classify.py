# -*- coding: utf-8 -*-
"""
B站关注UP主分类脚本
从 data/classify_rules.json 加载分类规则，对 UP主 进行自动分类。

首次使用请先创建规则文件：
  复制 classify_rules.example.json 到 data/classify_rules.json，然后按需修改。
"""

import json
import re
from pathlib import Path
from collections import Counter

base_path = Path(__file__).parent
data_path = base_path / "data"
rules_path = data_path / "classify_rules.json"

# ========== 加载规则 ==========
if not rules_path.exists():
    print(f"错误: 未找到分类规则文件 {rules_path}")
    print(f"请先复制 classify_rules.example.json 到 data/classify_rules.json，然后按需修改。")
    exit(1)

with open(rules_path, "r", encoding="utf-8") as f:
    rules = json.load(f)

CATEGORIES = rules["categories"]
DEFAULT_CATEGORY = rules.get("default_category", CATEGORIES[-1])
MANUAL = rules.get("manual", {})
KEYWORD_RULES = {k: [(kw, w) for kw, w in v] for k, v in rules.get("keyword_rules", {}).items()}
ZONE_MAPPING = rules.get("zone_mapping", {})

print(f"已加载规则: {len(CATEGORIES)}个分类, {len(MANUAL)}个手动指定")

# ========== 加载UP主数据 ==========
with open(data_path / "up主详细数据.json", "r", encoding="utf-8") as f:
    uploaders = json.load(f)

print(f"加载 {len(uploaders)} 个UP主数据")


def calculate_category_scores(up_info):
    """计算每个分类的得分"""
    scores = {cat: 0 for cat in CATEGORIES}

    # 收集所有文本
    texts = []
    texts.append(up_info.get("sign", "") or "")
    texts.append(up_info.get("official_verify", "") or "")
    texts.extend(up_info.get("channels", []))
    texts.extend(up_info.get("series", []))
    texts.extend(up_info.get("video_titles", []))
    texts.extend(up_info.get("tags", []))
    texts.extend(up_info.get("articles", []))

    combined_text = " ".join(texts).lower()

    # 视频分区
    video_zones = up_info.get("video_zones", [])
    zones_text = " ".join(video_zones).lower()

    # 根据分区加分
    for category, zone_keywords in ZONE_MAPPING.items():
        if category in scores:
            for kw in zone_keywords:
                if kw in zones_text:
                    scores[category] += 50

    # 名称特征识别
    name = up_info.get("name", "").lower()

    if any(kw in name for kw in ["机器人", "robomaster", "战队"]):
        if "电气/电子/自动化" in scores:
            scores["电气/电子/自动化"] += 80

    if "半导体" in name:
        if "电气/电子/自动化" in scores:
            scores["电气/电子/自动化"] += 80

    # 大学官方号
    official = up_info.get("official_verify", "") or ""
    if "大学" in official and "官方" in official:
        if "校园生活/校园日常" in scores:
            scores["校园生活/校园日常"] += 100

    # 招聘号
    if "招聘" in name:
        if DEFAULT_CATEGORY in scores:
            scores[DEFAULT_CATEGORY] += 80

    # 关键词评分
    for category, keywords in KEYWORD_RULES.items():
        if category in scores:
            for keyword, weight in keywords:
                count = len(re.findall(re.escape(keyword.lower()), combined_text))
                if count > 0:
                    scores[category] += weight * min(count, 5)

    return scores


def classify_up(up_info):
    """分类单个UP主"""
    name = up_info.get("name", "")

    # 1. 手动指定优先
    if name in MANUAL:
        return MANUAL[name], "手动指定"

    # 2. 计算分数
    scores = calculate_category_scores(up_info)

    # 3. 找最高分
    max_score = max(scores.values())
    if max_score == 0:
        return DEFAULT_CATEGORY, "无明确特征，默认归类"

    best_category = max(scores, key=scores.get)

    # 4. 生成理由
    reason_parts = []
    sign = up_info.get("sign", "") or ""
    if sign:
        reason_parts.append(f"签名含'{sign[:30]}..'" if len(sign) > 30 else f"签名'{sign}'")

    channels = up_info.get("channels", [])
    if channels:
        reason_parts.append(f"合集有{channels[:3]}")

    tags = up_info.get("tags", [])[:5]
    if tags:
        reason_parts.append(f"标签含{tags}")

    reason = "；".join(reason_parts) if reason_parts else "综合分析得分最高"

    return best_category, reason


# ========== 执行分类 ==========
if __name__ == "__main__":
    results = {cat: [] for cat in CATEGORIES}

    for up in uploaders:
        category, reason = classify_up(up)
        results[category].append({
            "name": up["name"],
            "mid": up["mid"],
            "reason": reason
        })

    # 统计
    print("\n分类统计:")
    for cat in CATEGORIES:
        count = len(results[cat])
        if count > 0:
            print(f"  {cat}: {count}")

    # 移除空分类
    results = {k: v for k, v in results.items() if v}

    # 按数量排序
    sorted_results = dict(sorted(results.items(), key=lambda x: (-len(x[1]), x[0])))

    # 保存JSON
    output = {"categories": sorted_results}
    with open(data_path / "分类结果.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 保存Markdown
    total = sum(len(ups) for ups in sorted_results.values())
    with open(data_path / "分类结果.md", "w", encoding="utf-8") as f:
        f.write("# B站关注UP主分类结果\n\n")
        f.write(f"总计: {total} 个UP主，{len(sorted_results)} 个分类\n\n")
        f.write("---\n\n")

        for category, ups in sorted_results.items():
            f.write(f"## {category} ({len(ups)}个)\n\n")
            for up in sorted(ups, key=lambda x: x["name"]):
                mid = up.get("mid", "")
                f.write(f"- [{up['name']}](https://space.bilibili.com/{mid})\n")
            f.write("\n")

    print(f"\n完成！共 {total} 个UP主，{len(sorted_results)} 个分类")
    print(f"结果保存到: data/分类结果.json, data/分类结果.md")
