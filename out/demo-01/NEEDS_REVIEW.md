<!-- Generated from manifest.json by `reframe`. Do not edit: the next run overwrites this file. Record corrections in fixtures/<slug>.yaml instead. -->

# Needs review — demo-01

- **Source:** `/private/tmp/claude-501/-Users-vimalkumaryadav-epic-reframe/2aef8729-d3c4-4279-9954-ebdd5c0e2f64/scratchpad/fake_app.mp4`
- **Duration:** 00:30 · 1920×1080 @ 30 fps
- **Frames sampled:** 30 · **kept:** 6 · **screens:** 6
- **Config hash:** `sha256:b955cf0f80c1d98bb9af55c9e2421b9a1c29e0066f3856ea3983664d35d5e0c2`
- **Classified against:** demoapp at commit `41b6eb3f` (5 entries)

3 item(s), ordered by timestamp so you can watch them in one pass. Each says what the pipeline could not settle and what would resolve it.

| ~time | span | what to check |
| --- | --- | --- |
| 00:00–00:02 | `low-confidence` (stage 06) | 'Dashboard' — confidence 0.57 is below confidence.accept_threshold 0.75 |
| 00:00–00:02 | `confirm-partial` (stage 07) | 'Dashboard' is built at /dashboard; the footage shows tabs [Summary, Activity, Alerts]. If the component is missing any of them, add 'Dashboard' to classify.partial_labels to move it into the build queue |
| 00:12–00:17 | `confirm-partial` (stage 07) | 'Work Queue' is built at /work-queue; the footage shows tabs [Open, Assigned, Closed]. If the component is missing any of them, add 'Work Queue' to classify.partial_labels to move it into the build queue |

## Frames to open

- 00:00 `06:low-confidence`: `f_000000`
- 00:00 `07:confirm-partial`: `f_000000`
- 00:12 `07:confirm-partial`: `f_000012`

