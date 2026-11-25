# abstain-dti: project notes for AI agents

## Weekly deliverables: Notion to GitHub sync

Starting with W07 (2026-11-21), each track (ML, Agent, Curation) reports its weekly results (산출물) on the Notion progress page:

- Page: 📍 abstain-dti 진행 현황, https://app.notion.com/p/40c1dab2a09381d69fe6e0f21934a7c7
- Where: the `WXX` toggle under 주간 회의록. Each track has a cell with 진행된것 and TODO.

Notion is the source. Only two kinds of items get synced to GitHub:

1. **Decisions** go to `docs/weekly/WXX.md` under `## 결정`, using the template in `docs/weekly/README.md`. Write one line per decision and say which track it belongs to.
2. **Code, scripts and prompts** go to the track that owns them:
   - ML: `track_ml-baselines/`
   - Agent: `track_agent/`, with prompts in `track_agent/prompts/`
   - Curation: `track_curation/`

Everything else stays in Notion only: discussion notes, reading links, slides, TODO lists and progress notes.

How to sync a week:

- Read the `WXX` toggle (through a Notion connector if your agent has one, otherwise ask the user to paste it) and list which items are decisions and which are code, scripts or prompts. Confirm that list with the user before writing anything.
- If a code item exists only as a link (Colab, Drive, a personal machine), ask for the file. Do not reconstruct it.
- Follow the git rules: work on a `wXX/...` branch and leave commits and pushes to the user unless they ask you to do them.
- Once the items are on GitHub, add what landed to the "GitHub 반영" column for that week in the 주차별 진행 계획 table on the Notion page.
