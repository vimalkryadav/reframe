# Build brief 14 — Beacon Admin: the builders and the security editors

**Branch:** `pharmacy-admin`. **Depends on brief 12** for the `Beacon Admin ▾`
menu and its `Therapy Plan Tools ▸` submenu.

Six screens plus one shared launcher wizard, 03:08–05:46 of v02.

**Evidence:** `~/build-evidence/14-v02-beacon/` — 18 frames.

**Provenance:** rectified handheld footage — labels, order, states yes; geometry
no. Inherit spacing from existing primitives.

---

## Read this first: four names in the catalogue are not screens

The v02 catalogue lists `Protocol`, `Protocol Version`, `Order Group Contact` and
`Locator` as screens. **They are not.** They are the two step labels of the
launcher wizard below. `Workbench` is likewise not a screen — it is the workspace
tab these builders open in. Do not create pages for any of them.

`MODIFICATION` is also not a screen name. It is `Treatment Modification Builder`
— see §3.

---

## 1. The launchers — TWO shapes, seven configurations

> **SUPERSEDED — read the corrections at the end of this brief first.** This
> section models every launcher as one two-step wizard with five configurations.
> Both halves are wrong: three of the seven are single-step pickers with no step
> chevrons at all, and the count is seven, not five.

Every builder in this brief opens through the same two-step dialog. Three frames
show it, and they agree on the shape:

```
┌ Launching <Activity>                                              × ┐
│  ┌──────────────── step 1 ───────────────┐┌──── step 2 ────┐        │
│  │ <Subject>                             ││ <Version>      │        │
│  └───────────────────────────────────────┘└────────────────┘        │
│  <search field> [Search]        (step 1 only)                       │
│  ┌─────────────────────── grid ──────────────────────────────┐      │
│  └───────────────────────────────────────────────────────────┘      │
│  Records loaded: N. …                                               │
│  + Create a New <Thing>   [▼ Show Filter Panel]   [➡ Continue |     │
│                                                    ✓ Accept] [✗ Cancel]
└─────────────────────────────────────────────────────────────────────┘
```

Step tabs are Epic chevron tabs — the completed step keeps its subject text
beneath the label, the active step is teal.

**The three observed configurations, verbatim:**

| frame | title | step 1 | step 2 |
| --- | --- | --- | --- |
| `launching-treatment-mod-builder-step1-f_000239` | Launching Treatment Modification Builder | `Locator` (active) | `Locator Version` |
| `launching-therapy-protocol-builder-step2-f_000328` | Launching Therapy Protocol Builder | `Protocol` + `FILGRASTIM (NEUPOGEN) DAILY X 5 DOSES [570]` | `Protocol Version` (active) |
| `launching-order-group-builder-step2-f_000226` | Launching Order Group Builder | `Order Group` + `TX CONDS (HOLD IF ANC < OR = 1400, PLATELETS < 100,000) [210]` | `Order Group Contact` (active) |

**Step 1 grid** (`f_000239`), columns `ID` | `Record Name` | `Type` | `Released?`,
under a group header `All Available Records`:

`2038 MODIFICATION ONCBCN RSH TRASTUZUMAB REDUCTION` (selected) · `2481 ONCBCN IP
CHEMO CYTOXAN` · `2482 ONCBCN IP CHEMO CYTOXAN CYCLE 2 OR GREATER` · `1388 ONCBCN
IRINOTECAN - REDUCTION FOR ENZYME-INDUCING ANTIEPILEPTIC DRUGS` · `2521 / 2512 /
1370 / 1867 / 1870 / 3928 RULE ONCBCN CAPECITABINE 150 MG TAB DOSING - 1000 /
1250 / 625 / 650 / 750 / 830 MG/M2` · `2518 RULE ONCBCN CAPECITABINE 500 MG TAB
DOSING - 1000 MG/M2`. Every row `Type = Treatment Modification`, `Released? =
Yes`. Footer `Records loaded: 30. More records to load.` and
`+ Create a New Record`, `➡ Continue`, `✗ Cancel`.

**Step 2 grid** (both frames), columns `Number` | `Contact Date` |
`Release Status` | `Publish Status` | `Version Comment`:

