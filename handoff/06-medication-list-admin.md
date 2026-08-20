# Build brief 06 — Medication List Admin

**Branch:** `pharmacy-admin` — same branch as 01–05.
**This is a third page archetype.** Briefs 03–05 are all sidebar-tree settings
pages. This one is not: horizontal tabs, a data grid, its own action toolbar,
and a footer ending in `Close` rather than `Accept`. Do not force it into
`AdminRecordPage`.

What it *does* share is **read-only page state** from brief 05 — differently
worded, same concept. That should need no new code.

**Verification:** the operator replays the source recording against the built
page. Trust the images over this text.

## Evidence

```
~/build-evidence/06-medication-list-admin/
  f_000333-t05m33s.jpg      \
  f_000335-t05m35s.jpg       |
  f_000337-t05m37s.jpg       |  all seven on the Medications tab,
  f_000339-t05m39s.jpg       |  at differing scroll positions
  f_000341-t05m41s.jpg       |
  f_000346-t05m46s.jpg       |
  f_000348-t05m48s.jpg      /
  detail-action-toolbar.jpg heading, actions and banner, 2.6x
  detail-tab-strip.jpg      the four tabs, 3.0x
  detail-p-column.jpg       the grid's dot column, 2.6x
  detail-footer.jpg         the footer bar, 2.2x
```

Named by frame id. Anything this text asserts is a claim to check.

---

## What this is

Reached as: hub → `Rx Admin ▸ Medication List Admin` → picker → this page.

Record `CHEMO ONLY [98]`, seven frames across **fifteen seconds**. The operator
scrolled the grid twice and opened nothing else.

Note the activity tab reads **`Med List Admin`** — the short form, matching the
picker's dialog title rather than the menu's `Medication List Admin`. Brief 02
records both names; this is the third place the short form appears.

---

## Page structure

### Heading

`Medication List: CHEMO ONLY [98] (Read-Only)` — activity, record, and the mode
appended in parentheses. Briefs 03–05 do not put the mode in the heading; this
one does.

### Action toolbar

Seven actions on one row beneath the heading, each with a glyph:

```
📂 Open   ✎ Edit   ▥ Inactive Packages   ☰ Link Pref. List
👥 Edit Access Groups   ⟳ Refresh   ⇱ Update Med Lists
```

Not a segmented control like brief 05's mode bar — these read as separate
actions. Accelerator underlines are present; read them off
`detail-action-toolbar.jpg` rather than trusting a transcription here.

### Read-only banner

⚠ `The medication list is currently in read-only mode.`

A **warning triangle**, where brief 05's is a padlock, and the wording names the
*list* rather than the *activity*. Same page state, different copy — so the
banner text belongs in data, which brief 05's `willow_admin_activity` table
already allows for.

### Tab strip

Four tabs. `Medications` is selected in all seven frames.

```
Medications  |  ADS  |  Billing  |  Related Information
```

Selected tab renders with a box/underline treatment distinct from the others.
**Only `Medications` was ever opened** — see unknowns.

### Grid

Three visible columns: `P` · `ID` · `Medication`.

`P` is a narrow marker column holding a **dot on some rows, in at least two
tints** — a brighter green and a darker one — with many rows carrying none.
The footer's `● Include medication in preference list (F6)` uses the same dot,
which suggests the column marks preference-list membership, but the two tints
are not explained by anything on screen. **Record the dot and its tint per row;
do not name what the tints mean.**

Selected row highlights across its full width. The grid scrolls — two frames
show different alphabetical starting points (`ABIRATERONE…` and `ALDESLEUKIN…`),
so the rows below the fold are real, not absent.

### Footer

Left: ☐ `Show additional columns` · ● `Include medication in preference list (F6)`

Right: `📊 Export to Excel` · `☰ Details` · `➕ Add` · `➖ Remove` · `✔ Close`

`Add` and `Remove` appear greyed — consistent with read-only, though nothing was
clicked to prove the link. `Close` where briefs 03–05 have `Accept`.

