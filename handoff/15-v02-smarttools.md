# Build brief 15 — SmartTool Editors, SmartForms, and two standalones

**Branch:** `pharmacy-admin`. **Depends on brief 12** for `Beacon Admin ▾`, and
reuses brief 14's launcher wizard.

Nine screens and three modal pickers, 06:09–09:36 of v02 — the last chapter.

**Evidence:** `~/build-evidence/15-v02-smarttools/` — 19 frames.

**Provenance:** rectified handheld footage. Labels, order, control types and
states yes. **Geometry no.**

---

## The coverage warning that belongs at the top

Most of this brief lives under `Beacon Admin ▸ SmartTool Editors ▸`, and **that
submenu was never expanded.** At 07:48 the cursor rests on it and the frame still
does not show its children. So:

**Do not state a coverage figure for SmartTool Editors.** Do not write "five of
seven" or any such fraction. The denominator is unknown, and brief 08's
"six of twenty-two" is the cautionary example.

There is one indirect signal, and it is a *navigator rail inside the workspace*,
not the menu: `system-smartphrase-f_000518` and its siblings show a left rail
reading `SmartTexts` · `Paper Settings…` · `SmartList` · `SmartPhrases` ·
`Manage Phrases` · `SmartLinks` · `Find SmartLinks`. Record that in the gaps doc
as the closest thing observed. It is **not** evidence of the submenu's contents.

---

## 1. The SmartTools shell — five screens share it

`SmartText`, `System SmartList`, `System SmartPhrase` and `SmartLink` all render
in a `SmartTools` workspace tab with the same three-part layout. Build once in
this feature folder, copy per editor.

- **Left rail**: icon + label entries, with the open record shown as a selected
  child beneath its category. Observed order: `SmartTexts` · `Paper Settings…` ·
  `SmartList` · `SmartPhrases` · `Manage Phrases` · `SmartLinks` ·
  `Find SmartLinks`. Different frames clip different ends of the labels — compare
  `f_000518`, `f_000538`, `f_000484`, `f_000511` before settling each string.
- **Centre**: the editor pane — a rich-text body, a grid, or a form depending on
  the editor.
- **Right**: a `⚙ Settings` panel of label + segmented-control rows, sometimes
  with further collapsible panels beneath.
- **Footer**: varies per editor; `Open` and `Preview` are common, then some subset
  of `Metadata`, `Restore`, `Create Copy`, `Save`, `✓ Accept`, `✗ Cancel`.

Heading form throughout: `<Editor Name> – <RECORD> [id]` (en dash, not hyphen).

### 1a. `SmartText` — `smarttext-deprecated-f_000484`

Heading `SmartText - (DEPRECATED) - EHS SBO SERVICE AREA - GUARANTOR BILLING
ACCESS ADDED FROM ADDRESS …` — clipped by the window. `SmartText` and the long
`(DEPRECATED)` form are **one screen**; the long form is the heading with a
record loaded.

Editor toolbar: two search glyphs, undo, redo, `?`, an insert glyph, `+`, then
`Insert SmartText` · `Insert SmartList`, a list glyph, arrows, a scissors icon,
and a `100% ▾` zoom control on a second row.

Body content, verbatim: `donotreply@12345678901234567890`

`⚙ Settings`:

| control | value |
| --- | --- |
| Name | `(DEPRECATED) - EHS SBO SERVICE AREA - GUARANTOR BILLING ACCESS AD…` (clipped) |
| Additional Notes | empty, with a ⚠ glyph inside the box |
| Search Availability ⓘ | `Always Available` **selected** \| `Build Only` \| `Never Available` |
| SmartLink Text Size and Font ⓘ | `Match Template Formatting` **selected** \| `Keep SmartLink Formatting` |
| Log Events | `Default` **selected** \| `Yes` \| `No` |
| SmartText Language ⓘ | lookup, empty |
| Version | `Version: 1 (4/28/2025)` with a `✓ Released` pill |

Footer: `Metadata` · `Open` · `Preview` — then `Create Copy` · `Save` ·
`✓ Accept` · `✗ Cancel`. The frame catches the Accept tooltip:
`Save changes and close (Alt+…`.

