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
    modalActivities.ts, app/ routes)       label, route,        about Epic)
                                           status, aliases)
```

---

## Schema

```jsonc
{
  "schema_version": 1,
  "project": "rl_epic",
  "generated_from": {
    "commit": "9a0a4ad9",
    "sources": ["lib/nav.ts", "shell/modalActivities.ts", "shell/menuConfig.ts", "app/**/page.tsx"]
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
| `patient_scoped` | Reached via a patient-lookup modal, then a patient-scoped route. Built, but not directly addressable. | `built` |
| `disabled` | The activity is **known and deliberately unbuilt** — in `rl_epic` this is a `disabled: true` marker in `menuConfig.ts`. | `new` |
| `stub` | Falls through to a generic `/activity/<slug>` placeholder page. Reachable, but not implemented. | `new` |

`disabled` versus never-mentioned is the distinction most worth preserving. A
`disabled` entry means someone already looked at the reference, recognised the
activity, and chose not to build it — that is different information from a screen
nobody has ever catalogued, and it belongs in the build queue with that context
attached.

---

## What the `rl_epic` exporter must do

Lives at `rl_epic/scripts/export-inventory.mjs`. Reads four sources, all of
which are already maintained as part of normal development:

| Source | Entries (at commit `9a0a4ad9`) | Contributes |
| --- | --- | --- |
| `frontend/lib/nav.ts` → `ACTIVITY_OVERRIDES` | 85 | Activity label → real route. Status `built`. |
| `frontend/components/shell/modalActivities.ts` | 34 | Patient-scoped activities. Status `patient_scoped`. |
| `frontend/components/shell/menuConfig.ts` → `disabled: true` | 27 | Known but unbuilt. Status `disabled`. |
| `frontend/app/**/page.tsx` | 150 | Ground truth on which routes actually exist. |

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