- Therapy Protocol Builder, under `Select Version for FILGRASTIM (NEUPOGEN) DAILY
  X 5 DOSES`: `8 · 4/22/24 · Released · Not Published · Added additional types
  Infusion Treatment 2 and Infusion Treatment 3` (selected), then `7 5/28/19`,
  `6 12/9/16`, `5 11/28/16`, `4 11/28/16`, `3 8/4/16`, `2 4/29/14`, `1 4/11/14` —
  all `Retired` / `Not Published`, no comment. `Contacts loaded: 8. All contacts
  loaded.`
- Order Group Builder, under `Select a contact for TX CONDS (…)`: `5 · 9/27/12 ·
  Released · Published` (selected), `4 4/27/12 Retired Published`,
  `3 8/27/06 Retired Retired`, `2 8/6/06`, `1 8/3/06`. `Contacts loaded: 5. All
  contacts loaded.` Footer `+ Create a New Contact`, `▼ Show Filter Panel`,
  `✓ Accept`, `✗ Cancel`.

Note the difference: step 1 ends in `Continue`, step 2 in `Accept`.

**Two more configurations are observed but only as titles**, because their frames
catch the dialog mid-load: `launching-protocol-builder-f_000193` and
`launching-beacon-security-f_000311`, plus
`launching-therapy-plan-security-f_000340` and
`launching-episode-type-admin-f_000302` (with `episode-type-picker-2/-3` showing
an `Episode Type:` search field over a two-column grid). Seed those as
configurations with the title observed and the grid `not_captured`.

`WillowLaunch/RecordPickerGrid.tsx` already exists for the Rx Admin pickers. This
is a **two-step** variant. Judge whether to extend it or copy it into a Beacon
folder — Replicate-don't-generalise leans toward copying — and say which you did.

---

## 2. The Workbench builder shell — four screens share it

`Protocol Builder`, `Treatment Modification Builder`, `Order Group Builder` and
`Therapy Protocol Builder` are the same shell:

- workspace tab `Workbench`
- heading: `<RECORD NAME> [id] - <date> [version] - <Activity Name>`
- a left rail showing the record name truncated (`BLANK TREA…`, `MODIFICATIO…`,
  `TX CONDS (H…`, `FILGRASTIM …`) with `Settings` pinned at the bottom
- a toolbar starting `Open · Version · Save · Save As · Restore`, with `Save`
  greyed on every one of the four
- a read-only banner + `Try Lock` button
- tabs, then a tree or grid

Build it once here and copy per activity as the repo's rules prefer.

### 2a. `Protocol Builder` — `protocol-builder-f_000208`

Heading `BLANK TREATMENT PLAN [11519019] - 10/21/2019 [3] - Protocol Builder`.

Toolbar adds: `+ Add Task` · `+ Add Order` · `+ Add Order Group` ·
`+ Add Blank Day` · `+ Add Blank Cycle` · `Show ▾` · `Test Release` · `More ▾`.

Banner: `View is currently read-only.` / `This contact is Released. Lock the
record to make limited changes, or create a new contact to fully edit the record.`

Tabs: `Orders` (selected) | `Information` | `Dosing`.

Tree, under a `BLANK TREATMENT PLAN` root:

- `Cycle 1 — Perform: 1 time. Length: 1 day.`
  - `Day 1 — Perform 1 time on day 1 of the cycle. Day length: 1 day.`
    - `APPOINTMENT REQUEST - CALCULATED LENGTH INFUSION 1`
      - `Infusion Appointment Request` → `Appointment Requests, Expected: S,
        Schedule appointment at most 0 days before or at most 0 days after,
        Schedule at EMC Chemo Infusion or EMH Chemo Infusion`
    - `OP LABS CBC+DIFF / CMP / HCG URINE — Selection mode: Multi-Select.
      Selection requirement: None`
      - ☑ `CBC and differential` → `Labs, Expected: S, Clinic Collect, Blood,
        Venous, Blood`
      - ☑ `Comprehensive metabolic panel` → `Labs, Clinic Collect, Blood, Venous,
        Blood`
      - ☑ `hCG, urine, qualitative` → `Labs, Expected: S, Lab Collect, Urine,
        Clean Catch, Urine`; `Inclusion conditions: Patient could become pregnant`

This frame carries motion ghosting. The text is legible but **do not measure it**.

### 2b. `Treatment Modification Builder` — `treatment-modification-builder-f_000243`

Heading `MODIFICATION ONCBCN RSH TRASTUZUMAB REDUCTION [2038] - 11/06/2013 [1] -
Treatment Modification B…` — the activity name is itself clipped by the window;
carry it clipped.

