# Architecture

How Reframe is put together, stage by stage. For *why* each choice was made, see
[`DECISIONS.md`](DECISIONS.md) — this document describes the design; that one
defends it.

---

## Contents

- [Operating constraints](#operating-constraints)
- [Data flow](#data-flow)
- [Module layout](#module-layout)
- [On-disk layout](#on-disk-layout)
- [Stage 00 — Probe](#stage-00--probe)
- [Stage 01 — Sample](#stage-01--sample)
- [Stage 02 — Rectify](#stage-02--rectify)
- [Stage 03 — Clean](#stage-03--clean)
- [Stage 04 — Dedupe](#stage-04--dedupe)
- [Stage 05 — OCR](#stage-05--ocr)
- [Stage 06 — Identify](#stage-06--identify)
- [Stage 07 — Classify](#stage-07--classify)
- [Stage 08 — Emit](#stage-08--emit)
- [Manifest schema](#manifest-schema)
- [Config reference](#config-reference)
- [Determinism rules](#determinism-rules)
- [Fixtures and verification](#fixtures-and-verification)
- [Working across videos](#working-across-videos)
- [Out of scope](#out-of-scope)

---

## Operating constraints

Every design decision traces to one of these. They are established facts about
this specific corpus, not assumptions.

| Constraint | Consequence |
| --- | --- |
| Recorded on a **phone pointed at a laptop screen** | Constant shake, perspective distortion, glare, moiré. Nearly every default carried over from native screen-capture is wrong. |
| **8 videos, ~15 min each** (~2 h total) | ~7,200 frames at 1 fps. Small enough to be thorough rather than clever about sampling. |
| **Fixed corpus** — re-recording is impossible | Quality must come from processing. There is no capture-side fix available. |
| **Framing varies** between videos and possibly within one | Screen-corner detection needs a fallback chain, not a single algorithm. |
| Videos **overlap already-built work** | The built/partial/new classifier is a primary output, not a bonus. |
| Human **validates after each video** | Tunables must live in config; corrections must be recorded as fixtures. |

---

## Data flow

```
  video file
      │
 [00] ├──► probe metadata ─────────────► videos/<slug>/config.yaml
      │                                   (all tunables live here)
 [01] ├──► sample @ fixed fps ──────────► frames/raw/f_NNNNNN__tXXmYYs.jpg
      │
 [02] ├──► detect screen quad + warp ───► frames/rect/     + rectify records
      │     (auto → smooth → manual → flag)
      │
 [03] ├──► align, normalise, deglare ───► frames/clean/
      │
 [04] ├──► band-hash vs LAST KEPT ──────► frames/kept/     ~dozens of screens
      │
 [05] ├──► OCR title + tab bands ───────► ocr records (raw text + per-word conf)
      │
 [06] ├──► montages ──► model ──────────► identity records + confidence
      │
 [07] ├──► match vs inventory.json ─────► classification records
      │
 [08] └──► render ──────────────────────► manifest.json
                                          SCREEN_CATALOG.md
                                          BUILD_QUEUE.md
                                          NEEDS_REVIEW.md
```

Each stage reads the manifest, adds its own records, and writes it back. Stages
are independently re-runnable: editing a dedupe threshold and re-running stage
04 does not re-sample or re-rectify.

---

## Module layout

```
src/reframe/
├── cli.py               entrypoint: init | run | stage | fixture | verify
├── config.py            VideoConfig (pydantic), defaults, layering, hashing
├── manifest.py          Manifest / FrameRecord / ScreenRecord models, load+save
├── confidence.py        multi-signal scoring; the accept/escalate decision
├── inventory.py         load inventory.json, alias + fuzzy matching
├── montage.py           title-band contact sheets with burnt-in labels
├── fixtures.py          ground-truth records, diffing, regression reporting
├── stages/
│   ├── s00_probe.py
│   ├── s01_sample.py
│   ├── s02_rectify.py
│   ├── s03_clean.py
│   ├── s04_dedupe.py
│   ├── s05_ocr.py
│   ├── s06_identify.py
│   ├── s07_classify.py
│   └── s08_emit.py
├── vision/
│   ├── quad.py          screen-corner detection + temporal smoothing
│   ├── warp.py          perspective transform to canonical size
│   ├── enhance.py       CLAHE, glare suppression, moiré reduction
│   └── hashing.py       perceptual hashing, band comparison
└── model/
    ├── client.py        Anthropic client, retry, batching
    ├── prompts.py       identification prompt (versioned)
    └── schema.py        structured-output schema for identity records
```

**Hard rule:** `vision/` and `model/` contain no pipeline logic, and `stages/`
contains no algorithms. Stages orchestrate; the other packages compute. This is
what keeps stages independently testable against fixture frames.

---

## On-disk layout

```
reframe/
├── configs/defaults.yaml          tool defaults — generic, committed
├── projects/<name>.yaml           project profile — GITIGNORED
├── videos/<slug>/
│   ├── config.yaml                per-video overrides — THE tuning surface
│   └── source.txt                 absolute path + sha256 of the source video
├── out/<slug>/
│   ├── manifest.json
│   ├── SCREEN_CATALOG.md
│   ├── BUILD_QUEUE.md
│   ├── NEEDS_REVIEW.md
│   ├── montages/titles-NN.jpg
│   └── frames/
│       ├── raw/                   gitignored — re-extractable
│       ├── rect/                  gitignored — re-extractable
│       ├── clean/                 gitignored — re-extractable
│       └── kept/                  COMMITTED — the deduped set
├── fixtures/<slug>.yaml           ground truth from validation rounds
└── inventory.json                 imported from rl_epic (gitignored)
```

Only `frames/kept/` is committed. Everything else is regenerable — which works
*only* because sampling is deterministic (see [Determinism rules](#determinism-rules)).

---

## Stage 00 — Probe

**Reads:** the video file · **Writes:** `videos/<slug>/config.yaml`, `source.txt`

Probes with `ffprobe` for resolution, frame rate, duration, codec and rotation
metadata, then generates a config file pre-filled with defaults derived from
those numbers.

Rotation matters and is easy to get wrong: phone video routinely carries a
rotation flag in metadata rather than baked into the pixels. Reading it wrong
gives you a sideways screen that corner-detection will still happily "find".
The probe records the flag explicitly; stage 01 leaves the rotation to ffmpeg's
own autorotate and then **verifies** the result against the probed display size,
because applying it a second time is what actually produces the sideways screen
(see [DEC-020](DECISIONS.md#dec-020--rotation-is-applied-by-ffmpeg-and-then-verified-not-re-applied)).

The generated config is the point of this stage. **Every threshold, crop,
corner override and alias in the entire pipeline lives in that file** — never as
a literal in Python. A validation round is a YAML edit.

---

## Stage 01 — Sample

**Reads:** the video file, config · **Writes:** `frames/raw/`, frame records

Samples at a **fixed frame rate** (default 1 fps). Scene detection is not used —
see [DEC-003](DECISIONS.md#dec-003--fixed-rate-sampling-not-scene-detection).

Filenames carry the source timestamp directly:

```
f_000842__t14m02s.jpg
  │         └── source timestamp, human-readable
  └── zero-padded sequential id, stable across re-runs
```

This is deliberate. The equivalent script in `rl_epic`
(`scripts/extract_frames.sh`) documents a `_frames.txt` index mapping frames to
timestamps, but the implementation only ever writes three comment lines — so in
scene mode the source timestamp is unrecoverable, and the documented
*"re-extract any screen full-res: `ffmpeg -ss <sec> …`"* workflow silently
breaks. Putting the timestamp in the filename makes that class of bug impossible.

**Config:** `sample.fps`, `sample.quality`, `sample.skip_ranges`, `sample.max_frames`

`max_frames` is a safety cap and, if hit, is recorded in the manifest and
surfaced as a warning — never a silent truncation.

---

## Stage 02 — Rectify

**Reads:** `frames/raw/`, config · **Writes:** `frames/rect/`, rectify records

Finds the four corners of the laptop screen in each frame and warps that
quadrilateral into a true rectangle at a fixed canonical size (default
1600 × 1000). Everything downstream — dedupe, OCR, model reading — improves
dramatically once frames are flat, aligned and identically sized.

**This is the highest-risk stage.** Every later stage assumes rectified input.

### Detection

The screen is a bright, high-contrast quadrilateral against a darker room.
Candidate approach, in order of preference:

1. Threshold on luminance to isolate the bright region.
2. Find contours; keep the largest 4-sided convex polygon with plausible aspect.
3. Refine corners sub-pixel.
4. Sanity-check against the previous frame's quad — a screen cannot jump.

### Fallback chain

Detection is not assumed to succeed. It degrades in steps:

| Situation | `rectify.method` | Behaviour |
| --- | --- | --- |
| Confident detection | `auto` | Use it. |
| Weak or noisy detection | `interpolated` | Interpolate from neighbouring frames within a smoothing window. |
| Detection fails across a span | `manual` | Use corners supplied in `config.yaml` for that time range. Human clicks four points once per stable segment. |
| Screen genuinely out of frame | `failed` | Mark `framing: partial` or `lost`, keep the frame, and escalate the span to `NEEDS_REVIEW.md`. |

The last row is the important one. **Never emit a confident crop of a cut-off
screen** — that produces a plausible-looking frame missing a column, which is
exactly the kind of silent error the whole tool exists to avoid.

### Temporal smoothing

Corners are detected per frame, then smoothed across a window (default 9 frames,
median) before warping. Per-frame detection alone produces visible wobble;
solving once per video fails when framing drifts. Smoothing is the middle path
and it is why `interpolated` exists as a distinct method.

**Config:** `rectify.canonical_size`, `rectify.smooth_window`,
`rectify.min_quad_confidence`, `rectify.manual_corners[]`, `rectify.aspect_bounds`

---

## Stage 03 — Clean

**Reads:** `frames/rect/` · **Writes:** `frames/clean/`

Applied to the rectified copy only; `frames/rect/` is kept untouched because
aggressive cleaning trades away exactly the fine detail that makes small labels
readable.

- **Sub-pixel alignment** — cancels residual jitter that survived rectification.
- **Local contrast normalisation** (CLAHE) — screen brightness is uneven across
  the frame when photographed at an angle; global normalisation makes one side
  worse.
- **Glare suppression** — bounded; a blown-out highlight has no recoverable
  detail and pretending otherwise invents pixels.
- **Moiré reduction** — mild low-pass. Off by default; enable per video only if
  the interference pattern is actually harming OCR.

Every step is individually switchable in config, because the right combination
will differ per video and is discovered during validation.

**Config:** `clean.align`, `clean.clahe`, `clean.deglare`, `clean.moire`

---

## Stage 04 — Dedupe

**Reads:** `frames/clean/`, config · **Writes:** `frames/kept/`, dedupe records

Reduces ~900 frames per video to a few dozen distinct screens.

### Why the inherited method inverts

`rl_epic`'s `CLAUDE.md` specifies: greyscale, crop the taskbar, resize to ~320px,
`GaussianBlur(1.2)`, then keep a frame when **>5.5% of pixels differ from the
last kept frame**. That works on a clean screen recording.

On handheld footage it **inverts**: hand shake alone displaces the whole image
by more than that threshold, so *nothing* registers as a duplicate and every
frame survives. The stage would return 900 "distinct screens" per video.

### What replaces it

Two changes:

1. **Rectification (stage 02) removes most of the false movement** before this
   stage ever runs. This is the larger half of the fix.
2. **Compare the title and tab band specifically**, not the whole frame. That
   band is what actually identifies a screen. Perceptual hash (dHash/pHash) over
   the band is the primary signal; a full-frame comparison is secondary, used to
   catch dialogs opening and scroll position changing within the same screen.

### One rule carried over unchanged

**Compare against the last kept frame, not the previous frame.** Comparing
against the previous frame collapses slow scrolls to nothing, because each
individual step is below threshold. This mistake is already recorded in
`rl_epic`'s RL_EPIC loop; it is not re-learnable cheaply.

**Config:** `dedupe.band_rect`, `dedupe.hash_distance`, `dedupe.full_frame_weight`,
`dedupe.min_gap_frames`

---

## Stage 05 — OCR

**Reads:** `frames/kept/` · **Writes:** OCR records

Runs OCR over the chrome regions only — title bar, workspace tab strip, activity
name — storing raw text with per-word confidence.

**On this footage OCR is a hint, not a source of truth.** It feeds the model in
stage 06 and cross-checks the model's answer in `confidence.py`; it never
decides a screen's identity alone. `rl_epic`'s existing catalogue already marks
phone-of-monitor reads with `(?)` for exactly this reason.

**Data grids are never OCR'd.** See [Out of scope](#out-of-scope).

**Config:** `ocr.regions[]`, `ocr.region_rects{}`, `ocr.engine`, `ocr.min_word_confidence`, `ocr.psm`

---

## Stage 06 — Identify

**Reads:** `frames/kept/`, OCR records · **Writes:** identity records, confidence

### Montages

Crops the title + tab band of every kept frame and stacks ~20 per sheet with a
burnt-in `frame-id · timestamp` label. Reading nine montages beats reading 196
full frames — an economy already proven in the `rl_epic` workflow, and it also
cuts model cost by an order of magnitude.

Full frames are sent only for screens the montage pass could not resolve.

### The model call

Montages plus OCR hints go to the model, which returns structured output per
screen: name, module, visible tabs, whether a dialog is open, and a short
description of structure (never of values, never of colour).

### Confidence

Computed in `confidence.py` from **independent signals agreeing** — not from the
model rating its own work, which is not a measurement.

| Signal | What it asks |
| --- | --- |
| OCR agreement | Does the model's name match the OCR'd title string? |
| Cross-frame consistency | Do repeat sightings of the same screen get the same name? |
| Framing quality | Did stage 02 flag this span as `partial`/`lost`/`manual`? |
| Band legibility | Contrast, blur and glare metrics over the title band. |
| Inventory match | Does the name resolve to a known activity (stage 07 feeds back)? |

Screens scoring below `confidence.accept_threshold` are **not guessed**. They
are written to `NEEDS_REVIEW.md` with their timestamp, and their identity record
is marked `verdict: review`.

Expect this list to be long on video 1. That is the tool working, not failing.

**Config:** `identify.montage_rows`, `identify.model`, `identify.prompt_version`,
`confidence.accept_threshold`, `confidence.weights`

---

## Stage 07 — Classify

**Reads:** identity records, `inventory.json` · **Writes:** classification records

Matches each identified screen against the inventory exported by the consuming
project and sorts it into one of four buckets. This is the stage that turns a
catalogue into a work plan.

**The inventory is refreshed before this stage runs, every time.** Because the
loop is *process video N → build those screens → process video N+1*, a stale
inventory would report screens as `new` that were finished last week. Reframe
runs the project's `inventory_cmd`, compares `generated_from.commit` against the
project's `HEAD`, and **aborts on a mismatch** rather than classifying against an
old snapshot ([DEC-018](DECISIONS.md#dec-018--the-inventory-is-regenerated-per-run-and-staleness-is-a-hard-error)).
The commit used is recorded in the manifest.

| Bucket | Meaning | Action |
| --- | --- | --- |
| `built` | Name resolves to a live route | Regression-check only |
| `partial` | Route exists, but the video shows tabs/columns/dialogs the component lacks | Targeted extension — usually the cheapest wins |
| `new` | No route, **or** explicitly `disabled: true` in the menu | Full build |
| `other` | Belongs to a module outside current scope | Catalogue, don't build |

The `disabled: true` distinction is preserved deliberately: it means *known and
deliberately unbuilt*, which is different information from *never heard of*.

Matching is exact-label first, then alias table, then bounded fuzzy match with
the score recorded. A fuzzy match below threshold produces `new` **with a
`possible_match` note** rather than silently claiming the screen is unbuilt.

See [`CONTRACT.md`](CONTRACT.md) for the inventory schema and matching rules.

**Config:** `classify.fuzzy_threshold`, `classify.near_miss_margin`, `classify.aliases{}`, `classify.modules_in_scope[]`, `classify.partial_labels[]` (see [DEC-023](DECISIONS.md#dec-023--partial-is-a-humans-answer-recorded-in-the-project-profile))

---

## Stage 08 — Emit

**Reads:** the manifest · **Writes:** the four output files

`manifest.json` is the join key for everything. The three Markdown files are
**generated from it and never hand-edited**, so a re-run cannot drift from the
data. Corrections go into `fixtures/<slug>.yaml`, not into the Markdown.

- **`SCREEN_CATALOG.md`** — every distinct screen, in the shape `rl_epic` already
  uses in `docs/reference/full_dfs/SCREEN_CATALOG.md`: `# | ~sec | Screen |
  Module | Key content`. Consistency with the existing format is intentional.
- **`BUILD_QUEUE.md`** — `new` and `partial` screens only, grouped by module,
  each with its representative frame and timestamp.
- **`NEEDS_REVIEW.md`** — the escalation list: every low-confidence screen and
  every flagged framing span, with timestamps, ordered by time so you can watch
  them in one pass.

---

## Manifest schema

```jsonc
{
  "schema_version": 1,
  "reframe_version": "0.1.0",
  "config_hash": "sha256:…",          // hash of the fully-resolved config
  "video": {
    "slug": "radiant-01",
    "source_path": "/Users/…/IMG_2601.MOV",
    "sha256": "…",
    "duration_s": 903.4,
    "width": 1920, "height": 1080,
    "fps": 30.0,
    "rotation": 90,
    "codec": "hevc"
  },

  // Which stages have run, and the per-config-section hashes each one consumed.
  // Together they make stale output detectable per stage: editing
  // `dedupe.hash_distance` marks 04 onwards stale and leaves 01–03 alone.
  "stages_completed": ["00", "01", "02", "03", "04", "05", "06", "07", "08"],
  "stage_inputs": {
    "04": {"rectify": "04b400b357f9579b", "clean": "c89cce023ad4413f", "dedupe": "de450809d0561cef"}
  },

  // Structured, and owned by the stage that raised it, so a re-running stage can
  // replace its own warnings without duplicating them or erasing another's.
  "warnings": [
    {"stage": "01", "message": "sample.max_frames cap of 900 hit …", "t_ms_start": 900000, "t_ms_end": 903400}
  ],

  // The escalation list stage 08 renders into NEEDS_REVIEW.md. `reason` is
  // namespaced by stage so a re-run can withdraw its own escalations.
  "review_spans": [
    {
      "t_ms_start": 838000, "t_ms_end": 851000,
      "reason": "06:low-confidence",
      "detail": "'Bed Control' — confidence 0.62 is below confidence.accept_threshold 0.75",
      "frame_ids": ["f_000842"]
    }
  ],

  // Which snapshot of the consuming project the buckets were true against.
  "inventory": {
    "project": "example-app",
    "commit": "9a0a4ad9",
    "path": "/…/inventory.json",
    "entry_count": 146
  },

  "frames": [
    {
      "id": "f_000842",
      "t_ms": 842000,
      // The raw sample. The rectified, cleaned and kept copies share this
      // basename and are derived, not stored, so four paths cannot disagree.
      "path": "frames/raw/f_000842__t14m02s.jpg",
      "rectify": {
        "method": "auto",              // auto | interpolated | manual | failed
        "corners": [[x,y],[x,y],[x,y],[x,y]],
        "quad_confidence": 0.87,
        "framing": "full"              // full | partial | lost
      },
      "dedupe": {
        // "<cols>x<rows>:<hex>" — the grid is part of the hash, because two
        // hashes taken at different shapes are not comparable (DEC-021).
        "band_hash": "32x4:…",
        // The combined score: band distance plus the full-frame distance weighted
        // by dedupe.full_frame_weight. Fractional because the weight is, and
        // rounding would hide why a frame sat just under threshold.
        "distance_from_last_kept": 14.2,
        "kept": true
      }
    }
  ],

  "screens": [
    {
      "id": "s_014",
      "representative_frame": "f_000842",
      // Every comparable frame folded into this screen. Membership has to survive
      // into the manifest because cross-frame agreement is computed from it.
      "frame_ids": ["f_000842", "f_000843", "f_000844"],
      "t_ms_start": 838000,
      "t_ms_end": 851000,
      "ocr": {
        "title_raw": "Bed Control",
        "title_confidence": 0.71,
        "tabs_raw": ["Unit", "Bed", "Events"]
      },
      "identity": {
        "name": "Bed Control",
        "module": "Grand Central",
        "tabs": ["Unit", "Bed", "Events"],
        "dialog": null,
        "description": "Unit grid with four sub-tabs and a right-hand action rail"
      },
      "confidence": {
        "score": 0.83,
        "signals": { "ocr_agreement": 0.9, "cross_frame": 1.0, "framing": 1.0, "legibility": 0.6 },
        "verdict": "accepted"          // accepted | review
      },
      "classification": {
        "bucket": "built",             // built | partial | new | other
        "matched_label": "Bed Board",
        "route": "/grand-central/bed-board",
        "match_kind": "alias",         // exact | alias | fuzzy | none
        "match_score": 1.0,
        "evidence": "ACTIVITY_OVERRIDES"
      }
    }
  ]
}
```

`generated_at` is deliberately absent — see [Determinism rules](#determinism-rules).

---

## Config reference

Config resolves in three layers, each overriding the one before. Only the
resolved result is hashed into the manifest.

| Layer | File | Scope | Committed? |
| --- | --- | --- | --- |
| 1 | `configs/defaults.yaml` | Tool defaults. Generic. Improves as the tool learns across videos. | ✅ |
| 2 | `projects/<name>.yaml` | *Which project*: inventory path, modules in scope, project-wide aliases, publish destination. | ❌ gitignored |
| 3 | `videos/<slug>/config.yaml` | *Which video*: framing, glare, thresholds. Generated fresh by stage 00. | ✅ |

```bash
reframe run radiant-01 --project rl_epic
```

The middle layer is what keeps the tool project-agnostic ([DEC-017](DECISIONS.md#dec-017--one-repo-three-config-layers-never-cloned-per-video)).
Nothing in layers 1 or 3 may name a consuming application, and
`scripts/check_isolation.sh` fails the build if anything does.

The alias tables in layers 2 and 3 are deliberately separate: a misread caused by
the *app* (its chrome font, its abbreviations) is a project fact and belongs in
layer 2, where every video inherits the correction; a misread caused by *one
video's* footage quality belongs in layer 3.

Layers 1 and 3 below; see `projects/_example.yaml` for layer 2.

```yaml
sample:
  fps: 1.0
  quality: 3
  skip_ranges: []              # [["0:00","0:12"]] — intros, desk shots
  max_frames: 2000

rectify:
  canonical_size: [1600, 1000]
  smooth_window: 9
  min_quad_confidence: 0.55
  aspect_bounds: [1.3, 1.9]
  manual_corners: []           # [{from: "4:10", to: "6:30", corners: [[..]] }]

clean:
  align: true
  clahe: {enabled: true, clip: 2.0, grid: 8}
  deglare: {enabled: true, max_correction: 0.3}
  moire: {enabled: false, sigma: 0.6}

dedupe:
  band_rect: [0, 0, 1600, 190]  # title + tab strip, in canonical coords
  hash_distance: 12
  full_frame_weight: 0.3
  min_gap_frames: 2

ocr:
  engine: tesseract
  # Which bands to read. `activity` is off by default: it sits where a grid header
  # or first data row often begins, and a default that OCR'd a data row would
  # break DEC-011 by accident.
  regions: [title, tabs]
  # Where those bands are, in CANONICAL coordinates — the same space as
  # dedupe.band_rect, so all of them move together when canonical_size changes.
  region_rects:
    title: [0, 0, 720, 72]
    tabs: [0, 72, 1600, 64]
    activity: [0, 136, 1600, 56]
  min_word_confidence: 0.4
  psm: 7

identify:
  montage_rows: 20
  provider: openai
  model: gpt-5.2
  prompt_version: 2
  # Ceiling on one call's output. On a reasoning model this covers the reasoning
  # as well as the answer, which is why it is a tunable and not a constant
  # (DEC-029). Not part of the response cache key.
  max_output_tokens: 48000
  corroborate: true
  full_frames: false

confidence:
  accept_threshold: 0.75
  weights: {ocr_agreement: 0.3, cross_frame: 0.3, framing: 0.2, legibility: 0.2}

classify:
  fuzzy_threshold: 0.82
  # How close a rejected match must come to the threshold to reach
  # NEEDS_REVIEW.md. The candidate is recorded in the manifest either way.
  near_miss_margin: 0.15
  aliases: {}                  # per-video corrections only
```

Layer 2 (`projects/<name>.yaml`) adds the project-scoped keys — `inventory`,
`inventory_cmd`, `project_root`, `classify.modules_in_scope`,
`classify.partial_labels`, project-wide `classify.aliases` and `publish_to`. They
are absent from layers 1 and 3 by design.

### Deliberately not configurable

Two values are constants in code rather than tunables, and the distinction is
worth keeping: a tunable is something a validation round would move.

| Value | Where | Why not config |
| --- | --- | --- |
| Derived-frame JPEG quality | `vision.DERIVED_JPEG_QUALITY` | Frames in `rect/`, `clean/` and `kept/` feed OCR and a model. Nobody tuning this pipeline ever wants them *worse*, and every set except `kept/` is regenerable. |
| The band-hash dead zone | `vision.hashing._FLAT_EPSILON` | A noise floor in grey levels, not a quality bar. Cell averaging puts sensor noise far below it and real text far above (DEC-021). |

Also note what `confidence.weights` can and cannot reach: a signal with no weight
takes no part at all. That is how `inventory_match` stays opt-in — it is the only
signal that describes the consuming project rather than the footage.

---

## Determinism rules

Only `frames/kept/` is committed; everything else is re-extractable on demand.
That is only safe if a re-run reproduces identical frame IDs. A note saying
"see frame 0142" is worthless if a re-run renumbers everything.

Therefore:

1. **No wall-clock time and no randomness** anywhere in stages 00–05, 07, 08.
   No `datetime.now()` in the manifest — the caller stamps timestamps if it
   wants them.
2. **The resolved config is hashed into the manifest.** Changing any tunable
   changes the hash, which makes stale output detectable rather than confusing.
3. **The source video is hashed.** A different file with the same name is a hard
   error, not a silent reprocess.
4. **Stage 06 is the sole non-deterministic stage** (it calls a model). Its raw
   responses are cached keyed by `(montage_hash, prompt_version, model)`, so
   re-running stage 06 without changing inputs replays the cache rather than
   re-querying.

---

## Fixtures and verification

The improvement loop only compounds if corrections survive. Fix video 1's misses
without recording them and you will silently regress at video 4.

After validating a video, `reframe fixture <slug>` records ground truth.

Fixtures hold **two kinds of fact**, and conflating them breaks verification
([DEC-019](DECISIONS.md#dec-019--fixtures-separate-stable-observations-from-time-varying-classifications)):

| Kind | Examples | Property of | Change means |
| --- | --- | --- | --- |
| **Stable observation** | screen present at a timestamp, its name, its module, a span the run missed | the *footage* — true forever | **regression**, fails `verify` |
| **Time-varying classification** | bucket, matched route | the *consuming project* at one commit | **drift**, informational |

The distinction is forced by the loop itself. Video 1 first reports
`Study Images → new`; after you build it, the same video correctly reports
`built`. Treating that as a regression would make `verify` cry wolf on every
video after the first build — and a verification step people learn to ignore is
worse than none, because it destroys the ratchet it exists to protect.

```yaml
slug: video-01
inventory_commit: 9a0a4ad9        # what the buckets below were true against

screens:
  - t: "14:02"
    name: "Bed Control"           # stable
    module: "Grand Central"       # stable
    bucket: built                 # time-varying
  - t: "22:41"
    name: "Study Images"          # stable
    bucket: new                   # time-varying
    note: "missed on run 1 — dedupe collapsed it into the previous screen"

missed_spans:
  - {from: "31:10", to: "33:40", note: "scroll through order list — no screen emitted"}
```

`reframe verify` re-runs **every video that has a fixture** and separates the two:

```
✗ REGRESSION  video-01 @ 14:02  screen no longer detected
✗ REGRESSION  video-03 @ 08:15  name changed: "Bed Control" → "Bed Coetrol"
~ drift       video-01 @ 22:41  bucket new → built (inventory 9a0a4ad9 → 4f2b117)
? unfixtured  video-02 @ 41:03  new screen found, not in fixture
```

Only regressions fail. Drift in the direction `new → built` is the expected
signal that building is working; drift the other way, `built → new`, is worth
investigating — and is visible precisely because drift is reported rather than
suppressed.

Verification runs before any tuning change is accepted. This is what turns
*process → validate → next* into a ratchet rather than a treadmill.

---

## Working across videos

Videos are processed one at a time, and the repo is **cloned once, never per
video** ([DEC-017](DECISIONS.md#dec-017--one-repo-three-config-layers-never-cloned-per-video)).
Because the work is sequential, history is a chain rather than parallel
branches, and the conflict surface is one file.

```
── reframe ────────────────────────────────────────────────────
   git checkout -b video/<slug>
   reframe init <video> --slug <slug>
   reframe run <slug> --project <name>
   reframe verify                     # all prior videos still pass
   merge to main

── consuming project ──────────────────────────────────────────
   git checkout -b feat/<thing>
   build from out/<slug>/BUILD_QUEUE.md
   PR → main
```

Everything a video produces lands on a **new path** — `videos/<slug>/`,
`fixtures/<slug>.yaml`, `out/<slug>/` — so it cannot conflict. The only shared
mutable file is `configs/defaults.yaml`.

**A conflict there is information.** If one video wants `hash_distance: 9` and
another settled on `12`, git is telling you the key should not be a global
default and belongs in the per-video layer instead. That signal is the reason
the shared file is worth having.

Video *N+1* branches from a main that already contains every fix and fixture
from videos 1…*N*, and `reframe verify` proves those earlier videos still pass
before any tuning change is accepted.

---

## Out of scope

Each of these is something the tool could plausibly attempt and would get wrong.
Naming them matters more than the feature list.

| Not doing | Why |
| --- | --- |
| **Measuring geometry** | The RL_EPIC loop's `source px ÷ 1.345 = CSS px` needs a flat image at a fixed, known scale. Handheld video has neither — perspective correction recovers shape but not absolute scale, and any residual keystone error propagates into every measurement. Column widths and row heights come from screens already built in `rl_epic`. |
| **Extracting colour** | The reference is a *green* Epic build; the target app is *purple HyperDrive* and its theme is locked. Any colour read off a frame is actively misleading — and a phone camera's white balance and the monitor's own colour profile make it doubly so. |
| **Reading data-grid values** | An OCR error and a fabrication are indistinguishable downstream. `rl_epic`'s rule is explicit: *never invent data to fill a column.* Cell contents are read by a human off a full-res frame. |
| **Flow / transition detection** | Deferred to v2. Hardest stage and the most likely to be rewritten once real footage shows how transitions actually look; kept out of v1 so it cannot destabilise the parts that work. |

What the videos *are* authoritative for — and what this tool does capture —
is structure, labels, column sets, column order, control types, states and
workflow. That is the majority of the value, and it matches what `rl_epic`'s
`CLAUDE.md` already says a reference frame is authoritative for.
