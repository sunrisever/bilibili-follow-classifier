English | [简体中文](README_CN.md)

# Bilibili Follow Classifier

> Auto-classify Bilibili followed UP masters and sync them to follow groups | B站关注 UP 主自动分类与分组同步工具

Organize a large Bilibili follow list into practical groups such as exam prep, AI, programming, math, news, or entertainment. This project fetches profile and content signals for each followed UP master, scores them with your rule set, and syncs the final categories back to Bilibili follow groups.

## Why this project

If you follow hundreds or thousands of UP masters, the default Bilibili follow list quickly becomes noisy. This repo turns your follow list into a maintainable system:

- fetch structured signals from followed accounts
- classify them with editable keyword and zone rules
- review edge cases with an LLM or by hand
- sync the final result back to Bilibili groups

## Highlights

- Full follow-list fetch with posting zones, tags, series, collections, and profile metadata
- Rule-based classification that stays editable and auditable
- Manual override support for stable, high-confidence mapping
- Incremental add flow for newly followed UP masters
- Dry-run sync before destructive updates
- AI coding assistant support via `SKILL.md`, `AGENTS.md`, and `CLAUDE.md`

## Quick Links

- [SKILL.md](SKILL.md)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md)

## Workflow at a glance

1. Copy `data_example/` to `data/`
2. Fill in your Bilibili cookies in `data/config.json`
3. Edit `data/classify_rules.json` to define your categories
4. Run `python fetch.py all`
5. Run `python classify.py`
6. Review doubtful cases manually or with an LLM
7. Run `python sync_groups.py --dry-run`
8. If the preview looks right, run `python sync_groups.py`

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Copy the example data directory first:

```bash
cp -r data_example data
```

Then edit `data/config.json`:

```json
{
  "bilibili": {
    "sessdata": "YOUR_SESSDATA",
    "bili_jct": "YOUR_bili_jct",
    "buvid3": "YOUR_buvid3",
    "dedeuserid": "YOUR_UID"
  }
}
```

How to get the cookies:

- Log in to Bilibili
- Open Developer Tools
- Go to `Application -> Cookies`
- Copy the required fields

## Classification rules

The core rule file is `data/classify_rules.json`.

- `categories`: category list, where the last item is typically the fallback category
- `manual`: hard overrides for specific UP masters
- `keyword_rules`: weighted keyword map per category
- `zone_mapping`: Bilibili posting zone to category mapping

The project is intentionally rule-first: you can audit and evolve your taxonomy over time instead of locking yourself into an opaque model output.

## Main commands

### Fetch all follows

```bash
python fetch.py all
```

Optional:

```bash
python fetch.py zones
python fetch.py <mid>
```

### Run classification

```bash
python classify.py
```

Outputs:

- `data/分类结果.json`
- `data/分类结果.md`

### Regenerate readable summaries

```bash
python generate_info.py
```

### Add newly followed accounts

```bash
python add_new.py <mid>
```

### Preview and sync to Bilibili

```bash
python sync_groups.py --dry-run
python sync_groups.py
```

## Recommended review loop

The best results usually come from this layered process:

1. let the rules classify everything
2. export readable summaries
3. ask an LLM to flag suspicious assignments
4. manually confirm the truly ambiguous accounts
5. move stable cases into `manual` overrides

That keeps the system improving over time instead of repeating the same corrections.

## Project structure

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

## Privacy and safety

- `data/` contains personal cookies and classification data and should stay local
- The repository is set up to keep local/private data out of Git
- Always review sync actions with `--dry-run` before changing Bilibili groups

## Important cautions

- `sync_groups.py` is destructive for custom Bilibili follow groups
- Cookies expire periodically
- Large-scale fetches may hit Bilibili throttling; use zone backfill later if needed
- Group names cannot contain `/`

## Related projects

- [bilibili-favorites-classifier](https://github.com/sunrisever/bilibili-favorites-classifier): classify and rebuild Bilibili favorites folders

## License

MIT
