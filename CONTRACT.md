# The inventory contract

How Reframe learns what a target project has already built, without knowing
anything about that project.

Rationale is in [DEC-012](DECISIONS.md#dec-012--the-inventory-contract-is-owned-by-rl_epic).
Short version: the classifier needs `rl_epic`'s route knowledge, but Reframe must
stay ignorant of Epic — so the coupling is inverted. The target project exports a
generic file; Reframe matches names against a list.

```
rl_epic/scripts/export-inventory.mjs  →  inventory.json  →  reframe stage 07
   (knows nav.ts, menuConfig.ts,          (generic:            (knows nothing
    modalActivities.ts, moduleChrome.ts,   label, route,        about Epic)
    app/ routes)                           status, aliases)
```

---

## Schema

```jsonc
{
  "schema_version": 1,
  "project": "rl_epic",
  "generated_from": {
    "commit": "9a0a4ad9",
    "sources": ["lib/nav.ts", "shell/modalActivities.ts", "shell/menuConfig.ts",
                "shell/moduleChrome.ts", "app/**/page.tsx"]
  },
  "entries": [
    {
      "label": "Bed Board",                          // required — the canonical activity name
      "aliases": ["Bed Planning", "Bed Events Summary"],
      "route": "/grand-central/bed-board",           // null when status is disabled/stub
      "module": "Grand Central",
      "status": "built",                             // see status values below
      "source": "ACTIVITY_OVERRIDES",                // provenance, for debugging a bad match
      "component_paths": ["frontend/components/GrandCentral/BedBoard/"]
    }
  ]
}
```

### Required vs optional

| Field | Required | Notes |
| --- | --- | --- |
| `label` | ✅ | Must be unique across entries. Duplicates are a hard error. |
| `status` | ✅ | One of the four values below. |
| `aliases` | — | Defaults to `[]`. Must not collide with any `label`. |
| `route` | — | `null` is meaningful for `disabled` and `stub`. |
| `module` | — | Used for the `other` bucket and for grouping `BUILD_QUEUE.md`. |
| `source` | — | Provenance only; never affects matching. |
| `component_paths` | — | Lets the reviewer jump straight to the code for a `partial`. |

### Status values

These four are the reason the contract is worth designing rather than dumping a
list of route strings. Each carries different information for the build queue.

| Status | Meaning | Classifier maps to |
| --- | --- | --- |
| `built` | A real page exists at `route`. | `built` |
| `lookup_scoped` | Reached by choosing a record in a lookup first — a patient, but equally a formulary, a medication or a workstation. Built, but not directly addressable. | `built` |
| `disabled` | The activity is **known and deliberately unbuilt** — in `rl_epic` this is a `disabled: true` marker in `menuConfig.ts`. | `new` |
| `stub` | Falls through to a generic `/activity/<slug>` placeholder page. Reachable, but not implemented. | `new` |

`disabled` versus never-mentioned is the distinction most worth preserving. A
`disabled` entry means someone already looked at the reference, recognised the
activity, and chose not to build it — that is different information from a screen
nobody has ever catalogued, and it belongs in the build queue with that context
attached.

---

## What the `rl_epic` exporter must do

Lives at `rl_epic/scripts/export-inventory.mjs`. Reads five sources, all of
which are already maintained as part of normal development:

| Source | Entries (at commit `9a0a4ad9`) | Contributes |
| --- | --- | --- |
| `frontend/lib/nav.ts` → `ACTIVITY_OVERRIDES` | 85 | Activity label → real route. Status `built`. |
| `frontend/components/shell/modalActivities.ts` | 34 | Lookup-scoped activities. Status `lookup_scoped`. Also a LABEL source — see below. |
| `frontend/components/shell/menuConfig.ts` → `disabled: true` | 27 | Known but unbuilt. Status `disabled`. |
| `frontend/components/shell/moduleChrome.ts` → toolbar dropdowns | 22 | Activities reachable only from the activity toolbar, not the ☰ menu. |
| `frontend/app/**/page.tsx` | 150 | Ground truth on which routes actually exist. |

### The standing rule: if a structure names an activity, the exporter walks it

Three times now a real activity has been invisible to `inventory.json` because the
file naming it was not read — toolbar dropdown contents (brief 12), the modal-activity
map (brief 15), and a `moreMenu` field a parallel implementation introduced. Each
time the symptom was identical: reframe reports `bucket: new` for a screen that was
built weeks earlier, which is indistinguishable from a screen the target really
lacks, and that is the one confusion this file exists to remove.

Enumerating sources one at a time has now failed three times, so the rule is the
general one:

> **Any structure in the consuming project that names an activity is a source, and
> adding such a structure without teaching the exporter to walk it is an incomplete
> change.**

A screen's *reachability* and its *menu path* are different facts. The catalogue
needs the first. Where a screen has no menu path at all, its label belongs in
`ACTIVITY_OVERRIDES` — which is label→route by design — rather than being derived
from its route, because un-slugifying a path into a name lets a directory name
become an activity name.

The corollary for reviewers: a PR that adds a menu, a dropdown, a cascade or a
route-only screen should be checked against the exporter's output, not just against
the screen. The entry count moving is the evidence the change is finished.

#### `disabled` is a claim about the menu row, not about the screen

Found while merging a parallel implementation: deriving status from menu semantics
alone reported `Record Viewer` as `disabled` with no route, when it has been built
at `/roi/record-viewer` since the HIM work. A greyed menu row means *this row does
not navigate*. It does not mean the screen is absent, and `disabled` must not
short-circuit the ladder before reachability is read.

So: **an `ACTIVITY_OVERRIDES` entry is evidence of reachability and outranks a menu
row's `disabled` flag.** A screen can be greyed in one menu and live at a route,
and the catalogue has to say `built`, because that is what a consumer needs to know.

#### The remedy for menu data held inside a component is to move it, not to parse it

Two more instances turned up on `main` — a `MoreMenu` and a `BuildToolsMenu` holding
their rows as inline component data, so an In Basket suite and `Department
Providers` are named by no file the exporter reads.

By the rule above they are sources. But the fix is **not** to teach the exporter to
parse components: inline JSX data is a moving target, and an exporter that guesses at
it will eventually emit an entry nobody wrote. The fix is to extract the data to a
config module, which is what `willowMenus.ts` already exists to be — brief 10 split
the Willow menus out of a component for exactly this reason.

**Menu contents are configuration. A menu whose rows live only inside its renderer
is uncataloguable by construction**, and that is a defect in the component rather
than a gap in the contract.

### Why `modalActivities.ts` is a label source too

Added for brief 15, and the same failure as the toolbar one. Five activities built
in that brief had real pages but no menu path, because their menu path is a submenu
nobody ever expanded. `modalActivities.ts` was already read for *status* but not
for *labels*, so those five were invisible to `inventory.json` and would have come
back `bucket: new` — a screen that exists reported as one that does not.

Attaching them to a menu was not available: it would have meant inventing the
contents of the unexpanded submenu. Reading the map that already lists them was.
294 → 300 entries; the sixth was a pre-existing gap, `Patient Lookup`.

The general rule this establishes: **if the app can reach an activity, some file
names it, and that file is a candidate source.** A screen's reachability and its
menu path are different facts, and the catalogue needs the first.

### Why the toolbar is a source

Added for brief 12. The exporter walked `MODULE_ITEMS` — the ☰ activity menu — and
nothing else, so a transcribed **toolbar** dropdown was invisible to `inventory.json`
however well evidenced it was: brief 10's `Find Patients ▾` contributed nothing, and
brief 12's `Inventory ▾` and `Beacon Admin ▾` would have added another twenty-one
labels the app renders and this contract cannot see. Those come back `bucket: new`
with no matching entry — indistinguishable from a screen the target really lacks,
which is the one confusion this file exists to remove.

A dropdown row is an activity by any reasonable reading: same label, same screen,
resolved through the same `activityHref`. Its `module` is the toolbar BUTTON's label
(`Inventory`, `Beacon Admin`, `Find Patients`), which is the menu path a reader needs
to find the row again.

The alternative was attaching each menu into a ☰ module's activity list so the
existing walker caught it. Rejected: it changes what the ☰ fly-out *renders* in order
to fix what the exporter *reads*, and in `rl_epic` only `Rx Admin` has the evidence to
claim it is a module's own activity list.

Corollary, same change: `disabled` no longer cascades from a menu ROW to its submenu
rows — a parent and its children are separate claims about separate screens, and
`rl_epic`'s `Therapy Plan Tools ▸` is a parent nobody opened whose two children were
both filmed. A `disabled` MODULE still cascades to everything under it.

Requirements:

1. **Cross-check, don't just concatenate.** If `ACTIVITY_OVERRIDES` names a route
   with no corresponding `page.tsx`, that is a broken link in `rl_epic` and the
   exporter must fail loudly rather than emit `status: built` for a 404.
2. **Fold aliases, don't duplicate.** `menuConfig.ts` already routes several
   labels to one destination — `Bed Planning` and `Bed Events Summary` both land
   on `/grand-central/bed-board`. These become `aliases` on a single entry.
3. **Handle the deliberate label collision.** `Status Board` exists under both
   Radiology and Grand Central and is routed explicitly in `menuConfig.ts`
   precisely because of the clash. `nav.ts` documents keeping only Radiology's
   entry to avoid a duplicate object key. The exporter must emit both as
   distinct entries disambiguated by `module` — collapsing them loses a real
   screen.
4. **Emit deterministically.** Sorted by label, stable formatting. The file gets
   committed and diffed; churn makes it useless for spotting real changes.
5. **Record the commit** in `generated_from`, so a stale inventory is detectable.
6. **Be runnable as a single command** from the project root, with no arguments.
   Reframe executes it before every run (see below).

---

## Freshness is enforced, not assumed

The workflow is: process video *N* → **build those screens** → process video
*N+1*. So the inventory is out of date the moment you finish building, and a
stale one would report screens as `new` that were completed last week.

Reframe treats the inventory as **derived state, refreshed per run**
([DEC-018](DECISIONS.md#dec-018--the-inventory-is-regenerated-per-run-and-staleness-is-a-hard-error)):

1. `inventory.json` is gitignored — it is a build artifact, not data.
2. The project profile names `project_root` and `inventory_cmd`. Reframe runs
   that command before stage 07 unless `--no-refresh` is passed.
3. `generated_from.commit` is compared against the project's current `HEAD`.
   **A mismatch aborts the run** with the refresh command in the error — it is
   never a warning, because a warning about a stale classification is
   indistinguishable from a correct classification once it is in a Markdown file.
4. The inventory's commit is recorded in the manifest, so any catalogue can be
   traced to the exact state of the app it was classified against.

How the project itself gets refreshed — `git pull`, or a fresh clone before each
video — is outside Reframe's concern. It only requires that the inventory match
`HEAD`.

---

## How Reframe matches

Stage 07 resolves each identified screen name against the inventory in three
passes, recording which one succeeded in `classification.match_kind`:

1. **`exact`** — case-insensitive exact match on `label` or any `alias`.
2. **`alias`** — match through the per-video `classify.aliases` map in config.
   This is the tuning surface: when a validation round reveals that the model
   consistently reads a screen as "Bed Ctrl", the fix is one line of YAML, not a
   code change.
3. **`fuzzy`** — normalised edit distance above `classify.fuzzy_threshold`
   (default 0.82). The score is always recorded.

**A fuzzy match below threshold does not silently become `new`.** It produces
`bucket: new` *with* a `possible_match` field naming the closest candidate and
its score. Claiming a screen is unbuilt when it is merely misspelled is exactly
the kind of confident-but-wrong output this tool is designed to avoid.

### The `partial` bucket

`partial` cannot be determined from the inventory alone — it requires comparing
what the video shows against what the component contains. In v1 it is assigned
when the name matches a `built` entry **but** the model reports tabs, columns or
dialogs that the reviewer confirms are absent.

That confirmation is a human step in v1. Automating it would mean parsing the
target project's components, which reintroduces exactly the coupling
[DEC-001](DECISIONS.md#dec-001--standalone-repo-not-part-of-rl_epic) removed.
A future version could accept an optional `component_summary` field in the
inventory — the exporter is better placed to produce that than Reframe is.

---

## Adopting this in another project

Write an exporter that emits the schema above. That is the entire integration.

The minimum useful inventory is a list of `{label, status}` — `route`, `module`
and `component_paths` improve the output but nothing breaks without them. A
project with no concept of "deliberately unbuilt" simply never emits
`status: disabled`.

---

## Superseded status names

`lookup_scoped` was called `patient_scoped` until a pharmacy module arrived whose
activities are reached by choosing a formulary, a medication or a workstation —
no patient involved. The mechanism was always "pick a record first"; only the
name assumed which kind of record.

**Exporters emitting `patient_scoped` keep working.** It is accepted on input and
normalised to `lookup_scoped`; nothing needs changing in a consuming project
before it is convenient to. Unknown values are still rejected, so this cannot
turn a typo into a valid status.
