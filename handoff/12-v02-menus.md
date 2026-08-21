# Build brief 12 — the two toolbar menus v02 opens

**Branch:** `pharmacy-admin`, same as 01–11. Same recording family.

**Do this brief before 13–15.** It is small, exact, and it fixes the coverage
denominator for every screen those briefs specify. Brief 08's "six of twenty-two"
became a false claim because the denominator was a guess; these two menus remove
that risk for the Inventory and Beacon Admin modules.

Read [`11-v02-findings.md`](11-v02-findings.md) first for what v02 is and why its
screens are counted the way they are.

---

## Evidence

```
~/build-evidence/12-v02-menus/
  inventory-menu-f_000085-t01m25s.jpg        Inventory ▾ open, all 9 rows
  inventory-menu-f_000148-t02m28s.jpg        same menu, second sighting
  beacon-menu-f_000220-t03m40s.jpg           Beacon Admin ▾ open, all 10 rows
  beacon-menu-f_000498-t08m18s.jpg           same menu, second sighting
  therapy-plan-tools-f_000322-t05m22s.jpg    Therapy Plan Tools ▸ expanded
  smarttool-editors-cursor-f_000468-t07m48s.jpg   cursor on SmartTool Editors, NOT expanded
  inventory-activity-toolbar-f_000076-t01m16s.jpg the Inventory activity's own toolbar
  smarttools-rail-f_000518-t08m38s.jpg       the SmartTools left rail
```

Same provenance caveat as brief 10: rectified handheld footage. Authoritative for
labels, order, nesting and enabled state. **Not for geometry** — take spacing from
the existing menu components, do not measure these frames.

---

## What exists now

`moduleChrome.ts`'s `WILLOW_TOOLBAR` has nine items. Two of them are the targets
here:

```ts
{ label: "Inventory", Icon: Package, dropdown: true },
{ label: "Beacon Admin", Icon: Zap, dropdown: true },
```

Both are `dropdown: true` with no `groups`, so `TopToolbar` renders each as the
inert "menu not available" button. The buttons are correct and stay; only their
contents are missing.

Brief 10 established the whole mechanism — `FIND_PATIENTS_GROUPS` in
`shell/willowMenus.ts`, referenced from `WILLOW_TOOLBAR`, rendered by
`TopToolbar`'s `dropdown && groups?.length` branch. This brief is two more
constants in that same file, in that same shape. No new machinery.

Note also that `menuConfig.ts` re-exports the Willow menu constants and the ☰
Willow module spreads `RX_ADMIN_GROUPS` into its own groups — which is how brief
10's `Home Infusion` reached the inventory exporter. **These two menus are toolbar
dropdowns only and will NOT reach the exporter** unless they are also attached
where `walkActivities(MODULE_ITEMS)` can see them. See "the exporter question".

---

## A. `Inventory ▾` — nine rows, exactly

The panel's bottom border is visible below row 9 in `f_000085`, so this is the
complete menu, not a floor. Single column, no dividers, no submenus.

| # | label | state |
| --- | --- | --- |
| 1 | Update Balances | screen observed — brief 13 |
| 2 | Inventory | screen observed — brief 13 |
| 3 | Shortages | screen observed — brief 13 |
| 4 | Inventory Workqueues | screen observed — brief 13 |
| 5 | Lot and Expiration Manager | screen observed — brief 13 |
| 6 | **Inventory Item Report** | **never opened** |
| 7 | Adjust Par Levels | screen observed — brief 13 |
| 8 | Cycle Count | screen observed (empty body) — brief 13 |
| 9 | **Request Queue** | **never opened** |

In `f_000085` row 3 (`Shortages`) carries the hover highlight. That is a cursor
state, not a selected state — do not seed it as selected.

**Rows 6 and 9 are `disabled: true`**, consistent with how brief 10 treats
never-observed activities: greyed rather than clickable-but-dead, so an operator
verifying against the video can see where the build stops.

**Both also appear as buttons on the `Inventory` activity's own toolbar**
(`f_000076`): `Create Request ▾ · Direct Transfer · Update Balances · Request
Queue · Lot and Expiration Manager · Inventory Item Report · Print Item List ·
Print Item Labels · Adjust Par Levels · More ▾`. So they are reachable two ways,
and that toolbar is a second independent enumeration of the module. Brief 13 owns
the toolbar; it is listed here because it corroborates the menu.

---

## B. `Beacon Admin ▾` — ten rows, three of them submenus

Bottom border visible below row 10 in `f_000220`.