`smarttext-f_000480` is the same screen at 0.44 confidence — mid-transition. Do
not seed it separately.

### 1b. `System SmartPhrase` — `system-smartphrase-f_000518`

Heading `System SmartPhrase – A [103487]`.

Warning banner above the editor: `ⓘ Do not include PHI or patient-specific data
in SmartPhrases.`

Editor toolbar: `B` · undo · `?` · `Insert SmartText` · `Insert SmartList` · a
list glyph · a scissors glyph with caret. Beneath it a **ruler with tab stops
numbered 1–6**. Body: `ASSESSMENT:`

`⚙ Settings`:

| control | value |
| --- | --- |
| Name | `A` |
| Description | `ASSESSMENT:` with a `Populate from Text` link right-aligned |
| Text Format | `Rich Text` **selected** \| `Plain Text` |
| SmartLink Text Size and Font ⓘ | `Match Template Formatting` \| `Keep SmartLink Formatting` **selected** |
| Log Events? | `Default` **selected** \| `Yes` \| `No` |
| — | `✓ Released` pill |

Note this is the **opposite** SmartLink-formatting selection from `SmartText`.
Transcribe each editor's defaults separately.

Then a collapsed `📖 Synonyms` panel. Footer: `Open` · `Preview` —
`Create Copy` · `Save` · `✓ Accept` · `✗ Cancel`.

### 1c. `System SmartList` — `system-smartlist-f_000511`

Heading `System SmartList – 16676 [21538]`.

Centre pane is a **grid**, columns `Choice` | `Default?`:

| choice | default? | row actions |
| --- | --- | --- |
| `does have a urinary catheter in place.  *** mL of urine was drained when catheter was placed` (selected) | unchecked | `•••` then `↑ ↓ ✗` |
| `does not have a urinary catheter in place` | unchecked | — |
| (empty row) | unchecked | `•••` |

`⚙ Settings`:

| control | value |
| --- | --- |
| Name | `16676` · ID `21538` |
| Display Name | `16676`, plus an `Include as lab…` checkbox (clipped) |
| Version | `Version: 1 (9/26/2013)` + `✓ Released` |
| flags | `✓ Reselectable` · ☐ `Optional` · ☐ `Use Rules` · ☐ `Use Discrete Data` |
| Log events? | `Default` **selected** \| `Yes` \| `No` |

Then `≡ Selection Options`: `Selection Type` `Single` **selected** \| `Multiple`;
`Connection Logic` `And`; ☐ `Mutually exclusive groups`. Then a collapsed
`T Advanced` panel.

Footer: `Open` — `↺ Restore` · `Create Copy` · `Save` · `✓ Accept` · `✗ Cancel`.

### 1d. `SmartLink` — `smartlink-f_000538`

Heading `SmartLink (Type: SmartLink) - ENVELOPE ADDRESS - LETTER FROM [692]`.

Read-only banner: `This SmartLink is currently read-only.` / `This record is in
Epic's release range.` + `Try Lock`.

Panels down the centre:

- `Refreshable Settings` — one line: `Refreshable: Yes; Warn on Delete: No;
  Collapsible: Not Collapsible`
- `Default Configuration` — `Code Template` (empty); `User-Entered Parameters`
  segmented `No` **selected** \| `Yes - Optional` \| `Yes - Required`; `Code`
  showing `d FromAddr^LCOMMMG6A(ATTACH)`
- `Contexts` — ☐ `Available to all contexts`, then grid `Context` | `Code` with
  one row `MR Letter Template` | `Uses default code`

Right column: a collapsed `Overrides` panel (clipped at the top), then
`📝 Admin Notes` containing verbatim:

> Displays the letter author's address on an envelope printed from the
> Communication Management navigator section. This SmartLink is intended for use
> only in the letter template you use to generate envelopes in the Communication
> Management section. This SmartLink has no configurable parameters.

Then `⇄ Used By SmartTools (None)`.

Footer: `Metadata` · `Open` · `Preview` — `Create Copy` · `× Close`. **No Save or
Accept** — consistent with the read-only banner.

