# Build brief 01 — Willow Project Team (the Rx Admin hub)

**For:** a Claude session working in `rl_epic`
**Branch:** `reframe/01-willow-project-team`. Do not commit to `main`.
**Evidence:** `~/reframe-data/out/v01/frames/kept/` — frames named below
**Verification:** the operator will replay `VID_20260809_004826592.mp4` against
the built page and compare directly.

---

## Why this one first

Across a ten-minute recording the operator returns to this screen **fourteen
times**. Every other activity is reached from it and returns to it:

```
Willow Project Team  ──▸ [modal] "Launching <Activity>"  ──▸  the activity
        ▲                                                          │
        └──────────────────────────────────────────────────────────┘
```

Nothing else in the module can be navigated to until this exists.

---

## What it is

The landing workspace for the Willow (pharmacy) module. A three-column
dashboard of reports, workqueue counts and links. The page itself is
**read-only** — every control either runs a report or navigates away.

Best frames: `f_000607__t10m07s.jpg` (menu open, clearest chrome),
`f_000315__t05m15s.jpg` (dashboard unobstructed).

---

## Layout

Three columns under the standard shell chrome. Page heading is
`Willow Project Team` with a dropdown caret beside it.

### Left column — "Follow-up Required"

A section heading with a small pencil/edit affordance to its right, then a
vertical stack of report cards. Observed cards, in order:

1. **IB Messages Needing Follow-up** — a large centred ▶ button labelled
   `Run report` beneath it, then a caption line `Report: Rx Admin In Basket
   Messa…` (truncated in frame).
2. **Billing Errors by Medication** — same shape: ▶, `Run report`, then
   `Report: Rx Admin In Basket Messa…`.
3. **Interface Error Workqueue Summary** — different shape. A timestamp line
   `⊙ Data collected: Sat 8/8 02:18 PM`, then a two-column table with headings
   `Workqueue` and `Total Errors`. Rows carry a green check icon, a two-line
   workqueue name, and a count in a rounded pill:
   - `Willow Inpatient Interface Errors` → `0`
   - `Device Integration Interface Errors` → `0`

Card titles are links (they read as underlined/coloured text, distinct from the
body copy).

### Centre column — reports list

A grid, partially obscured in every frame by the open menu, so treat this as
**incompletely observed**. What is legible: a `Status` column whose cells all
read `Ready to run`, at least five rows. Row labels were never visible.

**Do not invent the row labels.** Build the grid with the `Status` column and
leave the label column driven by data; the operator will fill it in from the
video during verification.

### Right column — "Links/Info"

Two stacked panels.

**Project Team Message Board** — a list of posts. Each post has a bold title,
a body paragraph, a sign-off, and a right-aligned metadata line reading
`<date time> - <author>`. Observed:

- `Order Validate, Abraham` / "Please don't discontinue any of this patient's
  orders. I'm testing a release note." / "Thanks," / "Barb" /
  `Mon 11/19/2012 05:34 PM - Admin Willow Inpatient`
- "Working on the formulary today." / "Please don't lock the record." /
  `Mon 11/19/2012 05:29 PM - Admin Willow Inpatient`

Those are demo-environment contents, not fixtures to hard-code. Build the panel;
seed it from the database.

**Common Links** — a collapsible group headed `General` (with a ⌄ caret),
containing links:
`Record Viewer`, `Menu Summary`, `User Security`, `Show/Hide Print Groups`,
`Session Information`, `Turbocharger`, `Build Wizard`.

`Build Wizard` matters — it appears as its own screen at 10:01 in the footage,
so this link is a real navigation target.

---

## The Rx Admin menu — read this before naming anything

`f_000607` catches the `Rx Admin` toolbar menu open, which is the **only**
authoritative list of activity names in the corpus. Everything else in the
catalogue is a page *heading*, which shows the record being edited rather than
the activity.

Menu contents, in order:

```
Hospital/Clinic Admin        NDC Group Admin
Unit/Department Admin        Set NDC Costs
Care Area Admin              Merchandise and Fee Admin
Pharmacy Admin               Charge Table Admin
Workstation Admin            Charge Mapping Admin
Medication List Admin        Cart Admin
Medication Admin             Willow Security
Dispensable Mapping Admin    Pharmacy System Definitions
NDC Admin                    Label Printer Setup
                             Validate Barcodes
                             Pharmacy Workflow Configuration
                             Documents Definitions
                             Inventory Management Admin  ▸
```

`Inventory Management Admin` opens a submenu: `Prescription Fill Event Engine`,
`Payer Sheet Setup`, `Field Setup`, `Rule Deferral Admin ▸`.

**Use these names.** The catalogue reads `Medication` and `Hospital/Clinic`
because that is what the page heading says; the activity is
`Medication Admin` and `Hospital/Clinic Admin`. Naming pages after headings
would produce a menu that does not match the reference.

This menu is shell navigation, not part of this page. It probably deserves its
own brief — flag it if you disagree, but do not build it as part of this one.

---

## Out of scope for this brief

- The `Launching <Activity>` modal that appears between hub and activity. It is
  a real, observed state (four distinct variants) and gets its own brief.
- Any activity the menu lists. This brief is the hub only.
- The centre grid's row labels — obscured in every frame, see above.

---

## What is uncertain

State these back rather than guessing:

| Uncertain | Why |
| --- | --- |
| Centre grid row labels | the open menu covers them in every frame |
| Whether the left column scrolls | only three cards were ever visible |
| What the heading's dropdown caret opens | never clicked in the footage |
| Whether `Follow-up Required` is configurable | the pencil icon suggests yes; never used |

The operator verifies by replaying the video, so a page that is honestly
incomplete in these four places is more useful than one that guesses and looks
finished.

---

## Definition of done

- Route exists and is reachable from the module menu
- Three-column layout matching the frames
- Report cards render with title, ▶ `Run report`, caption
- The workqueue summary table renders with its two columns and count pills
- Message board and Common Links panels render from data, not hard-coded
- `Build Wizard` link navigates (target may be a stub for now)
- Added to `ACTIVITY_OVERRIDES` so the next inventory export marks it `built`