| # | label | submenu | state |
| --- | --- | --- | --- |
| 1 | Protocol Builder | — | screen observed — brief 14 |
| 2 | Order Group Builder | — | screen observed — brief 14 |
| 3 | Treatment Modification Builder | — | screen observed — brief 14 |
| 4 | Episode Type Editor | — | screen observed — brief 14 |
| 5 | Beacon Security | — | screen observed — brief 14 |
| 6 | Therapy Plan Tools | ▸ **enumerated** | see below |
| 7 | **Study Maintenance** | — | **never opened** |
| 8 | SmartForms | ▸ **not enumerated** | child screen observed — brief 15 |
| 9 | SmartTool Editors | ▸ **not enumerated** | child screens observed — brief 15 |
| 10 | Infusion Duration Table | — | screen observed — brief 15 |

Row 4 reads **`Episode Type Editor`** in the menu, while the activity it opens is
titled `Episode Type Admin` in its tab and `Episode Type - <record>` in its
heading. Keep the menu label as the menu shows it; brief 14 handles the screen's
own naming.

Row 7 is `disabled: true` for the same reason as Inventory's two.

### `Therapy Plan Tools ▸` — two rows, complete

From `f_000322`, where the submenu is open beside the parent:

1. `Therapy Protocol Builder` — screen observed (brief 14)
2. `Therapy Plan Security` — screen observed (brief 14)

### `SmartForms ▸` and `SmartTool Editors ▸` — contents NOT captured

Give both `hasMore: true` and no `children`, exactly as `Rule Deferral Admin`
already does in `RX_ADMIN_GROUPS`. **Do not infer their contents**, and this is
the one place in v02 where the temptation is real, because brief 15 will build
about nine screens that live under `SmartTool Editors`. Knowing the children
exist is not knowing the list.

There is one partial, indirect signal worth recording as a note but **not** as
menu children: the SmartTools workspace's own left rail (`f_000518`) lists
`SmartTexts`, `Paper Settings…`, `SmartList`, `SmartPhrases`, `Manage Phrases`,
`SmartLinks`, `Find SmartLinks`. That is a navigator rail inside the workspace,
not the menu's submenu, and the two need not match. Record it in the capture-gaps
doc as the closest thing seen; leave the submenu unenumerated.

At `f_000468` the cursor rests on `SmartTool Editors` and the submenu has not
opened — worth citing in the gap note, because it shows the operator went near it
and the frame still does not answer the question.

---

## The exporter question

`export-inventory.mjs` walks `MODULE_ITEMS`, not toolbars. Brief 10's
`Today's Patients` is invisible to the inventory for exactly this reason, and
these two menus would go the same way: nineteen activity labels that the app
renders and the catalogue cannot see.

That matters more here than it did for one row. reframe classifies v02's screens
against this inventory, so nineteen genuine activities would come back
`bucket: new` with no matching entry — indistinguishable from screens the app
really lacks.

**Decide it deliberately rather than by omission.** Two defensible options:

1. **Attach the menus where the walker sees them**, the way the ☰ Willow module
   spreads `RX_ADMIN_GROUPS`. Only correct if these activities genuinely belong to
   a module's activity list and not just to a toolbar.
2. **Add the toolbar as an exporter source**, so `WILLOW_TOOLBAR`'s transcribed
   dropdowns are walked too.

Option 2 looks right — a toolbar dropdown's contents are activities by any
reasonable reading, and it fixes `Today's Patients` in the same change. But it is
your call and it touches the contract, so it should be a recorded decision rather
than a side effect. Whichever way it goes, say so in
`docs/reference/WILLOW_CAPTURE_GAPS.md`.

---

## Acceptance

- [ ] `Inventory ▾` opens a real nine-row menu; rows 6 and 9 disabled; no dividers
- [ ] `Beacon Admin ▾` opens a real ten-row menu; row 7 disabled; rows 6, 8 and 9
      carry a submenu chevron
- [ ] `Therapy Plan Tools ▸` expands to its two transcribed rows
- [ ] `SmartForms ▸` and `SmartTool Editors ▸` carry `hasMore` and **no**
      children, with a comment saying their contents were never seen
- [ ] The seven rows that open a screen resolve through `nav.ts` once briefs 13–15
      build them; until then they behave like any not-yet-built activity
- [ ] `menuConfig.ts` and `willowMenus.ts` both stay under the 800-line cap
- [ ] `WILLOW_TOOLBAR`'s comment no longer implies only `Rx Admin` and
      `Find Patients` have known contents — it is four menus now
- [ ] The exporter question above is decided and recorded either way
- [ ] `WILLOW_CAPTURE_GAPS.md` records: `Inventory Item Report`, `Request Queue`
      and `Study Maintenance` as named-but-never-opened; `SmartForms` and
      `SmartTool Editors` submenus as unenumerated, citing `f_000468`; and the
      SmartTools rail as the closest indirect signal

## What this brief deliberately does not do

No screens. Every row above that opens something is specified in brief 13, 14 or
15. Building a menu row's destination from the row's label alone is the failure
this sequencing exists to prevent.
