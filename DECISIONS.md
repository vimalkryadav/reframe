# Decisions

An architecture decision log. Each entry records the context, the options
considered, what was chosen, and what it costs — so a future reader can tell a
*deliberate* choice from an accident, and can reopen a decision knowing what it
was originally weighed against.

**Status key:** `accepted` · `superseded` · `reopened`

Several of these are forced by the footage being handheld rather than a native
screen capture. Those are marked **[handheld]** — if the corpus ever changes,
they are the ones to revisit first.

---

## DEC-001 — Standalone repo, not part of `rl_epic`

**Status:** accepted

**Context.** The workflow this automates already exists inside `rl_epic` as a
mix of `scripts/extract_frames.sh`, the RL_EPIC loop in `CLAUDE.md`, and hand-
maintained notes in `docs/reference/`. It has been exercised across at least
three separate video batches.

**Options.**
1. Extend `rl_epic/scripts/` — closest to the status quo.
2. A standalone tool.
3. Put it in `rl_components` — the existing shared library.

**Decision.** Standalone repo at `~/epic/reframe/`.

Option 3 was rejected quickly: `rl_components` is a UI component/hook library,
and this is an ffmpeg/CV/CLI tool. Wrong kind of artifact.

Option 1 was rejected because in-repo scripts inevitably absorb project-specific
assumptions. The two worst offenders were already visible: a hardcoded
`÷ 1.345` scale factor specific to one recording's window size, and colour
handling entangled with Epic's theme. A tool that cannot see `rl_epic` cannot
absorb them.

