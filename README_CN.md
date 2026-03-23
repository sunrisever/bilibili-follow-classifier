[English](README.md) | 简体中文

# Bilibili Follow

> 导出 B 站关注列表，交给 ChatGPT / Claude / Gemini / Codex 等通用大模型辅助分组，再把结果同步回 B 站关注分组。

这个项目适合关注了很多 B 站 UP 主、又觉得 B 站自带分组体验不够强的人。它的核心不是“脚本内置了一个很厉害的 AI”，而是：

- 先从 B 站导出结构化关注数据
- 再交给更强的通用大模型辅助判断
- 最后仍然由你掌控分类体系
- 再把最终结果同步回 B 站

## 这个项目到底是干什么的

它把“整理关注列表”拆成一条清晰工作流：

1. 采集你关注的 UP 主及其公开信号
2. 用本地可编辑规则做初步分类
3. 导出可读摘要，方便 AI 审阅或人工复核
4. 最后把结果同步回 B 站关注分组

所以它的真实原理不是“浏览器里随便点一下 AI 分类”。
它更像是：

- 导出数据
- 用更强的外部 AI 模型辅助判断
- 保留你自己的分类规则
- 最后再同步回去

## 要不要 API Key？

**默认不需要。**

对大多数用户来说，最推荐的用法是：

- 本地跑采集和分类脚本
- 把导出的摘要文件交给 ChatGPT 网页端 / App、Claude 网页端 / App、Gemini、Codex、Claude Code、OpenCode 等工具
- 让 AI 帮你标记可疑项、建议规则修改
- 最后你自己确认并同步回 B 站

只有当你想把“AI 审阅”这一步也完全脚本化时，才需要自己接 API。
那属于高级自动化玩法，不是默认要求。

## 适合谁用

如果你有下面这些需求，这个项目就很适合：

- 关注了几百上千个 UP 主
- 想把学习、考研、AI、编程、数学、资讯、娱乐等内容分开管理
- 希望分类体系是自己能看懂、能修改、能长期维护的
- 希望效果明显强于 B 站默认的关注分组体验

## 设计思路

- **规则优先，AI 辅助**：规则是透明、可维护的；AI 主要帮助处理边界样本
- **分类体系掌握在你自己手里**：不是黑盒自动分完就结束
- **同步前先预览**：先 `--dry-run`，再真正写回 B 站
- **支持长期维护**：新关注可以增量加入，不必每次全部重做

## 小白推荐工作流

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 复制示例数据目录

```bash
cp -r data_example data
```

如果你在 Windows PowerShell 里，也可以直接手动复制文件夹。

### 3. 填好 B 站 Cookie

编辑 `data/config.json`，填写：

- `sessdata`
- `bili_jct`
- `buvid3`
- `dedeuserid`

这些字段的作用是让脚本能以你的账号身份读取和同步关注分组。

### 4. 定义你的分类体系

编辑 `data/classify_rules.json`。

里面最重要的是：

- `categories`：分类列表
- `manual`：你想手工指定的 UP 主分类
- `keyword_rules`：关键词提示规则
- `zone_mapping`：B 站投稿分区到你的分类映射

一个常见的分类体系可以是：

- 考研
- AI
- 编程
- 数学
- 资讯
- 娱乐
- 其他

## 第一次使用怎么跑

### Step 1：采集关注数据

```bash
python fetch.py all
```

可选：

```bash
python fetch.py zones
python fetch.py <mid>
```

主要输出：

- `data/up主详细数据.json`

### Step 2：运行本地分类器

```bash
python classify.py
```

主要输出：

- `data/分类结果.json`
- `data/分类结果.md`

### Step 3：让更强的 AI 帮你复核

这一步正是最容易被误解的地方。

你**不需要**在这个仓库里强绑某个 API Key。
更推荐的做法是：

1. 打开 `data/分类结果.md`
2. 把它交给 ChatGPT / Claude / Gemini / Codex / Claude Code / OpenCode
3. 问它：
   - 哪些账号明显分错了？
   - 哪些应该加入 `manual`？
   - 哪些关键词规则要调整？
   - 哪些分类太宽，哪些分类太碎？

然后你再去改 `data/classify_rules.json` 或 `manual` 覆盖。

### Step 4：预览同步

```bash
python sync_groups.py --dry-run
```

如果只想看部分分类，也可以：

```bash
python sync_groups.py --dry-run --category "考研"
```

### Step 5：真正同步回 B 站

```bash
python sync_groups.py
```

## 日常维护怎么做

第一次全量整理后，后面的长期维护通常是：

1. 把新关注的 UP 主加进来
2. 再跑一次分类
3. 用你喜欢的 AI 工具复核疑难项
4. 先 `--dry-run`
5. 再执行同步

增量添加新关注：

```bash
python add_new.py <mid>
```

## 你真正需要关心的文件

| 文件 | 作用 |
| --- | --- |
| `data/config.json` | 本地 Cookie 和运行配置 |
| `data/classify_rules.json` | 你自己的分类体系 |
| `data/up主详细数据.json` | 采集下来的关注数据 |
| `data/分类结果.json` | 机器可读结果 |
| `data/分类结果.md` | 给人看、给 AI 看都方便的摘要 |
| `generate_info.py` | 重新生成可读汇总 |
| `sync_groups.py` | 预览或执行同步 |

## 为什么它比浏览器里那种“内置 AI 分组”更强

很多工具也会说自己有 AI 分类，但往往不够强，原因通常是：

- 上下文太短
- 元数据太浅
- 分类逻辑是黑盒
- 分完之后很难持续优化

这个项目不一样的地方在于：

- 你可以导出更丰富的结构化数据
- 你可以自己选择最强的通用大模型
- 你的分类规则始终可编辑
- 你的工作流可以反复复用，而不是一次性结果

## 风险提醒

- `sync_groups.py` 会修改你在 B 站上的自定义关注分组，所以一定先 `--dry-run`
- Cookie 会过期，需要定期更新
- 大规模采集可能触发 B 站限流
- 分组名不能包含 `/`

## 配套项目

- [bilibili-favorites](https://github.com/sunrisever/bilibili-favorites)：用于整理 B 站收藏夹，思路和这个项目是一套

## AI 编程助手支持

仓库内已包含：

- `SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`

所以它天然适合和 Codex、Claude Code、OpenCode、OpenClaw 这类 agent 工作流一起用。

## 开源协议

MIT
