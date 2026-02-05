# -*- coding: utf-8 -*-
"""
将分类结果同步到B站关注分组
用法: python sync_groups.py [--dry-run] [--category 分类名]

--dry-run: 只显示将要执行的操作，不实际执行
--category: 只同步指定分类（可多次使用）
"""

import json
import asyncio
import sys
from pathlib import Path

from bilibili_api import user, Credential
from bilibili_api.utils.utils import get_api
from bilibili_api.utils.network import Api

BASE_PATH = Path(__file__).parent
DATA_PATH = BASE_PATH / "data"


def load_config():
    with open(DATA_PATH / "config.json", "r", encoding="utf-8") as f:
        return json.load(f)


def get_credential(config):
    bili = config["bilibili"]
    return Credential(
        sessdata=bili["sessdata"],
        bili_jct=bili["bili_jct"],
        buvid3=bili["buvid3"],
        dedeuserid=bili["dedeuserid"],
    )


def load_classify_result():
    with open(DATA_PATH / "分类结果.json", "r", encoding="utf-8") as f:
        return json.load(f)


async def get_existing_groups(credential):
    """获取B站已有的关注分组列表"""
    USER_API = get_api("user")
    api = USER_API["info"]["self_subscribe_group"]
    result = await Api(**api, credential=credential).result
    groups = {}
    for g in result:
        groups[g["name"]] = g["tagid"]
    return groups


async def delete_group(credential, tagid):
    """删除一个关注分组"""
    return await user.delete_subscribe_group(tagid, credential)


def sanitize_group_name(name):
    """替换B站不允许的特殊字符"""
    return name.replace("/", "")


async def create_group(credential, name):
    """创建一个新的关注分组，返回 tagid"""
    safe_name = sanitize_group_name(name)
    result = await user.create_subscribe_group(safe_name, credential)
    tagid = result.get("tagid")
    if tagid is None:
        raise Exception(f"创建分组 '{name}' 失败: {result}")
    return tagid


async def move_users_to_group(credential, uids, group_id):
    """将用户移入指定分组（批量）"""
    return await user.set_subscribe_group(uids, [group_id], credential)


async def sync(dry_run=False, only_categories=None):
    config = load_config()
    credential = get_credential(config)
    classify_data = load_classify_result()
    categories = classify_data["categories"]

    # 筛选要同步的分类
    if only_categories:
        categories = {k: v for k, v in categories.items() if k in only_categories}
        if not categories:
            print(f"未找到指定的分类: {only_categories}")
            return

    total_ups = sum(len(v) for v in categories.values())
    print(f"=== B站关注分组同步 ===")
    print(f"共 {len(categories)} 个分类，{total_ups} 个UP主")
    if dry_run:
        print("【试运行模式】不会实际执行任何操作")
    print()

    # 1. 获取已有分组
    print("第1步：获取已有分组...")
    existing_groups = await get_existing_groups(credential)
    print(f"已有 {len(existing_groups)} 个分组:")
    for name, tagid in existing_groups.items():
        print(f"  [{tagid}] {name}")
    print()

    # 2. 删除旧分组（保留"特别关注"和"默认分组"）
    KEEP_TAGIDS = {-10, 0}  # 特别关注、默认分组
    to_delete = {name: tagid for name, tagid in existing_groups.items()
                 if tagid not in KEEP_TAGIDS}

    if to_delete:
        print(f"第2步：删除 {len(to_delete)} 个旧分组...")
        if not dry_run:
            for name, tagid in to_delete.items():
                try:
                    await delete_group(credential, tagid)
                    print(f"  ✓ 删除: {name} (tagid={tagid})")
                    await asyncio.sleep(0.3)
                except Exception as e:
                    print(f"  ✗ 删除失败: {name} - {e}")
        else:
            for name, tagid in to_delete.items():
                print(f"  [试运行] 将删除: {name} (tagid={tagid})")
    else:
        print("第2步：没有需要删除的旧分组")
    print()

    # 3. 创建新分组
    print(f"第3步：创建 {len(categories)} 个新分组...")
    group_map = {}  # {分类名: tagid}
    if not dry_run:
        for name in categories:
            try:
                tagid = await create_group(credential, name)
                group_map[name] = tagid
                print(f"  ✓ 创建: {name} (tagid={tagid})")
                await asyncio.sleep(0.3)
            except Exception as e:
                print(f"  ✗ 创建失败: {name} - {e}")
                return
    else:
        for name in categories:
            print(f"  [试运行] 将创建: {name}")
            group_map[name] = -1
    print()

    # 4. 将UP主移入对应分组
    print("第4步：分配UP主到分组...\n")
    success_count = 0
    fail_count = 0
    batch_size = 20

    for cat_name, ups in categories.items():
        tagid = group_map.get(cat_name)
        if tagid is None:
            print(f"跳过 {cat_name}: 分组不存在")
            continue

        uids = [up["mid"] for up in ups]
        print(f"[{cat_name}] {len(uids)} 人 → tagid={tagid}")

        if dry_run:
            print(f"  [试运行] {len(uids)} 人将被移入此分组")
            continue

        # 分批处理
        for i in range(0, len(uids), batch_size):
            batch = uids[i:i + batch_size]
            batch_names = [up["name"] for up in ups[i:i + batch_size]]
            try:
                await move_users_to_group(credential, batch, tagid)
                success_count += len(batch)
                names_str = ', '.join(batch_names[:5])
                if len(batch_names) > 5:
                    names_str += f"...等{len(batch_names)}人"
                print(f"  ✓ 批{i // batch_size + 1} ({len(batch)}人): {names_str}")
                await asyncio.sleep(1)
            except Exception as e:
                fail_count += len(batch)
                print(f"  ✗ 批{i // batch_size + 1}失败: {e}")
                print(f"    逐个重试...")
                for j, uid in enumerate(batch):
                    try:
                        await move_users_to_group(credential, [uid], tagid)
                        success_count += 1
                        fail_count -= 1
                        await asyncio.sleep(0.5)
                    except Exception as e2:
                        print(f"    ✗ {batch_names[j]}: {e2}")
                        await asyncio.sleep(1)

    # 5. 总结
    print(f"\n=== 同步完成 ===")
    if not dry_run:
        print(f"成功: {success_count} 人")
        if fail_count > 0:
            print(f"失败: {fail_count} 人")
    else:
        print("试运行完毕，未执行任何实际操作")


def main():
    dry_run = "--dry-run" in sys.argv
    only_categories = []
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--category" and i + 1 < len(args):
            only_categories.append(args[i + 1])
            i += 2
        else:
            i += 1

    asyncio.run(sync(dry_run=dry_run, only_categories=only_categories or None))


if __name__ == "__main__":
    main()
