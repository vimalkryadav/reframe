# Task brief — inventory export for Reframe

**For:** a Claude session working in `rl_epic`
**From:** Reframe (`~/Epic/reframe`), which needs this to classify screens
**Branch:** work on `reframe-inventory-export`. Do not commit to `main`.

---

## Why this exists

Reframe processes handheld video of the reference application and produces a
catalogue of screens plus a build queue. To say *"you have already built this
one"* it needs to know what `rl_epic` contains.

**Reframe is forbidden from knowing anything about this project.** Its CI fails
if the string `epic`, `hyperspace`, `willow` or similar appears anywhere in its
`src/`, `configs/` or `tests/`. So the coupling is inverted: `rl_epic` describes
itself in a generic format, and Reframe matches names against that list without
ever knowing what application produced it.

That description is the deliverable. One script, one JSON file.

Full schema and rationale: `~/Epic/reframe/CONTRACT.md`.

---

## What to build

`scripts/export-inventory.mjs` — reads this repo's own navigation config and
writes `inventory.json` at the repo root.

```bash
node scripts/export-inventory.mjs            # -> ./inventory.json
node scripts/export-inventory.mjs --out /tmp/inv.json
```

### Output shape

```jsonc
{
  "schema_version": 1,
  "project": "rl_epic",
  "generated_from": {
    "commit": "9a0a4ad9",                    // short HEAD, or null if unavailable
    "sources": ["frontend/lib/nav.ts", "..."]
  },
  "entries": [
    {
      "label": "Bed Board",                  // REQUIRED, unique across all entries
      "aliases": ["Bed Planning"],           // defaults to []
      "route": "/grand-central/bed-board",   // null when there is no page
      "module": "Grand Central",             // the menu module it sits under
      "status": "built",                     // REQUIRED, see below
      "source": "ACTIVITY_OVERRIDES",        // provenance, for debugging a bad match
      "component_paths": []                  // optional, lets a reviewer jump to code
    }
  ]
}
```

### Where the data lives

| Source | What it gives |
| --- | --- |
| `frontend/components/shell/menuConfig.ts` → `MODULE_ITEMS` | every activity, its module, `disabled`, `aliases`, sometimes an explicit `route`. Nests: `groups[].items[].children[]` |
| `frontend/lib/nav.ts` → `ACTIVITY_OVERRIDES` | label → route, for activities with a real page |
| `frontend/components/shell/modalActivities.ts` → `MODAL_ACTIVITIES` | activities that open a lookup modal instead of navigating |

### The four statuses

These are the reason the contract is worth designing rather than dumping a list
of routes. Each carries different information for the build queue.

| Status | Means | Rule |
| --- | --- | --- |
| `disabled` | known and deliberately unbuilt | `disabled: true` on the menu item, or inherited from its parent. **Takes precedence over everything else.** Emit `route: null` |
| `patient_scoped` | a screen exists, but needs a patient chosen first | the label is a key in `MODAL_ACTIVITIES` |
| `built` | resolves to a live route | the menu item has an explicit `route`, or the label is in `ACTIVITY_OVERRIDES` |
| `stub` | in the menu, falls through to the `/activity/<slug>` placeholder | everything else |

`disabled` beating `stub` matters: *deliberately unbuilt* and *never heard of*
are different facts, and a build queue that conflates them wastes someone's day.

### Rules that are easy to get wrong

**An explicit `route` on a menu item beats the `ACTIVITY_OVERRIDES` lookup.** It
is the more specific statement, and it is how one label reaches a module-scoped
page.

**Duplicate labels are a hard error downstream.** One activity reachable from two
menu paths is one screen — keep the first occurrence, skip the rest. Reframe
matching one screen name to two entries has no right answer.

**An alias must never collide with a label, or with another entry's alias.** The
menu's `aliases` exist to widen in-app search, which is a different job, so
collisions are real. When one occurs the **label wins** and the alias is dropped
— but *print a warning*. Quietly narrowing the alias table is how a screen stops
matching and nobody finds out why. There is at least one real case:
`"Patient Flight Tracking"` is both an alias of `"Flight Tracker"` and an
activity in its own right.

**Include activities that have a page but are absent from the menu.** Reframe
will see them in a video regardless, and reporting a built screen as `new` puts
finished work back in the queue. Walk `ACTIVITY_OVERRIDES` for labels the menu
never produced and add them with `module: null`.

**Emit `commit: null` rather than a placeholder if `git rev-parse` fails.**
Reframe compares it against HEAD and aborts on a mismatch; a made-up value
defeats that check.

---

## Hard constraint: it must run with `node_modules` absent

Reframe regenerates the inventory **before every classification run** and aborts
if it does not match HEAD. An exporter that needs `pnpm install` first makes
every run fragile.

That is not trivial, because the config files are TypeScript that uses the `@/`
path alias and imports icon components. Node resolves neither. What works:

- **`module.registerHooks({ resolve })`** (synchronous, in-thread — not the
  deprecated `module.register()`) to rewrite `@/x` to `frontend/x`, trying
  `.ts`, `.mjs`, `.js`, `/index.ts` in turn.
- **Stub everything that is not inventory data** — bare package specifiers, and
  anything resolving to `.tsx`. Node strips types from `.ts` but does not parse
  JSX, so a `.tsx` import fails outright; no loss, since a React component is
  never inventory.
- **A stub must declare the exact named exports its importer asks for.** ESM
  validates named exports at link time, so a `Proxy` is not enough — read the
  importing file and generate `export const <name> = stub;` for each. Return it
  as a `data:text/javascript,` URL.

Node 26 strips TypeScript types natively, so `.ts` files import directly once
resolution is handled.

---

## Definition of done

```bash
rm -f node_modules -r 2>/dev/null   # must still work
node scripts/export-inventory.mjs
```

- Exits 0 and writes `inventory.json`
- Every entry has a unique `label` and a valid `status`
- No alias equals any label; collisions are reported on stderr
- `generated_from.commit` matches `git rev-parse --short HEAD`
- Prints a per-status count summary to stderr
- Add `inventory.json` to `.gitignore` — it is regenerated every run and must
  match HEAD, so a committed copy is only ever a stale one that looks
  authoritative

Expected magnitude at `9a0a4ad9`: **~244 activities** — roughly 85 built,
33 patient-scoped, 99 stub, 27 disabled. Numbers far from these mean the menu
walk is missing a nesting level.

---

## A reference implementation exists

Branch `reframe-inventory-export` in this repo has a working version, written
against the contract above and producing exactly those counts. **It has not been
reviewed by anyone who knows this codebase.**

Treat it as a starting point, not an answer. Reasonable outcomes: adopt it after
review, rewrite it in this repo's idiom, or take only the loader hooks — those
are the fiddly part.

---

## Not yet: building the screens themselves

The obvious next question is *"which pharmacy screens should we build?"* — and
that is **not ready to assign.**

Reframe has catalogued 133 screens from one 10-minute video. Of those, a human
has verified **five**. Two minutes of the footage produced no screens at all and
nobody has watched those spans yet. Building from that would produce a
confident-looking module with holes nobody can see, which is the exact failure
this whole pipeline exists to prevent.

A separate brief will follow once the catalogue has been through a review pass.
