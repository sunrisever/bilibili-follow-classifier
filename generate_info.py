# -*- coding: utf-8 -*-
"""
生成UP主信息汇总文本，供分类参考
"""

import json
from pathlib import Path

def main():
    # 读取详细数据
    data_path = Path(__file__).parent / "up主详细数据.json"
    with open(data_path, "r", encoding="utf-8") as f:
        uploaders = json.load(f)

    print(f"共加载 {len(uploaders)} 个UP主数据")

    # 生成信息文本
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

        # 合集（最多30个）
        if channels:
            display_channels = channels[:30]
            suffix = f"...还有{len(channels)-30}个" if len(channels) > 30 else ""
            output_lines.append(f"  合集({len(channels)}个): {', '.join(display_channels)}{suffix}")
        else:
            output_lines.append("  合集: 无")

        # 系列（最多30个）
        if series:
            display_series = series[:30]
            suffix = f"...还有{len(series)-30}个" if len(series) > 30 else ""
            output_lines.append(f"  系列({len(series)}个): {', '.join(display_series)}{suffix}")
        else:
            output_lines.append("  系列: 无")

        # 视频分区
        if video_zones:
            output_lines.append(f"  投稿分区: {', '.join(video_zones)}")
        else:
            output_lines.append("  投稿分区: 无")

        # 视频标题（全部展示）
        if video_titles:
            output_lines.append(f"  最近视频({len(video_titles)}个):")
            for j, title in enumerate(video_titles, 1):
                output_lines.append(f"    {j}. {title}")
        else:
            output_lines.append("  最近视频: 无")

        # 标签（全部展示）
        if tags:
            output_lines.append(f"  视频标签({len(tags)}个): {', '.join(tags)}")
        else:
            output_lines.append("  视频标签: 无")

        # 专栏（最多30篇）
        if articles:
            output_lines.append(f"  专栏文章({len(articles)}篇):")
            for j, title in enumerate(articles[:30], 1):
                output_lines.append(f"    {j}. {title}")
            if len(articles) > 30:
                output_lines.append(f"    ...还有{len(articles)-30}篇")
        else:
            output_lines.append("  专栏文章: 无")

        output_lines.append("")
        output_lines.append("-" * 80)
        output_lines.append("")

    # 保存文件
    output_path = Path(__file__).parent / "up主信息汇总.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"信息汇总已保存到: {output_path}")
    print(f"文件大小: {output_path.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
