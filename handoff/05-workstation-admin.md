# Build brief 05 — Workstation Admin (and read-only mode)

**Branch:** `pharmacy-admin` — same branch as 01–04.
**Read briefs 03 and 04 first.** Same page shape again; only the differences are
here. The new thing is **read-only mode**, which is a page state rather than an
activity, and appears on other activities too.

**Verification:** the operator replays the source recording against the built
page. Trust the images over this text.

## Evidence

```
~/build-evidence/05-workstation-admin/
  f_000303-t05m03s.jpg      Prescription Printing
  f_000306-t05m06s.jpg      Prescription Printing
  f_000308-t05m08s.jpg      Scanner Settings
  f_000310-t05m10s.jpg      Point of Sale Settings
  detail-mode-toolbar.jpg   heading, mode bar and lock banner, 2.4x
  detail-sidebar.jpg        the three-node tree, 3.4x
  detail-value-list.jpg     the field row with a value, and the list box, 2.1x
```

Files are named by frame id. The section beside each is a claim to check against
the sidebar's accent bar — two frames in earlier briefs were filed wrong because
a name was trusted instead of measured.

**`f_000303` is a mid-load frame** — a spinner over a double-rendered pane, with
the whole footer drawn undisabled. It cannot corroborate any enabled/disabled
reading. Use it for layout only.

In the page chrome, `?` help, `✕` close and the header `Search` all measure
**enabled**; the `← →` back/forward pair and the `⋯` overflow measure greyed.

---

## What this is

Reached as: hub → `Rx Admin ▸ Workstation Admin` → picker → this page.

Record `EPICSUPPORT [1]`, four frames across **ten seconds** — the shortest
visit in the recording. All three sections were opened, so unusually this
activity is **completely covered**.

---

## Read-only mode — the reason this brief exists

The whole page is in a read state, and it is signalled three ways at once.

### A mode toolbar, under the heading

`✎ Edit` · `🔭 Read-Only` · `🖥 Open Workstation`

The `Read-Only` glyph is **binoculars** — two barrels joined by a bridge, clear
at 7x. Not a padlock. The padlock is real but belongs to the banner line below.

`Read-Only` is the **selected** one — a filled accent block with a light glyph
and label, carrying a light outer ring and rounded corners. The three read as a
segmented mode control, not three loose buttons.

`Jump to an item (Alt+F9)` and its `Search` button sit on **this row**, not the
heading row — roughly 6–14px from the mode bar and 36–58px from the heading,
slope-corrected across the settled frames. Briefs 03 and 04 have no mode bar and
put them beside the heading; do not unify them.

### A lock banner

Directly beneath: `🔒 Activity is currently read-only.` Plain text with a lock
glyph, no coloured background.

### The footer loses a button

Brief 03 and 04 have `Open Another <Record type>` at the footer's left. Here
that is **absent** — `Open Workstation` sits in the mode toolbar instead. The
footer's left holds only `⏮ Restore`, greyed.

`Previous F7` / `Next F8` / `Accept` are unchanged. `Next F8` is greyed on
`Point of Sale Settings`, the last of three nodes — the positional behaviour
holding again.

**What read-only does to the inputs was not directly demonstrated.** The
checkboxes look greyed and no field was typed into, but nothing was clicked to
prove it. Render them non-interactive and say the enforcement is unverified.

---

## The activity tab carries the record

Briefs 03 and 04 have a tab reading the activity name — `Hospital/Clinic Admin`,
`Medication Admin`. Here the tab reads **`Workstation: EPICSUPPORT`**, the
record. Do not normalise this; it is what the reference shows.

---

## The tree — 3 nodes, flat

```
Prescription Printing
Scanner Settings
Point of Sale Settings
```

No groups, no children, no scrolling. All three observed.

---

## Controls not in briefs 03 or 04

### A value inside an ordinary field row — not its own control

`Primary Screen [2]` under `Customer Sale Completion Method` looks like a
bespoke control and is not one. It is the value sitting in a standard
full-width field row: the row measures 37px between two parallel full-width
rules, `Print Receipt by Default` further down the same panel is that identical
row with nothing in it, and `Scanner Name` is a third instance.

The value itself renders as a filled accent block with a thin light outline,
flush to the field's left edge. **Do not build a new component for it** — it is
the existing field row with a selected value in it.

What the unselected members are, and how one is chosen, is not observable.

### Multi-row list box

A bordered box holding stacked rows, no column headers:

```
Not Required [3]
Electronic Signature [1]
(an empty row, shaded)
```

Under `Available Signature Methods`. The trailing empty shaded row suggests an
add slot, but nothing was clicked. Distinct from brief 03's tables — no headers,
no row numbers, no row-action buttons.

---

## Observed section contents

Read the fields off the images. `Point of Sale Settings` is the fullest:

**Point of Sale Settings** — fieldset `Point of Sale Settings`; sub-heading
`Signature Settings`; sub-heading `Customer Sale Completion Method` with the
selected-value row `Primary Screen [2]`; ☐ `Show prescription names by default
to pharmacy customers`; ☐ `Show patient names by default to pharmacy customers`;
sub-heading `Available Signature Methods` with the list box above; sub-heading
`Print Receipt by Default` with an empty field; sub-heading `Cash Drawer`
*(cut off at the fold — do not invent its contents)*.

**Scanner Settings** holds two controls not otherwise in these briefs: a
three-member segmented group `Scanner Type` — `WIA` · `TWAIN` · `None`,
equal-width, `WIA` current — and a **field pair** putting `Color Scheme` and
`Resolution (DPI)` side by side on one row.

`Prescription Printing` has its own frame; transcribe from it.

---

## Rules carried forward

- **Do not manufacture content** — for `Cash Drawer` below the fold, or for the
  list box's empty row.
- **Do not complete clipped text.**
- **Blank is the observed state** for most fields.
- **Render the observed enabled/disabled state**; put undemonstrated behaviour
  in the tooltip.

---

## Known unknowns

| Unknown | Why |
| --- | --- |
| Whether read-only actually blocks input | nothing was typed or clicked |
| What `Edit` switches to | never clicked — the whole visit is read-only |
| What `Open Workstation` opens | never clicked |
| `Cash Drawer`'s contents | below the fold |
| The other values `Primary Screen [2]` selects among | only the selection is shown |
| Whether the list box's empty row adds | never clicked |
| Whether other activities can be read-only | see below |
| The table columns after `Tray` | ~63% of the table is off-view and it was never scrolled |

On read-only being shared: `Medication List Admin` is **also** read-only in this
recording, with a differently-worded banner. So read-only is a page state that
several activities can be in, not something specific to this one. Build it as
shared state rather than a Workstation feature — brief 06 covers the other case.

---

## Definition of done

- Route under the activity, reached from the picker with a record id
- Activity tab reads `Workstation: <record name>`, not the activity name
- Heading reads `Workstation: <record name> [<id>]`
- Mode toolbar with `Read-Only` shown selected, plus the lock banner
- Footer has **no** `Open Another …`; `Restore` greyed; `Next F8` greyed on the
  last node
- Three-node flat tree, all three sections rendering their observed controls
- Selected-value row and multi-row list box built as reusable controls, since
  read-only state is shared with at least one other activity
- Every unknown left visibly incomplete and listed when you report back
