# B站关注UP主分类系统

自动采集B站关注列表，通过关键词规则将UP主分类到自定义类别，并同步到B站关注分组。

## 功能

- 自动采集UP主信息（签名、合集、视频标题、标签、投稿分区等）
- 基于关键词规则自动分类（准确率约90%）
- 支持增量添加新关注的UP主
- 一键同步分类结果到B站关注分组

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置账号

创建 `data/config.json`：

```json
{
    "bilibili": {
        "sessdata": "你的SESSDATA",
        "bili_jct": "你的bili_jct",
        "buvid3": "你的buvid3",
        "dedeuserid": "你的UID"
    }
}
```

获取方式：浏览器登录B站 → F12打开开发者工具 → Application → Cookies → 找到对应字段。

### 3. 采集信息

```bash
# 全量采集所有关注UP主的详细信息
python fetch.py all
```

### 4. 自动分类

```bash
python classify.py
```

分类结果保存到 `data/分类结果.json` 和 `data/分类结果.md`。

### 5. 人工审核

查看 `data/分类结果.md` 或 `data/up主信息汇总.txt`，对分类不准确的手动修正 `data/分类结果.json`，然后同步MD：

```bash
python -c "from add_new import save_md, load_classify_result; save_md(load_classify_result())"
```

### 6. 同步到B站分组

```bash
# 试运行，查看将执行的操作
python sync_groups.py --dry-run

# 正式同步
python sync_groups.py
```

脚本会自动：删除旧分组 → 创建新分组 → 批量分配UP主。

## 日常使用

### 新增UP主

```bash
python add_new.py <mid>
```

自动：采集信息 → 算法分类 → 添加到分类结果 → 更新信息汇总。

### 其他命令

```bash
python fetch.py zones         # 补充缺失的投稿分区
python generate_info.py       # 重新生成信息汇总
python sync_groups.py --category 考研  # 只同步指定分类
```

## 自定义分类体系

分类规则在 `classify.py` 中定义，你可以根据自己的兴趣完全自定义：

1. **修改类别**：编辑 `CATEGORIES` 列表，增删改类别名称
2. **修改关键词**：编辑 `KEYWORDS` 字典，为每个类别设置匹配关键词
3. **修改分区映射**：编辑 `ZONE_CATEGORY_MAP`，将B站投稿分区映射到你的自定义类别
4. **手动指定**：编辑 `MANUAL` 字典，直接指定某些UP主的分类

修改后重新运行 `python classify.py` 即可。

## 项目结构

```
├── fetch.py             # 信息采集（全量/增量/补充分区）
├── classify.py          # 分类算法（关键词+规则+手动指定）
├── add_new.py           # 增量添加UP主（采集+分类一条龙）
├── generate_info.py     # 生成可读的信息汇总文本
├── sync_groups.py       # 同步分类结果到B站关注分组
├── requirements.txt     # Python依赖
├── data/                # 个人数据（不纳入版本控制）
│   ├── config.json      # B站cookie配置
│   ├── up主详细数据.json # UP主采集的原始数据
│   ├── up主信息汇总.txt  # 可读的信息汇总（供审核参考）
│   ├── 分类结果.json     # 分类结果（程序读写）
│   └── 分类结果.md       # 分类结果（人工浏览，带B站链接）
└── README.md
```

## 注意事项

- B站API有频率限制，短时间大量请求会触发风控（错误码-352）
- `data/` 目录包含个人隐私数据，已加入 `.gitignore`，不会上传到远端
- 全量分类（`classify.py`）会覆盖现有分类结果，之前的人工调整会丢失
- B站分组名不支持特殊字符（`/`等会被自动去除）
- 首次使用需先运行 `fetch.py all` 采集数据，再运行 `classify.py` 分类
