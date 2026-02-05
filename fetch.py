# -*- coding: utf-8 -*-
"""
B站UP主信息采集模块
支持：全量采集 / 单个UP主采集 / 补充投稿分区
"""

import json
import asyncio
from pathlib import Path
from bilibili_api import user, video, Credential

BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / "data"

# B站分区ID到名称的映射
ZONE_MAP = {
    1: "动画", 24: "MAD·AMV", 25: "MMD·3D", 47: "短片·手书·配音", 210: "手办·模玩",
    86: "特摄", 253: "动漫杂谈", 27: "综合",
    13: "番剧", 33: "连载动画", 32: "完结动画", 51: "资讯", 152: "官方延伸",
    167: "国创", 153: "国产动画", 168: "国产原创相关", 169: "布袋戏", 195: "动态漫·广播剧",
    3: "音乐", 28: "原创音乐", 31: "翻唱", 30: "VOCALOID·UTAU", 59: "演奏",
    193: "MV", 29: "音乐现场", 130: "音乐综合",
    129: "舞蹈", 20: "宅舞", 198: "街舞", 199: "明星舞蹈", 200: "中国舞", 154: "舞蹈综合", 156: "舞蹈教程",
    4: "游戏", 17: "单机游戏", 171: "电子竞技", 172: "手机游戏", 65: "网络游戏",
    173: "桌游棋牌", 121: "GMV", 136: "音游", 19: "Mugen",
    36: "知识", 201: "科学科普", 124: "社科·法律·心理", 228: "人文历史",
    207: "财经商业", 208: "校园学习", 209: "职业职场", 229: "设计·创意", 122: "野生技术协会",
    188: "科技", 95: "数码", 230: "软件应用", 231: "计算机技术", 232: "科工机械", 233: "极客DIY",
    234: "运动", 235: "篮球", 249: "足球", 164: "健身", 236: "竞技体育",
    237: "运动文化", 238: "运动综合",
    223: "汽车", 245: "赛车", 246: "改装玩车", 247: "新能源车", 248: "房车",
    240: "摩托车", 227: "购车攻略", 176: "汽车生活",
    160: "生活", 138: "搞笑", 250: "出行", 251: "三农", 239: "家居房产",
    161: "手工", 162: "绘画", 21: "日常",
    211: "美食", 76: "美食制作", 212: "美食侦探", 213: "美食测评", 214: "田园美食", 215: "美食记录",
    217: "动物圈", 218: "喵星人", 219: "汪星人", 220: "小宠异宠", 221: "野生动物", 222: "动物二创",
    119: "鬼畜", 22: "鬼畜调教", 26: "音MAD", 126: "人力VOCALOID", 216: "鬼畜剧场",
    155: "时尚", 157: "美妆护肤", 158: "穿搭", 159: "时尚潮流",
    202: "资讯", 203: "热点", 204: "环球", 205: "社会", 206: "综合",
    5: "娱乐", 71: "综艺", 241: "娱乐杂谈", 242: "粉丝创作", 137: "明星综合",
    181: "影视", 182: "影视杂谈", 183: "影视剪辑", 85: "小剧场", 184: "预告·资讯",
    177: "纪录片", 37: "人文·历史", 178: "科学·探索·自然", 179: "军事", 180: "社会·美食·旅行",
    23: "电影", 147: "华语电影", 145: "欧美电影", 146: "日本电影", 83: "其他国家",
    11: "电视剧", 185: "国产剧", 187: "海外剧",
}


