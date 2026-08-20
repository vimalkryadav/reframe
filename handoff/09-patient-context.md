# Build brief 09 — the patient-context workflow

**Branch:** `pharmacy-admin` — same branch as 01–08, even though this is a
different module. It is the same recording.

**This brief specifies deltas, not pages.** Unlike briefs 01–08, this repo
already has most of the scaffolding: `/patient/[id]/chart-review` and
`/patient/[id]/orders` exist, `PatientLookupModal` exists, and
`shell/patientSubTabs.ts` already implements a per-instance chart sub-tab store.
**Read those before writing anything.** Most of the work here is likely
configuration and two or three new sub-routes, not new architecture.

## Evidence

```
~/build-evidence/09-patient-context/
  f_000017-t00m17s.jpg   Search for a Patient
  f_000027-t00m27s.jpg   Search for a Patient
  f_000033-t00m33s.jpg   Patient Encounter Selection
  f_000038-t00m38s.jpg   Orders
  f_000047-t00m47s.jpg   Chart Review
  f_000058-t00m58s.jpg   Orders
  f_000064-t01m04s.jpg   Timeline
  f_000067-t01m07s.jpg   Summary
  f_000069-t01m09s.jpg   Medications
  f_000108-t01m48s.jpg   Report Settings - (New)
  f_000115-t01m55s.jpg   Report Settings - (New)
  detail-patient-header.jpg   the patient banner and sub-tab strip, 1.6x
```

Named by frame id. **Every name beside a frame is a claim to check** — read the
selected sub-tab from the strip, not from this list. Two frames in earlier briefs
were filed under the wrong screen exactly that way.

---

## The workflow

Ninety seconds, 00:17–01:55, and it is a coherent sequence rather than scraps:

```
Willow Project Team
   → Search for a Patient          00:17, 00:27
   → Patient Encounter Selection   00:33
   → the patient chart             00:38 – 01:09
        Orders · Chart Review · Orders · Timeline · Summary · Medications
   → back to the hub               01:18
   → Search for a Patient again    01:23
   → Report Settings - (New)       01:48, 01:55
```

Note the operator entered the chart, moved between **six sub-tabs**, and left.
The sub-tabs are the substance of this brief.

---

## What already exists

Check each before building:

| Screen | Existing route | State |
| --- | --- | --- |
| Chart Review | `/patient/[id]/chart-review` | **exists** |
| Orders | `/patient/[id]/orders` | **exists** |
| Timeline | — | not present |
| Summary | — | not present |
| Medications | — | not present |
| Search for a Patient | `PatientLookupModal` | exists, brief 02 configured a sibling |
| Patient Encounter Selection | `Encounter` is `lookup_scoped` in the inventory | route unclear — check |
| Report Settings - (New) | — | not present |

`shell/patientSubTabs.ts` implements the sub-tab store, but `CHART_SUB_ROUTES`
lists a HIM-oriented set — `chart-desk`, `special-chart-request`, `chart-edit`,
`chart-check-out`, `chart-check-in`. **The recording shows a different set.** Work
out whether these are two different chart types or one set that needs extending;
do not assume either.

---

## The chart sub-tab strip

`detail-patient-header.jpg`. Read the strip off the frame; from `f_000058` the
visible tabs are:

```
Summary · Timeline · Chart Review · Meds · Notes · MAR · Orders · … Sidebar Summary
```

Two things to be careful with:

**`Meds` in the strip, `Medications` as a heading.** The catalogue records a
screen named `Medications` at 01:09. Whether the strip's `Meds` is the same
screen under an abbreviated tab label is **not established** — check the frame
rather than assuming. The reference has already been seen to use a short form in
one place and a long form in another (`Med List Admin` versus
`Medication List Admin`, brief 02).

**`Notes` and `MAR` are in the strip but were never opened.** Two more
not-captured panels.

---

## Patient identity

The chart carries a patient banner. The record in these frames is
`Test, Joan` — demo-environment data from the same Foundation dataset as
everything else, so **seed it, do not hard-code it**.

`Test, Joan` is not in any picker masterfile from earlier briefs. Seed it with
that provenance noted, as briefs 04 and 06 did for their records.

---

## Rules carried forward

- **Read the activity from the activity tab, never from a heading.** The
  heading's prefix is a record-type label — this cost two phantom activities in
  brief 07.
- **Do not manufacture content.** Several of these screens have one frame.
- **Do not name what a tint distinguishes.** Three briefs running, I have read a
  category into a colour that did not support one.
- **Render the observed enabled/disabled state**, behaviour in the tooltip.
- **Screen for mid-load frames** — spinners, double-rendered panes, whole footers
  drawn undisabled. Three have turned up so far.

---

## Known unknowns

| Unknown | Why |
| --- | --- |
| `Notes` and `MAR` contents | in the sub-tab strip, never opened |
| What sits right of `Sidebar Summary` | clipped at the frame edge |
| Whether `Meds` and `Medications` are the same screen | tab label and heading differ |
| Whether these sub-tabs share the existing chart store or are a second type | `CHART_SUB_ROUTES` lists a different set |
| How `Patient Encounter Selection` is reached and what it does | one frame |
| What `Report Settings - (New)` belongs to | two frames, no context — it follows a return to the hub, not the chart |
| Whether the chart is reached only via patient lookup | the recording only ever enters that way |

`Report Settings - (New)` is the one to be most careful with. It has two frames,
no visible parent activity, and `(New)` in its title suggests a creation flow
nobody demonstrated. **It may not belong to the patient workflow at all** —
it simply follows one in time. Build it as its own thing or not at all; do not
attach it to the chart because it happens to be adjacent.

---

## Definition of done

- Existing routes reused, not duplicated — `chart-review` and `orders` in
  particular
- The sub-tab strip renders the observed tabs with the observed one selected
- `Timeline`, `Summary` and the `Meds`/`Medications` screen built from their
  frames; `Notes` and `MAR` as explicit not-captured panels
- Patient lookup and encounter selection reuse `PatientLookupModal` where it fits,
  with any divergence stated
- `Test, Joan` seeded with provenance, not hard-coded
- A written answer on whether this chart shares the existing sub-tab store or is
  a second chart type — that decision matters more than any single screen here
- Every unknown left visibly incomplete and listed when you report back
