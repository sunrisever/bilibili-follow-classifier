# -*- coding: utf-8 -*-
"""
增量添加UP主：采集信息 → 算法初分类 → 输出结果供人工审核
用法: python add_new.py <mid1> [mid2] [mid3] ...
"""

import json
import asyncio
import sys
from pathlib import Path

BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / "data"


def load_classify_result():
    path = DATA_PATH / "分类结果.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"categories": {}}


def save_classify_result(data):
    with open(DATA_PATH / "分类结果.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_md(data):
    """更新分类结果.md"""
    lines = ['# B站关注UP主分类结果\n\n']
    total = sum(len(v) for v in data['categories'].values())
    lines.append(f'> 共 {total} 个UP主，{len(data["categories"])} 个分类\n\n')
    for cat, ups in data['categories'].items():
        lines.append(f'## {cat}（{len(ups)}个）\n\n')
        for up in ups:
            link = f'https://space.bilibili.com/{up["mid"]}'
            lines.append(f'- [{up["name"]}]({link})\n')
        lines.append('\n')
    with open(DATA_PATH / '分类结果.md', 'w', encoding='utf-8') as f:
        f.writelines(lines)


def generate_info():
    """重新生成信息汇总文件"""
    data_path = DATA_PATH / "up主详细数据.json"
    with open(data_path, "r", encoding="utf-8") as f:
        uploaders = json.load(f)

    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("B站关注UP主信息汇总（供分类参考）")
    output_lines.append(f"共 {len(uploaders)} 个UP主")
    output_lines.append("=" * 80)
    output_lines.append("")

    for i, up in enumerate(uploaders, 1):
        name = up.get("name", "未知")
        mid = up.get("mid", "")
        sign = up.get("sign", "") or "无"
        official = up.get("official_verify", "") or "无"
        channels = up.get("channels", [])
        series = up.get("series", [])
        video_titles = up.get("video_titles", [])
        video_zones = up.get("video_zones", [])
        tags = up.get("tags", [])
        articles = up.get("articles", [])
        note = up.get("note", "")

        output_lines.append(f"【{i}】{name}")
        output_lines.append(f"  UID: {mid}")
        output_lines.append(f"  主页: https://space.bilibili.com/{mid}")
        if note:
            output_lines.append(f"  【备注】: {note}")
        output_lines.append(f"  个性签名: {sign[:100]}{'...' if len(sign) > 100 else ''}")
        output_lines.append(f"  官方认证: {official[:80]}{'...' if len(official) > 80 else ''}")

        if channels:
            display = channels[:30]
            suffix = f"...还有{len(channels)-30}个" if len(channels) > 30 else ""
            output_lines.append(f"  合集({len(channels)}个): {', '.join(display)}{suffix}")
        else:
            output_lines.append("  合集: 无")

        if series:
            display = series[:30]
            suffix = f"...还有{len(series)-30}个" if len(series) > 30 else ""
            output_lines.append(f"  系列({len(series)}个): {', '.join(display)}{suffix}")
        else:
            output_lines.append("  系列: 无")

        if video_zones:
            output_lines.append(f"  投稿分区: {', '.join(video_zones)}")
        else:
            output_lines.append("  投稿分区: 无")

        if video_titles:
            output_lines.append(f"  最近视频({len(video_titles)}个):")
            for j, title in enumerate(video_titles, 1):
                output_lines.append(f"    {j}. {title}")
        else:
            output_lines.append("  最近视频: 无")

        if tags:
            output_lines.append(f"  视频标签({len(tags)}个): {', '.join(tags)}")
        else:
            output_lines.append("  视频标签: 无")

        if articles:
            output_lines.append(f"  专栏文章({len(articles)}篇):")
            for j, title in enumerate(articles[:30], 1):
                output_lines.append(f"    {j}. {title}")
        else:
            output_lines.append("  专栏文章: 无")

        output_lines.append("")
        output_lines.append("-" * 80)
        output_lines.append("")

    output_path = DATA_PATH / "up主信息汇总.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
    print(f"信息汇总已更新: {output_path}")


async def main():
    if len(sys.argv) < 2:
        print("用法: python add_new.py <mid1> [mid2] [mid3] ...")
        print("示例: python add_new.py 12345678 87654321")
        return

    mids = []
    for arg in sys.argv[1:]:
        if arg.isdigit():
            mids.append(int(arg))
        else:
            print(f"无效的mid: {arg}，跳过")

    if not mids:
        print("没有有效的mid")
        return

    # 1. 采集信息
    print(f"=== 第1步：采集 {len(mids)} 个UP主信息 ===\n")
    from fetch import fetch_new
    added = await fetch_new(mids)

    if not added:
        print("没有新增UP主")
        return

    # 2. 算法初分类
    print(f"\n=== 第2步：算法初分类 ===\n")

    # 动态导入classify模块的分类函数
    from classify import classify_up

    classify_result = load_classify_result()

    for info in added:
        category, reason = classify_up(info)
        entry = {"name": info["name"], "mid": info["mid"], "reason": reason}

        if category not in classify_result["categories"]:
            classify_result["categories"][category] = []
        classify_result["categories"][category].append(entry)

        link = f"https://space.bilibili.com/{info['mid']}"
        print(f"  {info['name']} → {category}")
        print(f"    链接: {link}")
        print(f"    依据: {reason[:80]}")
        print()

    # 3. 保存结果
    save_classify_result(classify_result)
    save_md(classify_result)

    # 4. 更新信息汇总
    print("=== 第3步：更新信息汇总 ===\n")
    generate_info()

    print("\n=== 完成 ===")
    print("算法分类仅供参考，建议人工审核后在分类结果.json中调整")


if __name__ == "__main__":
    asyncio.run(main())
