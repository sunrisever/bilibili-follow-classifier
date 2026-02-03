# -*- coding: utf-8 -*-
import asyncio
import json
from bilibili_api import user, Credential

# 加载配置
with open("C:/Users/28033/Desktop/bilibili关注分类/config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

bili = config["bilibili"]
credential = Credential(
    sessdata=bili["sessdata"],
    bili_jct=bili["bili_jct"],
    buvid3=bili["buvid3"],
    dedeuserid=bili["dedeuserid"]
)

async def test():
    print("1. 测试凭证...")
    uid = int(bili["dedeuserid"])
    u = user.User(uid=uid, credential=credential)

    print("2. 获取关注列表第1页...")
    result = await u.get_followings(pn=1)
    followings = result.get("list", [])
    print(f"   成功！获取到 {len(followings)} 个UP主")

    if followings:
        print(f"   第一个UP主: {followings[0]['uname']}")

    print("3. 测试完成！")

asyncio.run(test())
