# CLAUDE.md — working rules for this repo

Rules for anyone, human or agent, writing code here. Read
[`ARCHITECTURE.md`](ARCHITECTURE.md) for the design and
[`DECISIONS.md`](DECISIONS.md) for why it is that way.

---

## What this tool is for

Reframe turns handheld phone recordings of a desktop application into a screen
catalogue, a build queue, and a list of timestamps a human must review.

**Its purpose is not to be fast. It is to be honest.** A confident, complete-
looking catalogue with a hole in it is worse than no catalogue, because you
cannot review a gap you were never told about. That failure is on record in the
consuming project and is the reason this tool exists in this shape.

Whenever a design choice trades certainty for coverage, choose certainty and
escalate the rest.

---

## Never fabricate, always escalate (highest priority)

This mirrors the evidence-first rule in `rl_epic/CLAUDE.md` and outranks
everything below.

- **Never emit a value the pixels do not support.** If a screen name cannot be
  read, its record is `verdict: review` with a timestamp — not a plausible guess.
- **Never emit a confident crop of a partially-visible screen.** Flag the span.
- **Never fill a missing field with something reasonable.** Missing is a valid
  state and is always more useful than invented.
- **When a stage cannot do its job, it says so in the manifest** and the
  information reaches `NEEDS_REVIEW.md`. Silent degradation is the one
  unacceptable failure mode.

An error a reviewer can see costs minutes. An error they cannot see costs the
whole point of the tool.

---

## Never do these

| Rule | Why |
| --- | --- |
| **Never extract or emit colour.** | The reference build and the target app have different themes, and the target's theme is locked. Camera white balance makes it worse. See [DEC-011](DECISIONS.md#dec-011--no-colour-extraction-no-data-grid-ocr). |
| **Never OCR data-grid cells.** | An OCR error and a fabrication are indistinguishable downstream. Chrome bands only. |
| **Never emit geometry or measurements.** | Handheld footage cannot support them. See [DEC-010](DECISIONS.md#dec-010--geometry-measurement-is-out-of-scope). |
| **Never hardcode a tunable.** | Thresholds, crops, weights and aliases live in `videos/<slug>/config.yaml`. See [DEC-014](DECISIONS.md#dec-014--tunables-live-in-config-code-holds-no-thresholds). |
| **Never reference the consuming project by name in `src/`.** | Reframe knows nothing about Epic. Project knowledge arrives as `inventory.json`. See [`CONTRACT.md`](CONTRACT.md). |
| **Never use wall-clock time or randomness in stages 00–05, 07, 08.** | Determinism is what makes re-extraction safe. See [DEC-013](DECISIONS.md#dec-013--determinism-and-only-the-deduped-frames-are-committed). |
| **Never silently truncate.** | Caps (`max_frames`, montage limits, model batch sizes) record a warning in the manifest when hit. |

---

## Structure

```
stages/    orchestrate — read manifest, call compute, write manifest
vision/    compute — pure image functions, no pipeline awareness
model/     compute — prompts, client, schema
config.py  parameterise
```

**`stages/` contains no algorithms and `vision/`/`model/` contain no pipeline
logic.** This is what lets stages be tested against a folder of fixture frames
without a video, and lets vision functions be tested without a manifest.

- Each stage is independently re-runnable and must be idempotent.
- A stage reads only what earlier stages wrote. No stage reaches forward.
- Files stay under **500 lines**. Split before you reach it.

---

## Types

- **Full type hints, everywhere. No bare `Any`.**
- Pydantic models for the manifest, config and model output. The manifest is a
  contract between stages and between runs — it gets a schema, not a dict.
- `uv run mypy src` must pass clean before any commit.

---

## Configuration

- `configs/defaults.yaml` holds the baseline. `videos/<slug>/config.yaml` holds
  overrides. Only the resolved result is hashed into the manifest.
- **Every config key needs a comment saying what it does and what moving it
  trades away.** These files are the tuning surface for someone who did not
  write the code — likely months later.
- Adding a tunable means adding it to `configs/defaults.yaml` *and* the config
  reference in `ARCHITECTURE.md`.

---

## The model stage

- Stage 06 is the only stage allowed to call a model.
- **Cache responses** keyed by `(montage_hash, prompt_version, model)`. Re-running
  without changed inputs replays the cache.
- **Bump `prompt_version` whenever the prompt changes.** An unchanged version
  with a changed prompt silently serves stale cache and makes a tuning round
  meaningless.
- Prompts live in `model/prompts.py` as versioned constants, never inline.
- **Confidence is never the model's self-report.** It is computed in
  `confidence.py` from independent signals. See [DEC-009](DECISIONS.md#dec-009--confidence-is-signal-agreement-not-model-self-report).

---

## Testing

- `vision/` functions get unit tests against committed fixture frames.
- Stages get tests against a small synthetic manifest — no video required.
- **`reframe verify` must pass before any tuning change is accepted.** It re-runs
  every video that has a fixture and reports regressions. A change that improves
  video 3 and breaks video 1 is not an improvement.

---

## When a decision changes

Add or amend an entry in [`DECISIONS.md`](DECISIONS.md) — do not bury the
reasoning in a commit message or a code comment. Mark superseded entries rather
than deleting them; knowing what was tried and rejected is most of the value of
the log.

Decisions marked **[handheld]** are forced by the current corpus being phone-of-
monitor footage. If a native screen recording ever arrives, those are the ones
to revisit first — several would flip.

---

## Commands

```bash
uv sync                            # install
uv run reframe init <video> --slug <slug>
uv run reframe run <slug>          # all stages
uv run reframe stage 04 <slug>     # one stage
uv run reframe fixture <slug>      # record validated ground truth
uv run reframe verify              # regression-check every fixtured video
uv run mypy src                    # type check
uv run pytest                      # tests
uv run ruff check src              # lint
```

---

## Before committing

- [ ] `uv run mypy src` clean
- [ ] `uv run ruff check src` clean
- [ ] `uv run pytest` passing
- [ ] `uv run reframe verify` shows no regressions
- [ ] No hardcoded thresholds — all tunables in config, documented
- [ ] Files under 500 lines
- [ ] New/changed decisions recorded in `DECISIONS.md`
