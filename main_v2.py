# -*- coding: utf-8 -*-
"""
B站关注UP主智能分类工具（V2 - 增加合集信息）
- 自动获取你的B站关注列表
- 获取UP主的合集/系列信息（重要分类依据）
- 使用AI动态分析并生成分类
"""

import json
import time
import asyncio
from pathlib import Path
from collections import Counter
from bilibili_api import user, video, Credential
import httpx


def load_config():
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_credential(config):
    bili_config = config["bilibili"]
    return Credential(
        sessdata=bili_config["sessdata"],
        bili_jct=bili_config["bili_jct"],
        buvid3=bili_config["buvid3"],
        dedeuserid=bili_config["dedeuserid"]
    )


async def get_all_followings(credential, uid):
    """获取所有关注的UP主"""
    u = user.User(uid=int(uid), credential=credential)
    all_followings = []
    page = 1

    print("正在获取关注列表...")

    while True:
        try:
            result = await u.get_followings(pn=page)
            followings = result.get("list", [])
            if not followings:
                break
            all_followings.extend(followings)
            print(f"  已获取 {len(all_followings)} 个UP主...")
            page += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            print(f"获取第 {page} 页时出错: {e}")
            break

    print(f"共获取 {len(all_followings)} 个关注的UP主")
    return all_followings


async def get_user_channel_series(credential, mid):
    """获取UP主的合集和系列列表（重要分类依据）"""
    try:
        u = user.User(uid=mid, credential=credential)

        # 获取频道列表（合集）
        channels = await u.get_channel_list()
        channel_names = []
        if channels:
            for ch in channels.get("list", []):
                channel_names.append(ch.get("name", ""))

        # 获取系列列表
        series_list = []
        try:
            series = await u.get_series()
            if series and "items_lists" in series:
                for item in series.get("items_lists", {}).get("series_list", []):
                    series_list.append(item.get("meta", {}).get("name", ""))
        except:
            pass

        return channel_names, series_list
    except Exception as e:
        return [], []


async def get_user_videos_info(credential, mid, limit=5):
    """获取UP主最近视频信息"""
    try:
        u = user.User(uid=mid, credential=credential)
        videos_data = await u.get_videos(pn=1, ps=limit)
        video_list = videos_data.get("list", {}).get("vlist", [])

        videos_info = []
        all_tags = []

        for v in video_list[:3]:
            bvid = v.get("bvid")
            video_info = {
                "title": v.get("title", ""),
                "typeid": v.get("typeid", 0),
                "play": v.get("play", 0),
            }

            # 获取视频标签
            if bvid:
                try:
                    vid = video.Video(bvid=bvid, credential=credential)
                    tags = await vid.get_tags()
                    tag_names = [t.get("tag_name", "") for t in tags]
                    video_info["tags"] = tag_names
                    all_tags.extend(tag_names)
                    await asyncio.sleep(0.2)
                except:
                    video_info["tags"] = []

            videos_info.append(video_info)

        return videos_info, list(set(all_tags))[:10]
    except:
        return [], []


# B站分区ID到名称的映射
TNAME_MAP = {
    1: "动画", 13: "番剧", 167: "国创", 3: "音乐", 129: "舞蹈",
    4: "游戏", 36: "知识", 188: "科技", 234: "运动", 223: "汽车",
    160: "生活", 211: "美食", 217: "动物圈", 119: "鬼畜",
    155: "时尚", 5: "娱乐", 181: "影视", 177: "纪录片",
    201: "科学科普", 124: "社科人文", 228: "人文历史", 207: "财经商业",
    208: "校园学习", 209: "职业职场", 229: "设计创意", 122: "野生技能",
    95: "数码", 230: "软件应用", 231: "计算机技术", 232: "科工机械",
    138: "搞笑", 254: "亲子", 161: "手工", 162: "绘画", 21: "日常",
}