Toolbar: `Open · Version · Save (greyed) · Save As · Restore · Release (greyed) ·
Usage Report · Metadata`.

Banner: `View is currently read-only.` / `Record contact is released.` — note this
is **shorter** than Protocol Builder's, and there is **no `Try Lock`** button.

Body: `Name:` with `MODIFICATION ONCBCN RSH TRASTUZUMAB REDUCTION` selected;
`Type:` `Dose Modification`; buttons `+ Add Criterion` and `+ Add Modification`,
**both greyed**. Grid `Criterion` | `Modification` | `Reference` | `Rule`, one
row: `> Grade 4 Thrombocytopenia` | `Dose: 3 mg/kg` | `For research purposes
only` | `ONCBCN GRADE 4 THROMBOCYTOPENIA`.

### 2c. `Order Group Builder` — `order-group-builder-f_000230`

Heading `TX CONDS (HOLD IF ANC < OR = 1400, PLATELETS < 100,000) [210] -
09/27/2012 [5] - Order Group Builder`.

Toolbar: `Open · Version · Save (greyed) · Save As · Restore · Add Order ·
Delete (greyed) · Copy From · Test Release · ✓ Release · Publish · ✗ Retire ·
Usage Report · Metadata · More ▾`.

Banner: `View is currently read-only.` / `This contact is Released. Lock the
record to make limited changes, or create a new contact to fully edit the
record.` + `Try Lock`.

Section `Order Group Properties`:

| label | value |
| --- | --- |
| Name: | `TX CONDS (HOLD IF ANC < OR = 1400, PLATELETS < 100,000)` |
| Display name: | empty |
| Version comment: | empty |
| Selection mode: | `Basic` |
| Default category: | `Nursing Orders` |
| For build only | checkbox, **unchecked** |

Beside it, `Synonyms` as a numbered list: `1  RN COMMUNICATION`, `2` empty.

Below, the record name repeated as a band, then a **selected** (teal) panel
`Treatment conditions` containing `Nursing Orders, Routine, Once, Starting when
released, Hold if ANC <= 1400 or Platelets < 100,000 and notify MD, Hospital
Performed`. A collapse chevron sits top-right of the properties area.

### 2d. `Therapy Protocol Builder` — `therapy-protocol-builder-f_000330`

Heading `FILGRASTIM (NEUPOGEN) DAILY X 5 DOSES [570] - 04/22/2024 [8] - Therapy
Protocol Builder`.

Toolbar: `Open · Version · Save (greyed) · Save As · Restore · Add Order ·
Add Order Group · Test Release (greyed) · ✓ Release · Publish (greyed) ·
✗ Retire · Metadata · Show IDs`.

Banner wording differs again — `Therapy protocol builder is currently read-only.`
/ same second line + `Try Lock`. **Transcribe each banner separately**; three of
the four differ.

Tabs `Orders` (selected) | `Properties`. Then `☑ Order Details` and a greyed
`View Quick Intervals` button.

Grid: leading checkbox column, then `Interval` | `Defer Until` | `Duration`:

- ☑ `Therapeutic Medications` (group)
  - ☑ `filgrastim (NEUPOgen) injection 300 mcg` | `Every 1 day` | `S` |
    `For 5 treatments`
    - `300 mcg, Subcutaneous, Once, Starting when released, For 1 dose`

Note the deliberate lowercase/uppercase mix in `filgrastim (NEUPOgen)` — that is
Epic's tall-man lettering. Preserve it exactly.

---

## 3. `Episode Type` — `episode-type-f_000261`

The longest dwell in v02 (32 frames) and the only screen here **not** on the
Workbench shell.

- workspace tab **`Admin`**, not `Pharmacy Admin` and not `Workbench`
- activity tab `Episode Type Admin`
- heading `Episode Type - Adult Condition Management [5850002]`
- toolbar `Restore · ✓ Accept · ✗ Cancel | ✏ Open Episode Type · ♡ View Related
  Records`
- **eleven tabs plus an overflow caret**: `Definition` (selected) · `Restrictions`
  · `Resolve Settings` · `Notifications` · `Miscellaneous` · `Problems` ·
  `SmartForms` · `Therapy Plan` · `Treatment Plan` · `Plan Hold` ·
  `Care Management` · `▾`. Ten of the eleven were never opened — mark them
  `not_captured` individually, and note the overflow means eleven is a floor.

