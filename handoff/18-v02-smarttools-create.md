# Build brief 18 — the two SmartTools create-states

**Branch:** `pharmacy-admin`. Two screens. The last of v02.

**Evidence:** `~/build-evidence/18-v02-smarttools-create/` — 4 frames: the two to
build, plus brief 15's loaded equivalents for contrast. **The contrast frames are
the point** — every field named below is one the loaded view does not have, and
that is how we know these are distinct states rather than the same screens empty.

**Provenance:** rectified handheld footage. Labels, order, control states yes.
Geometry no.

---

## Why these were missed

Both sat in v02's fixture as `SmartTools` — the workspace tab label, read as a
screen name, the same error that produced `Pharmacy Admin` and `Workbench`. I filed
all four as probable tab misreads and did not open them, so brief 15 built five
loaded editors and no create-state.

They are on brief 15's SmartTools shell — icon rail, editor pane, right-hand
`Settings` panel, `Open` / `Preview` footer. Reuse it. What differs is the body and
the Settings fields.

---

## 1. `f_000516` (08:36) — a blank editor with a `Levels` panel

The rail still shows `16676 [21538]` selected under `SmartList`, so a record is
loaded elsewhere while this editor is blank.

- **Editor pane**: the full toolbar — `B` · undo · `?` · `Insert SmartText` ·
  `Insert SmartList` · a list glyph · scissors with caret · `•••` at the right —
  over an **empty body** carrying a single small red `!` glyph at its centre. No
  ruler, unlike brief 15's `System SmartPhrase`.
- **`⚙ Settings`**: `Name` (empty) · `Description` (empty, with
  `Populate from Text` right-aligned) · `Text Format` — **label present, no
  segmented control rendered** · `☐ Released` unchecked
- Then `📖 Synonyms`, collapsed — and **`Levels`**, a green-headed collapsed panel
  that **no built screen has**.
- Footer: `Open` · `Preview` only. No `Create Copy`, no `Save`, no `Accept`, no
  `Cancel` — brief 15's loaded editors all have those.

**Which record type this creates is not settled.** The rail selection points at
`SmartList` but the toolbar is the SmartText/SmartPhrase one, and `Levels` appears
on neither. Seed it under the closest activity and **record the ambiguity** — do not
name it `New SmartList` or `New SmartText` as though the frame said so.

The red `!` is the only red pixel in the frame. What it means is not evidenced.

## 2. `f_000529` (08:49) — the SmartLink create-state

Rail shows `A [103487]` selected under `SmartPhrases`.

- **Editor pane**: the balloon empty state, with a **heart/pulse tile** beside it
  and the caption **`Select a SmartLink type.`** The mountain backdrop is the same
  artwork brief 13's balloon component uses — reuse that component, don't redraw.
- **`⚙ Settings`**: `Name` (empty) · **`Mnemonic`** (empty) · `Description` (empty)
  · `SmartLink Type` — **label only, no control** · `Search Availability ⓘ` —
  **label only, no segmented control** · `☐ Released` unchecked
- Then `📖 Synonyms` and **`Overrides`**, both collapsed.
- Footer: `Open` · `Preview` · `× Close`.

**`Mnemonic` does not exist on brief 15's loaded SmartLink** (`smartlink-f_000538`),
which shows `Refreshable Settings`, `Default Configuration`, `Contexts`,
`Admin Notes` and `Used By SmartTools` instead. That asymmetry is the evidence these
are two states of one screen rather than two screens — model accordingly.

Note `Search Availability` appears here **without** its `Always Available / Build
Only / Never Available` control, where brief 15's `SmartText` renders all three. A
label with no control is what the frame shows; render it that way.

---

## The pattern both frames establish

In a create-state, **segmented controls are absent rather than unselected.**
`Text Format`, `SmartLink Type` and `Search Availability` are labels with nothing
beneath them, where the loaded editors render full segment groups. Brief 13's
`Update Balances` had a segmented group with *no segment selected*; this is a
different thing and should not be flattened into it.

---

## Acceptance

- [ ] Both render on brief 15's SmartTools shell, reusing its rail and Settings
      layout
- [ ] `Levels` exists on `f_000516`'s screen and nowhere else
- [ ] `Mnemonic` exists on the SmartLink create-state and **not** on brief 15's
      loaded SmartLink
- [ ] Labels whose controls are absent render as labels with no control — not as
      unselected segment groups
- [ ] Footers differ from the loaded editors': `f_000516` has only Open/Preview;
      `f_000529` adds `× Close`. No Save/Accept/Create Copy on either
- [ ] The balloon reuses brief 13's component rather than a second drawing
- [ ] `f_000516`'s record type is recorded as **unsettled**, not guessed
- [ ] The red `!` glyph is rendered with its meaning marked unevidenced
- [ ] No geometry measured