async def get_uploader_full_info(credential, up_basic, index, total):
    """获取UP主的完整信息（包括合集）"""
    mid = up_basic["mid"]

    info = {
        "mid": mid,
        "name": up_basic["uname"],
        "sign": up_basic.get("sign", "") or "",
        "official_verify": up_basic.get("official_verify", {}).get("desc", ""),
    }

    try:
        # 1. 获取合集和系列（重要！）
        channels, series = await get_user_channel_series(credential, mid)
        info["channels"] = channels  # 合集名称列表
        info["series"] = series  # 系列名称列表
        await asyncio.sleep(0.3)

        # 2. 获取视频和标签
        videos, tags = await get_user_videos_info(credential, mid)
        info["videos"] = videos
        info["tags"] = tags

        # 3. 统计主要投稿分区
        if videos:
            typeids = [v.get("typeid", 0) for v in videos if v.get("typeid")]
            tnames = [TNAME_MAP.get(tid, f"分区{tid}") for tid in typeids]
            if tnames:
                info["main_categories"] = list(set(tnames))[:3]

        await asyncio.sleep(0.3)

    except Exception as e:
        print(f"    获取 {up_basic['uname']} 详情时出错: {e}")
        info["channels"] = []
        info["series"] = []
        info["videos"] = []
        info["tags"] = []

    if (index + 1) % 10 == 0:
        print(f"  已处理 {index + 1}/{total} 个UP主...")

    return info


