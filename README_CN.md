[English](README.md) | 简体中文

# Bilibili Follow

> 导出 B 站关注列表，先在本地做规则分类，再把疑难项交给 ChatGPT / Claude / Gemini / Codex 等强模型辅助复核，最后把结果同步回 B 站关注分组。

这个项目适合关注了很多 B 站 UP 主、并且已经觉得平台原生分组方式不够用的人。

这里先把原理纠正清楚：

- B 站关注分组本身并没有一套成熟、强力、可持续优化的 AI 分类工作流。
- 这个仓库也不是“脚本里内置一个 AI 分类器”。
- 它真正做的是：导出结构化数据 -> 用本地规则先分 -> 再把疑难项交给外部强模型辅助判断 -> 最后把结果写回 B 站。

## 这个项目到底是干什么的

它是一条“关注列表整理流水线”，不是一次性黑盒分类器。

完整链路是：

1. 抓取你关注的 UP 主及其公开信号
2. 用你自己的本地规则做初分
3. 导出一份人能看、AI 也容易看的摘要
4. 可选地让强模型帮你复核边界样本
5. 最终再把你确认过的分组同步回 B 站

## 要不要 API Key？

默认不需要。

推荐的小白路径是：

- 本地跑采集和分类脚本
- 打开导出的 Markdown 摘要
- 交给 ChatGPT 网页端 / App、Claude 网页端 / App、Gemini、Codex、Claude Code、OpenCode 等工具
- 让它帮你指出疑难项、补人工覆盖、优化规则
- 最后你自己确认，再同步回 B 站

也就是说，这个项目默认是“订阅态工具友好”，不是 API-first。

## 零基础最快上手

如果你什么都不想研究，只想先跑通一次，按下面 6 步走。

### Step 1：安装依赖

```bash
pip install -r requirements.txt
```

### Step 2：准备数据目录

把 `data_example` 复制成 `data`。

### Step 3：填 B 站 Cookie

打开 `data/config.json`，填这 4 项：

- `sessdata`
- `bili_jct`
- `buvid3`
- `dedeuserid`

### Step 4：第一次采集

```bash
python fetch.py all
```

跑完后你应该能看到：

- `data/up主详细数据.json`

这一步只是在本地采集数据，还不会改你的 B 站分组。

### Step 5：第一次分类

```bash
python classify.py
```

跑完后你应该能看到：

- `data/分类结果.json`
- `data/分类结果.md`

### Step 6：复核并同步

1. 打开 `data/分类结果.md`
2. 把它交给 ChatGPT / Claude / Gemini / Codex
3. 问它哪些账号可能分错
4. 回来修改 `data/classify_rules.json`
5. 先预览：

```bash
python sync_groups.py --dry-run
```

6. 确认没问题后再同步：

```bash
python sync_groups.py
```

## 像看截图一样的使用流程

这一节专门按“小白照着点、照着看文件”的方式写。

### 第一步，你需要打开什么文件

先打开这两个：

- `data/config.json`
- `data/classify_rules.json`

你主要会碰到的内容只有两类：

- `config.json` 里的 Cookie
- `classify_rules.json` 里的分类名称和人工覆盖

### 第二步，你先跑哪条命令

```bash
python fetch.py all
```

跑完以后，你可以把它理解成“第一张截图里应该看到的是”：

- `data/` 目录里多了一个 `up主详细数据.json`
- 里面是你关注的 UP 主数据
- 这时还没有任何写回 B 站的动作

### 第三步，你再跑哪条命令

```bash
python classify.py
```

这一步结束后，你应该看到：

- 一份机器可读结果：`data/分类结果.json`
- 一份适合看和适合交给 AI 的摘要：`data/分类结果.md`

### 第四步，你把什么交给 AI

不是整个仓库，不是 API，不是 Cookie。  
你真正要交出去的是：

- `data/分类结果.md`

你可以直接问：

- 哪些 UP 主明显分错了？
- 哪些应该加入 `manual`？
- 哪些分类太宽泛？
- 哪些关键词规则需要补？

### 第五步，什么时候才会改动 B 站

只有这一步才会真正动你的关注分组：

```bash
python sync_groups.py --dry-run
python sync_groups.py
```

也就是说，前面的采集、分类、复核，都只是本地工作流。

## 适合谁用

如果你符合这些情况，这个项目就很适合：

- 关注了几百上千个 UP 主
- 想按学习、考研、AI、编程、数学、资讯、娱乐等维度管理
- 不想再靠手工一点点拖分组
- 想要一个能持续迭代的工作流，而不是一次性的“AI 分完就完”

## 日常维护怎么做

第一次全量整理之后，后面正常是这样维护：

1. 采集新关注
2. 再跑分类
3. 用你喜欢的 AI 工具复核边界样本
4. 先 `--dry-run`
5. 再同步

增量添加：

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

## 常见误解

### “B 站本身不是已经能智能分组了吗？”

不是这个意思。  
这个项目解决的是“平台原生分组不够强、不够细、不够可维护”的问题。

### “这个仓库是不是自带一个很厉害的 AI 分类器？”

也不是。  
真正的强度来自：

- 你导出的结构化数据
- 你自己的可编辑规则
- 你选用的外部强模型

### “是不是必须走 API 才能用？”

不是。  
默认推荐的就是订阅态网页端 / App / agent 工具的用法。

## 风险提醒

- 真正同步前一定先 `--dry-run`
- Cookie 会过期，要定期更新
- 大规模采集可能触发风控
- 分组名不能包含 `/`

## 开源协议

MIT
