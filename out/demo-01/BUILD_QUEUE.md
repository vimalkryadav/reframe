<!-- Generated from manifest.json by `reframe`. Do not edit: the next run overwrites this file. Record corrections in fixtures/<slug>.yaml instead. -->

# Build queue — demo-01

- **Source:** `/private/tmp/claude-501/-Users-vimalkumaryadav-epic-reframe/2aef8729-d3c4-4279-9954-ebdd5c0e2f64/scratchpad/fake_app.mp4`
- **Duration:** 00:30 · 1920×1080 @ 30 fps
- **Frames sampled:** 30 · **kept:** 6 · **screens:** 6
- **Config hash:** `sha256:b955cf0f80c1d98bb9af55c9e2421b9a1c29e0066f3856ea3983664d35d5e0c2`
- **Classified against:** demoapp at commit `41b6eb3f` (5 entries)

3 screen(s) to build, grouped by module. `partial` first: an existing component that needs extending is usually the cheapest win.

## partial (1)

### Core

- **Order Entry** — 00:06, frame `f_000006`
  - Tabs seen: Details, History, Notes, Audit
  - Structure: Title bar over a tab strip, with a five-column grid below.
  - Existing route: `/orders`
  - Existing components: `src/components/Core/OrderEntry/`

## new (2)

### Reporting

- **Report Viewer** — 00:18, frame `f_000018`
  - Tabs seen: Preview, Parameters
  - Structure: Title bar over a tab strip, with a five-column grid below.
  - Existing route: `/activity/report-viewr`
  - reachable but falls through to a placeholder page

### Unassigned

- **Settings** — 00:24, frame `f_000024`
  - Tabs seen: General, Users, Integrations, Advanced
  - Structure: Title bar over a tab strip, with a five-column grid below.
  - ⚠️ Resembles `Report Viewr` at 0.30 — confirm it is genuinely new before building
  - closest inventory entry is 'Report Viewr' at 0.30, below classify.fuzzy_threshold — treated as new, but check the alias table before building it