`Definition` tab, section `Episode Type Definition`:

| label | value |
| --- | --- |
| Name: | `Adult Condition Management` (selected) |
| Class: | `Compass Rose Program` |
| Comments: | `This is a population health program designed to help adult patients manage their chronic conditions.` |

Then an info panel `ⓘ Review Flowsheets Setup` whose body is transcribed verbatim:

> Use the Review Flowsheets (FSH) field to configure flowsheets for the legacy VB
> Review Flowsheets activity. Use the Review Flowsheets (TIM) field to configure
> flowsheets for the web activity.
> To determine which version of the activity different groups of users see, check
> the Use Web Review Flowsheets (I LPR 37205) field in profile records. For more
> information about migrating to the web Review Flowsheets activity, refer to the
> Review Flowsheets Setup and Support Guide in Galaxy.

Below it, two lookups: `Review Flowsheets (FSH)` and `Review Flowsheets (TIM)`,
both empty. The panel is cut by the viewport — more of the tab exists below and
was never scrolled to.

`episode-type-admin-tab-f_000252` is the same screen mid-load; do not seed it as a
second screen.

---

## 4. The Security Class Editor — one component, two records

`beacon-security-class-editor-f_000314` and
`therapy-plan-security-class-editor-f_000342` are **the same screen** with
different records. Build once, seed twice.

Shell:

- workspace tab `Security Class Editor`
- two activity tabs: `🔑 Security Class Editor` and `<RECORD NAME> [id]`
- heading `<Module> - Security Class Editor - <RECORD NAME> [id]`
- `Name` field, and a `Comments` box
- tabs `Security Points` (selected) | `Usage Report`
- `Toggle All` button + `Filter security points` input
- grid `Active` | `Number` | `Name` | `Categories`, where `Active` renders as a
  teal `Yes` pill
- a right-hand pane reading `Select a Row to View Its Help Text`
- footer `↺ Restore` · `✓ Accept` · `✗ Cancel`. `f_000314` also catches the
  Accept tooltip: `Save all changes and close the activity (Alt+Shift+A)`

**Beacon** — `Beacon - Security Class Editor - ONCBCN PHYSICIAN CAN CREATE PLANS
[11510000020]`. Comments shows the **placeholder** `Enter comments`, i.e. empty.
Rows: `1 Treatment Plan Manager` · `2 Queue Up Future Plan` · `3 Create Plan` ·
`4 Put Plan on Hold` · `5 Release Plan from Hold` — all `Yes`, all category
`Edit Plan`. Scrollbar shows more below.

**Therapy Plan** — `Therapy Plan - Security Class Editor - THERAPY PLAN PHYSICIAN
[11510000100]`. Comments: `Grants user access to create and edit therapy plans.`
Rows: `1 Edit Therapy Plan` · `3 Create Plan` · `4 Put Plan on Hold` ·
`5 Release Plan from Hold` · `9 Access Plan Properties` — all `Yes` / `Edit
Plan`. **The numbers are non-contiguous — 1, 3, 4, 5, 9.** That is real; do not
renumber, and do not invent 2, 6, 7, 8.

---

## Acceptance

- [ ] No page exists for `Protocol`, `Protocol Version`, `Order Group Contact`,
      `Locator` or `Workbench`
- [ ] `MODIFICATION` appears nowhere as a screen name; the activity is
      `Treatment Modification Builder`
- [ ] One two-step launcher wizard, five configurations, `Continue` on step 1 and
      `Accept` on step 2; the two mid-load configurations have their grids marked
      `not_captured`
- [ ] Four builders on one copied Workbench shell, each with **its own**
      transcribed toolbar and read-only banner — they differ
- [ ] `Treatment Modification Builder` has no `Try Lock`; the other three do
- [ ] `filgrastim (NEUPOgen)` keeps its exact casing
- [ ] `Episode Type` renders eleven tabs plus overflow, ten marked never-opened,
      with a note that eleven is a floor; its info-panel text is verbatim
- [ ] One Security Class Editor component, two seeded records, security-point
      numbers left non-contiguous
- [ ] Every clipped string stays clipped with a note
- [ ] No geometry measured from these frames
- [ ] `WILLOW_CAPTURE_GAPS.md` records: `Study Maintenance` never opened, ten of
      Episode Type's eleven tabs never opened, both Security Class Editor grids
      scroll beyond what was seen, and no builder was ever unlocked or edited


