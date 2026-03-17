# Release Checklist

## 1. Source Of Truth
- 以当前桌面仓库作为主源，不要把 `~/.claude/skills/` 或 `~/.agents/skills/` 副本当主源。
- 如果这是 skill 项目，发布前要先把最新源码/文档同步到本地 skill 副本。

## 2. Privacy Gate
- 严禁把真实账号、Cookie、API Key、Session、个人导出数据、聊天记录、浏览记录直接提交到仓库。
- 严禁把老师姓名、学号、手机号、邮箱、订单信息、真实截图中的私人内容放进公开 README / assets / demo。
- 真实本地数据统一放进 `local/`、`private/`、`secrets/` 或其他被 `.gitignore` 覆盖的目录。
- 仓库里只保留脱敏样例，例如 `.env.example`、`data_example/`、示例 JSON。

## 3. Repo Hygiene
- 检查 `.gitignore` 是否覆盖 `.env`、`local/`、`private/`、`secrets/`、`exports/`、`artifacts/`、缓存、数据库、cookie/session 文件。
- 双语公开仓库保持 `README.md` / `README_CN.md` 成对更新。
- `AGENTS.md` 与 `CLAUDE.md` 保持一致。
- skill 项目根目录应有 `SKILL.md`。

## 4. Validation
- 运行该项目对应的最小可用验证，不要只改文档不测。
- 发布前至少检查一次 `git status` 与 `git diff --stat`。
- 如果新增了截图或示意图，逐张确认没有私人信息。

## 5. Sync Order
1. 本地副本同步
2. GitHub commit / push
3. 若为公开 skill 项目，再同步到 `skills.pub`

## 6. skills.pub
- 默认走 memory 里记录的 API 提交方式，不要先用 Playwright。
