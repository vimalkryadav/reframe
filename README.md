# Reframe

Turns handheld phone recordings of a desktop application into a reviewed screen
catalogue and a build queue — and points at the moments a human still has to
watch, instead of hiding them.

Built for the `rl_epic` workflow: 8 phone-of-monitor recordings of Epic
Hyperspace (~15 min each, ~2 h total) need to become a list of screens to
clone, with the screens that are *already built* filtered out automatically.

**Status:** implemented, and exercised end to end against synthetic footage. Not
yet run on a real recording — the corpus this exists for is phone-of-monitor video,
and several defaults are explicitly provisional until the first one goes through.
See [what is and is not verified](#what-is-verified) below.

---

## What is verified

The pipeline runs start to finish and its outputs are checked, but be clear about
against what:

| Verified | How |
| --- | --- |
| All nine stages run end to end | A synthetic 30 s recording: five app screens, perspective-projected onto a dark room with per-frame shake and sensor noise |
| Determinism (DEC-013) | Two full runs produce a **byte-identical** `manifest.json`; frame ids and filenames are stable |
| Rectification | 30/30 frames detected and warped automatically on that footage |
| Dedupe | Finds every real screen boundary; the tuning trade-off is measured and recorded in [DEC-021](DECISIONS.md#dec-021--the-band-hash-needs-an-aspect-matched-grid-and-a-dead-zone) |
| OCR | Reads all five screen titles and their tab strips |
| Confidence | Accepts the five screens where signals agree and escalates the one where OCR contradicts the model |
| Classification | `built` / `partial` / `new` / `other`, exact + alias + fuzzy matching, near-miss reporting, and the staleness abort — against a throwaway git project with a real exporter |
| Verify | Regression fails with exit 1; bucket drift reports and exits 0 |

| Not verified | Why |
| --- | --- |
| **Real handheld footage** | None exists in the repo yet. This is the big one: corner detection, glare, moiré and OCR quality are all guesses until then. |
| **A live model call** | Stage 06 was exercised through its response cache, which covers montage building, parsing, mis-attribution handling and scoring — but not the request itself. |
| **Tesseract on a real screen photo** | The synthetic frames are far cleaner than a photograph of a monitor. |
| **Automated tests** | There are none. Verification so far is the end-to-end runs above plus `mypy --strict`; `CLAUDE.md` still asks for unit tests against fixture frames, and that debt is unpaid. |

Provisional defaults to re-check on the first real video: `confidence.weights` and
the two legibility constants ([DEC-022](DECISIONS.md#dec-022--a-signal-that-cannot-be-measured-is-reported-unmeasurable)),
`dedupe.hash_distance`, and every rectangle in `ocr.region_rects`.

---

## Why this exists

Watching two hours of footage and taking notes by hand is slow, and the notes go
stale the moment the app changes. The mechanical half of that job — sampling,
straightening, de-duplicating, timestamping — is fully automatable. The
judgement half — *"that's the Ancillary Orders screen with a dialog over it"* —
is not.

Reframe automates the mechanical half completely, does the judgement half with a
model, and **scores how sure it is** so the uncertain parts get escalated rather
than quietly guessed.

That last property is the whole point. The failure this tool exists to prevent
is already on record in `rl_epic`, in `docs/reference/full_dfs/SCREEN_INDEX.md`:

> ⚠️ **CORRECTION of my earlier passes:** I had wrongly said IMG_2506 held "only
> one claim screen." FALSE — the **last ~3 min of IMG_2506 is a full live PB
> Account-Maintenance + Self-Pay Payment Collection walkthrough**. This is the
> most valuable PB video evidence. Lesson: scan the END of every video.

A confident, complete-looking catalogue with a hole in it is worse than no
catalogue, because you cannot review a gap you were never told about.

---

## What it produces

```
out/<video-slug>/
├── manifest.json         machine-readable; the join key for everything
├── SCREEN_CATALOG.md     every distinct screen in the video
├── BUILD_QUEUE.md        the new + partially-built screens, ordered
├── NEEDS_REVIEW.md       timestamps you need to open yourself
└── frames/kept/          the deduped, rectified frames (committed)
```

The three Markdown files are generated from `manifest.json` and are never
hand-edited, so a re-run cannot drift from the data.

---

## Documentation

| Doc | What's in it |
| --- | --- |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | The nine stages in detail, module layout, data flow, manifest schema, config reference |
| [`DECISIONS.md`](DECISIONS.md) | Every design decision with its context, the options rejected, and the consequences |
| [`CONTRACT.md`](CONTRACT.md) | The `inventory.json` interface with `rl_epic` — schema, exporter requirements, matching rules |
| [`CLAUDE.md`](CLAUDE.md) | Working rules for anyone (human or agent) writing code in this repo |

Requires `ffmpeg` (stages 00–01), `tesseract` (stage 05), and an Anthropic
credential for stage 06 — `ANTHROPIC_API_KEY`, or a profile from `ant auth login`.

Read `DECISIONS.md` first if you're wondering *why* something is built a
particular way. Most of the non-obvious choices are forced by the footage being
handheld, and the reasoning is recorded there rather than repeated in comments.

---

## Quickstart

```bash
uv sync

# 0. once per consuming project — describes WHICH app, stays gitignored
cp projects/_example.yaml projects/myapp.yaml && $EDITOR projects/myapp.yaml

# 1. register a video and generate its config
uv run reframe init ~/Downloads/IMG_2601.MOV --slug video-01

# 2. run the whole pipeline
uv run reframe run video-01 --project myapp

# 3. re-run a single stage after editing videos/video-01/config.yaml
uv run reframe stage 04 video-01

# 4. after you've validated: record ground truth, then check for regressions
uv run reframe fixture video-01
uv run reframe verify            # re-runs ALL videos against their fixtures
```

### Configuration layers

| Layer | File | Holds | Committed? |
| --- | --- | --- | --- |
| 1 | `configs/defaults.yaml` | Generic tool defaults | ✅ |
| 2 | `projects/<name>.yaml` | *Which project* — inventory path, modules in scope, project aliases | ❌ |
| 3 | `videos/<slug>/config.yaml` | *Which video* — framing, glare, thresholds | ✅ |

Layer 2 is what keeps the tool project-agnostic; `scripts/check_isolation.sh`
fails the build if a consuming app is named anywhere in layers 1 or 3.

---

## The loop this is built for

```
process video → build from the queue → validate against the video → tune → next video
```

Accuracy is expected to be mediocre on video 1 and to improve on each pass. Three
design properties exist purely to make that true:

1. **Every tunable lives in config**, never as a literal in code. A validation
   round edits YAML, not Python.
2. **Corrections are recorded as fixtures**, and `reframe verify` re-runs every
   prior video. Without this you fix video 1's misses and silently regress at
   video 4.
3. **The repo is cloned once, not per video.** Fixtures, tuned defaults, the
   alias table and the model cache are shared state — they *are* the compounding.
   Video *N+1* branches from a main containing every fix from videos 1…*N*.
   See [DEC-017](DECISIONS.md#dec-017--one-repo-three-config-layers-never-cloned-per-video).

```
reframe    git checkout -b video/<slug> → run → verify → merge to main
<project>  git checkout -b feat/<thing> → build from BUILD_QUEUE.md → PR → main
```

---

## Relationship to `rl_epic`

Reframe is a standalone tool and knows nothing about Epic. The one thing it
needs from `rl_epic` — the list of what's already built — arrives as a generic
`inventory.json` produced by an exporter that lives *inside* `rl_epic`.

```
rl_epic/scripts/export-inventory.mjs  →  inventory.json  →  reframe
   (knows nav.ts, menuConfig.ts,          (generic:            (knows nothing
    modalActivities.ts, app/ routes)       label, route,        about Epic)
                                           status, aliases)
```

See [`CONTRACT.md`](CONTRACT.md). Any other project can write its own 60-line
exporter and inherit the classifier for free.