**Consequences.**
- The built/partial/new classifier can no longer read `nav.ts` directly. That
  coupling has to be inverted — see [DEC-012](#dec-012--the-inventory-contract-is-owned-by-rl_epic).
- Any future RL environment can use the tool by writing a short exporter.
- The *outputs* still belong in `rl_epic/docs/reference/` — the tool is
  separate, its evidence is not.

---

## DEC-002 — Python + uv

**Status:** accepted

**Context.** The work is video decoding, computer vision, OCR and a model call.

**Decision.** Python, managed with `uv`.

The CV and OCR ecosystem is decisively Python. `uv` matches the toolchain
`rl_epic`'s backend already uses, so there is nothing new to learn operationally.
A Node implementation would shell out to ffmpeg and Python for the image work
anyway; a pure-bash implementation cannot carry a manifest, fixtures or real
data structures, which caps what the tool can become.

---

## DEC-003 — Fixed-rate sampling, not scene detection **[handheld]**

**Status:** accepted

**Context.** Scene detection is the obvious way to extract "one frame per
screen" and it is what `rl_epic`'s existing `extract_frames.sh` defaults to
(`--mode scene`, threshold 0.12).

**The problem is already documented in that script's own header:**

> *"handheld video of a screen has constant micro-motion/blur, so hard scene
> cuts are rare and the default threshold yields too few frames. For that
> footage use a low threshold (`--scene 0.04`) or fixed sampling."*

**Decision.** Sample at a fixed rate, default 1 fps. Scene detection is not
offered at all in v1.

**Consequences.**
- ~900 frames per 15-minute video, ~7,200 across the corpus. Entirely tractable
  at this scale — the corpus being small is what makes brute force acceptable.
- All the reduction burden moves to stage 04, which is where it can be done
  properly on rectified frames anyway.
- If the corpus ever grows an order of magnitude, revisit.

---

## DEC-004 — Source timestamps live in frame filenames

**Status:** accepted

**Context.** `rl_epic`'s `extract_frames.sh` documents an output file:

> `_frames.txt` (index: frame file -> source timestamp)

The implementation writes three `#` comment lines and no per-frame rows. Combined
with `-frame_pts 0` and sequential `frame-%04d.png` numbering, this means **in
scene mode the source timestamp is unrecoverable** — which silently breaks the
documented workflow in `SCREEN_CATALOG.md`:

> *"Re-extract any screen full-res: `ffmpeg -ss <sec> -i <video> -frames:v 1 out.png`"*

**Decision.** Encode the timestamp in the filename: `f_000842__t14m02s.jpg`, and
carry `t_ms` in the manifest as the machine-readable form.

**Consequences.** The failure mode becomes impossible rather than merely
avoided. Timestamps are the join key between frames, notes, fixtures and the
video itself; losing them costs far more than the redundancy costs.

---

## DEC-005 — Rectification is a mandatory stage **[handheld]**

**Status:** accepted

**Context.** Handheld footage of a screen gives you a moving, keystoned,
partially-glared quadrilateral floating in a picture of a room. Every downstream
algorithm — differencing, hashing, OCR, model reading — assumes a flat, stable,
consistently-framed image.

**Options.**
1. Work on raw frames and make every downstream stage shake-tolerant.
2. Detect the screen, warp it flat once, and let everything downstream stay
   simple.

**Decision.** Option 2, as a mandatory stage 02.

Option 1 spreads the same problem across five stages, each solving it partially
and differently. It is also the path where the project quietly fails: each stage
looks *nearly* right, and the compounding error only shows up as a mysteriously
bad catalogue.

**Consequences.**
- Stage 02 is the highest-risk component and the correct place to concentrate
  effort and testing.
- It needs a fallback chain, not just an algorithm — see [DEC-006](#dec-006--rectification-degrades-in-steps-and-never-fakes-success).
- Everything after it can assume canonical-size input, which makes fixed
  pixel coordinates in config (band rectangles, OCR regions) meaningful at all.

---

## DEC-006 — Rectification degrades in steps and never fakes success

**Status:** accepted

**Context.** Whether the laptop screen stays fully inside the phone's frame for
the whole recording is **unknown, and may vary per video**. A detector that
always returns four corners will happily return four corners for a screen whose
right edge is out of shot.

**Decision.** Four explicit outcomes, recorded per frame as `rectify.method`:

| Outcome | Behaviour |
| --- | --- |
| `auto` | Confident detection; use it. |
| `interpolated` | Weak detection; interpolate from neighbours within the smoothing window. |
| `manual` | Detection failed across a span; use corners from `config.yaml` for that time range. |
| `failed` | Screen genuinely out of frame; mark `framing: partial`/`lost` and escalate the span. |

**Consequences.**
- A human may need to click four corners once per stable segment. Acceptable —
  it is bounded, and it is the difference between a usable video and a discarded
  one.
- **A cut-off screen is never silently cropped into a confident-looking frame.**
  That would produce a plausible frame missing a column, which is precisely the
  class of error this tool exists to prevent.

---

## DEC-007 — Dedupe on the title band, against the last kept frame **[handheld]**

**Status:** accepted · supersedes the method in `rl_epic/CLAUDE.md` for this footage

**Context.** The inherited method: greyscale, crop the taskbar, resize to ~320px,
`GaussianBlur(1.2)`, keep a frame when >5.5% of pixels differ from the last kept
one. Correct for a native screen recording.

**On handheld footage it inverts.** Hand shake alone displaces the image by more
than 5.5%, so nothing registers as a duplicate and all ~900 frames survive. The
stage does not degrade — it produces the exact opposite of its purpose.

**Decision.** Two changes, plus one rule preserved.

1. Rectification (stage 02) removes most of the false movement *before* this
   stage runs. This is the larger half of the fix.
2. Compare a perceptual hash of the **title + tab band** as the primary signal —
   that band is what identifies a screen. Full-frame comparison stays as a
   weighted secondary signal to catch dialogs and scroll changes within one
   screen.
3. **Preserved unchanged:** compare against the *last kept* frame, not the
   previous frame. `rl_epic`'s loop records why — comparing against the previous
   frame collapses slow scrolls to nothing, because each step is individually
   below threshold.

**Consequences.** A screen whose chrome is identical but whose body differs
(same screen, different record) may collapse into one entry. That is usually
correct for a build queue, and the full-frame weight is the knob that adjusts it
per video.

**Amended during implementation** — see [DEC-021](#dec-021--the-band-hash-needs-an-aspect-matched-grid-and-a-dead-zone),
which records what a stock perceptual hash actually did to a title band, and the
measured relationship between `hash_distance` and drift.

---

## DEC-008 — A model identifies screens, with confidence-based escalation

**Status:** accepted

**Context.** Something must turn pixels into *"this is the Ancillary Orders
screen."* Three arrangements were considered, discussed at length before this
log existed:

| | Approach | Verdict |
| --- | --- | --- |
| A | No model in the tool. It emits montages + OCR; a human/agent session reads them and writes the catalogue. | Viable, less to build |
| B | Model identifies everything; output is a finished catalogue. | **Rejected** |
| C | Model identifies, scores confidence, escalates the uncertain. | **Chosen** |

**Decision.** C.

**B is rejected on evidence, not taste.** The exact failure is on record in
`rl_epic/docs/reference/full_dfs/SCREEN_INDEX.md`: an automated pass concluded a
video held "only one claim screen," and the last three minutes turned out to
contain the most valuable footage in the entire corpus. It produced a confident,
complete-looking catalogue with a hole in it. **You cannot review a gap you were
never told about.**

**A became untenable when the footage was confirmed handheld.** A depended on
OCR being reliable enough to carry most of the naming. On phone-of-monitor
footage OCR is exactly what degrades — `rl_epic`'s own catalogue marks such
reads `(?)`. Without reliable OCR, A degenerates into a human reading every
montage manually, which is the cost the tool was built to remove.

**Consequences.**
- The tool needs an API key and a versioned prompt.
- `NEEDS_REVIEW.md` will be long on video 1. That is the design working.
- A → C would have been additive; C → A is always available by ignoring the
  model stage.

---

## DEC-009 — Confidence is signal agreement, not model self-report

**Status:** accepted

**Context.** The obvious implementation of "how sure are you" is to ask the
model. That is not a measurement — it is another generated value with the same
failure modes as the answer it is meant to qualify, and it correlates with
fluency rather than correctness.

**Decision.** Compute confidence in `confidence.py` from independent signals:
OCR agreement with the model's name, cross-frame consistency of repeat sightings,
framing quality flags from stage 02, band legibility metrics, and whether the
name resolves against the inventory.

**Consequences.**
- Confidence is explainable — the manifest records each signal separately, so a
  bad score can be diagnosed rather than merely distrusted.
- The weights are config, and tuning them is expected to be a main activity of
  the validation rounds.
- Cross-frame consistency only works because dedupe keeps repeat sightings as
  separate screens when they are separated in time. Do not "optimise" that away.

---

## DEC-010 — Geometry measurement is out of scope **[handheld]**

**Status:** accepted

**Context.** Step 5 of the RL_EPIC loop is *"measure, don't eyeball"* —
`source px ÷ 1.345 = CSS px`, measure with Pillow, target ≤2px against the DOM.
It is the step that catches defects reading cannot, and losing it is a real cost.

**Decision.** Out of scope. The videos will not yield reliable geometry.

Perspective correction recovers *shape* but not absolute *scale*: there is no
known-size reference in frame, the camera distance varies, and residual keystone
error after warping propagates into every measurement. A number that is wrong by
3% looks exactly like a number that is right, which is worse than no number.

**Consequences.**
- Column widths, row heights and spacing come from screens already built in
  `rl_epic` — which is what its "Reference-This-Repo-First" rule already says to
  do for chrome and layout.
- The videos remain authoritative for structure, labels, column sets, column
  order, control types, states and workflow. That is most of the value.
- **If a future recording is a native screen capture, reopen this.**

---

## DEC-011 — No colour extraction, no data-grid OCR

**Status:** accepted

**Context.** Both are things the tool could easily attempt and would get wrong
in ways that are hard to detect downstream.

**Decision.** Neither is implemented, at any confidence level.

**Colour.** The reference is a *green* Epic build; the target is the *purple
HyperDrive* theme, which `rl_epic/CLAUDE.md` locks explicitly. A colour read off
a frame is actively misleading before you even account for the phone's white
balance and the monitor's colour profile.

**Data-grid values.** `rl_epic`'s rule: *"Never invent data to fill a column."*
An OCR error and a fabrication are indistinguishable once written into a
catalogue — and on blurry footage, digits are exactly where OCR fails. Cell
contents get read by a human off a full-res frame.

**Consequences.** Descriptions in the catalogue name *structure* — "four
sub-tabs, right-hand action rail, six-column grid" — and never values.

---

## DEC-012 — The inventory contract is owned by `rl_epic`

**Status:** accepted

**Context.** The classifier needs to know what is already built. That knowledge
lives in `rl_epic`'s TypeScript: `ACTIVITY_OVERRIDES` in `lib/nav.ts` (85
entries), `modalActivities.ts` (34), `menuConfig.ts` `disabled: true` markers
(27), and 150 `page.tsx` routes. But [DEC-001](#dec-001--standalone-repo-not-part-of-rl_epic)
says Reframe must not know about Epic.

**Options.**
1. Reframe parses `rl_epic`'s TypeScript.
2. `rl_epic` exports a generic `inventory.json`; Reframe consumes it.

**Decision.** Option 2. The exporter lives in `rl_epic/scripts/`.

Option 1 couples Reframe permanently to one project's file layout and defeats
the separation entirely.

**Consequences.**
- Every Epic-specific fact stays where it is already maintained and already
  changes alongside the code.
- Reframe's matching logic is generic string/alias/fuzzy matching over a list.
- Any other project writes a short exporter and inherits the classifier.
- See [`CONTRACT.md`](CONTRACT.md) for the schema.

---

## DEC-013 — Determinism, and only the deduped frames are committed

**Status:** accepted

**Context.** `rl_epic`'s `SCREEN_INDEX.md` records that full-res frames were not
stored (2.9 GB) and are re-extracted on demand. That is the right call at this
corpus size too — but it only works if re-extraction reproduces the same frames.

**Decision.** Stages 00–05, 07 and 08 are fully deterministic: no wall-clock, no
randomness, no `generated_at` in the manifest. The resolved config and the source
video are both hashed into the manifest. Stage 06 is the sole non-deterministic
stage and caches model responses keyed by `(montage_hash, prompt_version, model)`.

**Consequences.**
- A note saying "see `f_000842`" resolves correctly forever.
- Changing a tunable changes `config_hash`, which makes stale output detectable
  instead of confusing.
- The same input never costs a second model call.

---

## DEC-014 — Tunables live in config; code holds no thresholds

**Status:** accepted

**Context.** The stated workflow is *process → build → validate → tune → next
video*, across 8 videos. Accuracy is expected to be mediocre initially and to
improve each round.

**Decision.** Every threshold, crop rectangle, corner override, weight and alias
lives in `videos/<slug>/config.yaml`, layered over `configs/defaults.yaml`. No
tunable value appears as a literal in Python.

**Consequences.**
- A validation round is a YAML edit, not a refactor. This is the difference
  between feedback that compounds and feedback that thrashes.
- Per-video configs are expected to diverge — different videos will have
  different framing, glare and legibility. That is a feature.
- It forces a clean split: `stages/` orchestrates, `vision/` and `model/`
  compute, config parameterises.

---

## DEC-015 — Fixtures and regression verification ship in v1

**Status:** accepted

**Context.** The improvement loop only compounds if corrections survive. Fix
video 1's misses without recording them and you regress at video 4 without
noticing — which is the same silent-gap failure as [DEC-008](#dec-008--a-model-identifies-screens-with-confidence-based-escalation),
arriving by a different route.

**Decision.** `reframe fixture <slug>` records validated ground truth;
`reframe verify` re-runs **every video that has a fixture** and reports
regressions, changed classifications, and newly-found screens.

**Consequences.**
- Roughly a hundred lines now; genuinely painful to retrofit once three videos
  of undocumented corrections exist.
- Verification gates tuning changes, which is what makes the process a ratchet
  rather than a treadmill.

---

## DEC-016 — Flow / transition detection deferred to v2

**Status:** accepted

**Context.** Inferring *"clicking here opens this dialog"* would be the most
valuable single output — it captures workflow, not just inventory.

**Decision.** Not in v1. Kept out of the stage graph entirely rather than
stubbed, so it cannot influence the design of stages that work.

It is the hardest stage and the one most likely to be rewritten once real
footage shows how transitions actually look on this corpus — and it depends on
stages 02 and 04 being well-tuned, which will not be true until several videos
have been processed.

**Consequences.** Workflow information still reaches the build queue, via the
model's description of each screen and the human review pass. It is just not
extracted as a graph.

---

## DEC-017 — One repo, three config layers, never cloned per video

**Status:** accepted

**Context.** Videos are processed one at a time: process → build → validate →
tune → next. Two questions came up while scoping that loop: whether project
details were leaking into the tool, and whether a fresh start per video was
needed.

The leak was real and is fixed here. Refreshing the *consuming project's* state
per video is a separate and correct requirement, handled in
[DEC-018](#dec-018--the-inventory-is-regenerated-per-run-and-staleness-is-a-hard-error).
This entry covers only Reframe's own repo.

**Why cloning Reframe per video would fail.** Everything that makes the loop
compound is shared state:

| Lost per clone | Consequence |
| --- | --- |
| `fixtures/*.yaml` | `reframe verify` has nothing to check against; a tuning change for video 3 can break video 1 undetected |
| Tuned `configs/defaults.yaml` | Re-tuning from factory defaults 8 times instead of once |
| Accumulated aliases | Every misread screen name rediscovered from scratch |
| Model response cache | Identical calls paid for repeatedly |

Video 8 would be no more accurate than video 1 — a treadmill, not a ratchet,
which is the exact outcome [DEC-015](#dec-015--fixtures-and-regression-verification-ship-in-v1)
exists to prevent. Cloning also converts every bug fix from a `git merge` into
manual copying across eight directories, with no way to verify the copies.

Meanwhile the isolation cloning was meant to provide is already there:
`videos/<slug>/` and `out/<slug>/` are per-video paths, and a clean slate is
`rm -rf out/<slug>`.

**Decision.** One repo, cloned once. Three config layers:

```
configs/defaults.yaml      tool defaults. Generic. Committed. Improves each round.
projects/<name>.yaml       WHICH project: inventory path, modules in scope,
                           project-wide aliases. GITIGNORED.
videos/<slug>/config.yaml  WHICH video: framing, glare, thresholds. Generated fresh.
```

Resolved via `reframe run <slug> --project <name>`.

Project knowledge is genuinely disposable and genuinely absent from the
committed tool, while Reframe's own learning stays shared.

**Enforcement.** The isolation is a discipline, and disciplines decay across
eight rounds of tuning — so it is checked mechanically.
`scripts/check_isolation.sh` fails the build if a consuming project's name
appears anywhere in `src/`, `configs/` or `tests/`. That guard addresses the real
risk behind the original proposal directly, without giving up the merge flow.

**Git flow.** Two repos, two independent flows. Because videos are processed
sequentially, reframe's history is a chain rather than parallel branches:

```
reframe    git checkout -b video/<slug> → run → commit → merge to main
           new files per video (config, fixture, out/) never conflict;
           configs/defaults.yaml is the only shared mutable file

<project>  git checkout -b feat/<thing> → build from BUILD_QUEUE.md → PR → main
```

A conflict in `configs/defaults.yaml` is **information**: two videos wanting
different values means the key should not be a global default and should move
into the per-video layer. That signal does not exist across clones.

**Consequences.**
- Reprocessing an early video with later improvements is a re-run, not an
  archaeology exercise.
- A fix made during video 4 is inherited by videos 5–8 automatically, and
  `reframe verify` proves videos 1–3 still pass.
- Adding a new consuming project means adding a line to the banned-name list in
  `check_isolation.sh` — treat that as part of onboarding.

---

## DEC-018 — The inventory is regenerated per run, and staleness is a hard error

**Status:** accepted

**Context.** The loop is: process video *N* → **build those screens into the
consuming project** → validate → process video *N+1*. So by the time video *N+1*
runs, the consuming project contains screens that did not exist when video *N*
was processed.

If the classifier reads a stale `inventory.json`, it will report screens as
`new` that were built last week — sending you to rebuild work you just finished.
That is the same class of failure as a silent gap: confident, plausible, wrong.

**Decision.** The inventory is **derived state, refreshed on every run** — never
a committed snapshot.

1. `inventory.json` stays gitignored. It is a build artifact of the consuming
   project, not data.
2. The project profile carries an `inventory_cmd` — the command that regenerates
   it. `reframe run` executes it before stage 07 unless `--no-refresh` is passed.
3. **Staleness is a hard error, not a warning.** `generated_from.commit` in the
   inventory is compared against the consuming project's current `HEAD`. A
   mismatch aborts the run with the refresh command in the message.
4. The commit the inventory was built from is recorded in the manifest, so any
   catalogue can be traced to the exact state of the app it was classified
   against.

Whether the user refreshes by `git pull` or by re-cloning the consuming project
is their business — Reframe only requires that the inventory match `HEAD`.

**Consequences.**
- The classifier's answers are only ever as fresh as the last build, which is
  the correct semantics.
- Re-running an old video after building yields *different and more correct*
  classifications. See [DEC-019](#dec-019--fixtures-separate-stable-observations-from-time-varying-classifications).
- The consuming project must expose a working exporter command, which
  [`CONTRACT.md`](CONTRACT.md) already requires.

---

## DEC-019 — Fixtures separate stable observations from time-varying classifications

**Status:** accepted · refines [DEC-015](#dec-015--fixtures-and-regression-verification-ship-in-v1)

**Context.** [DEC-018](#dec-018--the-inventory-is-regenerated-per-run-and-staleness-is-a-hard-error)
exposes a problem in the fixture design. Consider video 1:

| When | What the run says |
| --- | --- |
| First pass | `Study Images` → `bucket: new` |
| After you build it | `Study Images` → `bucket: built` |

Under the original design that reads as a **regression** — the fixture said `new`
and the run says `built`. It is the opposite: the run is now more correct, and
the fixture has aged out. Left unfixed, `reframe verify` would cry wolf on every
video after the first build, and would get muted, which destroys the ratchet it
exists to protect.

**Decision.** Fixtures record two kinds of fact, checked differently.

**Stable observations** — properties of the *footage*, true forever:
screen present at a timestamp, its name, its module, spans the run missed
entirely. A change here is a **regression** and fails `verify`.

**Time-varying classifications** — properties of the *consuming project* at a
point in time: the bucket, the matched route. A change here is **informational**
and is reported as drift, not failure.

```yaml
slug: video-01
inventory_commit: 9a0a4ad9        # what the buckets below were true against

screens:
  - t: "22:41"
    name: "Study Images"          # stable — regression if this changes
    module: "Radiology"           # stable
    bucket: new                   # time-varying — drift if this changes
```

`reframe verify` reports the two separately:

```
✗ REGRESSION  video-01 @ 14:02  screen no longer detected
~ drift       video-01 @ 22:41  bucket new → built (inventory 9a0a4ad9 → 4f2b117)
```

**Consequences.**
- Drift is the *expected* signal that building is working. Seeing it is
  reassuring, not alarming.
- A drift in the wrong direction — `built` → `new` — is worth investigating, and
  is visible precisely because drift is reported rather than suppressed.
- Fixtures record which inventory commit their buckets were true against, so
  drift can always be explained.

---

## DEC-020 — Rotation is applied by ffmpeg and then verified, not re-applied

**Status:** accepted · refines [DEC-004](#dec-004--source-timestamps-live-in-frame-filenames)

**Context.** [Stage 00](ARCHITECTURE.md#stage-00--probe) records the source's
rotation flag and `ARCHITECTURE.md` said stage 01 applies it. In practice ffmpeg
already applies the display matrix by default. Doing it a second time rotates the
frame *away* from upright — and a sideways screen is the one kind of broken input
corner detection will still happily accept, because a rotated rectangle is a
perfectly good bright quadrilateral. The result would be a whole video of
confidently rectified, unusable frames.

**Decision.** Sampling relies on ffmpeg's own autorotate. Stage 01 then
**cross-checks** the emitted frame size against the probed display size and
escalates a mismatch — a swap of width and height means the rotation was applied
twice or not at all.

**Consequences.**
- One less place for the two rotations to disagree.
- The check is the only thing between a mis-rotated source and a wasted run, so it
  escalates the whole video rather than logging a note.
- Deliberately no `-noautorotate`: the pixels a player would show are the pixels
  the pipeline reads, which is also what a reviewer sees when they open the file.

---

## DEC-021 — The band hash needs an aspect-matched grid and a dead zone

**Status:** accepted · amends [DEC-007](#dec-007--dedupe-on-the-title-band-against-the-last-kept-frame-handheld)

**Context.** DEC-007 chose "perceptual hash of the title band" without saying
*which* hash. A stock 8×8 dHash was tried first and measured on static footage:
two frames of the **same** screen came out 8–13 bits apart, while two **different**
screens sat 10–18 apart. No threshold separates those distributions, so the
primary dedupe signal carried no information at all.

Two causes, both measured:

1. **The grid ignored the region's shape.** A 1600×190 band squashed into 9×8
   cells averages the title text away entirely.
2. **Flat cells were coin flips.** A title bar is mostly uniform; where adjacent
   cells differ by less than the sensor noise, a `left > right` test returns noise.

**Decision.** Hash with a grid matched to the region's aspect ratio, average with
`INTER_AREA` so per-pixel noise falls with cell size, and give each cell pair *two*
bits — brighter and darker — so a pair flatter than a fixed grey-level dead zone
sets neither and reads as flat on every frame. Distances are reported on a fixed
64-bit scale whatever grid was used, so `dedupe.hash_distance` keeps one meaning.

After the change, on the same footage: same-screen 1–2, real screen changes 5.5–9.7.

**`imagehash` was dropped as a dependency.** It cannot express a non-square grid,
and the replacement is about fifteen lines of numpy. That also drops `scipy` and
`pywavelets`.

**Consequences.**
- **`hash_distance` must sit above the drift floor, not just below the change
  size.** Distance is measured against the *last kept* frame (DEC-007), so noise
  accumulates across a long static screen and a threshold tuned only against
  adjacent frames will split one screen in two.
- Measured on the synthetic fixture: 4 → six screens for five real ones (one
  duplicate row); 6 → four screens (one screen lost silently). **Tune low.** A
  duplicate row is visible in the catalogue; a missing screen is not.
- The stage escalates any frame that only `min_gap_frames` held back, so the other
  way of losing a short-lived screen is at least visible.

---

## DEC-022 — A signal that cannot be measured is reported unmeasurable

**Status:** accepted · refines [DEC-009](#dec-009--confidence-is-signal-agreement-not-model-self-report)

**Context.** DEC-009 defines confidence as agreement between independent signals.
Implementing them turned up two that cannot be measured as described, and in both
cases the plausible implementation produced a *wrong* number rather than a missing
one.

**Cross-frame agreement.** "Do repeat sightings of the same screen get the same
name?" needs the repeat sightings grouped. Grouping by band-hash distance does not
work: measured on footage whose screens share a chrome layout, two sightings of the
same screen sat 3 bits apart and two different screens also sat 3 bits apart. Any
threshold wide enough to catch the repeat merges unrelated screens — and then the
signal *penalises a correct reading* for disagreeing with a screen it has nothing
to do with. Observed: every screen scored 0.54 on a fixture where five of six
readings were correct.

**Glare.** A saturated-pixel count cannot distinguish a blown-out highlight from a
light UI theme. On a white-background application it condemns every frame; and
whiting out half a test band *raised* the contrast measure, because pure white
lifts the paper mean.

**Decision.** Both are measured only where they are real, and reported as
unmeasurable otherwise. Cross-frame agreement requires **identical** band hashes.
There is **no glare term** at all. `confidence.py` renormalises the weights over
the signals that exist and tracks coverage, so a screen scored from too little
evidence goes to review even when the score is high.

**Consequences.**
- Cross-frame agreement will rarely be measurable on real handheld footage, so
  coverage usually rests on three signals. That is the honest position, and the
  coverage floor is what stops one signal masquerading as agreement.
- Glare that destroys text is left to the human reading `NEEDS_REVIEW.md`. Stage
  02's framing signal already catches the framing half of the problem.
- **`legibility`'s two scaling constants are fitted to synthetic footage** and are
  the first thing to re-check against the first real video.

---

## DEC-023 — `partial` is a human's answer, recorded in the project profile

**Status:** accepted · implements the v1 note in [`CONTRACT.md`](CONTRACT.md#the-partial-bucket)

**Context.** `partial` cannot be derived from the inventory: it means the footage
shows tabs, columns or dialogs the built component lacks, and establishing that
means comparing the video against the component. Automating it would mean parsing
the consuming project, which reintroduces exactly the coupling
[DEC-001](#dec-001--standalone-repo-not-part-of-rl_epic) removed.

**Decision.** Stage 07 **asks** and the profile **answers**. Any screen that
matched a `built` entry while the footage shows tabs or a dialog is escalated to
`NEEDS_REVIEW.md` with the inventory label to add; listing that label in
`classify.partial_labels` in `projects/<name>.yaml` moves it to `partial`.

The question is asked once per inventory label, not once per sighting. A screen
visited five times would otherwise produce five identical review rows, and a review
list people skim is the failure mode `verify` is also designed around.

**Consequences.**
- `partial` never appears without a human having confirmed it, which is the point:
  it drives build work.
- The answer lives in layer 2, so every video inherits it — a component's
  incompleteness is a fact about the project, not about one recording.
- If nobody ever answers, the bucket stays empty and the build queue is still
  correct, just less specific.

---

## DEC-024 — Detection re-acquires after a genuine reframe

**[handheld]** Decided 2026-08-18, on the first real video (`v01`, 10:09 of
handheld Epic Hyperspace footage).

`is_plausible_successor` compares each detection against the last *accepted*
quad, on the rule that a screen cannot jump. The rule is right. The
implementation had no way to represent a second true statement: **a camera can
be re-aimed, and the footage after the move is as real as the footage before
it.**

On `v01` the camera was repositioned once, at 07:07, moving the screen centre
391px against a 220px budget. That frame was correctly rejected. But the anchor
then stayed pinned at the pre-move position, so every subsequent frame was
measured against somewhere the screen had left — and rejection cascaded to the
end of the video. The camera had settled into a *new* stable position and held
it to within 4–12px, the steadiest footage in the recording. All 181 frames of
it were discarded: the last three minutes of the workflow, absent from the
catalogue.

The failure mode is the one this tool exists to prevent, arriving from an
unexpected direction. It was not a silent hole — stage 02 warned, and the spans
reached `NEEDS_REVIEW.md` — but a reviewer told "07:07–10:08 screen-not-found"
would go looking for a problem in the footage, which is clean.

**Decided:**

- The movement budget becomes `rectify.max_jump_fraction` (default `0.10`).
  It was `0.1 * frame_diagonal`, inline in the function body — a tunable living
  in code, which DEC-014 forbids. Found only because it had to be changed.
- Detection re-acquires. Over-budget detections are held rather than dropped;
  when `rectify.reanchor_after_frames` (default `3`) of them agree with each
  other to within the same budget, the anchor moves there and the held frames
  are kept.
- **Agreement, not persistence, is the evidence.** A reflection or a second
  bright object wanders; a re-aimed camera settles. Requiring the run to be
  mutually consistent is what distinguishes them. A single over-budget frame
  never re-anchors, however confident.
- Held frames are kept once the run fires, rather than discarded as the cost of
  re-acquiring. Dropping them would blank the moment of the reposition — which
  is often exactly when the operator moved to show something.
- **A re-anchor is always recorded as a manifest warning.** If the detector
  re-acquired onto the wrong thing, every frame after it is a confident crop of
  something that is not the screen. That is the one outcome worse than dropping
  the frames, so it is never silent.

**Rejected:** raising the jump budget until the observed 391px move fits. It
would have worked on this video and left the cascade latent for the next one —
buying a green run at the cost of the failure recurring somewhere it would be
harder to recognise.

Also corrected in the same pass: `rectify.aspect_bounds` upper bound `1.9` →
`2.2`. A 16:9 screen does not read as 1.78 in this footage — the detected bright
region excludes the dark bezel and taskbar, and perspective compresses it
vertically, so `v01` measures 1.94–2.13 across every sampled frame. The old
bound rejected **100%** of them (0/96) at confidences of 0.55–0.67, and the
manifest reported that as `screen-not-found`. Widened in `configs/defaults.yaml`
rather than per-video: nothing about it is specific to this recording, and any
handheld video would have hit the same wall.

**Still open:** the manifest says `screen-not-found` when a candidate was found
and then rejected on aspect. Those are different problems with different fixes,
and the message should say which — the aspect case should report the measured
ratio and the bound it missed.

---

## DEC-025 — Cross-frame corroboration comes from dedupe's grouping, not from matching hashes

**[handheld]** Decided 2026-08-18, on the first real video.

`cross_frame` asks whether repeat sightings of one screen get the same name. It
is weighted 0.3 — joint-largest signal — and on the first real video it was
measured on **0 of 133 screens**. Everything else followed from that: with the
signal absent, coverage rarely cleared `MIN_SIGNAL_COVERAGE`, and 132 of 133
screens escalated to review despite a median confidence of 0.82 against a 0.75
threshold. A one-item catalogue and a 132-item review queue.

The cause was how repeats were recognised. `group_repeat_sightings` matched band
hashes **exactly**, on the reasoning — recorded in its own docstring — that a
distance threshold had been tried and could not separate same-screen from
different-screen pairs. That reasoning was right, and measuring it on real
footage rather than on a fixture only sharpens it:

| | same-name pairs | different-name pairs |
| --- | --- | --- |
| median hash distance | 70 | 83 |
| caught at `<=12` | 1 of 1081 | 0 |
| caught at `<=24` | 33 | 28 false merges (precision 0.54) |

Exact matching produced **zero** collisions across 133 screens — camera
micro-motion guarantees no two handheld frames are ever bit-identical. Loosening
the threshold is a coin flip. Neither end of the dial works.

**Decided:** stop trying to recognise repeats from pixels. Stage 04 has already
grouped them — every screen record holds the frames dedupe folded into it, and
those are genuinely different photographs of the same screen. Stage 06 reads a
second one and compares the two names.

- **The grouping comes from dedupe, not from the names being compared.** An
  earlier proposal — group by hash distance *and* require the names to agree —
  was rejected as circular: it would have scored every group 1.0 by construction,
  which is worse than the signal being absent, because it looks like evidence.
- **The frame chosen is the one furthest in time from the representative.** Two
  adjacent frames are nearly the same photograph, and agreeing about them
  corroborates almost nothing.
- **It costs roughly double the model calls for stage 06**, so it is
  `identify.corroborate` and can be turned off. Off is honest, not cheap: the
  signal reports unmeasurable and drops out of the average rather than scoring
  zero — but most screens then lack the evidence to be accepted at all.
- `group_repeat_sightings` and its band-hash plumbing are deleted rather than
  left unused. The reasoning that made exact matching look right is preserved
  here, which is where someone will look for it.

**Still open:** every screen on this corpus has at least two frames (133 of 133),
so corroboration is always available. A screen seen in a single frame would have
none, and would be unacceptable for want of evidence. That is the correct
outcome, but it has not been observed yet and may need a second look when it is.

---

## DEC-026 — `section` is a hint, and a prompt fix for it made things worse

**[handheld]** Decided 2026-08-20, after two mis-attributed frames.

The `section` field records which row of a left navigation list is selected. On
sidebar-driven screens it *is* the screen's identity — two views share a heading
and differ only by the highlighted row — so a wrong value is not a cosmetic
error, it names the wrong screen.

Twice, on two different activities, the model reported a section that was not
the selected row. Both were plausible: the reported name was a real row in the
same sidebar, on the right page, at a confidence indistinguishable from the
correct reads around it. One came from a card *titled* like a section; the other
from the row below the highlighted one. A human found both by measuring where
the accent bar sits.

**What was tried.** Prompt v3 tightened the field: read the marked row and
nowhere else, a heading in the content panel is not a section even when the
sidebar contains a row of that name, an unmarked sidebar means null. The
observed failure was quoted in the prompt.

**What happened.** Measured over four trials on a frame whose truth was verified
at 3.4x:

| | trials | correct |
| --- | --- | --- |
| v2 | Packaging, Packaging, Packaging, Billing | 3/4 |
| **v3** | None, Billing, Billing, Overrides | **0/4** |

The fix made it worse, and it was shipped as the default before being measured.
The extra prohibitions appear to have made the model doubt a read it was
otherwise getting right — telling it a plausible-looking answer might be wrong
did not make it more accurate, it made it less certain about the correct one.

**Decided:**

- **Revert to v2.** v3 stays in the table, marked superseded, because a log that
  cannot show what was rejected is not much of a log.
- **`section` is a hint, not a measurement.** It is useful for grouping and for
  drawing attention; it must not be treated as the identity of a screen without
  a human confirming the accent bar. The four trials above also show it is not
  deterministic at v2 — 3/4, not 4/4.
- **Stop naming evidence by it.** Both failures reached a downstream consumer
  because a file was *named* from the model's reading, which turned a hint into
  an assertion nobody re-checked. Evidence ships under its frame id, and the
  section is stated as a claim to verify.
- **No further prompt tuning without a measured baseline.** This change was
  reasonable, well-argued, and wrong, and only trials showed it. A prompt edit is
  a tuning change and gets the same evidence bar as a threshold.

**Rejected:** raising `confidence.weights` scrutiny of `section`, or gating it
behind a legibility floor. Neither addresses the failure — every wrong read here
was of a perfectly legible sidebar. The model was not struggling to see; it was
answering a different question.

**Amended 2026-08-21 — it is every chrome-structure field, not just `section`.**

A second pass over v01 put three more `section` misreads on the record, both by
the mechanisms above: two frames of a scrolled `Related Information` panel
reported as `Dispense Prep` and `Calcium Phosphate Solubility` (the panel's first
*card* title), and a `Packaging` frame reported as `Billing` (the expanded parent
row above the accented one). Five cases now, no new mechanism. The consuming
project caught all three by measuring the accent bar, which is what this entry
already tells a reader to do.

`tabs` fails the same way and was not covered:

- **It flattens nesting.** A dialog with three tabs, one of which has five
  sub-tabs, came back as one list of eight. Both levels were legible; nothing was
  guessed; the hierarchy was simply discarded.
- **It occasionally adds a member.** A four-tab strip came back with a fifth
  (`AQS` beside a real `ADS`).

Both landed at 0.79–0.82, inside `accept_threshold`, exactly as the `section`
failures did. So the scope of this decision widens: **no chrome-structure field —
`section`, `tabs`, `dialog` — is a measurement.** Each is a hint that points a
human at a frame, and none may be treated as an assertion without one.

**Still rejected: fixing it in the prompt.** The v3 trial above is the reason.
Any future attempt needs a measured baseline over repeated trials first, per this
entry's last bullet — and a flattening failure suggests the schema, not the
prompt, is the thing that cannot express a nested tab row.

---

## DEC-027 — Sample rate is a two-pass strategy, and 1 fps is the first pass

**[handheld]** Decided 2026-08-21, after running one video at both rates.

`sample.fps` was raised from 1.0 to 2.0 on v01 on the argument that a screen
visible for under a second can fall between samples — the toolbar's activity menu
appeared in one frame of 609, and a second either way would have lost every
activity name in the module. Reasonable, and untested until both rates had run.

**What the paired runs measured.** Same video, same code, same cache, all stages:

| | 1 fps | 2 fps |
| --- | --- | --- |
| frames sampled | 609 | 1219 |
| screens after dedupe | 133 | 145 |
| distinct names | 22 | 21 |
| accepted | 53 | 46 |
| review spans | 209 | 236 |

Doubling the rate found **one** thing the 1 fps pass did not surface: a second
toolbar menu, open for about a second. It cost twice the disk, twice the runtime,
and 47 fixture regressions (DEC-028).

**And that one find was not a sampling failure.** The 1 fps pass *sampled* that
second — the frame is in `frames/clean/`. Stage 04 folded it into the neighbouring
screen and elected the menu-shut frame as representative, so it never reached the
model. The lever was `dedupe.min_gap_frames` and representative selection, not
`sample.fps`. Raising fps happened to dodge a dedupe choice, which is why it
looked like it worked.

The rate also moved every screen's representative instant, which is what produced
the regression wall — a cost paid on every fixtured video, forever, in exchange
for one frame.

**Decided:**

- **1 fps is the default and the first pass.** It is enough to catalogue screens,
  pages and modals, which is what the first pass is for.
- **A 2 fps sweep is a deliberate second pass**, run when the first pass leaves a
  specific question — a suspected short-lived screen, an unexplained gap in the
  timeline — and compared against the first pass rather than replacing it. Keep
  the two runs in separate output roots (`REFRAME_OUT_ROOT`) so neither
  overwrites the other; v01's 2 fps pass overwrote its 1 fps outputs and only the
  fixture survived.
- **A missing short-lived screen is a dedupe question first.** Check
  `dedupe.min_gap_frames` and which frame a screen elected as representative
  before reaching for the sample rate.

**Rejected:** 2 fps as the default. One find per doubling, against a permanent
fixture-comparison cost, is not a trade worth making on every video. Also
rejected: deleting the 2 fps run. It is the evidence for this entry, and the
second pass is a real part of the workflow now.

---

## DEC-028 — A fixture carries the rate it was recorded at, and comparison uses the coarser

**[handheld]** Decided 2026-08-21.

A fixture pins a screen's name to a timestamp. A screen occupies a *span*, and
the pipeline records one instant inside it — the representative frame's. Change
the sample rate and that instant moves, so the same screen compares as a
different one.

Tolerance was already expressed in sampling intervals rather than seconds, which
holds while the rate does not change. Scaling it to *the run's* rate is backwards:
raising fps makes the drift larger and the tolerance smaller, exactly when it
needs to be wider.

**Decided:**

- A fixture records `sample_fps`, the rate it was recorded at. Absent means "the
  run's rate", which is the old behaviour and correct whenever the rate is
  unchanged.
- Comparison takes the interval from the **coarser** of the two rates.

**What this does not fix, measured.** With the tolerance widened from 1 s to 2 s,
a 1 fps fixture against a 2 fps run still reports 47 regressions on v01 — 22 of
them "screen no longer detected". At the finer rate dedupe re-partitions the
timeline, so a screen the fixture pins at 09:00 may not exist as a screen at
09:00 at all; it has become two screens at 08:57 and 09:01, and one of them is
unnamed. **Widening a window cannot survive a re-partition.** Matching a fixture
against a screen's span rather than its representative instant would, and is not
built.

So the honest statement is that a fixture validates the rate it was recorded at.
Cross-rate comparison is *less* wrong than it was, not right. Under DEC-027 that
is tolerable: the first pass is always 1 fps, so fixtures and runs agree by
default, and a 2 fps sweep is read as a comparison rather than gated by verify.

**Rejected:** re-recording every fixture at every new rate — it discards the
human corrections in the file, which are the whole point of a fixture. Also
rejected: dropping the timestamp and matching on name alone, which would stop
`verify` noticing a screen that moved to a different part of the video.

---

## DEC-029 — The model's output ceiling is a tunable, because reasoning spends it

Decided 2026-08-21.

The per-request output cap lived in `model/client.py` as a constant, at 16000,
with a comment reasoning that "a sheet of 20 short records needs a fraction of
it". That arithmetic is right about the answer and silent about the reasoning.

On a reasoning model the ceiling covers the thinking as well as the reply. A
full-frame read of a dense screen exhausted 16000 before finishing the JSON, and
the SDK surfaced the truncation as a parse error — which reads as *the model
returned nonsense* when it means *the model ran out of room*. Those have
different fixes and only one of them is a config change.

**Decided:**

- `identify.max_output_tokens` is a tunable in `configs/defaults.yaml`, default
  48000. It is a ceiling, not a target: calls that do not need it are unaffected,
  so raising it costs nothing and lowering it caps spend at the price of
  truncation.
- The OpenAI backend detects a mid-JSON cutoff and raises a `ModelError` that
  names the key and its current value, and says that on a reasoning model the
  budget covers reasoning too.
- It is **not** part of the response cache key. The cache is keyed by what was
  *sent* — image, prompt text, prompt version, provider/model. A ceiling that was
  not reached changes nothing about the answer, and putting it in the key would
  discard every cached response on a spend adjustment.

**Rejected:** retrying automatically at a higher ceiling. It hides a
misconfiguration behind a doubled bill, and the error already says which key to
move.

---

## Open questions

Not yet decided. None block starting.

- **Tool name.** *Reframe* is a working title — it is literally what stage 02
  does, and what the tool does to the footage.
- **Where outputs land.** Writing into `rl_epic/docs/reference/<module>/` keeps
  them beside the evidence folders already there. Leaning yes.
- **OCR engine.** Tesseract is the default assumption; the choice should be
  re-made after seeing how one real frame actually renders.
- **Capture resolution.** If the laptop ran at a high resolution, text will be
  physically small in frame and OCR will struggle more. May push `sample.fps` or
  the montage crop. Checkable on the first frame.
- **How a fixture records a read the model gets wrong every time.** This one is
  blocking a checklist item, so it needs deciding soon. v01's fixture carries two
  hand-corrections — `Package` → `NDC Admin`, `Orderable medication` →
  `Dispensable Mapping`. The model still reads the uncorrected value, and will on
  every future run, so `verify` reports two regressions forever and "shows no
  regressions" in the pre-commit checklist can never be satisfied. A permanent
  known-wrong read is not a regression; it is a standing defect, and the fixture
  has no way to say so. Options: a `known_misread` field that reports separately
  and does not fail the gate; treating a corrected entry as expected-to-differ;
  or accepting a non-zero floor and stating it per video. The first looks right
  but none is measured, and picking wrong makes `verify` either noisy or blind.
