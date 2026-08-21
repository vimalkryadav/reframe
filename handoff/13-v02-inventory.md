# Build brief 13 — the Inventory module

**Branch:** `pharmacy-admin`. **Depends on brief 12** for the `Inventory ▾` menu.

Nine activities and one picker modal, 00:00–03:06 of v02. This is the first of
three screen briefs and the most self-contained: the Inventory activities barely
reference each other, so they can be built in any order within the brief.

Read [`11-v02-findings.md`](11-v02-findings.md) §9 for how these were counted.

**Evidence:** `~/build-evidence/13-v02-inventory/` — 19 frames, named
`<screen>-<frameid>-<timestamp>.jpg`. Every name is a claim; check it against the
frame.

**Provenance:** rectified handheld footage. Authoritative for labels, order,
control types and states. **Not for geometry** — inherit spacing from existing
primitives, never measure these frames. Same rule as brief 10.

---

## The shape they share

Seven of the nine are a **full-window activity page**: a `Pharmacy Admin`
workspace tab, one or more activity tabs beneath it, a heading, then content, and
a `× Close` bottom-right. No left navigation sidebar — that is the Rx Admin
pattern from briefs 03–07 and it does **not** apply here.

Four of them show the same **empty-state idiom**: a hot-air-balloon illustration
over a faint mountain/cloud backdrop with one line of guidance text beneath.
`Update Balances`, `Direct Transfer`, `Inventory Workqueues` and `Adjust Par
Levels` all use it, with different text. Build it once in this feature folder and
reuse it *within* the folder — per Replicate-don't-generalise, do not promote it
to a shared component for other modules to import.

The illustration itself is Epic artwork. **Describe it, do not redraw it** — the
brief 10 rule for the Hyperdrive video card applies here too.

---

## 1. `Update Balances` — `update-balances-f_000027`

Activity tab `Update Balances`. Heading `Update Balances`.

Fields, in order:

| label | control | observed value |
| --- | --- | --- |
| Location: | lookup (magnifier) | `EMH Central Pharmacy` |
| Reason: | lookup + **required marker** | empty |
| Comments: | text, full width | empty |
| Inventory item: | lookup + **required marker** | empty |
| Current balance: | read-only | empty |
| Increase balance by: | short text | empty |
| Increase stock value by: | short text | empty |

Beside `Reason:` sits a `Type:` segmented group — `Increase stock` |
`Decrease stock` | `Set stock level`. **No segment is selected** in the frame.
Note the field labels say "Increase balance by" / "Increase stock value by",
which tracks the `Increase stock` segment; whether those labels change with the
segment was never demonstrated, so do not make them dynamic.

`Update` button sits inline right of `Increase balance by`, **greyed**.

Empty state below: balloon illustration + `Perform an update to see a summary of
previous balance updates`.

Footer: `× Close`.

## 2. `Inventory Item Selection` — a modal picker

`inventory-item-selection-f_000017`, plus two more sightings.

- Title `Inventory Item Selection`, `×` close at top right
- Search input + `Search` button
- `Search using:` — four checkboxes, **all checked**: `Associated Records`,
  `Identity IDs`, `Supplier IDs`, `NDCs`; then a `Limit to Item Types ▾` control
- Grid columns: `Matched On` | `Inventory Item` | `Is Active?`
- Rows are real and transcribable: `Abilify Maintena 300 MG intramuscular prsy`,
  `Abilify Maintena 400 MG intramuscular prsy`, `Abraxane 100 MG intravenous susr`,
  `acebutolol 200 MG oral capsule` (selected), `acetaminophen 120 MG rectal
  suppository`, `acetaminophen 160 MG/5ML oral solution, 5 mL`, … all `Is Active? =
  Yes`. `Matched On` reads `Inventory Item` on every visible row.
- `Show inactive` checkbox, bottom left, unchecked
- `Accept` / `Close` bottom right, both **greyed**