---

## Seed data

Rows legible across the two scroll positions, `P` tint noted where present:

`109776` ● ABIRATERONE ACETATE 250 MG PO TABS ·
`139026` ABIRATERONE ACETATE 500 MG PO TABS ·
`410045` ADO-TRASTUZUMAB CHEMO IVPB ·
`420543` ◐ ADO-TRASTUZUMAB EMTANSINE (KADCYLA) CHEMO IV ORDERABLE ·
`120086` ADO-TRASTUZUMAB EMTANSINE 100 MG IV SOLR ·
`120087` ADO-TRASTUZUMAB EMTANSINE 160 MG IV SOLR ·
`4300031` ADO-TRASTUZUMAB EMTANSINE 20 MG/ML IV (WRAPPED WET SOLR VIAL) ·
`122472` ● AFATINIB DIMALEATE 20 MG PO TABS ·
`122473` AFATINIB DIMALEATE 30 MG PO TABS ·
`122474` AFATINIB DIMALEATE 40 MG PO TABS ·
`410290` ALDESLEUKIN IVPB IN 25 ML D5W ·
`410001` ALDESLEUKIN IVPB IN 50 ML D5W ·
`420910` ◐ ALDESLEUKIN IVPB ORDERABLE ·
`420954` ● ALEMTUZUMAB (LEMTRADA) IV ORDERABLE ·
`421038` ◐ ALEMTUZUMAB (LEMTRADA) IV ORDERABLE IN 100 ML/M2 (PEDIATRIC) ·
`400998` ALEMTUZUMAB (LEMTRADA) IVPB ·
`127653` ALEMTUZUMAB 12 MG/1.2ML IV SOLN ·
`91000` AMIFOSTINE 500 MG IV SOLR ·
`43091000` AMIFOSTINE 500 MG/10ML IV (WET SOLR VIAL) ·
`4309100001` AMIFOSTINE 500 MG/3.125ML SQ (WET SOLR VIAL)

Read the tints off `detail-p-column.jpg` rather than trusting the marks above —
they are my reading of a soft frame, and the two tints are close.

---

## Rules carried forward

- **Do not manufacture rows** to fill the grid, and do not invent what the three
  unopened tabs contain.
- **Do not name the dot tints.** Record them; leave the meaning open.
- **Do not complete clipped text.**
- **Render the observed enabled/disabled state**; behaviour in the tooltip.

---

## Known unknowns

| Unknown | Why |
| --- | --- |
| `ADS`, `Billing`, `Related Information` contents | never opened — three of four tabs |
| What the two `P` dot tints distinguish | nothing on screen explains them |
| What `Show additional columns` reveals | never ticked; the grid may be wider than three columns |
| What any of the seven toolbar actions do | none clicked |
| Whether `Add`/`Remove` are greyed *because* of read-only | plausible, never demonstrated |
| What `Details` and `Export to Excel` do | never clicked |
| Whether `Close` returns to the hub | never clicked |
| Total row count | grid scrolled twice, never to an end |

`Show additional columns` is the one worth building carefully: an unticked
checkbox implies the grid has more columns than the three shown, so the three
are a *subset*, not the schema. Model the grid so columns are data.

---

## Definition of done

- Route under the activity, reached from the picker with a record id
- Activity tab reads `Med List Admin`, the short form
- Heading reads `Medication List: <record> [<id>] (Read-Only)` with the mode
  appended
- Seven-action toolbar; warning-triangle banner with this activity's wording,
  from data rather than hardcoded
- Four-tab strip with `Medications` selected; the other three render an explicit
  "not captured" state
- Grid with `P` · `ID` · `Medication`, dots recorded per row with their tint,
  full-width row selection, scrolling
- Footer: two left controls, five right actions, `Close` not `Accept`
- Read-only state reused from brief 05, not reimplemented
- Every unknown left visibly incomplete and listed when you report back
