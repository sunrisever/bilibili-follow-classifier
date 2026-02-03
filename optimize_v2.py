# -*- coding: utf-8 -*-
"""
优化分类结果 V2 - 更激进的合并
"""

import json
import re
from pathlib import Path

base_path = Path(__file__).parent

with open(base_path / "分类结果.json", "r", encoding="utf-8") as f:
    result = json.load(f)

with open(base_path / "up主原始数据.json", "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# ========== 用户手动修正 ==========
manual_corrections = {
    "沛沛瑶呀爱吃糖呀": "颜值/美女",
    "伢伢gagako": "颜值/美女",
    "甜粥粥": "颜值/美女",
    "小鹿Lawrence": "颜值/美女",
    "-童锣烧_": "颜值/美女",
    "十三会魔法": "两性情感",
    "峰哥亡命天涯": "两性情感",
    "大沛沛沛吖": "两性情感",
    "RM云汉交龙战队": "高校/科研",
    "猫哥mao": "大学生/校园",
    "彭酱酱LINYA": "大学生/校园",
    "卓叔增重": "健康/医疗",
    "兔叭咯": "健康/医疗",
    "Cello纳多": "音乐",
    "Cuppix_": "音乐",
    "不想做实验的锦鲤仔": "评测",
    "老爸评测": "评测",
    "清华护肤学长王植": "评测",
    "数学小呆瓜h": "数学",
    "电路通": "电气/电子",
    "鹏哥金融学考研": "财经/金融",
    "哔哩哔哩课堂": "官方/平台",
    "降B_大调": "娱乐/搞笑",
}

# 要删除的UP主
to_delete = {"浮泽动漫协会", "hello刘小备", "Larry想做技术大佬"}

# ========== 大分类映射 ==========
def get_main_category(cat):
    cat_lower = cat.lower()

    # 考研类
    if "考研" in cat and "数学" not in cat:
        return "考研"
    if any(x in cat for x in ["408", "专业课", "研究生"]):
        return "考研"

    # 数学类（不含考研）
    if "数学" in cat and "考研" not in cat:
        return "数学"
    if any(x in cat for x in ["高数", "线代", "概率", "微积分"]):
        return "数学"

    # 人工智能
    if any(x in cat_lower for x in ["ai", "人工智能", "机器学习", "深度学习", "机器人", "ros"]):
        return "人工智能/AI"

    # 编程计算机
    if any(x in cat for x in ["编程", "计算机", "程序员", "代码", "算法", "开发", "软件"]):
        return "编程/计算机"

    # 科技数码
    if any(x in cat for x in ["科技", "数码", "硬件", "评测", "手机", "电脑"]):
        return "科技/数码"

    # 财经金融
    if any(x in cat for x in ["财经", "金融", "投资", "理财", "股票", "基金", "商业"]):
        return "财经/金融"

    # 生活Vlog
    if any(x in cat for x in ["生活", "vlog", "日常", "日记"]):
        return "生活/Vlog"

    # 娱乐搞笑
    if any(x in cat for x in ["搞笑", "娱乐", "整活", "段子"]):
        return "娱乐/搞笑"

    # 高校科研
    if any(x in cat for x in ["高校", "大学", "实验室", "科研", "学院"]):
        return "高校/科研"

    # 官方平台
    if any(x in cat for x in ["官方", "平台", "媒体"]):
        return "官方/平台"

    # 教育学习
    if any(x in cat for x in ["教育", "学习", "课程", "教学"]):
        return "教育/学习"

    # 历史人文
    if any(x in cat for x in ["历史", "人文", "文化", "国学"]):
        return "历史/人文"

    # 时政新闻
    if any(x in cat for x in ["时政", "新闻", "政治", "国际"]):
        return "时政/新闻"

    # 摄影视频
    if any(x in cat for x in ["摄影", "视频", "剪辑", "后期"]):
        return "摄影/创作"

    # 健康医疗
    if any(x in cat for x in ["健康", "医疗", "医学", "养生", "健身"]):
        return "健康/医疗"

    # 美食
    if any(x in cat for x in ["美食", "吃", "烹饪", "做饭"]):
        return "美食"

    # 旅行
    if any(x in cat for x in ["旅行", "旅游", "户外", "探险"]):
        return "旅行/户外"

    # 音乐
    if any(x in cat for x in ["音乐", "钢琴", "吉他", "唱歌"]):
        return "音乐"

    # 游戏
    if any(x in cat for x in ["游戏", "电竞"]):
        return "游戏"

    # 动漫
    if any(x in cat for x in ["动漫", "番剧", "二次元"]):
        return "动漫"

    # 舞蹈
    if any(x in cat for x in ["舞蹈", "跳舞"]):
        return "舞蹈"

    # 电气电子
    if any(x in cat for x in ["电气", "电子", "电路", "单片机", "嵌入式"]):
        return "电气/电子"

    # 汽车
    if any(x in cat for x in ["汽车", "车", "驾驶"]):
        return "汽车"

    # 心理情感
    if any(x in cat for x in ["情感", "两性", "心理", "恋爱"]):
        return "两性情感"

    # 颜值美女
    if any(x in cat for x in ["颜值", "美女", "美妆", "时尚"]):
        return "颜值/美女"

    # 大学生
    if any(x in cat for x in ["大学生", "校园", "留学"]):
        return "大学生/校园"

    # 知识科普
    if any(x in cat for x in ["知识", "科普"]):
        return "知识科普"

    # 效率工具
    if any(x in cat for x in ["效率", "工具", "PKM", "笔记"]):
        return "效率工具"

    # 未分类
    if any(x in cat for x in ["未分类", "未明确", "综合", "信息不足"]):
        return "未分类"

    return cat  # 保持原分类

# ========== 处理逻辑 ==========

# 1. 提取所有UP主
all_ups = []
for cat, ups in result["categories"].items():
    for up in ups:
        up["original_category"] = cat
        all_ups.append(up)

print(f"原始UP主总数: {len(all_ups)}")

# 2. 删除指定的UP主
all_ups = [up for up in all_ups if up["name"] not in to_delete]
print(f"删除后UP主数: {len(all_ups)}")

# 3. 应用手动修正和分类映射
for up in all_ups:
    if up["name"] in manual_corrections:
        up["new_category"] = manual_corrections[up["name"]]
    else:
        up["new_category"] = get_main_category(up["original_category"])

# 4. 重新组织分类
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

# 5. 按分类大小排序
sorted_categories = dict(sorted(
    new_categories.items(),
    key=lambda x: (-len(x[1]), x[0])  # 先按数量降序，再按名称排序
))

# 6. 保存结果
new_result = {"categories": sorted_categories}

output_path = base_path / "分类结果_最终版.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(new_result, f, ensure_ascii=False, indent=2)

# 7. 生成Markdown
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
print(f"\n结果已保存到:")
print(f"  {output_path}")
print(f"  {md_path}")
