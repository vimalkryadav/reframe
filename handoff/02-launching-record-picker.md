# Build brief 02 — the "Launching …" record picker

**Branch:** `pharmacy-admin` — same branch as brief 01.
**Verification:** the operator replays the source recording against the built
screen. Trust the images over this text; brief 01 had five descriptions that
did not survive magnification, and the build session was right every time.

## Evidence

```
~/build-evidence/02-launching-modal/
  a-compact-ndc-admin.jpg          variant A, over the hub          (08:57)
  a-compact-detail.jpg             variant A at 2.4x
  b-picker-med-list-admin.jpg      variant B — Formulary            (05:26)
  b-picker-medication-admin.jpg    variant B — Medication           (06:06)
  b-picker-workstation-admin.jpg   variant B — Workstation          (04:58)
  b-picker-dispensable-mapping.jpg variant B — Medication, grouped  (08:40)
  b-footer-detail.jpg              variant B footer at 2x
```

---

## What this actually is

Not a progress dialog. **It is Epic's record-selection gateway** — every admin
activity opens by asking which record to work on, and the activity underneath
then shows that record. This is why page headings read
`Medication: 2-DEOXY-D-GLUCOSE POWD [25782]` rather than just `Medication`.

```
Willow Project Team ──▸ Launching <Activity> ──▸ <Activity> for the chosen record
```

Nothing in the module is reachable without it, which is why it comes before the
activities themselves. It appears **17 times** across ten minutes.

### Look at `LookupModal.tsx` first

`frontend/components/shell/LookupModal.tsx` and its siblings
(`PatientLookupModal`, `GuarantorLookupModal`) already implement search-then-pick
in this repo. This is very likely a new configuration of that component, not a
new component. If it is not a fit, say why rather than duplicating it.

---

## Two variants

### Variant A — compact lookup

Observed once, on **NDC Admin** (`a-compact-detail.jpg`). A small centred
dialog over the page, which stays visible around it — and **not dimmed**.
Measured: the hub's three regions read 171 behind the dialog against 180
unobstructed, which is exposure drift, not a scrim. A 30% scrim would read ~126.

- Title bar: `Launching NDC Admin`, `✕` at the right
- A help paragraph, verbatim:
  > You can look up an NDC record in dashed format (00001-0001-11) or in raw 11
  > digit format (00001000111). To find an NDC record by Chronicles ID, prepend
  > a "C." (C.12345). To find an NDC record via Identity IDs, prepend the
  > Identity ID type abbreviation (CABID.12345).
- One labelled field `NDC:` with a **magnifier inside the field's right edge** —
  no separate Search button
- A read-only panel `NDC Information`, four label/value rows, all `N/A` before a
  record is picked: `NDC:` · `Medication:` · `Package size:` · `Manufacturer:`
- Footer: `➕ Create New` on the left; `✎ Edit` (greyed) and `✕ Cancel` on the right

### Variant B — record picker

Observed on four activities. A large dialog filling most of the window, its top
edge just below the Epic title bar.

Earlier revisions of this brief called the surround a dark scrim. It is not —
its luminance swings 38 / 71 / 124 / 158 across the four frames, which is the
off-screen bezel of the photographed monitor, not anything the page renders.
The dialog covers everything behind it, so variant B's real backdrop was never
observable; use the repo default.

- Title bar: `Launching <Activity>`, `✕` at the right
- A label on its own row; below it an empty text input and a `🔍 Search` button
  **joined together**, no gap between them
- A results grid, already populated before any search
- Row selection highlights the **entire row** in blue
- Hovering a row shows a tooltip with that row's full text (seen on Med List
  Admin, where names are clipped)
- A vertical scrollbar
- Footer left: `Records loaded: 30. More records to load.`
- Footer right: `✔ Accept` · `✕ Cancel`
- Buttons carry keyboard accelerator underlines, legible at 6x: `A̲ccept`,
  `C̲ancel`, and `r` on both create buttons (which is why it does not collide
  with Cancel). `Edit`'s accelerator is illegible even at 2.4x — render it
  without one rather than guessing.

---

## Per-activity parameters

Everything below is the same component with different inputs.

**The dialog title is not always the activity name.** Verified at 5x: the menu
reads `Medication List Admin` and `Dispensable Mapping Admin`, while the dialogs
read `Launching Med List Admin` and `Launching Dispensable Mapping`. Epic
shortens some of them. Store both — keying config on the dialog title makes
those two activities unreachable from the menu.

| Activity (menu name) | Dialog title | Field label | Grid columns | Create button |
| --- | --- | --- | --- | --- |
| Medication List Admin | Launching **Med List Admin** | `Formulary:` | Formulary Name · Formulary ID | **`➕ Create a New Record`** |
| Medication Admin | Launching Medication Admin | `Medication:` | ID · Name · Generic Name | none |
| Workstation Admin | Launching Workstation Admin | `Workstation:` | Workstation Name · Type · Identifier · ID | none |
| Dispensable Mapping Admin | Launching **Dispensable Mapping** | `Medication:` | ID · Name · Generic Name | none |
| NDC Admin | Launching NDC Admin | `NDC:` | *(variant A — no grid)* | `➕ Create New` |