def load_config():
    with open(DATA_PATH / "config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_credential(config):
    bili = config["bilibili"]
    return Credential(
        sessdata=bili["sessdata"],
        bili_jct=bili["bili_jct"],
        buvid3=bili["buvid3"],
        dedeuserid=bili["dedeuserid"]
    )


def load_data():
    """加载现有UP主数据"""
    data_path = DATA_PATH / "up主详细数据.json"
    if data_path.exists():
        with open(data_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_data(uploaders):
    """保存UP主数据"""
    data_path = DATA_PATH / "up主详细数据.json"
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(uploaders, f, ensure_ascii=False, indent=2)


async def get_all_followings(credential, uid):
    """获取所有关注的UP主"""
    u = user.User(uid=int(uid), credential=credential)
    all_followings = []
    page = 1
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
    return all_followings


async def get_channels_and_series(credential, mid):
    """获取UP主的合集和系列名称"""
    channel_names, series_names = [], []
    try:
        u = user.User(uid=mid, credential=credential)
        data = await u.get_channel_list()
        if data and "items_lists" in data:
            items = data["items_lists"]
            for s in items.get("seasons_list", []):
                meta = s.get("meta", {})
                name = (meta.get("name", "") or s.get("name", "")).replace("合集·", "").strip()
                if name:
                    channel_names.append(name)
            for s in items.get("series_list", []):
                meta = s.get("meta", {})
                name = meta.get("name", "") or s.get("name", "")
                if name:
                    series_names.append(name)
    except:
        pass
    return channel_names, series_names


async def get_videos(credential, mid, limit=30):
    """获取UP主最近视频标题"""
    try:
        u = user.User(uid=mid, credential=credential)
        videos_data = await u.get_videos(pn=1, ps=min(limit, 30))
        video_list = videos_data.get("list", {}).get("vlist", [])
        return [v.get("title", "") for v in video_list]
    except:
        return []


async def get_video_zones(credential, mid):
    """获取UP主最近30个视频的投稿分区"""
    try:
        u = user.User(uid=mid, credential=credential)
        videos_data = await u.get_videos(pn=1, ps=30)
        video_list = videos_data.get("list", {}).get("vlist", [])
        zones = []
        for v in video_list:
            typeid = v.get("typeid", 0)
            zone_name = ZONE_MAP.get(typeid, "")
            if zone_name and zone_name not in zones:
                zones.append(zone_name)
        return zones
    except:
        return []


async def get_video_tags(credential, bvid):
    """获取单个视频的标签"""
    try:
        vid = video.Video(bvid=bvid, credential=credential)
        tags = await vid.get_tags()
        return [t.get("tag_name", "") for t in tags]
    except:
        return []


async def get_user_video_tags(credential, mid, limit=5):
    """获取UP主最近几个视频的标签"""
    try:
        u = user.User(uid=mid, credential=credential)
        videos_data = await u.get_videos(pn=1, ps=limit)
        video_list = videos_data.get("list", {}).get("vlist", [])
        all_tags = []
        for v in video_list[:limit]:
            bvid = v.get("bvid")
            if bvid:
                tags = await get_video_tags(credential, bvid)
                all_tags.extend(tags)
                await asyncio.sleep(0.2)
        return list(set(all_tags))
    except:
        return []


async def get_articles(credential, mid, limit=30):
    """获取UP主的专栏文章标题"""
    try:
        u = user.User(uid=mid, credential=credential)
        articles_data = await u.get_articles(pn=1, ps=min(limit, 30))
        articles = articles_data.get("articles", [])
        return [a.get("title", "") for a in articles if a.get("title")]
    except:
        return []


async def fetch_one(credential, mid, name=None):
    """采集单个UP主的完整信息"""
    info = {"mid": mid, "name": name or str(mid)}

    try:
        # 如果没有名字，先获取基本信息
        if not name:
            u = user.User(uid=mid, credential=credential)
            user_info = await u.get_user_info()
            info["name"] = user_info.get("name", str(mid))
            info["sign"] = user_info.get("sign", "")
            official = user_info.get("official", {})
            info["official_verify"] = official.get("title", "")
            await asyncio.sleep(0.3)
        else:
            info["sign"] = ""
            info["official_verify"] = ""

        # 合集和系列
        channels, series = await get_channels_and_series(credential, mid)
        info["channels"] = channels
        info["series"] = series
        await asyncio.sleep(0.3)

        # 视频标题
        info["video_titles"] = await get_videos(credential, mid)
        await asyncio.sleep(0.2)

        # 投稿分区
        info["video_zones"] = await get_video_zones(credential, mid)
        await asyncio.sleep(0.2)

        # 视频标签
        info["tags"] = await get_user_video_tags(credential, mid)
        await asyncio.sleep(0.2)

        # 专栏文章
        info["articles"] = await get_articles(credential, mid)

    except Exception as e:
        print(f"  采集 {info['name']} 时出错: {e}")
        for key in ["channels", "series", "video_titles", "video_zones", "tags", "articles"]:
            info.setdefault(key, [])

    return info


async def fetch_all():
    """全量采集：获取所有关注UP主的详细信息"""
    config = load_config()
    credential = get_credential(config)
    uid = config["bilibili"]["dedeuserid"]

    print("正在获取关注列表...")
    followings = await get_all_followings(credential, uid)
    if not followings:
        print("未获取到关注列表")
        return

    print(f"\n开始采集 {len(followings)} 个UP主的详细信息...\n")
    uploaders = []
    for i, up in enumerate(followings):
        info = await fetch_one(credential, up["mid"], up["uname"])
        info["sign"] = up.get("sign", "") or ""
        info["official_verify"] = up.get("official_verify", {}).get("desc", "")
        uploaders.append(info)

        if (i + 1) % 10 == 0:
            print(f"  已处理 {i + 1}/{len(followings)}")
        if (i + 1) % 20 == 0:
            await asyncio.sleep(2)

    save_data(uploaders)
    print(f"\n完成！共采集 {len(uploaders)} 个UP主")


async def fetch_new(mids):
    """增量采集：获取指定mid的UP主信息，添加到现有数据"""
    config = load_config()
    credential = get_credential(config)
    uploaders = load_data()
    existing_mids = {up["mid"] for up in uploaders}

    added = []
    for mid in mids:
        if mid in existing_mids:
            print(f"  mid={mid} 已存在，跳过")
            continue

        print(f"  正在采集 mid={mid}...")
        info = await fetch_one(credential, mid)
        uploaders.append(info)
        added.append(info)
        print(f"  -> {info['name']}")
        await asyncio.sleep(1)

    if added:
        save_data(uploaders)
        print(f"\n新增 {len(added)} 个UP主")
    return added


async def fetch_missing_zones():
    """补充缺失的投稿分区"""
    config = load_config()
    credential = get_credential(config)
    uploaders = load_data()

    missing = [up for up in uploaders if not up.get("video_zones", [])]
    print(f"缺失投稿分区: {len(missing)} 个")

    success = 0
    fail_count = 0
    for i, up in enumerate(missing):
        try:
            zones = await get_video_zones(credential, up["mid"])
            if zones is not None:
                up["video_zones"] = zones
                zone_str = ", ".join(zones[:3]) if zones else "无视频"
                print(f"  [{i+1}/{len(missing)}] {up['name']} - {zone_str}")
                success += 1
                fail_count = 0
            else:
                fail_count += 1
                print(f"  [{i+1}/{len(missing)}] {up['name']} - 失败")
        except Exception as e:
            fail_count += 1
            print(f"  [{i+1}/{len(missing)}] {up['name']} - {e}")

        if fail_count >= 5:
            print("连续失败过多，停止")
            break

        await asyncio.sleep(0.5)
        if (i + 1) % 20 == 0:
            save_data(uploaders)
            await asyncio.sleep(2)

    save_data(uploaders)
    still_missing = sum(1 for up in uploaders if not up.get("video_zones", []))
    print(f"\n成功: {success}，仍缺失: {still_missing}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "all":
            asyncio.run(fetch_all())
        elif cmd == "zones":
            asyncio.run(fetch_missing_zones())
        elif cmd.isdigit():
            asyncio.run(fetch_new([int(cmd)]))
        else:
            print("用法: python fetch.py [all|zones|<mid>]")
    else:
        print("用法:")
        print("  python fetch.py all       # 全量采集所有关注")
        print("  python fetch.py zones     # 补充缺失投稿分区")
        print("  python fetch.py <mid>     # 采集指定UP主")
