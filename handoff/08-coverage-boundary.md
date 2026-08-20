# Build brief 08 — make the coverage boundary visible

**Branch:** `pharmacy-admin` — same branch as 01–07.

This brief builds no new screens. It draws the line between **what the recording
showed** and **what it did not**, and puts that line in the interface instead of
only in a document.

---

## Why

Seven briefs have built everything one ten-minute recording supports. Measured:

| | seen | total |
| --- | --- | --- |
| **Rx Admin activities** | **6** | **≥23** |
| Hospital/Clinic Admin sections | 8 | 26 |
| Medication Admin sections | 6 | 9 |
| Workstation Admin sections | 3 | 3 |
| Medication List Admin tabs | 1 | 4 |
| NDC Admin sections | 1 | 14 |

**Sixteen of the twenty-two readable activities have never been seen at all**, and
the menu holds at least one more row that the frame clips before its name. Right now they
are simply absent — not in the ☰ module, and not anywhere else, because the
`Rx Admin` toolbar menu has never been built. `TOOLBAR_ITEMS` is a billing list
with no `Rx Admin` entry.

Absent is the wrong state. Someone reading the app cannot tell "this activity
does not exist" from "nobody has looked at it yet", and that is the same
confusion every not-captured panel in briefs 03–07 exists to prevent.

---

## 1. Build the `Rx Admin ▾` toolbar menu

Brief 01 transcribed it from the one frame that catches it open
(`~/build-evidence/01-willow-project-team/rx-admin-menu-detail.jpg`). It is a
**single column** — an earlier revision of that brief laid it out in two, and the
panel beside it in the frame is the already-open submenu.

```
Hospital/Clinic Admin          ← built
Unit/Department Admin
Care Area Admin
Pharmacy Admin
Workstation Admin              ← built
Medication List Admin          ← built
Medication Admin               ← built
Dispensable Mapping Admin      ← built
NDC Admin                      ← built
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
(one more row, clipped by the frame — name unread)
```

`Inventory Management Admin` opens a submenu, visible open in that frame:
`Prescription Fill Event Engine` · `Payer Sheet Setup` · `Field Setup` ·
`Rule Deferral Admin ▸`. That fourth entry has its own chevron and its contents
were never seen.

**The six marked "built" navigate as they do today. The other sixteen, and all
four submenu entries, are `disabled: true`.**

---

## 2. What `disabled` means here, and the trade-off

`disabled: true` gives a greyed, non-navigable row, and the inventory exporter
maps it to status `disabled` — *known and deliberately unbuilt*, which is
exactly right and distinct from `stub`.

**Be aware this makes the app deliberately disagree with the reference.** In the
recording all 22 are enabled. This is a considered divergence, not an oversight:
an activity you can click that leads nowhere is worse than one visibly greyed,
and the operator verifying against the video needs to see where the build stops.
Record it as a decision in the gap doc, not as a fidelity defect to fix later.

Each disabled row's tooltip should say why — *not yet observed in a recording* —
not *not implemented*. The distinction matters: nobody has looked, rather than
somebody looked and skipped it.

---

## 3. Everything else not in the recording

Apply the same treatment wherever it is currently invisible rather than marked:

- **The ☰ Willow module** currently lists only the six built activities. Bring it
  into line with the toolbar menu — all 22, sixteen disabled. Note the ☰
  *placement* of the Willow module is still unevidenced (the recording never
  opens ☰); leave that judgement as it stands and keep its existing note.
- **Sections and tabs already handled** — briefs 03–07's not-captured panels
  already do this. Do not change them.
- **Anything else you know to be absent** rather than marked. You have built all
  seven; if something is missing that a reader would assume exists, mark it.

---

## 4. The gap doc becomes the index

`docs/reference/WILLOW_CAPTURE_GAPS.md` is generated from the seed modules, so it
cannot drift. Extend it to cover this boundary:

- The coverage table above, generated rather than typed
- The sixteen unseen activities, with the reason
- Which recording each observation came from — `v01` today, so that when a second
  recording is processed the doc can say which findings are new

That last point is the one worth doing properly. **A second recording will
resolve many standing unknowns across all seven briefs** — `Edit` mode, `Accept`,
`Test Mapping`, sidebar collapse, the `P` dot, and quite possibly the ☰ placement
if any recording opens it. The doc should be ready to absorb that rather than
need rewriting.

---

## Not in this brief

- **The patient-context screens** at 00:17–01:44 — `Search for a Patient`,
  `Patient Encounter Selection`, `Orders`, `Chart Review`, `Timeline`, `Summary`.
  A different module with its own archetype, and this repo has existing
  precedent (`PatientLookupModal`, the patient-care routes) that wants checking
  before anything is specified. That is its own brief.
- **The shared-settings-page fidelity pass** — the ~190px field-column error and
  eight other items across four activities. Separate, and worth doing first.
- **The three shell-scoped carry-overs** — the title bar reading `Feb 2026` where
  the frames read `Aug 2026`, the session identity defaulting instead of showing
  `PRIME W.` / `PW`, and the missing wrench at the workspace tab row's right end.
  One shell pass, once someone decides.

---

## Definition of done

- `Rx Admin ▾` exists in the toolbar with all 22 readable activities in the
  reference's order, single column, plus the four-entry submenu, plus the clipped
  23rd row rendered present-but-unnamed
- Six navigate; sixteen plus all four submenu entries are `disabled: true` with a
  tooltip saying they have not been observed in a recording
- The ☰ Willow module matches
- A fresh `node scripts/export-inventory.mjs` shows the unseen entries as status
  `disabled`. The six seen ones will **not** all be `built` — five are reached
  through the record picker, and the exporter's own taxonomy carries that
  distinction. Do not flatten it to match this sentence.
- The gap doc carries the coverage table, generated, and records which recording
  each observation came from
- The deliberate divergence from the reference is recorded as a decision