---

## 2. Three modal pickers

All three follow the same pattern: two `+ New …` buttons, a search field, a grid
with a leading pencil/check column, a scoping checkbox bottom-left, and
`✓ Accept` / `✗ Cancel`. Use `shared/DialogShell.tsx`.

### 2a. `SmartList` — `smartlist-modal-f_000503`

**This is a modal, not a workspace screen.** Title `SmartList`. Buttons
`+ New User SmartList` · `+ New System SmartList`. Search field, plus a
`Search by:` toggle `Name` **selected** | `Conten…` (clipped).

Grid `ID` | `Name` | `Level` | `Selection Type` | `Connection` | `Choices`:

`21538 16676 · System · Single · — · does have a urinary catheter in place. *** mL
of urine was drained…` (selected) · `24193 RLE JOINT STABLE/UNSTABLE PE · System ·
Single` · `33606 % CORRECTION · System · Multiple · And` · `20013 (BH) RANGE
ABSENT/SEVERE · Single · Absent_Mild_Moderate_Marked_Severe` · `20012 (BH) RANGE
IMPROVED /WORSE` · `24559 (no name) · Multiple · And` · `25719 1/2,1` ·
`22773 1ST/2ND · Multiple · None` · `25709 2-12 by 2` · `33903 2-6` ·
`34446 4-6 steps/1flight of stairs` · `25737 6,8,10,12,14` · `21509 A/NO` ·
`304650003 AAP 2022 Bilirubin Discharge Follow-Up Recommendation` ·
`304650000 AAP 2022 Bilirubin Interpretation`.

Row `24559` has a **blank Name** — that is observed, not missing data.

Bottom left: ☑ `Only Lists I Can Use`.

### 2b. `SmartPhrase Lookup` — `smartphrase-lookup-modal-f_000513`

Title `SmartPhrase Lookup`, with a `Go to My Phrases` link top right. Buttons
`+ New User Phrase` · `+ New System Phrase`, a search field top right and a
`Search SmartPhrases` field below.

Grid `ID` | `Name` | `Level` | `Description`:

`103487 A · Facility · ASSESSMENT:` (selected) · `103488 AA · Profile · antacids` ·
`103489 AAA · Facility · abdominal aortic aneurysm` · `103490 AAT · Profile ·
activities as tolerated` · `103491 AB · Profile · antibody` · `103492 ABG ·
Profile · arterial blood gases` · `103493 ABGRESULT · Profile · Arterial Blood Gas
result: pO2 ***; pCO2 ***; pH ***; HCO3 ***_` · `103495 ABNL · Profile · abnormal`
· `103496 ABNTSH · Facility · TSH is abnormal: @LASTTSH@ Plan: (thyroid
plan:310573)` (row-hover highlight) · `103497 ABPM · Facility · ambulatory home
blood pressure monitoring` · `103498 ABS · Profile · absolutely` ·
`102927 ABSCESSOFSKIN · Facility · Plan text for an Abscess of Skin` ·
`103499 ABX · Profile · antibiotics` · `103500 AC · Profile · anticoagulation` ·
`102926 ACANTHOSISNIGRICANS · Facility · Plan for Acanthosis Nigricans of the ***`.

Note `103494` and the gap around `102926/102927` — IDs are not contiguous.
Preserve them.

Bottom left: ☑ `Search Only Phrases I Can Use First ⓘ`.

### 2c. `Select a SmartForm` — `select-a-smartform-modal-f_000391`

Filter fields over a multi-column SmartForms table. **Read the frame before
seeding**; I have its recorded structure but not a verified transcription, so
treat any column list as a claim to check.

---

## 3. `SmartForm Designer` — `smartform-designer-f_000405`

Workspace tab `Workbench`. Heading `SmartForm Designer - (LEGACY) AUTH APPEAL
INFORMATION [330518019] - CRM Forms (Read-Only Mode)`. The short `SmartForm
Designer` and this long form are **one screen**.

Banner: `ⓘ This SmartForm is released and cannot be edited. To make changes, make
a copy of this form.`