def call_llm(config, prompt):
    """调用大模型API"""
    llm_config = config["llm"]
    provider = llm_config.get("provider", "openai")

    system_prompt = """你是一个智能分类助手。你的任务是分析B站UP主的信息，并进行智能分类。

你会收到每个UP主的详细信息，包括：
- 昵称、简介、认证信息
- **合集/系列名称**（这是判断UP主内容方向的重要依据！）
- 最近视频的标题和标签
- 主要投稿分区

分类规则：
1. **优先根据合集/系列名称判断**，这直接反映UP主的主要内容方向
2. 结合视频标签、投稿分区、视频标题综合判断
3. 分类应该具体有意义，如"数学"、"考研"、"编程"等
4. 如果UP主内容很杂，根据最主要的内容方向分类
5. 返回格式必须是有效的JSON"""

    if provider == "claude":
        headers = {
            "Content-Type": "application/json",
            "x-api-key": llm_config["api_key"],
            "anthropic-version": "2023-06-01"
        }
        data = {
            "model": llm_config["model"],
            "max_tokens": 8192,
            "system": system_prompt,
            "messages": [{"role": "user", "content": prompt}]
        }
        with httpx.Client(timeout=180) as client:
            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers, json=data
            )
            response.raise_for_status()
            return response.json()["content"][0]["text"]
    else:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {llm_config['api_key']}"
        }
        data = {
            "model": llm_config["model"],
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3
        }
        base_url = llm_config.get("base_url", "https://api.openai.com/v1")
        with httpx.Client(timeout=180) as client:
            response = client.post(
                f"{base_url}/chat/completions",
                headers=headers, json=data
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


def format_number(num):
    if num >= 100000000:
        return f"{num/100000000:.1f}亿"
    elif num >= 10000:
        return f"{num/10000:.1f}万"
    return str(num)


def classify_uploaders(config, uploaders_info):
    """使用AI对UP主进行分类"""

    info_text = "以下是需要分类的B站UP主详细信息：\n\n"

    for up in uploaders_info:
        info_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        info_text += f"【{up['name']}】(UID: {up['mid']})\n"

        if up.get('official_verify'):
            info_text += f"  认证: {up['official_verify']}\n"

        info_text += f"  简介: {up['sign'][:100] if up['sign'] else '无'}\n"

        # 合集信息（重要！）
        if up.get('channels'):
            info_text += f"  📂 合集: {', '.join(up['channels'][:5])}\n"

        if up.get('series'):
            info_text += f"  📁 系列: {', '.join(up['series'][:5])}\n"

        if up.get('main_categories'):
            info_text += f"  主要分区: {', '.join(up['main_categories'])}\n"

        if up.get('tags'):
            info_text += f"  视频标签: {', '.join(up['tags'][:8])}\n"

        if up.get('videos'):
            info_text += f"  最近视频:\n"
            for v in up['videos'][:3]:
                info_text += f"    - {v['title']}\n"

        info_text += "\n"

    prompt = f"""{info_text}

请根据以上UP主的详细信息进行智能分类。

**重要**：优先根据"合集"和"系列"名称来判断UP主的内容方向，这是最直接的分类依据。

要求：
1. 自动决定分类类别，不要使用预设分类
2. 类别名称要具体，可以用"/"表示子分类
3. 每个UP主只属于一个最合适的分类

请以以下JSON格式返回：
{{
    "categories": {{
        "分类名1": [
            {{"name": "UP主名", "mid": UID, "reason": "分类依据（引用合集/系列/标签）"}}
        ],
        "分类名2": [...]
    }}
}}"""

    print("\n正在使用AI分析并分类...")
    result = call_llm(config, prompt)

    try:
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        return json.loads(result.strip())
    except json.JSONDecodeError as e:
        print(f"解析AI返回结果时出错: {e}")
        return None


async def main():
    print("=" * 60)
    print("B站关注UP主智能分类工具（V2 - 增加合集信息）")
    print("=" * 60)

    config = load_config()
    credential = get_credential(config)
    uid = config["bilibili"]["dedeuserid"]

    followings = await get_all_followings(credential, uid)

    if not followings:
        print("未获取到关注列表，请检查配置")
        return

    print("\n正在获取UP主详细信息（包括合集、系列、视频、标签等）...")
    print("这可能需要一些时间，请耐心等待...\n")

    uploaders_info = []
    total = len(followings)

    for i, up in enumerate(followings):
        info = await get_uploader_full_info(credential, up, i, total)
        uploaders_info.append(info)

        if (i + 1) % 20 == 0:
            await asyncio.sleep(1)

    print(f"\n已收集 {len(uploaders_info)} 个UP主的详细信息")

    # 保存原始数据
    raw_data_path = Path(__file__).parent / "up主原始数据_v2.json"
    with open(raw_data_path, "w", encoding="utf-8") as f:
        json.dump(uploaders_info, f, ensure_ascii=False, indent=2)
    print(f"原始数据已保存到: {raw_data_path}")

    # 分批让AI分类
    batch_size = 25
    all_results = {"categories": {}}

    for i in range(0, len(uploaders_info), batch_size):
        batch = uploaders_info[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(uploaders_info) + batch_size - 1) // batch_size
        print(f"\n处理第 {batch_num}/{total_batches} 批 ({len(batch)} 个UP主)...")

        result = classify_uploaders(config, batch)

        if result and "categories" in result:
            for cat, ups in result["categories"].items():
                if cat not in all_results["categories"]:
                    all_results["categories"][cat] = []
                all_results["categories"][cat].extend(ups)

        time.sleep(2)

    # 按分类大小排序
    sorted_categories = dict(sorted(
        all_results["categories"].items(),
        key=lambda x: len(x[1]),
        reverse=True
    ))

    # 输出结果
    print("\n" + "=" * 60)
    print("分类结果")
    print("=" * 60)

    for category, ups in sorted_categories.items():
        print(f"\n【{category}】({len(ups)}个)")
        for up in ups[:5]:
            print(f"  - {up['name']}")
        if len(ups) > 5:
            print(f"  ... 等{len(ups)}个")

    # 保存结果
    output_path = Path(__file__).parent / "分类结果_v2.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"categories": sorted_categories}, f, ensure_ascii=False, indent=2)

    md_path = Path(__file__).parent / "分类结果_v2.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# B站关注UP主分类结果（V2 - 基于合集信息）\n\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"总计: {len(uploaders_info)} 个UP主，{len(sorted_categories)} 个分类\n\n")
        f.write("---\n\n")

        for category, ups in sorted_categories.items():
            f.write(f"## {category} ({len(ups)}个)\n\n")
            for up in ups:
                mid = up.get('mid', '')
                reason = up.get('reason', '')
                f.write(f"- [{up['name']}](https://space.bilibili.com/{mid})")
                if reason:
                    f.write(f" - {reason}")
                f.write("\n")
            f.write("\n")

    print(f"\n结果已保存到: {output_path}")
    print(f"Markdown报告: {md_path}")

    print("\n" + "=" * 60)
    print(f"总UP主数: {len(uploaders_info)}")
    print(f"分类数量: {len(sorted_categories)}")


if __name__ == "__main__":
    asyncio.run(main())