Use `shared/DialogShell.tsx`. It is opened from `Update Balances`' `Inventory
item:` magnifier — that is the transition the frames show.

## 3. `Inventory` — `inventory-emc-central-fill-f_000076`

The richest screen in the brief. Heading `Inventory: EMC Central Fill`; the
activity tab reads the same. `Inventory` and `Inventory: EMC Central Fill` are
**one screen** — the long form is the heading with a record loaded.

**Its own toolbar is an enumeration of the module** and must be transcribed in
order: `+ Create Request ▾` · `+ Direct Transfer` · `Update Balances` ·
`Request Queue` · `Lot and Expiration Manager` · `Inventory Item Report` ·
`Print Item List` · `Print Item Labels` · `Adjust Par Levels` · `More ▾`.

Note it contains `Request Queue` and `Inventory Item Report` — the two
`Inventory ▾` rows nobody opened. They are enabled-looking buttons here. Follow
brief 12's convention: render them, disabled, saying they were never exercised.

Three panels across the top:

- **left**: `Inventory Items ▾` dropdown over a search field placeholder
  `Search by medication, NDC, or inventory…`, and a partly-visible `Inventory
  Item` row beneath
- **centre**: `Upcoming needs within the following number of days:` with a spinner
  showing `1` and a date-picker glyph; `+ Add` / `Edit` / `Remove` (Edit and
  Remove greyed) plus two icon buttons. Grid columns `Active?` | `Projected Stock
  …` | `Order ID` | `Department` | `Package` | `Upcoming Need`. Empty state:
  `No Upcoming Needs in the next 1 days`
- **right**: `▼ Advanced Filters` — `Rule` (lookup), `Purchase Contract` with a
  selected radio `Include items in contract`

Lower pane, `Inventory Balances`, with its own icon toolbar and a search field:

- a **yellow band** reading `Review Status:`
- `[412011295]` as a heading
- `Note: Changes made to item balance in this session will not be displayed in
  this report until those changes are accepted`
- `Last refreshed Sat Aug 8, 2026 1458` right-aligned
- a card headed `EMC Central Fill` with a `Balance History` link; body
  `Total Balance: 85 each`, `Inventory class: Prescription`,
  `Average daily usage (last 1 month): —`

Footer: `1302 items shown, 1302 items total` · `+ Add Item` · `Remove Item` ·
`× Close`.

## 4. `Draft Medication Request` — `draft-medication-request-f_000054`

Reached from `Inventory`'s `Create Request ▾`. Two activity tabs:
`Inventory: EMC Central Fill` and `Draft Medication Request` (selected) — so this
opens *beside* Inventory rather than replacing it.

- `Priority:` segmented `High` | `Normal` — **`Normal` selected**
- `Expected date:` date field, empty
- `Add Request Comment` button
- `Search request` field top right with a wrench dropdown
- Sub-tabs `Request` (selected) | `Review`
- Item entry field + `+ Add Item` / `− Remove Item`
- Grid: three leading icon columns then `Item`, and truncated headers `P.. S.. S.`
  — **carry them clipped**, the way `NDC_TREE` carries `Fill Label and Barcode
  Scan R`
- Right pane: the balloon empty state
- Lower pane `Requisition`: `Contract: —  Expected Date: —  Supplier: —
  Deliver To: EMC Central Fill`; right side `Draft` and a
  `Show Request Audit Trail` link
- `Summary` section: `Created Date/Time  8/8/2026 2:58 PM`, `User  Prime Admin
  Willow Inpatient`, then columns `Inventory Item` | `Package` | `Quantity` |
  `Package Cost` | `Cost` with em-dash values
- Footer: `🗑 Discard` · `✓ Submit` · `✗ Close Draft`

## 5. `Direct Transfer` — `direct-transfer-f_000063`

Same two-tab arrangement as Draft Medication Request.

- `Source` lookup, value `EMC Central Fill`
- `Destination` lookup, **required marker**, empty
- `Add Transfer Comment` button
- `− Remove Item` (no Add Item button visible)
- Grid: icon columns then `Item`, truncated `P.. S.. S.. S`
- Right: balloon + `Add an item to get started`
- Footer: `Suppress Printouts` checkbox (unchecked) · `Transfer Stock`
  (**greyed**) · `Cancel`

## 6. `Shortages` — `shortages-f_000108`

- Heading `Shortages`; `+ Create Shortage` beneath it; refresh icon top right
- Left `Filters` panel: `Affected Locations`, `Affected Items`,
  `Affected Packages` (all lookups, empty), `Status` (lookup) carrying four
  removable chips — `Draft ×`, `Pending ×`, `Active ×`, `Cleaning Up ×` — then
  `Severity` (lookup), cut by the panel's scroll
- Grid columns: `Shortage` | `Status` | `Latest Status Change` |
  `Your Next Task Due` | `In Stock` | `Average Dail…` (clipped)
- Empty state: `No shortages found`
- A second pane below, showing the balloon illustration
- Footer: `Open Shortage` · `× Close`

## 7. `Inventory Workqueues` — `inventory-workqueues-f_000130`

- Heading `Inventory Workqueues`
- Toolbar: `✓ Mark as Resolved` · `− Remove` · `Filter` (**pressed/active**) ·
  `Workqueue Maintenance` · `Refresh`
- Tabs: `Purchase Requests (0)` (selected) | `Balance Updates (0)` — keep the
  counts in the labels
- Grid columns: `Workque…` | `Entry Date` | `Reasons` | `Request N…` | `Status` |
  `Destination` | `Estimated Cost` | `Bloc…` | `User` (two clipped)
- Empty state: `No requests to review`
- Lower tabs: `Purchase Request Summary` (selected) | `Workqueue History`;
  balloon + `Click on a request to view the report`
- Right `Filter` panel: `Blocked?`, `Destination`, `Estimated Cost`, `Reasons`,
  `Request Number`, `Status` — all lookups, empty — then `✓ Apply` / `Clear`
- Footer: `0 items loaded, 0 items shown, 0 items filtered.` /
  `Last Refreshed: 8/8/2026 2:59:42 PM` · `× Close`

## 8. `Lot and Expiration Manager` — `lot-and-expiration-manager-f_000140`

- Heading `Lot and Expiration Manager`
- `Search by:` group — `Location` lookup with `EMH Central Pharmacy` **selected
  (highlighted text)**, `Lot Number` input
- `▼ Filters` group — `Inventory Item`, `Sublocation`, and
  `Expiring on or Before` as a checkbox + field
- `Showing: 0 of 0` top right
- `Active` | `Inactive` segmented — **`Active` selected**; then an input and
  `+ Add Lot`
- Toolbar: `Refresh` · `Location Balance History ▾` · `× Deactivate at Location` ·
  `× Deactivate All` · `Edit Lot`
- Grid columns: `Lot Number` | `Item Type` | `Expiration` | `Inventory Item` |
  `Package` | `Location` | `Sublocation` | `Manufacturer` | `Comments`
- Empty state: `No lots found based on current search.`
- Right detail panel, all empty: `Lot Number`, `Expiration Date`,
  `Inventory Item`, `Manufacturer`, `Comments`, `Status`

## 9. `Adjust Par Levels` — `adjust-par-levels-f_000156`

**No heading text** — the activity tab is the only identification. Do not invent
one.

- `Clear Filter` button top right
- `Filter by:` then `Last action:` lookup
- Label `Set par and optimum levels:`
- `▾ Apply To Remaining` button, right-aligned
- Body: a heart glyph tile, a small empty dropdown, then the balloon +
  `Select an inventory balance to view how par and optimum were calculated`
- Footer: `0 items shown, 0 items total` · `Open Location` · `Accept` · `Close`

## 10. `Cycle Count` — `cycle-count-f_000176`

**`observed_empty`, not `not_captured`.** The screen was opened and its body is
genuinely empty — a heart glyph and nothing else. Do not render a grid.

- Activity tab `Cycle Count`, no heading text
- Toolbar: `Refresh` · `Print Counting Worksheet` · `Display Options`
- Footer: `Open another location` bottom left · `× Close` bottom right

Its picker is `launching-cycle-count-f_000172` — the `Launching Cycle Count`
dialog. **Brief 14 owns the launcher wizard**; if 14 lands first, reuse it, and
if this brief lands first, build the picker here and 14 will reuse it. Say which
way it went in the component comment.

---

## Two pickers that belong to this chapter

- `launching-inventory-picker-f_000036` — a **Location** picker: `Location` search
  field + `Search`, two-column grid `Location ID` | `Location Name`,
  `Accept` / `Cancel`.
- `location-picker-unnamed-f_000151` — a nearly blank window with `Location:`, an
  empty field and `Search`. Almost certainly the same picker mid-load. Treat as
  one component in two states; do not seed two.

---

## Acceptance

- [ ] Nine activity pages exist and are reachable from `Inventory ▾` (brief 12)
- [ ] `Inventory` renders its ten-button toolbar in order, with `Request Queue`
      and `Inventory Item Report` disabled and labelled never-exercised
- [ ] `Inventory Item Selection` opens from `Update Balances`' `Inventory item:`
      magnifier, on `DialogShell`, with its four checked search-using boxes
- [ ] Required markers appear on `Reason:`, `Inventory item:` and `Destination`
      and nowhere else
- [ ] Greyed controls are greyed: `Update`, `Transfer Stock`, `Accept`/`Close` on
      the picker, `Edit`/`Remove` on Inventory's upcoming-needs panel
- [ ] `Cycle Count` and `Adjust Par Levels` carry no invented heading; Cycle
      Count's body is `observed_empty`
- [ ] Clipped column headers stay clipped, with a note that the full name is
      unknown
- [ ] The balloon empty state is one component inside this feature folder, used
      four times with four different strings, and the artwork is a described
      placeholder rather than a drawing
- [ ] No geometry measured from these frames; component comments say spacing is
      inherited
- [ ] `WILLOW_CAPTURE_GAPS.md` records what each screen did **not** show — no
      populated grid anywhere in this module, no submitted request, no completed
      transfer, and `Create Request ▾` / `More ▾` / `Display Options` never opened