**Left pane — the form canvas being designed.** Checkboxes, all unchecked:
`Did not receive timely notice of adverse dete…` · `Difficult to locate
documentation` · `Lacked capacity to understand timeframe` · `Provided
insufficient information about appe…` · `Seeking help related to disability` ·
`Sent request on time to incorrect address` · `Serious illness`. Then:

| label | control |
| --- | --- |
| Reason for late filing valid? | `Yes` \| `No` + required marker |
| Extension requested? | `Yes` \| `No` |
| Extension requested by: | 2×2 button grid — `Health Plan` \| `Member` / `Member Representative` \| `Provider` |
| Extension reason: | doc glyph + ☐ `Need more time to obtain evidence` |
| Override number of days to extend by: | spinner, empty |
| Extension granted? | `Yes` \| `No` + required marker |

No segment is selected in any pair. Canvas footer: `Add Component` ·
`Layout:` `Table` \| `Row` \| `Cell` \| `Formlet` · `Issues`.

**Right pane.** Tabs `Design` (selected) | `Scripting` | `Change History`. Then
`📁 Data Binding — Not available for this component type`. Then `🔧 Properties`:
`Component` `[Root Component]`; `Component Name` `RootComponent` + ☐ `Autoname`;
`Miscellaneous` `✓ Wrap captions`; `Content Source`, `Locking Group`,
`Print Group` all empty; an `Appearance` heading clipped at the bottom.

Footer: `Open` · `Restore` · undo/redo · `Preview` · `••• More ▾` — then
`Current contact status: Released ⓘ`, ☐ `Release this contact` (greyed),
`Save` (greyed), `Accept` (greyed), `× Close`.

---

## 4. `Relationship Builder` — `relationship-builder-f_000435`

Workspace tab `Workbench`. Heading `Relationship Builder - ABDOMINAL TENDERNESS
[35200]`. Left rail `ABDOMINAL …` + `Settings`.

Banner: `ⓘ Relationship record is released by Epic and may not be edited.`

Grid columns: `Description` | `Group 1 Elements` | `Group 1 Values` |
`Group 1 Disable` | `Group 2 Elements` | `Group 2 Values` | `Group 2 Disable`.

One row group, `Exclusions`:

- Description `No Tenderness`
- Group 1 Elements `EPIC#IPPO0070 (no abdominal tenderness)`; Group 1 Values `1`
- Group 2 Elements, a stacked list: `EPIC#PEAB0201 (generalized tenderness)` ·
  `EPIC#PEAB0205 (epigastric)` · `EPIC#PEAB0206 (periumbilical)` ·
  `EPIC#PEAB0211 (LLQ)` · `EPIC#PEAB0210 (LUQ)` · `EPIC#PEAB0213 (guarding)` ·
  `EPIC#PEAB0214 (rebound)` · `EPIC#PEAB0209 (RLQ)` · `EPIC#PEAB0208 (RUQ)` ·
  `EPIC#IPPO0050 (incisional tenderness)` · `EPIC#PEAB0207 (suprapubic)`;
  Group 2 Values `1`
- both `Disable` columns empty

Footer: `Context:` field + ⓘ — then ☐ `Release` (greyed), `Save` (greyed),
`Accept` (greyed), `× Cancel`.

Its picker is `launching-relationship-builder-f_000428`. A
`Welcome to the Relationship Builder` dialog is also recorded at 07:13 — read the
frame before modelling it; it is a first-run card in the brief-10 sense.

---

## 5. `Macro Editor` — `macro-editor-f_000454`

**`observed_empty`.** Workspace tab `Admin`, activity tab `Macro Editor`.
Toolbar: `Search or add back` input · `+ Find` · `+ Create New Macro` ·
`↕ Alphabetize`. **The body is empty.** No grid, no list, no empty-state text.

This screen had twenty frames of dwell and shows nothing in all of them, which is
the clearest case in v02 that dwell time and content are different things. Do not
render a list here.

---

## 6. `Infusion Duration Table` — `infusion-duration-table-f_000552`

