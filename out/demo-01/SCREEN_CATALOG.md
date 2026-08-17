<!-- Generated from manifest.json by `reframe`. Do not edit: the next run overwrites this file. Record corrections in fixtures/<slug>.yaml instead. -->

# Screen catalogue — demo-01

- **Source:** `/private/tmp/claude-501/-Users-vimalkumaryadav-epic-reframe/2aef8729-d3c4-4279-9954-ebdd5c0e2f64/scratchpad/fake_app.mp4`
- **Duration:** 00:30 · 1920×1080 @ 30 fps
- **Frames sampled:** 30 · **kept:** 6 · **screens:** 6
- **Config hash:** `sha256:b955cf0f80c1d98bb9af55c9e2421b9a1c29e0066f3856ea3983664d35d5e0c2`
- **Classified against:** demoapp at commit `41b6eb3f` (5 entries)

## Screens

| # | ~time | Screen | Module | Bucket | Confidence | Key content |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 00:00 | Dashboard | Core | built | 0.57 ⚠️ | tabs: Summary, Activity, Alerts; Title bar over a tab strip, with a five-column grid below. |
| 2 | 00:03 | Dashboard | Core | built | 0.98 | tabs: Summary, Activity, Alerts; Title bar over a tab strip, with a five-column grid below. |
| 3 | 00:06 | Order Entry | Core | partial | 1.00 | tabs: Details, History, Notes, Audit; Title bar over a tab strip, with a five-column grid below. |
| 4 | 00:12 | Work Queue | Core | built | 1.00 | tabs: Open, Assigned, Closed; Title bar over a tab strip, with a five-column grid below. |
| 5 | 00:18 | Report Viewer | Reporting | new | 1.00 | tabs: Preview, Parameters; Title bar over a tab strip, with a five-column grid below. |
| 6 | 00:24 | Settings | — | new | 1.00 | tabs: General, Users, Integrations, Advanced; Title bar over a tab strip, with a five-column grid below. |

## Evidence

### s_000 · 00:00–00:02 · Dashboard

- Frame: `f_000000` (3 sampled)
- OCR title: `7` at 0.48
- Confidence: 0.57 (review) — framing=1.00, legibility=1.00, ocr_agreement=0.00
- Classified `built` via exact (1.00) → `Dashboard` at `/dashboard`

### s_001 · 00:03–00:05 · Dashboard

- Frame: `f_000003` (3 sampled)
- OCR title: `| Dashboard` at 0.85
- Confidence: 0.98 (accepted) — framing=1.00, legibility=0.94, ocr_agreement=1.00
- Classified `built` via exact (1.00) → `Dashboard` at `/dashboard`

### s_002 · 00:06–00:11 · Order Entry

- Frame: `f_000006` (6 sampled)
- OCR title: `| Order Entry` at 0.95
- Confidence: 1.00 (accepted) — framing=1.00, legibility=1.00, ocr_agreement=1.00
- Classified `partial` via exact (1.00) → `Order Entry` at `/orders`
- Components: `src/components/Core/OrderEntry/`

### s_003 · 00:12–00:17 · Work Queue

- Frame: `f_000012` (6 sampled)
- OCR title: `Work Queue` at 0.96
- Confidence: 1.00 (accepted) — framing=1.00, legibility=1.00, ocr_agreement=1.00
- Classified `built` via exact (1.00) → `Work Queue` at `/work-queue`

### s_004 · 00:18–00:23 · Report Viewer

- Frame: `f_000018` (6 sampled)
- OCR title: `Report Viewer` at 0.96
- Confidence: 1.00 (accepted) — framing=1.00, legibility=1.00, ocr_agreement=1.00
- Classified `new` via fuzzy (0.96) → `Report Viewr` at `/activity/report-viewr`
- Note: reachable but falls through to a placeholder page

### s_005 · 00:24–00:29 · Settings

- Frame: `f_000024` (6 sampled)
- OCR title: `| Settings` at 0.95
- Confidence: 1.00 (accepted) — framing=1.00, legibility=1.00, ocr_agreement=1.00
- Classified `new` via none
- Closest inventory entry: `Report Viewr` at 0.30 (below threshold — not treated as a match)
- Note: closest inventory entry is 'Report Viewr' at 0.30, below classify.fuzzy_threshold — treated as new, but check the alias table before building it

