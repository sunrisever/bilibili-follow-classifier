# -*- coding: utf-8 -*-
"""
B站关注UP主智能分类工具（增强版）
- 自动获取你的B站关注列表
- 获取丰富的UP主信息用于AI分析
- 使用AI动态分析并生成分类
- 分类类别由AI根据实际内容决定
"""

import json
import time
import asyncio
from pathlib import Path
from collections import Counter
from bilibili_api import user, video, Credential
import httpx


def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_credential(config):
    """获取B站凭证"""
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


async def get_user_stat(credential, mid):
    """获取UP主的统计信息（粉丝数、播放量等）"""
    try:
        u = user.User(uid=mid, credential=credential)
        stat = await u.get_relation_info()
        up_stat = await u.get_up_stat()

        return {
            "follower": stat.get("follower", 0),  # 粉丝数
            "following": stat.get("following", 0),  # 关注数
            "archive_view": up_stat.get("archive", {}).get("view", 0),  # 总播放量
            "article_view": up_stat.get("article", {}).get("view", 0),  # 文章阅读量
        }
    except Exception as e:
        return {"follower": 0, "following": 0, "archive_view": 0, "article_view": 0}


async def get_user_videos_detail(credential, mid, limit=10):
    """获取UP主最近视频的详细信息"""
    try:
        u = user.User(uid=mid, credential=credential)
        videos_data = await u.get_videos(pn=1, ps=limit)
        video_list = videos_data.get("list", {}).get("vlist", [])

        videos_info = []
        # 统计分区
        tnames = []

        for v in video_list:
            video_info = {
                "title": v.get("title", ""),
                "tname": v.get("typeid", ""),  # 分区ID
                "play": v.get("play", 0),  # 播放量
                "comment": v.get("comment", 0),  # 评论数
                "description": v.get("description", "")[:100],  # 简介前100字
            }
            videos_info.append(video_info)

            # 记录分区名
            if v.get("typeid"):
                tnames.append(str(v.get("typeid")))

        return videos_info, tnames
    except Exception as e:
        return [], []


async def get_video_tags(credential, bvid):
    """获取视频标签"""
    try:
        v = video.Video(bvid=bvid, credential=credential)
        tags = await v.get_tags()
        return [tag.get("tag_name", "") for tag in tags]
    except:
        return []


async def get_user_top_videos_with_tags(credential, mid, limit=5):
    """获取UP主热门视频及其标签"""
    try:
        u = user.User(uid=mid, credential=credential)
        videos_data = await u.get_videos(pn=1, ps=limit, order=video.VideoOrder.PUBDATE)
        video_list = videos_data.get("list", {}).get("vlist", [])

        all_tags = []
        video_details = []

        for v in video_list[:3]:  # 只取前3个视频的标签，避免请求过多
            bvid = v.get("bvid")
            if bvid:
                tags = await get_video_tags(credential, bvid)
                all_tags.extend(tags)
                video_details.append({
                    "title": v.get("title", ""),
                    "tname": v.get("typeid", ""),
                    "play": v.get("play", 0),
                    "tags": tags
                })
                await asyncio.sleep(0.2)  # 避免请求过快

        return video_details, all_tags
    except Exception as e:
        return [], []


# B站分区ID到名称的映射（常用分区）
TNAME_MAP = {
    1: "动画", 13: "番剧", 167: "国创", 3: "音乐", 129: "舞蹈",
    4: "游戏", 36: "知识", 188: "科技", 234: "运动", 223: "汽车",
    160: "生活", 211: "美食", 217: "动物圈", 119: "鬼畜",
    155: "时尚", 5: "娱乐", 181: "影视", 177: "纪录片",
    23: "电影", 11: "电视剧", 202: "资讯",
    # 知识子分区
    201: "科学科普", 124: "社科人文", 228: "人文历史", 207: "财经商业",
    208: "校园学习", 209: "职业职场", 229: "设计创意", 122: "野生技能",
    # 科技子分区
    95: "数码", 230: "软件应用", 231: "计算机技术", 232: "科工机械",
    # 生活子分区
    138: "搞笑", 254: "亲子", 161: "手工", 162: "绘画", 21: "日常",
}


