English | [简体中文](README_CN.md)

# Bilibili Follow

> Export your Bilibili follow list, classify it locally, optionally let ChatGPT / Claude / Gemini / Codex review the difficult cases, then sync the final grouping plan back to Bilibili follow groups.

This project is for people who follow a lot of Bilibili creators and want something stronger than Bilibili's ordinary manual grouping workflow.

Important clarification:

- Bilibili follow groups do **not** provide a strong built-in AI grouping workflow.
- This repository does **not** rely on a built-in AI model inside the script.
- The real workflow is: export structured data -> run local rules -> optionally ask a stronger external model to review edge cases -> sync the final result back.

## What this project is

This is a follow-management pipeline:

1. Fetch followed creators and their public signals.
2. Classify them with editable local rules.
3. Export a human-readable summary.
4. Optionally let a frontier LLM review suspicious cases.
5. Sync the final grouping plan back to Bilibili follow groups.

## Do I need an API key?

No, not for the recommended workflow.

The intended beginner path is:

- run the local scripts
- open the exported Markdown summary
- send it to ChatGPT web/app, Claude web/app, Gemini, Codex, Claude Code, OpenCode, or another strong general-purpose model
- ask for review suggestions
- apply the final result locally and sync back

API integration is an advanced automation mode, not the default.

## Beginner quick start

### Step 1. Install dependencies

```bash
pip install -r requirements.txt
```

### Step 2. Prepare the data folder

Copy `data_example` to `data`.

### Step 3. Fill in Bilibili cookies

Edit `data/config.json` and fill:

- `sessdata`
- `bili_jct`
- `buvid3`
- `dedeuserid`

### Step 4. Run the first fetch

```bash
python fetch.py all
```

You should then see:

- `data/up主详细数据.json`

### Step 5. Run local classification

```bash
python classify.py
```

You should then see:

- `data/分类结果.json`
- `data/分类结果.md`

### Step 6. Review and sync

1. Open `data/分类结果.md`
2. Give it to your preferred model
3. Ask for suspicious items, overly broad categories, or suggested manual overrides
4. Update your local rules
5. Preview:

```bash
python sync_groups.py --dry-run
```

6. Sync:

```bash
python sync_groups.py
```

## Screenshot-style beginner walkthrough

### What you edit first

Open:

- `data/config.json`
- `data/classify_rules.json`

You mainly need:

- cookies in `config.json`
- category names in `classify_rules.json`

### What you run first

```bash
python fetch.py all
```

After that, imagine the first “result screen” as:

- a JSON file appears in `data/`
- it contains your followed creators
- nothing has been written back to Bilibili yet

### What you run second

```bash
python classify.py
```

Now you should get:

- a machine-readable result file
- a Markdown summary for human/AI review

### What you hand to AI

You do **not** need to build an API flow.
Just open or upload:

- `data/分类结果.md`

Recommended questions:

- Which creators are obviously in the wrong group?
- Which manual overrides should I add?
- Which categories are too broad?
- Which keyword rules need improvement?

### What you sync back

Only after your manual review and dry-run:

```bash
python sync_groups.py --dry-run
python sync_groups.py
```

That is the point where Bilibili groups are actually changed.

## Typical maintenance flow

After the first full run, the normal long-term workflow is:

1. fetch newly followed creators
2. classify again
3. review edge cases with your preferred AI tool
4. dry-run
5. sync

Incremental add:

```bash
python add_new.py <mid>
```

## Files that matter

| File | Purpose |
| --- | --- |
| `data/config.json` | local cookies and runtime config |
| `data/classify_rules.json` | your category system |
| `data/up主详细数据.json` | fetched creator data |
| `data/分类结果.json` | machine-readable result |
| `data/分类结果.md` | AI-friendly review file |
| `generate_info.py` | regenerate readable summaries |
| `sync_groups.py` | dry-run or real sync |

## Common misunderstandings

### “Does Bilibili already have good AI grouping for this?”

No. This project exists because the normal grouping experience is limited, and many users want a stronger workflow.

### “Does this repo come with a hidden powerful AI model?”

No. The strength comes from:

- your structured export
- your editable rules
- whichever strong external model you choose for review

### “Do I have to pay for APIs?”

No. Subscription-based web/app tools are the default path.

## Safety notes

- Always run `--dry-run` before real sync.
- Cookies expire and need refresh.
- Very large fetches may hit throttling.
- Group names cannot contain `/`.

## License

MIT
