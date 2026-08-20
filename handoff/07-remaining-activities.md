# Build brief 07 — the four barely-observed activities

**Branch:** `pharmacy-admin` — same branch as 01–06.

**Read this framing before anything else.** These four activities were visited
in passing at the end of the recording: one has five frames, the other three
have **one frame each**. This brief is deliberately thin, and it is thin because
the evidence is. Three of the four will be mostly not-captured panels, and that
is the correct outcome — not a gap to fill in.

Do not treat "one frame" as "enough to infer the rest."

## Evidence

```
~/build-evidence/07-remaining-activities/
  f_000522-t08m42s.jpg  \
  f_000524-t08m44s.jpg   |
  f_000526-t08m46s.jpg   |  Dispensable Mapping — 5 frames
  f_000528-t08m48s.jpg   |
  f_000530-t08m50s.jpg  /
  detail-dm-grid.jpg     its grid, 1.7x
  detail-dm-form.jpg     its lower form, 1.9x

  f_000548-t09m08s.jpg   NDC Admin        — one frame
  f_000577-t09m37s.jpg   Package          — one frame
  f_000601-t10m01s.jpg   Build Wizard     — one frame
```

Named by frame id. Everything below is a claim to check.

---

## 1. Dispensable Mapping — a fourth archetype

Five frames, 08:42–08:50. Reached from the hub through the picker.

**Not a sidebar page and not a tabbed page.** A grid above a form, no left nav
at all. Do not force it into `AdminRecordPage` or the med-list component.

### Heading

`Orderable medication: HEPATITIS B VAC RECOMBINANT IJ ORDERABLE [207570]`

Note the label is **`Orderable medication:`**, not the activity name. Briefs
03–06 all label the heading with the activity; this one names the record type
instead. That is why the pipeline catalogued one of these frames as a separate
activity called "Orderable medication" — it is not one.

### Upper grid

Columns: `Dispensable Drug` · `Patient Age` · `Patient Weight` · `Patient Rule` ·
`Dose` · `Routes` · `Order Mode` · `From …` *(clipped at the frame edge — more
columns exist)*.

Rows are numbered. Each `Dispensable Drug` cell carries a **double-chevron
expander** before its text. Observed rows:

| # | Dispensable Drug | Patient Age | Patient Rule | Order Mode |
| --- | --- | --- | --- | --- |
| 1 | VFC HEPATITIS B VAC RECOMBINA… *(clipped)* | 0 Years to 19 Years | VFC Eligible IP Rx | IP |
| 2 | VFC HEPATITIS B VAC RECOMBINA… *(clipped)* | 0 Years to 19 Years | VFC Eligible IP Rx | IP |
| 3 | VFC HEPATITIS B VAC RECOMBINA… *(clipped)* | 0 Years to 19 Years | VFC Eligible IP Rx | IP |
| 4 | HEPATITIS B VAC RECOMBINANT 5 *(clipped)* | — | — | IP; OP |

`Patient Weight` and `Dose` are empty on every observed row.

Rows 1–3 carry a band that rows 4+ do not. Whether that is a multi-row
selection, a grouping, or something else is **not determinable** — do not model
it as selection without more evidence. This is the same trap as brief 06's dot
tints.

### Row actions

`Insert Row` · `Delete Row` · `Move Up` · `Move Down` — all four appear greyed.

**Different labels from brief 04's** `Insert (F4)` / `Delete (Shift+F4)`. Same
concept, different words. Do not unify them.

Right-aligned on the same row: `Test Mapping`.

### Lower form

- `Medication unit:` → `mL`, with a magnifier, then a `✎ Edit Orderable Record`
  button
- `Prescribable?` → `Yes` — a label/value pair on the right, no input
- `Failsafe dispensable drug:` → `HEPATITIS B VAC RECOMBINANT 10 MCG/ML IJ SUSY [187817]`
- `Outpatient failsafe dispensable drug:` → the same value
- `Edit rate, administration duration, and label comments when placing orders:` →
  empty