def get_tname(typeid):
    """根据分区ID获取分区名"""
    return TNAME_MAP.get(typeid, f"分区{typeid}")


async def get_uploader_full_info(credential, up_basic, index, total):
    """获取UP主的完整信息"""
    mid = up_basic["mid"]

    info = {
        "mid": mid,
        "name": up_basic["uname"],
        "sign": up_basic.get("sign", "") or "",
        "official_verify": up_basic.get("official_verify", {}).get("desc", ""),  # 认证信息
    }

    try:
        # 1. 获取统计信息
        stat = await get_user_stat(credential, mid)
        info["stat"] = stat
        await asyncio.sleep(0.2)

        # 2. 获取视频详情和标签
        video_details, all_tags = await get_user_top_videos_with_tags(credential, mid, limit=5)
        info["videos"] = video_details
        info["tags"] = list(set(all_tags))[:10]  # 去重，取前10个标签

        # 3. 统计主要投稿分区
        if video_details:
            tnames = [get_tname(v.get("tname", 0)) for v in video_details if v.get("tname")]
            if tnames:
                tname_counter = Counter(tnames)
                info["main_categories"] = [cat for cat, _ in tname_counter.most_common(3)]

        await asyncio.sleep(0.3)

    except Exception as e:
        print(f"    获取 {up_basic['uname']} 详情时出错: {e}")
        info["stat"] = {"follower": 0, "following": 0, "archive_view": 0}
        info["videos"] = []
        info["tags"] = []

    if (index + 1) % 10 == 0:
        print(f"  已处理 {index + 1}/{total} 个UP主...")

    return info


def call_llm(config, prompt):
    """调用大模型API（支持Claude和OpenAI兼容接口）"""
    llm_config = config["llm"]
    provider = llm_config.get("provider", "openai")

    system_prompt = """你是一个智能分类助手。你的任务是分析B站UP主的信息，并进行智能分类。

你会收到每个UP主的详细信息，包括：
- 昵称、简介、认证信息
- 粉丝数、总播放量
- 最近视频的标题、分区、播放量、标签
- 主要投稿分区

分类规则：
1. 综合分析所有信息，特别重视：视频标签、投稿分区、视频标题
2. 你需要自己决定合适的分类类别，类别应该具体有意义
3. 可以创建多层级分类，如"编程/Python"、"考研/数学"
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
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }

        with httpx.Client(timeout=180) as client:
            response = client.post(
                "https://api.anthropic.com/v1/messages",
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["content"][0]["text"]

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
                headers=headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]


def format_number(num):
    """格式化数字显示"""
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

        stat = up.get('stat', {})
        info_text += f"  粉丝: {format_number(stat.get('follower', 0))} | "
        info_text += f"总播放: {format_number(stat.get('archive_view', 0))}\n"

        if up.get('main_categories'):
            info_text += f"  主要分区: {', '.join(up['main_categories'])}\n"

        if up.get('tags'):
            info_text += f"  视频标签: {', '.join(up['tags'][:8])}\n"

        if up.get('videos'):
            info_text += f"  最近视频:\n"
            for v in up['videos'][:3]:
                info_text += f"    - {v['title']}"
                if v.get('tags'):
                    info_text += f" [标签: {', '.join(v['tags'][:3])}]"
                info_text += "\n"

        info_text += "\n"

    prompt = f"""{info_text}

请根据以上UP主的详细信息进行智能分类。

要求：
1. 综合分析认证信息、简介、分区、标签、视频标题来判断内容类型
2. 自动决定分类类别，不要使用预设分类
3. 类别名称要具体，可以用"/"表示子分类，如"编程/Python"
4. 每个UP主只属于一个最合适的分类