**Only Med List Admin shows a create button in variant B.** Do not add it to the
others — that is observed, not an oversight.

### Grid grouping

`Dispensable Mapping` renders a full-width group header row reading
`All Available Records` above its first data row. None of the other three shows
one. Treat grouping as a capability of the grid that this activity switches on.

### Column widths are uneven and content-driven

`Medication Admin` puts `ID` and `Name` at the far left and `Generic Name` about
half way across, leaving a wide gap. `Workstation Admin` spaces four columns
across the full width. Do not normalise these into equal columns.

---

## Loading behaviour

`Records loaded: 30. More records to load.` is present on **every** variant-B
frame, always reading 30, and the operator scrolls without it changing. So:

- The grid loads a first page of 30
- More exist and load on demand
- The footer states the count loaded so far and whether more remain

What was **never observed**: the message after a further page loads, and whether
loading is triggered by scroll or by a control. Build the first page and the
message; leave the load trigger unresolved and say so.

**Do not manufacture rows to reach 30.** Only 13–14 rows per set are legible in
the frames. Seeding the rest would put invented masterfile records into the
build, which is worse than a count that does not match the reference. Expect two
honest consequences: the footer reads the real count, and the grid's scrollbar
does not appear because the rows fit.

---

## Sample data — seed, do not hard-code

Real values from the frames, useful as seed rows so the screen looks right on
replay. This is demo-environment content.

**Formulary** — `EMC OPH SUBSPECIALTIES MEDICATION ROOM` 194 ·
`EMC PRESCRIPTION CENTRAL FILL` 104 · `EMC PRESCRIPTION CENTRAL FILL (AUTO-GENERATED)` 57 ·
`EMC PRESCRIPTION CENTRAL FILL APFS` 103 · `EMC PRESCRIPTION HOSPICE PHARMACY (AUTO…)` 38 ·
`EMC PRESCRIPTION MAIL PHARMACY (AUTO-GENERATED)` 58 ·
`EMC PRESCRIPTION MIXTURE PRINT SUPRESSION LIST` 100 *(sic — one "P")* ·
`EMC PRESCRIPTION PATIENT ID MEDICATIONS` 109 · `EMC PRESCRIPTION PHARMACY NORTH` 102

**Workstation** — `KC EMH HOSPITAL ARRIVAL` / Workstation / — / 456 ·
`K ROOT` / Workstation / — / 458 · `K EMC FAMILY MEDICINE 01` / Workstation / `EMCFAMMED01` / 459 ·
`K EMH MAIN OR 01` / Workstation / `EMHMAINOR01` / 460 · `LAB INTERFACE WORKSTATION` / Workstation / `LABINTF` / 506

Note `Identifier` is empty for some rows and `Type` is `Workstation` for all of
them — a column that does not vary in the sample.

**Medication** — `160481` / `1ST MEDX-PATCH/ LIDOCAINE 4-0.0375-5-20 % EX PTCH` /
`Lidocaine-Capsaicin-Men-Methyl Sal Patch 4-0.0375-5-20%` · `127826` /
`1ST RELIEF SPRAY 4-1 % EX LIQD` / `Lidocaine-Menthol Liquid Spray 4-1%` ·
`100332` / `1ST TIER UNIFINE PENTIPS 29G X 12MM MISC` / `Insulin Pen Needle 29 G X 12 MM (1/2")`

**Dispensable** — `207570` / `HEPATITIS B VAC RECOMBINANT IJ ORDERABLE` ·
`400901` / `NIMODIPINE ORAL ORDERABLE` · `420001` / `ACYCLOVIR IV ORDERABLE`
(Generic Name column is empty for all observed rows)

---

## `Accept` is evidenced — build it

The transition animation is never in frame, but the destination is not in doubt:
the activity opens showing the chosen record, which is why its heading reads
`Medication: <record> [id]`. Enable `Accept`, require a selection, and navigate
to the activity with the record id. A stub destination is fine.

---

## Known unknowns — leave visibly incomplete

Use the `disabled` + `title="… — not demonstrated"` idiom from brief 01.

| Unknown | Why |
| --- | --- |
| What `Create New` opens | never clicked |
| Whether `Search` filters in place or re-queries | the field is empty in every frame |
| What triggers the next page of 30 | never observed loading more |
| Variant A's `Edit` button | greyed in the only frame; enable condition unknown |
| Whether variant A has a grid once a record is found | the field is empty in the only frame |
| The two small glyphs in variant A's title bar | too soft to identify even at 2.4x |
| Which variant an unobserved activity uses | only five of 22 activities were opened |

That last one matters for the 17 activities in the Rx Admin menu nobody opened.
**Do not guess a variant for them** — build the two observed variants and the
five configurations above.

---

## Definition of done

- One component, configured per activity — not five components
- Both variants, selected by configuration
- Grid: column config, row selection highlight, hover tooltip, group header,
  scrollbar, uneven content-driven widths
- `Records loaded: N. More records to load.` from real counts
- `Accept` / `Cancel` / conditional create button per the table
- Seeded from the database, nothing hard-coded in a component
- Opening it from the hub works for all five configured activities
- Every unknown above left disabled and labelled, and listed when you report back