- An ⓘ callout: *"Editing rate, administration duration, and label comments is
  DISABLED. All default values will come from the selected dispensable record."*

### Footer

`📂 Open` on the left; `✔ Accept` · `✕ Cancel` on the right. No `Restore`, no
`Previous`/`Next`, no `Open Another …`.

---

## 2. NDC Admin — one frame

`f_000548-t09m08s.jpg`. A **sidebar page** — same archetype as briefs 03–05, so
it should reuse `AdminRecordPage` with its own tree and content.

**Transcribe the tree and the visible section from the frame.** I am not
summarising it here: with one frame and no second view to cross-check, my
reading would be a single unverified source, and this brief has already been
wrong twice from exactly that.

Everything not visible in that one frame is not captured.

---

## 3. Package — one frame

`f_000577-t09m37s.jpg`. Also a **sidebar page**. Record
`9999990180 (Active) (CEFOT…)` — note the record carries a status in parentheses,
which no other activity's record does.

The visible section shows an `Identity Settings` table above `ADS Settings`
fields. Its sidebar row is `Identity/ADS`.

**That name also appears in Medication Admin's tree** (brief 04), where it was
never opened. They are different activities — **do not borrow this content for
that one.** Brief 04 says so explicitly.

Transcribe from the frame; everything else is not captured.

---

## 4. Build Wizard — one frame, an empty state

`f_000601-t10m01s.jpg`. Reached from the hub's `Common Links ▸ Build Wizard`
(brief 01).

Three things worth noting:

**It opens a new workspace.** The workspace tab reads `Build Wizard`, not
`Pharmacy Admin` — the only place in the recording where that tab changes. The
tab also carries a **spinner** beside its label, so the frame is mid-load; treat
its chrome states with the caution brief 05 established for `f_000303`.

**The activity tab reads `Build Wizard List`** — the workspace and the activity
have different names.

**The content is an empty state:** a centred wand-and-sparkles illustration
above the text `No features match the current filters`.

That wording implies filters exist and are set. **No filter control is visible
in the frame** — there are two collapsed side panels, one at each edge, each
showing only a `‹` chevron. Whether the filters live in those panels is not
observable.

Build the empty state. Do not build filters you cannot see.

---

## Rules carried forward

- **Do not manufacture content** from one frame. Three of these four have one
  frame; almost everything about them is not captured.
- **Do not model the banded rows as selection** without evidence.
- **Do not complete clipped text** — several grid cells and the `From …` column
  are cut at the frame edge.
- **Render the observed enabled/disabled state**; behaviour in the tooltip.

---

## Known unknowns

| Unknown | Why |
| --- | --- |
| Everything about NDC Admin beyond one frame | one frame |
| Everything about Package beyond one frame | one frame |
| Build Wizard's populated state, and its filters | only the empty state was seen, and no filter control is visible |
| What the two collapsed panels on Build Wizard hold | never expanded |
| What the band on Dispensable Mapping rows 1–3 means | could be selection, grouping, or neither |
| Dispensable Mapping's columns after `From …` | clipped at the frame edge |
| What the row expanders reveal | never expanded |
| What `Test Mapping` does | never clicked |
| Why all four row actions are greyed | nothing on screen explains it |
| Whether Build Wizard's spinner means the frame is mid-load | it is; the frame may not show a settled state |

---

## Definition of done

- Dispensable Mapping: its own component — grid over form, no sidebar, no tabs —
  reached from the picker, with the observed grid, row actions, `Test Mapping`,
  lower form and ⓘ callout
- NDC Admin and Package: `AdminRecordPage` with trees and content transcribed
  from their single frames, everything else explicitly not captured
- Build Wizard: a new workspace tab, activity tab `Build Wizard List`, and the
  empty state with its illustration and text
- Every unknown above left visibly incomplete and listed when you report back
- **No content invented for the three single-frame activities.** If a page looks
  sparse, that is the recording, not a defect
