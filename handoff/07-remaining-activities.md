# Build brief 07 — the three barely-observed activities

**Branch:** `pharmacy-admin` — same branch as 01–06.

**Read this framing before anything else.** These activities were visited in
passing at the end of the recording: one has five frames, one has two, one has
one.

**An earlier revision of this brief listed four activities. There are three.**
`Package` is not an activity — it is the record-type label in **NDC Admin's**
heading. Same trap this brief documents for `Orderable medication:` one section
later, walked into two sections earlier.

This brief is deliberately thin, and it is thin because the evidence is. Two of
the three will be mostly not-captured panels, and that is the correct outcome —
not a gap to fill in.

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

  f_000548-t09m08s.jpg   NDC Admin — mid-load, contributes the tree only
  f_000577-t09m37s.jpg   NDC Admin — the settled frame ("Package:" is its record)
  f_000601-t10m01s.jpg   Build Wizard — one frame
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

An earlier revision claimed rows 1–3 carry a band that row 4 does not, and
flagged it as possible selection. **There is no band.** The tint is *columnar*,
not row-wise: a vertical profile reads B-R +18/+19 continuously from y318 to
y480 with no step at any row boundary, and per cell the first column samples
neutral on all four rows while every column right of it samples +14 to +20 on
all four — row 4 included, and highest there.

So the first column is white and editable, the rest tinted and read-only.
**Model nothing as selection; there is nothing to model.**

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
- A **circled `?`** callout — the same help glyph as briefs 03/05/06, not the
  `ⓘ` an earlier revision described: *"Editing rate, administration duration, and label comments is
  DISABLED. All default values will come from the selected dispensable record."*

### Footer

`📂 Open` on the left; `✔ Accept` · `✕ Cancel` on the right. No `Restore`, no
`Previous`/`Next`, no `Open Another …`.

---

## 2. NDC Admin — two frames

A **sidebar page** — same archetype as briefs 03–05, so it reuses
`AdminRecordPage` with its own tree and content.

**Both frames are this activity.** `f_000577`'s heading reads
`Package: 9999990180 (Active) (CEFOTAXIME SODIUM 500 M…` and its activity tab
reads `NDC Admin`. `Package:` is the record-type label, exactly as
`Orderable medication:` is for Dispensable Mapping.

That gives NDC Admin **two frames, not one**, and makes its `Identity/ADS`
section transcribable — an `Identity Settings` table above `ADS Settings`
fields. An earlier revision filed that content under a separate activity.

Note the record carries a status in parentheses — `(Active)` — which no other
activity's record does.

`f_000548` is **mid-load**: no heading rendered, no sidebar row selected, the
panel a skeleton, and the footer drawing everything undisabled. It contributes
the tree and nothing else. Brief 05's `f_000303` rule.

**`Identity/ADS` also appears in Medication Admin's tree** (brief 04), unopened.
That is a third activity again — **do not borrow this content for it.**

Transcribe the tree and the section from the frames; everything else is not
captured.

---

## 3. Build Wizard — one frame, an empty state

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

- **Do not manufacture content** from one frame. Build Wizard has one; NDC Admin
  has one settled frame and one skeleton. Almost everything about them is not
  captured.
- **Read the activity from the activity tab, never from the heading.** The
  heading's prefix is a record-type label. It matched the activity on the first
  four pages and does not here — `Package:` is NDC Admin, `Orderable medication:`
  is Dispensable Mapping. Both phantom activities in the catalogue came from
  this.
- **Do not complete clipped text** — several grid cells and the `From …` column
  are cut at the frame edge.
- **Render the observed enabled/disabled state**; behaviour in the tooltip.

---

## Known unknowns

| Unknown | Why |
| --- | --- |
| NDC Admin's 13 unopened sections | only `Identity/ADS` was opened |
| Build Wizard's populated state, and its filters | only the empty state was seen, and no filter control is visible |
| What the two collapsed panels on Build Wizard hold | never expanded |
| Dispensable Mapping's unseen grid rows | the scrollbar thumb covers ~18% of its track, so ~20 rows exist and 4 were seen |
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
