# B站关注UP主分类系统

自动采集B站关注列表，通过关键词规则将UP主分类到自定义类别，并同步到B站关注分组。

## 功能

- 自动采集UP主信息（签名、合集、视频标题、标签、投稿分区等）
- 基于关键词规则自动分类 + AI大模型二次审核
- 支持增量添加新关注的UP主
- 一键同步分类结果到B站关注分组

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 初始化 data 目录

将 `data_example/` 复制为 `data/`，然后修改配置：

```bash
cp -r data_example data
```

编辑 `data/config.json`，填入你的B站cookie：

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

获取方式：浏览器登录B站 → F12开发者工具 → Application → Cookies → 复制对应字段。

### 3. 自定义分类规则

编辑 `data/classify_rules.json`，定义你自己的分类体系：

- **categories**：分类名称列表，最后一个作为默认分类
- **manual**：手动指定某些UP主的分类（优先级最高）
- **keyword_rules**：每个分类的关键词和权重，用于自动匹配
- **zone_mapping**：B站投稿分区到自定义分类的映射

`data_example/classify_rules.json` 提供了一个简单示例，可以在此基础上扩展。

### 4. 采集信息

```bash
# 全量采集所有关注UP主的详细信息
python fetch.py all
```

> 注意：B站API有频率限制，短时间大量请求会触发风控（错误码-352）。投稿分区数据可能因限流而缺失，过一段时间后运行 `python fetch.py zones` 可以补充。

### 5. 算法分类

```bash
python classify.py
```

分类结果保存到 `data/分类结果.json` 和 `data/分类结果.md`。算法基于关键词规则匹配，准确率约90%。

### 6. AI大模型审核

算法分类完成后，建议使用AI大模型（如 Claude、ChatGPT、DeepSeek 等）对分类结果进行二次审核。

将 `data/分类结果.json` 和 `data/up主信息汇总.txt` 提供给AI，让它逐个检查分类是否合理，AI会标注出它认为有疑问的分类。常见需要修正的情况：
- AI相关内容被归到编程（应细分到AI学术/产品/教程三个子类）
- 纯数学内容被归到编程（应归数学/物理）
- 时政类被归到科普/人文（应归时政类）
- 美女vlog被归到生活（应归美女/颜值）

### 7. 人工审核

针对AI大模型标注有疑问的分类，人工逐个核实并最终确认。查看UP主主页判断其内容方向，修正 `data/分类结果.json` 中的错误分类。

修正后同步MD文件：

```bash
python -c "from add_new import save_md, load_classify_result; save_md(load_classify_result())"
```

审核过程中可以将确认正确的UP主加入 `data/classify_rules.json` 的 `manual` 字段，这样下次全量分类时不会被覆盖。

### 8. 同步到B站分组

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

### 补充缺失的投稿分区

采集时如果触发B站频率限制，部分UP主的投稿分区数据会缺失。过一段时间后运行：

```bash
python fetch.py zones
```

补充后建议重新运行 `python classify.py`，因为投稿分区是分类的重要依据。

### 其他命令

```bash
python generate_info.py       # 重新生成信息汇总
python sync_groups.py --category 考研  # 只同步指定分类
```

## 项目结构

```
├── classify.py                    # 分类算法（从规则文件加载配置）
├── fetch.py                       # 信息采集（全量/增量/补充分区）
├── add_new.py                     # 增量添加UP主（采集+分类一条龙）
├── generate_info.py               # 生成可读的信息汇总文本
├── sync_groups.py                 # 同步分类结果到B站关注分组
├── requirements.txt               # Python依赖
├── classify_rules.example.json    # 分类规则示例（供参考）
├── data_example/                  # 示例data目录（首次使用复制为data/）
│   ├── config.json                # B站cookie配置模板
│   └── classify_rules.json        # 分类规则模板
└── data/                          # 个人数据（不纳入版本控制）
    ├── config.json                # B站cookie配置
    ├── classify_rules.json        # 你的分类规则
    ├── up主详细数据.json           # UP主采集的原始数据
    ├── up主信息汇总.txt            # 可读的信息汇总（供审核参考）
    ├── 分类结果.json               # 分类结果（程序读写）
    └── 分类结果.md                 # 分类结果（人工浏览，带B站链接）
```

## 注意事项

- `data/` 目录包含个人隐私数据，已加入 `.gitignore`，不会上传到远端
- 全量分类（`classify.py`）会覆盖现有分类结果，之前的人工调整会丢失（建议把调整写入 `manual` 字段保留）
- B站分组名不支持特殊字符（`/`等会被自动去除）
- 首次使用需按顺序执行：复制data目录 → 填写cookie → 采集 → 算法分类 → AI审核 → 人工审核 → 同步
