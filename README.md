English | [简体中文](README_CN.md)

# Bilibili Follow

> Export your Bilibili follow list, let ChatGPT / Claude / Gemini / Codex or any frontier LLM help with grouping, then sync the result back to Bilibili follow groups.

This project is for people who follow a lot of Bilibili UP masters and want a workflow that is stronger than the built-in follow grouping experience. Instead of relying on a weak in-product heuristic, you first export structured follow data, then let a stronger general-purpose AI model help you review or refine the grouping plan, and finally sync the result back to Bilibili.

## What this project actually does

It builds a practical follow-management pipeline:

1. Fetch your followed UP masters and their public signals.
2. Classify them with editable local rules.
3. Export readable summaries for AI review or manual review.
4. Sync the final grouping result back to Bilibili follow groups.

So the core idea is not "the extension or script has its own built-in AI".
The real idea is:

- export data from Bilibili
- use a stronger external AI model if needed
- keep the final taxonomy under your own control
- sync the final result back

## Do I need an API key?

No, not for the recommended beginner workflow.

The easiest path is:

- run the local scripts to fetch and classify
- open the exported summary in ChatGPT web/app, Claude web/app, Gemini, Codex, Claude Code, OpenCode, or another LLM tool
- ask it to review suspicious items or suggest better category rules
- apply the final result locally and sync back to Bilibili

You only need an API key if you want to automate the AI-review step inside your own scripts.
That is an advanced mode, not the default requirement.

## Who this is for

This project is useful if you:

- follow hundreds or thousands of UP masters
- want categories like exam prep, AI, programming, math, news, lifestyle, or entertainment
- prefer a workflow you can inspect and improve over time
- want something stronger than Bilibili's default grouping experience

## Core ideas

- **Rule-first, AI-assisted**: rules stay auditable; AI is used to review edge cases, not to hide the logic.
- **Human-controlled taxonomy**: you decide the category system.
- **Safe sync**: dry-run before changing Bilibili groups.
- **Incremental maintenance**: new follows can be added later without rebuilding everything from scratch.

## Beginner workflow

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Copy the example data folder

```bash
cp -r data_example data
```

If you are on Windows PowerShell, you can simply copy the folder manually.

### 3. Fill in your Bilibili cookies

Edit `data/config.json` and provide:

- `sessdata`
- `bili_jct`
- `buvid3`
- `dedeuserid`

These are required because the script needs your own account context to read and later sync follow groups.

### 4. Define your category system

Edit `data/classify_rules.json`.

Important sections:

- `categories`: your category list
- `manual`: hard overrides for specific UP masters
- `keyword_rules`: keyword-based hints
- `zone_mapping`: mapping from Bilibili posting zones to your categories

A common setup is to create categories such as:

- Exam Prep
- AI
- Programming
- Math
- News
- Entertainment
- Others

## Recommended first run

### Step 1: Fetch your follow data

```bash
python fetch.py all
```

Optional commands:

```bash
python fetch.py zones
python fetch.py <mid>
```

Main output:

- `data/up主详细数据.json`

### Step 2: Run the local classifier

```bash
python classify.py
```

Main outputs:

- `data/分类结果.json`
- `data/分类结果.md`

### Step 3: Let a stronger AI review the result

This is the key step many beginners misunderstand.

You do **not** need to wire an API key into this repo.
Instead, you can simply:

1. Open `data/分类结果.md`
2. Paste or upload it to ChatGPT / Claude / Gemini / Codex / Claude Code / OpenCode
3. Ask questions like:
   - which accounts look suspiciously misclassified?
   - which manual overrides should be added?
   - how should I improve my keyword rules?
   - which categories are too broad or too fragmented?

Then you update `data/classify_rules.json` or `manual` overrides accordingly.

### Step 4: Preview the sync

```bash
python sync_groups.py --dry-run
```

You can also preview only selected categories:

```bash
python sync_groups.py --dry-run --category "Exam Prep"
```

### Step 5: Sync back to Bilibili

```bash
python sync_groups.py
```

## Typical maintenance workflow

After your first full run, the usual long-term workflow is:

1. add newly followed UP masters
2. run classification again
3. review edge cases with your preferred AI tool
4. dry-run sync
5. sync the final result

For incremental updates:

```bash
python add_new.py <mid>
```

## Files you should care about

| File | Purpose |
| --- | --- |
| `data/config.json` | local cookies and runtime config |
| `data/classify_rules.json` | your editable category system |
| `data/up主详细数据.json` | fetched follow data |
| `data/分类结果.json` | machine-readable result |
| `data/分类结果.md` | AI-friendly and human-friendly review file |
| `generate_info.py` | regenerate readable summaries |
| `sync_groups.py` | preview or apply follow-group sync |

## Why this is better than basic AI grouping inside the browser

Many tools claim "AI grouping", but their built-in grouping is often too weak because:

- the context window is too small
- the metadata is too shallow
- the taxonomy is opaque
- the result is hard to audit or improve

This project is different because it lets you:

- export richer structured data
- use whichever frontier model you think is best
- keep your rules editable
- repeat the workflow whenever your interests change

## Safety notes

- `sync_groups.py` changes your custom Bilibili follow groups, so always run `--dry-run` first.
- Cookies expire periodically and need refresh.
- Very large fetches may hit Bilibili throttling.
- Group names cannot contain `/`.

## Companion project

- [bilibili-favorites](https://github.com/sunrisever/bilibili-favorites): organize Bilibili favorites folders with a similar export -> review -> sync workflow

## AI coding assistant support

This repository includes:

- `SKILL.md`
- `AGENTS.md`
- `CLAUDE.md`

So it works well with Codex, Claude Code, OpenCode, OpenClaw, and other agent-based coding workflows.

## License

MIT