请以以下JSON格式返回：
{{
    "categories": {{
        "分类名1": [
            {{"name": "UP主名", "mid": UID, "reason": "分类依据（提及关键标签/分区）"}}
        ],
        "分类名2": [...]
    }},
    "category_descriptions": {{
        "分类名1": "该分类的简要说明",
        "分类名2": "..."
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
        print(f"原始返回: {result[:500]}...")
        return None


async def main():
    print("=" * 60)
    print("B站关注UP主智能分类工具（增强版）")
    print("=" * 60)

    config = load_config()
    credential = get_credential(config)
    uid = config["bilibili"]["dedeuserid"]

    # 获取关注列表
    followings = await get_all_followings(credential, uid)

    if not followings:
        print("未获取到关注列表，请检查配置")
        return

    # 收集UP主详细信息
    print("\n正在获取UP主详细信息（包括视频、标签、分区等）...")
    print("这可能需要一些时间，请耐心等待...\n")

    uploaders_info = []
    total = len(followings)

    for i, up in enumerate(followings):
        info = await get_uploader_full_info(credential, up, i, total)
        uploaders_info.append(info)

        # 每处理20个休息一下，避免被限流
        if (i + 1) % 20 == 0:
            await asyncio.sleep(1)

    print(f"\n已收集 {len(uploaders_info)} 个UP主的详细信息")

    # 保存原始数据（方便调试）
    raw_data_path = Path(__file__).parent / "up主原始数据.json"
    with open(raw_data_path, "w", encoding="utf-8") as f:
        json.dump(uploaders_info, f, ensure_ascii=False, indent=2)
    print(f"原始数据已保存到: {raw_data_path}")

    # 分批让AI分类
    batch_size = 25  # 每批25个，信息更丰富所以批次小一点
    all_results = {"categories": {}, "category_descriptions": {}}

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

            # 合并分类描述
            if "category_descriptions" in result:
                all_results["category_descriptions"].update(result["category_descriptions"])

        time.sleep(2)  # 避免API限流

    # 输出结果
    print("\n" + "=" * 60)
    print("分类结果")
    print("=" * 60)

    # 按分类内UP主数量排序
    sorted_categories = sorted(
        all_results["categories"].items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    for category, ups in sorted_categories:
        desc = all_results.get("category_descriptions", {}).get(category, "")
        print(f"\n【{category}】({len(ups)}个)")
        if desc:
            print(f"  {desc}")
        for up in ups:
            print(f"  - {up['name']}")
            if up.get('reason'):
                print(f"    └ {up['reason']}")

    # 保存JSON结果
    output_path = Path(__file__).parent / "分类结果.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存到: {output_path}")

    # 生成Markdown报告
    md_path = Path(__file__).parent / "分类结果.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# B站关注UP主分类结果\n\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"总计: {len(uploaders_info)} 个UP主，{len(all_results['categories'])} 个分类\n\n")
        f.write("---\n\n")

        for category, ups in sorted_categories:
            desc = all_results.get("category_descriptions", {}).get(category, "")
            f.write(f"## {category} ({len(ups)}个)\n\n")
            if desc:
                f.write(f"> {desc}\n\n")
            for up in ups:
                mid = up.get('mid', '')
                reason = up.get('reason', '')
                f.write(f"- [{up['name']}](https://space.bilibili.com/{mid})")
                if reason:
                    f.write(f" - {reason}")
                f.write("\n")
            f.write("\n")

    print(f"Markdown报告已保存到: {md_path}")

    # 统计信息
    print("\n" + "=" * 60)
    print("统计信息")
    print("=" * 60)
    print(f"总UP主数: {len(uploaders_info)}")
    print(f"分类数量: {len(all_results['categories'])}")
    print("\n各分类UP主数量:")
    for category, ups in sorted_categories:
        print(f"  {category}: {len(ups)}")


if __name__ == "__main__":
    asyncio.run(main())
