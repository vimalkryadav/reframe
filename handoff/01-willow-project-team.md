# Build brief 01 — Willow Project Team (the Rx Admin hub)

**Branch:** `pharmacy-admin` — one branch for the whole module. Every brief in
this series lands on it. Do not commit to `main`.
**Verification:** the operator replays the source recording against the built
page and compares directly, so anything guessed here will be caught — and
anything left honestly blank is cheaper than anything invented.

## Evidence — look at these before writing code

```
~/build-evidence/01-willow-project-team/
  dashboard-full.jpg            the whole page, unobstructed   (05:15)
  header-and-toolbar.jpg        shell chrome + page heading
  col-1-follow-up-required.jpg  left column, 2x
  col-2-reports.jpg             centre column, 2x
  col-3-links-info.jpg          right column, 2x
  rx-admin-menu-open.jpg        the toolbar menu, open         (10:07)
  rx-admin-menu-detail.jpg      that menu, 2x
```

These are stills from a handheld phone recording of the reference application,
so text is soft — where a label below is marked uncertain, it is because the
pixels genuinely do not settle it.

---

## Why this screen first

Across ten minutes of recording the operator returns here **fourteen times**. Every activity
is launched from it and comes back to it:

```
Willow Project Team ──▸ [modal] "Launching <Activity>" ──▸ the activity
        ▲                                                       │
        └───────────────────────────────────────────────────────┘
```

Nothing else in the module is reachable until this exists.

---

## Page shell

Heading `Willow Project Team` with a dropdown caret, on its own row below the
toolbar. Right of that row, **five controls in this order** — verified at 6x,
because at 1x two of them read as something else entirely:

1. layout-picker pill (a 3x3 grid glyph in a rounded rectangle)
2. a caret `▾` belonging to it
3. filter funnel
4. a **broken ring** — a share/link glyph, not a refresh circle
5. a **multi-colour petal mark** — not a wrench; it only reads as one at 1x
6. a `⋮` More button at the far right, partly out of frame

The same cluster in the same order already exists on `CadenceAdminDashboard` in
this repo — reuse those glyphs rather than re-deriving them.

Below the heading, three columns of equal width — they measure 566 vs 491 px in
frame, but that is perspective skew from the handheld camera, not layout, each with a plain
section title above a stack of bordered panels: **Follow-up Required**,
**Reports**, **Links/Info**.

The page is read-only. Every control either runs a report or navigates away.

---

## Column 1 — Follow-up Required

Section title with a small pencil affordance to its right (suggests the column
is configurable; never exercised in the footage).

### Card: IB Messages Needing Follow-up

- Title is a link, with a small "open in new" glyph after it
- A large centred ▶ play button
- Caption under the button: `Run report`
- Footer line: `Report: Rx Admin In Basket Messages Last Month`

### Card: Billing Errors by Medication

Identical shape. Footer line is the **same** string:
`Report: Rx Admin In Basket Messages Last Month`. That repetition is in the
source, not a transcription slip.

### Card: Interface Error Workqueue Summary

Different shape — a table, not a button.

- Title, then `⊙ Data collected: Sat 8/8 02:18 PM`
- Four columns: `Workqueue` · `Total Errors` · `Added Today` · `Last Accessed`
- Rows carry a green circled check, a two-line workqueue name, and the count in
  a rounded **green** pill — sampled interior RGB (143,151,141) against a neutral
  panel of (187,186,187). The green is semantic here (no outstanding errors), so
  it is one of the cases allowed to depart from the theme:

| Workqueue | Total Errors | Added Today | Last Accessed |
| --- | --- | --- | --- |
| Willow Inpatient Interface Errors | `0` | 0 | Never |
| Device Integration Interface Errors | `0` | 0 | Never |

Only `Total Errors` is pill-rendered; the other two are plain text.

**Card titles and the section title are the same size.** Measured width ratio in
the frame is 1.626 and 1.621 at equal size in the DOM — there is no type
hierarchy between them, despite how this document's headings are nested.

---

## Column 2 — Reports

### Panel: Favorited & Saved Results

- Title with the same "open in new" glyph
- `Last Refresh: 02:18:38 PM`
- Empty state: `No reports are available for display.`

Build the empty state — it is the observed state and worth getting right.

### Panel: Rx Project Team Reports

Four columns: `Report Name` · `Finished On` · `Results` · `Status`.
Only `Report Name` and `Status` carry values in the footage; `Finished On` and
`Results` are empty for every row, consistent with nothing having been run.

| Report Name | Status |
| --- | --- |
| All Retrospective Renal Dosing Rules | Ready to run |
| Controlled Dispenses to LTC Facilities | Ready to run |
| Deprecated Print Groups | Ready to run |
| Infusion Pump Integration Errors | Ready to run |
| IP Pump Programming Compliance - Analyst | Ready to run |