---

# Corrections after the build

Seven, from the build session. The first three are structural and I verified each
against the frames myself.

## C1. There are TWO launcher shapes, not one

My "one two-step wizard" model is wrong. The frames show two distinct dialogs:

**Single-step pickers** — no step chevrons anywhere. A labelled search field, one
grid, `+ Create a New Record`, then `✓ Accept` / `✗ Cancel`.

| activity | search label | grid columns | rows |
| --- | --- | --- | --- |
| Beacon Security (`f_000311`) | `Security Class:` | `Security Class ID` · `Security Class Name` · `Application` | 8, `Records loaded: 8. All records loaded.` |
| Episode Type Admin (`f_000252`) | `Episode Type:` | `Episode Type Name` · `Episode Type ID` | 13 visible, `Records loaded: 30. More records to load.` |
| Therapy Plan Security | `Security Class:` | as Beacon Security | 7 |

**Two-step wizards** — the chevron stepper, `Continue` on step 1, `Accept` on
step 2. Protocol Builder, Treatment Modification Builder, Therapy Protocol
Builder, Order Group Builder.

So a launcher's shape depends on whether the record is versioned. Security classes
and episode types are picked outright; protocols, order groups and treatment
modifications need a contact chosen after the record.

## C2. Three of the four "mid-load" launchers are fully captured

I marked four configurations as mid-load and told you to seed their grids
`not_captured`. Only **Protocol Builder's step 1** is genuinely mid-load. Beacon
Security, Therapy Plan Security and Episode Type Admin are all fully loaded with
their grids legible — see the table above. Transcribe them; do not mark them
uncaptured.

## C3. `f_000201` is Protocol Builder's step 2, and it has a sixth column

I filed it as `protocol-step` and never described it. It is `Launching Protocol
Builder` step 2, fully loaded, and its grid carries **`Contents`** — a column
neither other step-2 grid has:

`Number` · `Contact Date` · `Release Status` · `Publish Status` · **`Contents`** ·
`Version Comment`

Rows: `3 · 10/21/19 · Released · Not Published · Clinical Only` (selected) ·
`2 · 7/12/18 · Released · Not Published · Clinical Only` ·
`1 · 6/28/18 · Released · Not Published · Clinical Only`. All three `Released`,
unlike the other two step-2 grids where only the top row is. `Contacts loaded: 3.
All contacts loaded.`

So the step-2 grid is **column-configured per activity**, not one fixed shape.

## C4. `f_000252` is the picker, not the screen mid-load

I wrote "the same screen mid-load; do not seed it as a second screen." Do not seed
it as a second screen — but because it is the **`Launching Episode Type Admin`
picker**, a different dialog entirely, not a half-rendered `Episode Type`.

## C5. The `Recent` group is session state, not seed data

At 04:14 the Episode Type picker has no `Recent` group and reads `Records loaded:
30`. At 05:02, after that record had been opened, `Recent` holds exactly it and
the count reads `31`. So `Recent` is produced by the session's own history.

Do not seed a `Recent` group with fixed contents — it is a consequence of use.

## C6. Order Group step 2's bottom two rows are legible

I left rows 1 and 2 without a status. Both are `Retired` / `Retired`.

## C7. Counting slips

The "three names are not screens" heading lists four (plus `Workbench`, five).
And §1 said "five configurations" while naming seven. Both fixed above.

---

## A measurement caution worth carrying forward

The build session tried to verify my per-button greyed/enabled calls on the four
builder toolbars by ink contrast, tilt-corrected and glyph-excluded, and **could
not**. The split tracks the **glyph**, not the state: `Open`'s folder, `Save As`'s
disk and `Metadata`'s pin all land at 127–154 regardless of state, while the low
band mixes `Save` (transcribed greyed) with `Add Order` (transcribed enabled).

So ink-contrast measurement resolves **label-only** controls — which is why it
settled brief 10's four row actions — and is confounded by **iconned** ones. My
toolbar greyed states in this brief therefore remain an eyeball transcription and
should be treated as unverified until a cleaner capture exists. The negative
result and its numbers are recorded in the gaps doc so nobody "corrects" the
build from those measurements later.

That is the right outcome: measurement that cannot decide should be reported as
undecided, not resolved in whichever direction it leans.
