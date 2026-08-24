# v02 findings — what the second recording shows, and what rl_epic does not have

Not a build brief. This is the survey that decides what the briefs should be, and
in what order. Read it before writing any of them.

**Source:** `VID_20260809_012734083.mp4`, 09:38, same night and camera as v01,
thirty-nine minutes later. Run at 1 fps (DEC-027's first pass), all stages,
inventory verified at rl_epic `5d0a1233`.

**578 frames → 168 screens → 46 distinct names → 20 unnamed.** 148 named, 75
accepted, 256 review items.

**What this evidence supports:** labels and their exact wording, row and tab
order, nesting, control types, enabled/disabled/selected state, presence and
absence. **Not geometry** — same handheld caveat as brief 10, same instruction:
inherit spacing from existing primitives, never scan these frames for pixels.

---

## 1. The headline: v02 is a tour, not a workflow

This is the finding that governs everything else.

**174 of 578 frames — 30% — are the hub.** The operator returns to Willow
Project Team between nearly every activity. What the recording contains is a
rapid pass over roughly forty-five activities in nine and a half minutes, not
sustained work on a few.

Dwell, counted in frames (≈ seconds at 1 fps):

| | count |
| --- | --- |
| non-hub screens with ≥ 10 frames | 14 |
| with 4–9 frames | 21 |
| with ≤ 3 frames | 10 |

The longest single dwell outside the hub is **Episode Type at 32 frames**. The
median non-hub screen gets about four seconds.

v01 was the opposite shape: six activities, two of them worked through section by
section for two minutes each. Briefs 03–07 could specify a page because the
recording demonstrated a page.

**Consequence: v02 cannot yield forty-five built screens, and any brief that asks
for that is asking for invention.** Four seconds of a screen shows a heading, a
rough layout and maybe a toolbar. It does not show a column set, an empty state,
a validation message or what a button does. The repo already has the vocabulary
for this — `observed`, `observed_empty`, `not_captured` with a reason — and most
of v02 belongs in the third category with a note, not in a component.

---

## 2. The most valuable finding: two toolbar modules, fully enumerated

Same class of find as v01's Rx Admin menu, and for the same reason — a menu
transcribes cheaply, at high confidence, and it fixes the *denominator* for
module coverage. v01's coverage boundary listed seven never-opened dropdowns.
v02 opens two of them completely.

### `Inventory ▾` — 9 rows, and that is the whole menu

The panel's bottom border is visible below the last row, so this is exact rather
than a floor.

| # | row | seen? | frames |
| --- | --- | --- | --- |
| 1 | Update Balances | yes | 17 |
| 2 | Inventory | yes | 13 |
| 3 | Shortages | yes | 25 |
| 4 | Inventory Workqueues | yes | 4 |
| 5 | Lot and Expiration Manager | yes | 6 |
| 6 | **Inventory Item Report** | **never opened** | — |
| 7 | Adjust Par Levels | yes | 11 |
| 8 | Cycle Count | yes | 10 |
| 9 | **Request Queue** | **never opened** | — |

Best frame: `f_000085` (01:25). Also open at `f_000083`, `f_000126`, `f_000136`,
`f_000148`, `f_000188`.

### `Beacon Admin ▾` — 10 rows, three of them submenus

Bottom border visible below `Infusion Duration Table`.

| # | row | seen? | frames |
| --- | --- | --- | --- |
| 1 | Protocol Builder | yes | 11 |
| 2 | Order Group Builder | yes | 3 |
| 3 | Treatment Modification Builder | probably — see below | 5 |
| 4 | Episode Type Editor | yes | 32 |
| 5 | Beacon Security | yes | 4 |
| 6 | Therapy Plan Tools ▸ | submenu enumerated | — |
| 7 | **Study Maintenance** | **never opened** | — |
| 8 | SmartForms ▸ | submenu NOT enumerated | — |
| 9 | SmartTool Editors ▸ | submenu NOT enumerated | — |
| 10 | Infusion Duration Table | yes | 8 |

Best frame: `f_000220` (03:40). Also `f_000336`, `f_000498`.

**`Therapy Plan Tools ▸` is enumerated** at `f_000322` (05:22): exactly two rows,
`Therapy Protocol Builder` and `Therapy Plan Security`. Both were visited.

**`SmartForms ▸` and `SmartTool Editors ▸` were never expanded.** At `f_000468`
(07:48) the cursor rests on `SmartTool Editors` but the submenu has not opened.
This matters more than the other gaps: roughly nine of v02's screens live under
`SmartTool Editors`, so the largest chapter of this recording has **no known
denominator**. Do not state coverage for it.

### Two corrections this forces

- **`Infusion Duration Table` is a Beacon Admin row, not a Home Infusion child.**
  Stage 07 matched it to `Home Infusion` at 0.76 and I initially read that as the
  first thing behind brief 10's newly-named chevron. Wrong — string coincidence.
  The menu shows it as a top-level Beacon Admin activity.
- **The SmartTools screens are not a separate module.** They sit under
  `Beacon Admin ▸ SmartTool Editors`. Any brief should nest them accordingly.

### And one still unresolved

`MODIFICATION` at 04:03 (5 frames, read at 0.98) is almost certainly
`Treatment Modification Builder`'s screen, caught mid-render or with a truncated
heading. **Do not seed it under either name until a frame settles it** — that is
exactly how brief 07's phantom activities happened.

---

## 3. What rl_epic already has: one screen out of forty-six

I grepped every one of the 46 names across `frontend/app`, `frontend/components`,
`frontend/lib` and `backend`.

- **35 names: no match anywhere.**
- **10 names: matched, but all false positives.** `Locator` matched a `ruff`
  binary inside `backend/.venv`. `MODIFICATION` matched `cpt_codes.csv` and a
  swagger bundle. `Episode Type` matched Hospice intake. `Protocol` matched
  nurse-triage protocols. `SmartText` / `SmartList` / `SmartTools` matched ROI
  letter composers and IdentityManager advisory fields — usages of the concept,
  not the editors. `Inventory` matched the Hospital/Clinic Admin *section* of
  that name and the toolbar label. `Pharmacy Admin` matched a workspace-tab
  label. `Workbench` matched CadenceAdmin.
- **1 name genuinely exists:** `Willow Project Team`.

So v02 is essentially all-new surface. The hub is the only thing already built,
and it is only there because it is where the operator starts.

---

## 4. Codebase context — what to build *on*

Nothing here needs inventing from scratch. Every archetype v02 shows already has
a home in the repo, which is what Reference-This-Repo-First is for.

| v02 archetype | Screens | Reuse |
| --- | --- | --- |
| Record picker (`Launching …`) | 6 (`Cycle Count`, `Protocol Builder`, `Episode Type Admin`, `Beacon Security`, `Therapy Plan Security`, `Relationship Builder`) | `WillowLaunch/RecordPickerGrid.tsx` — brief 10 already proved it takes new activity names cheaply |
| Left sidebar + section panels | `Inventory`, `Episode Type`, `Protocol Builder` | `WillowAdminPage/` — `AdminRecordPage`, `SectionTree`, `SectionPanel`, `SectionControls`, `FieldLookup` |
| Horizontal tabs over a data grid | `SmartList`, `System SmartList`, `SmartText` | `WillowMedList/` — `MedListChrome`, `MedListGrid` |
| Form page, no sidebar | `Update Balances`, `Adjust Par Levels` | `epic/EpicForm.tsx` label:field rows |
| Modal dialog | `Inventory Item Selection` | `shared/DialogShell.tsx` + `useDialogFocusTrap` |
| Toolbar dropdown with real contents | `Inventory ▾`, `Beacon Admin ▾` | `shell/willowMenus.ts` + `TopToolbar` — exactly the `FIND_PATIENTS_GROUPS` pattern brief 10 established |
| Read-only banner / mode toolbar | `SmartForm Designer … (Read-Only Mode)` | `WillowAdminPage/ModeToolbar.tsx` |
| Capture-state bookkeeping | all of it | `backend/app/models/willow_admin_pages.py` + the `willow_*_content.py` seed shape |

The menus in particular are near-free: brief 10 built the machinery, and these
two menus are transcription into an existing structure.

---

## 5. Buildability, by tier

**Tier A — enough footage to specify a screen (≥ 10 frames).** Fourteen:
Episode Type (32), Shortages (25), Macro Editor (20), SmartForm Designer (19),
Update Balances (17), ProcDoc Charge Mapping Tester (14), Inventory (13),
System SmartPhrase (13), Adjust Par Levels (11), Protocol Builder (11),
SmartText-(DEPRECATED) (11), Inventory Item Selection (10), Cycle Count (10),
SmartLink (10).

**Tier B — partial, 4–9 frames.** Twenty-one, including `Inventory: EMC Central
Fill`, `Infusion Duration Table`, `Direct Transfer`, `Lot and Expiration
Manager`, `Relationship Builder`, `Workbench`, `Locator`, the two Security Class
Editors, `SmartList`, `System SmartList`, `SmartTools`. Build the chrome and the
heading; mark the body `not_captured` unless a frame shows it.

**Tier C — a glimpse, ≤ 3 frames.** Ten: `Order Group Builder`, `SmartPhrase
Lookup`, `Pharmacy Admin`, `Order Group Contact`, `Episode Type Admin`,
`Protocol Version`, and four `Launching …` frames. **Catalogue these; do not
build pages for them.** Two seconds of a screen is evidence it exists, nothing
more.

---

## 6. Proposed brief series, in the video's own order

The recording's chapters are clean, so the briefs can follow them:

| Brief | Span | Covers |
| --- | --- | --- |
| **12** | menus first | `Inventory ▾` (9 rows) and `Beacon Admin ▾` (10 rows + `Therapy Plan Tools ▸`). Cheap, exact, and it makes every later brief's coverage claim checkable. Do this one first. |
| **13** | 00:00–03:06 | Inventory module. Tier A: `Update Balances` (+ its `Inventory Item Selection` picker), `Shortages`, `Inventory`, `Adjust Par Levels`, `Cycle Count`. Tier B/C the rest. |
| **14** | 03:08–05:46 | Beacon Admin core. Tier A: `Episode Type`, `Protocol Builder`. Then the two Security Class Editors and `Therapy Protocol Builder` as Tier B. |
| **15** | 06:09–09:36 | `SmartTool Editors` and friends. Tier A: `SmartForm Designer`, `Macro Editor`, `System SmartPhrase`, `SmartLink`, `ProcDoc Charge Mapping Tester`. Note the missing submenu denominator. |

Brief 12 first is the important sequencing point. Without it, briefs 13–15 have
to guess how many activities each module contains, which is how "six of
twenty-two" became a false coverage claim in brief 08.

---

## 7. What to distrust in this catalogue

- **`ProcDoc Charge Mapping Tester` was auto-matched to `Charge Mapping Admin`
  at 0.8235**, just over `classify.fuzzy_threshold` (0.82). They are not the same
  thing. The bucket is `new` either way so nothing downstream breaks, but the
  manifest asserts an identity the pixels do not support. This is the mirror of
  the subset rejections and the contains-one-another rule does not catch it.
- **`section`, `tabs` and `dialog` are hints, not measurements** (DEC-026, widened
  2026-08-21). In v01 three of four `section` values I checked were wrong, all at
  0.79–0.82. Every structural value in this catalogue needs a frame check before
  it reaches a seed.
- **96 of 168 screens had no readable title band.** Names came from the
  full-frame read, not OCR agreement, so the cross-check that usually catches a
  misread was unavailable for most of this video.
- **20 screens were never named at all**, and **50 frames were suppressed by
  `dedupe.min_gap_frames`** in a recording that navigates this fast. Both are
  places a screen could still be hiding — and per DEC-027, dedupe is the first
  thing to examine here, not the sample rate.

---

## 8. What a 2 fps sweep would and would not buy

Not yet, and here is the reasoning so it does not get relitigated.

The DEC-027 trigger is a *specific* question — a suspected short-lived screen, an
unexplained gap. v02 has two candidate questions: the 50 suppressed frames, and
the 20 unnamed screens. But neither is a sampling problem on its face: at 1 fps
this video already yields 168 screens from 578 frames, and the unnamed ones are
unnamed because the title band was illegible, which a higher rate does not fix.

Check `dedupe.min_gap_frames` and representative-frame selection first. That is
where v01's one genuine 2 fps find actually lived.

---

# 9. Frame pass — the corrected numbers

Section 5's tiering was wrong and is superseded. It gated buildability on frame
count (≥10 frames = buildable), which produced "14 of 45". A frame pass over one
representative frame per screen shows that was the wrong criterion twice over:
`Order Group Builder` at 3 frames is one of the most completely legible screens in
the recording, and the repo's own precedent — Report Settings, built to full
fidelity from **two** frames — already said so.

The right criterion is: **is there one frame where the screen is legible and
unoccluded?** A static replica needs one good look, not thirty.

## What 46 names actually resolve to

| | count | share |
| --- | --- | --- |
| Already built | 1 | 2% |
| **Not a screen at all** — a label misread as one | 7 | 15% |
| Alias of another screen (heading vs activity tab) | 4 | 9% |
| Configuration of one shared launcher component | 6 | 13% |
| **Real screens to build** | **28** | **61%** |

### The 7 that are not screens

- `Pharmacy Admin`, `Workbench`, `SmartTools` — **workspace tab** labels. Same
  class of error as v01's `Package`.
- `Locator`, `Protocol`, `Protocol Version`, `Order Group Contact` — **stepper tab
  labels inside the `Launching …` picker modals.**

That last group is the significant find. The `Launching X Builder` pickers are a
**two-step wizard**: step 1 picks the record, step 2 picks the version/contact.
Confirmed in three frames — `f_000239` (Treatment Modification Builder: `Locator`
→ `Locator Version`), `f_000328` (Therapy Protocol Builder: `Protocol` →
`Protocol Version`), `f_000226` (Order Group Builder: `Order Group` → `Order Group
Contact`). Each shows a grid, a `Create a New …` action, and Continue/Accept +
Cancel. One component, six observed configurations.

### The 4 aliases

`Inventory: EMC Central Fill` = `Inventory` · `Episode Type Admin` =
`Episode Type` · `SmartForm Designer - (LEGACY) AUTH APPEAL…` =
`SmartForm Designer` · `SmartText - (DEPRECATED) - EHS SBO…` = `SmartText`.
In every case the long name is the heading with a record loaded and the short one
is the activity tab.

### One identity resolved

**`MODIFICATION` is `Treatment Modification Builder`.** `f_000243`'s heading reads
`MODIFICATION ONCBCN RSH TRASTUZUMAB REDUCTION [2038] - 11/06/2013 [1] -
Treatment Modification B…`. The model returned the record's first word as the
screen name. Section 2's "do not seed it under either name" is now settled.

## Of the 28, how much is specifiable

24 inspected directly; 4 not yet opened (`Relationship Builder`, `SmartList`,
`System SmartList`, `SmartPhrase Lookup`). Of the 24:

- **22 are fully specifiable** — heading, toolbar, tabs, field labels, control
  types, states, grid columns and visible rows all legible.
- **2 are chrome-only and genuinely empty**: `Cycle Count` (toolbar + "Open
  another location" + an empty body) and `Macro Editor` (search/Find/Create New
  Macro/Alphabetize over an empty body). These are `observed_empty` — the state
  was observed and it is empty — not `not_captured`. `Macro Editor` had 20 frames
  of dwell and still shows nothing, which is the clearest proof that dwell time
  and content are different things.

## Five shells cover nineteen of the screens

The build is far smaller than 28 separate screens:

| Shell | Screens on it |
| --- | --- |
| **Workbench builder** — left rail breadcrumb, Open/Version/Save/Save As/Restore toolbar, read-only banner + `Try Lock`, tabs, tree or grid | Protocol Builder, Therapy Protocol Builder, Treatment Modification Builder, Order Group Builder, SmartForm Designer, Infusion Duration Table (6) |
| **Security Class Editor** — Name + Comments, Security Points/Usage Report tabs, Toggle All + filter, Active/Number/Name/Categories grid, help-text pane | Beacon -, Therapy Plan - (2) |
| **SmartTools** — icon rail (SmartTexts / SmartList / SmartPhrases / SmartLinks), editor pane, right-hand Settings panel | SmartText, System SmartPhrase, SmartLink, SmartList, System SmartList (5) |
| **Two-step launcher wizard** | 6 picker configurations |
| **Inventory activity pages** — mostly distinct, sharing the empty-state illustration idiom | Update Balances, Draft Medication Request, Direct Transfer, Inventory, Shortages, Inventory Workqueues, Lot and Expiration Manager, Adjust Par Levels, Cycle Count (9) |

Standalone: `Episode Type` (11 tabs + overflow), `ProcDoc Charge Mapping Tester`,
`Macro Editor`, `Inventory Item Selection`, `Relationship Builder`,
`SmartPhrase Lookup`.

## Bonus enumerations the frame pass turned up

- **`Inventory: EMC Central Fill`'s own toolbar** lists the module's activities —
  Create Request, Direct Transfer, Update Balances, Request Queue, Lot and
  Expiration Manager, Inventory Item Report, Print Item List, Print Item Labels,
  Adjust Par Levels, More. It includes both rows the `Inventory ▾` menu never
  opened, so they are reachable two ways.
- **The SmartTools left rail** lists SmartTexts, SmartList, SmartPhrases,
  SmartLinks — partially recovering the `SmartTool Editors ▸` denominator that
  section 2 recorded as unknown.

## Headline

**28 screens, 5 shells, 1 launcher wizard, 2 menus.** Not 45 pages, and not the
14 I first estimated. 22 of the 28 are specifiable today from frames already in
hand; 4 need a look; 2 are legitimately empty.

---

# 10. Closing the audit — what the fixture's unaudited entries turned out to be

v02's fixture was recorded with 20 `name: null` entries and four workspace-tab
labels nobody had opened. Auditing all 24:

| | count | outcome |
| --- | --- | --- |
| Launcher/picker states of built screens | 14 | already covered |
| The hub with a menu open | 4 | already covered |
| Shortages' populated `Affected Packages` lookup | 2 | **brief 17** |
| Alternate states of built screens | 2 | Protocol Builder scrolled, Order Group Builder |
| **Blank create-states, not built** | **2** | **need a brief** |

## The two that still need building

Both are on the SmartTools shell, both are the **new-record** state, and neither is
a variant of what brief 15 built — brief 15's editors all had a record loaded.

**`f_000516` (08:36)** — a blank editor: empty `Name`, `Description` with a
`Populate from Text` link, `Text Format` with **no segment selected**, unchecked
`Released`, then `Synonyms` and a green **`Levels`** panel. No built screen has
`Levels`. Which record type this creates is not settled by the frame; `SmartText` is
the closest activity, not a confirmed identity.

**`f_000529` (08:49)** — the blank **SmartLink** create-state: `Select a SmartLink
type.` centred over the balloon empty state, and a Settings panel carrying `Name`,
**`Mnemonic`**, `Description`, `SmartLink Type`, `Search Availability ⓘ`, unchecked
`Released`, `Synonyms`, `Overrides`. Brief 15's loaded SmartLink shows neither
`Mnemonic` nor a type-selection state.

Both frames are staged in `~/build-evidence/17-v02-shortages-lookup/`'s sibling —
they are **not** yet shipped anywhere. Ship them before citing them; that mistake
has now been made twice in this sequence.

## What this closes

Every one of v02's 168 fixture entries has now been either audited against a frame
or explicitly marked unaudited. 13 carry `known_misread`. The remaining `null`
entries are launcher states whose parent screens are built, and one — 02:31,
`Launching Adjust Par Levels` — is a name a human has read that the fixture format
cannot yet express (DEC-030's open question).