Report names wrap onto several lines within a narrow first column — the row
height grows to fit. `Status` renders as link-styled text, not a badge.

The list continues below the fold; five rows is what the viewport showed.

---

## Column 3 — Links/Info

### Panel: Project Team Message Board

A list of posts, each with a large title, a body paragraph, an optional
sign-off, and a right-aligned `<date> <time> - <author>` line. A hairline rule
sits **below** that line, not beside it (checked at 6x — at 1x it reads as an
inline rule).

Observed posts:

1. **Order Validate, Abraham**
   "Please don't discontinue any of this patient's orders. I'm testing a release
   note."
   "Thanks," / "Barb"
   `Mon 11/19/2012 05:34 PM - Admin Willow Inpatient`

2. "Working on the formulary today."
   "Please don't lock the record."
   `Mon 11/19/2012 05:29 PM - Admin Willow Inpatient`

Note the second post has no title. Titles are optional.

**This is demo-environment content — seed it, do not hard-code it.** The 2012
dates are the demo dataset's, not today's.

### Panel: Common Links

A collapsible group `⌄ General` containing links, in this order:

```
Record Viewer
Menu Summary
User Security
Show/Hide Print Groups
Session Information
Turbocharger
Build Wizard
Content Management        ← partially below the fold, name uncertain
```

`Build Wizard` is a real navigation target — it appears as its own screen at
10:01 in the footage.

---

## The Rx Admin menu — read before naming anything

`rx-admin-menu-detail.jpg` catches the toolbar's `Rx Admin` menu open. It is the
**only** place in ten minutes of footage where activity names are visible.
Every other name gathered from this recording is a page *heading*, and a heading
shows the record being edited rather than the activity.

**One column, not two.** An earlier revision of this brief laid the list out in
two columns to save space, which is not what the frame shows — the panel to the
right of it is the already-open `Inventory Management Admin` submenu.

```
Hospital/Clinic Admin
Unit/Department Admin
Care Area Admin
Pharmacy Admin
Workstation Admin
Medication List Admin
Medication Admin
Dispensable Mapping Admin
NDC Admin
NDC Group Admin
Set NDC Costs
Merchandise and Fee Admin
Charge Table Admin
Charge Mapping Admin
Cart Admin
Willow Security
Pharmacy System Definitions
Label Printer Setup
Validate Barcodes
Pharmacy Workflow Configuration
Documents Definitions
Inventory Management Admin  ▸
```

`Inventory Management Admin` opens a submenu, visible open in the frame:
`Prescription Fill Event Engine`, `Payer Sheet Setup`, `Field Setup`,
`Rule Deferral Admin ▸`.

**There is at least one more row below it**, clipped by the bottom of the frame
with only its ascenders showing. The menu extends past what was captured, so
**22 is a floor, not a count** — treat it as "at least 23 entries, the 23rd
unread and anything beyond it unknown". Render the clipped row as present and
unnamed; do not read the ascenders into a name.

**Use these names for routes and menu entries.** A page heading reads
`Medication` or `Hospital/Clinic`; the activities are `Medication Admin` and
`Hospital/Clinic Admin`.

The menu belongs to the shell, not this page. It likely needs its own brief —
do not build it here.

---

## Out of scope

- The `Launching <Activity>` modal between hub and activity — brief 02
- Any activity the menu lists — later briefs
- The Rx Admin menu itself — see above

---

## Known unknowns — state these back, do not resolve them

| Unknown | Why |
| --- | --- |
| The last Common Links entry (`Content Management`?) | sits on the fold, never fully in frame |
| Session user's full name — **resolved**, see below | not an unknown after all |
| Whether any column scrolls | content ran past the viewport in all three |
| What the heading's dropdown caret opens | never clicked |
| Whether `Follow-up Required` is user-configurable | the pencil suggests yes; never used |
| What the three top-right icon buttons do | never clicked |
| Rows below the fifth in Rx Project Team Reports | never scrolled |

---

## Session identity — resolved

`PRIME W.` is **not clipped by the window edge**; that is Epic's own display
format — given name, surname initial, full stop. The avatar beside it reads
`PW` in green. Department context is `EMH IP PHARMACY ▾`.

So: user `Prime W.`, initials `PW`, department `EMH IP PHARMACY`.

---

## Definition of done

- Route exists, reachable from the module menu, added to `ACTIVITY_OVERRIDES`
- Three-column layout matching `dashboard-full.jpg`
- Report cards: title link, ▶ button, `Run report`, footer report line
- Workqueue summary: four columns, green check, count pill
- `Favorited & Saved Results` renders its empty state
- `Rx Project Team Reports` renders all five rows with wrapping names
- Message board and Common Links render from seeded data, not literals
- `Build Wizard` navigates (a stub target is fine for now)
- The six unknowns above left visibly incomplete rather than invented