Workspace tab `Workbench`. Heading `Infusion Duration Table`. Left rail
`Infusion Dura…` + `Settings`. Toolbar `✏ Edit` · `Save` · `↺ Restore`.

**Yellow warning banner**, verbatim:

> Infusion Duration Table is disabled. To enable it, in Text go to Clinical
> Administration > Management Options > Edit System Definitions (LSD) >
> Specialties, Other Modules > Treatment Plan Scheduling Screen, set Enable
> calculated durations? to 1-Infusion Duration Table.

**Info banner**, verbatim:

> Use the following grids to specify medications and medication combinations that
> are relevant to scheduling. The durations will be used to automatically
> calculate the length of the infusion visit using the medications in the
> treatment day. For each entry, a default scheduling duration must be specified
> in the second column.

Tabs `Single Medications` (selected) | `Combination Medications` — the second was
never opened.

Grid `Medication` | `Duration (minutes)`, rows visible:

| medication | duration |
| --- | --- |
| Ado-Trastuzumab Emtansine | 90 |
| Arsenic Trioxide | 120 |
| azaCITIDine | 90 |
| Bendamustine HCl | 120 *(selected)* |
| Bevacizumab | 60 |
| Bleomycin Sulfate | 120 |
| Bortezomib | 120 |
| Brentuximab Vedotin | 60 |
| CARBOplatin | 120 |
| Carfilzomib | 180 |
| Carmustine | 240 |
| Cetuximab | 120 |

The list scrolls beyond `Cetuximab` — **seed only these twelve** and record that
more exist. Preserve the tall-man casing (`azaCITIDine`, `CARBOplatin`).

---

## 7. `ProcDoc Charge Mapping Tester` — `procdoc-charge-mapping-tester-f_000369`

A standalone workspace with no visible parent breadcrumb. **Its parentage is
unknown** — it sits chronologically where `Study Maintenance` falls in the Beacon
Admin menu, and the `More ▾` dropdown was open shortly after, so either is
possible. Do not attach it to a menu row on positional evidence alone.

Fields, all lookups:

| label | value |
| --- | --- |
| Procedure | empty |
| Test Patient (optional) | empty |
| Test as User: | `WILLOW INPATIENT, PRIME ADMIN` |
| in Context (optional): | `Emergency Department` |
| in Dept: | `EMH IP PHARMACY` |
| LQF: | empty |

Then `Computed Charges` with the empty state `No charges found`, and
`Last updated: 3:03:43 PM`.

Also in this chapter: a `Research Study Lookup` modal
(`research-study-lookup-f_000353`) with search-by toggles `Study` / `Employee` /
`Provider`, and a `Troubleshooting Tools` dialog at 09:36. Read both frames
before modelling; I have their recorded structure but not verified
transcriptions.

---

## Acceptance

- [ ] **No coverage fraction is stated for `SmartTool Editors`**; the gaps doc
      says the submenu was never expanded, cites `f_000468`, and records the
      workspace rail as an indirect signal only
- [ ] One SmartTools shell copied per editor; each editor's `Settings` panel
      transcribed **separately** — `SmartText` and `System SmartPhrase` disagree
      on the SmartLink-formatting default and both are correct
- [ ] `SmartList` and `SmartPhrase Lookup` are modals, not workspace pages
- [ ] `SmartList` row `24559` keeps its blank name; `SmartPhrase Lookup` keeps its
      non-contiguous IDs
- [ ] `SmartLink` has no Save/Accept, matching its read-only state
- [ ] `SmartForm Designer` renders the designed form's controls with no segment
      selected, and its right-hand Properties panel
- [ ] `Macro Editor` renders chrome over an empty body — `observed_empty`
- [ ] `Infusion Duration Table` seeds exactly twelve rows and records that the
      list continues; both banners verbatim; `Combination Medications` never opened
- [ ] `ProcDoc Charge Mapping Tester` is not attached to any menu row
- [ ] Tall-man casing preserved: `azaCITIDine`, `CARBOplatin`, `NEUPOgen`
- [ ] Every clipped string stays clipped with a note
- [ ] No geometry measured from these frames
