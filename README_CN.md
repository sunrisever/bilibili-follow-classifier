[English](README.md) | 简体中文

# Bilibili Follow

> B站关注 UP 主整理与分组同步工具

这个项目用来把混乱的 B 站关注列表整理成可维护的分组系统。它会采集每个已关注 UP 主的主页和内容信号，用你定义的规则做分类，并把结果同步回 B 站关注分组。

## 这个项目解决什么问题

关注几百上千个 UP 主之后，默认关注列表通常已经失去整理能力。这个仓库把关注管理拆成一条清晰的流水线：

- 采集关注对象的结构化信息
- 用可编辑、可审计的规则体系做分类
- 用大模型或人工复核边界样本
- 把最终结果同步回 B 站分组

## 核心特点

- 全量采集关注列表，包含签名、合集、系列、视频标题、标签、投稿分区等信号
- 规则优先的分类方式，方便长期迭代和人工维护
- 支持 `manual` 手工覆盖，稳定保留高置信度分类
- 支持增量添加新关注的 UP 主
- 同步前支持 `--dry-run` 预览
- 内置 `SKILL.md`、`AGENTS.md`、`CLAUDE.md`，适合 Claude Code、Codex、OpenCode、OpenClaw 等 AI 编程助手

## 快速入口

- [SKILL.md](SKILL.md)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)

## 使用流程总览

1. 把 `data_example/` 复制成 `data/`
2. 在 `data/config.json` 中填写 B 站 Cookie
3. 在 `data/classify_rules.json` 中定义你的分类体系
4. 运行 `python fetch.py all`
5. 运行 `python classify.py`
6. 用大模型或人工复核疑难项
7. 运行 `python sync_groups.py --dry-run`
8. 确认无误后运行 `python sync_groups.py`

## 安装

```bash
pip install -r requirements.txt
```

## 配置

先复制示例目录：

```bash
cp -r data_example data
```

再编辑 `data/config.json`：

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

Cookie 获取方式：

- 登录 B 站
- 打开开发者工具
- 进入 `Application -> Cookies`
- 复制对应字段

## 分类规则说明

核心规则文件是 `data/classify_rules.json`。

- `categories`：分类列表，通常最后一个作为兜底分类
- `manual`：对特定 UP 主的人工硬覆盖
- `keyword_rules`：每个分类的关键词与权重
- `zone_mapping`：B 站投稿分区到分类的映射

这个项目故意采用“规则优先”的方式，而不是把分类完全交给黑盒模型。这样你可以持续积累自己的分类体系，而不是每次都重新猜。

## 常用命令

### 全量采集

```bash
python fetch.py all
```

可选：

```bash
python fetch.py zones
python fetch.py <mid>
```

### 运行分类

```bash
python classify.py
```

输出：

- `data/分类结果.json`
- `data/分类结果.md`

### 重新生成可读汇总

```bash
python generate_info.py
```

### 增量添加新关注

```bash
python add_new.py <mid>
```

### 预览并同步到 B 站

```bash
python sync_groups.py --dry-run
python sync_groups.py
```

## 推荐复核方式

这类分类工具最稳的用法通常是：

1. 先让规则跑完整体分类
2. 导出可读摘要
3. 让大模型标记可疑分类
4. 人工确认真正模糊的样本
5. 把稳定样本补回 `manual`

这样系统会越用越稳，而不是每次都从头返工。

## 项目结构

```text
├── fetch.py
├── classify.py
├── sync_groups.py
├── add_new.py
├── generate_info.py
├── SKILL.md
├── AGENTS.md
├── CLAUDE.md
├── RELEASE_CHECKLIST.md
├── data_example/
└── data/
```

## 隐私与安全

- `data/` 中包含 Cookie 和个人分类数据，应只保存在本地
- 仓库已按隐私型规则配置，避免把本地敏感数据提交到 Git
- 正式同步前一定先用 `--dry-run` 检查

## 风险提醒

- `sync_groups.py` 会重建你在 B 站上的自定义关注分组
- Cookie 会过期
- 大规模采集可能会触发 B 站限流，投稿分区可以后补
- 分组名不能包含 `/`

## 相关项目

- [bilibili-favorites](https://github.com/sunrisever/bilibili-favorites)：用于整理和重建 B 站收藏夹

## 开源协议

MIT
