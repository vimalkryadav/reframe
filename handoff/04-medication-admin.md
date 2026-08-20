# Build brief 04 — Medication Admin

**Branch:** `pharmacy-admin` — same branch as 01–03.
**Read brief 03 first.** This is the same page shape: activity tab, record
heading, `Jump to an item`, a sidebar tree driving a content panel, and a footer
action bar. That brief documents the shared control vocabulary — fieldsets,
label+field+magnifier rows, numbered multi-value controls, checkbox styling,
`Open Record` buttons. None of it is repeated here. **This brief covers only
what differs.**

**Verification:** the operator replays the source recording against the built
page. Trust the images over this text.

## Evidence

```
~/build-evidence/04-medication-admin/
  sidebar-tree.jpg          the whole tree, 3.4x — it fits without scrolling
  f_000391-t06m31s.jpg      Packaging
  f_000409-t06m49s.jpg      Packaging again — a lookup open, a second table row
  f_000427-t07m07s.jpg      Overrides
  f_000440-t07m20s.jpg      Prescription
  f_000470-t07m50s.jpg      Equivalency
  f_000499-t08m19s.jpg      Dispense Prep/CNR
  f_000509-t08m29s.jpg      Related Information
  detail-info-callout.jpg   the ⓘ callout, 1.9x
  detail-editable-table.jpg the row-action table, 1.9x
  detail-related-cards.jpg  the card stack, 1.7x
```

**Files are named by frame id, and the section beside each is a claim to check,
not a label to trust.** Two frames in earlier briefs were filed under the wrong
section because the filename came from a model reading nobody re-verified. The
section is whichever sidebar row carries the accent bar — measure it.

---

## What this is

Reached as: hub → `Rx Admin ▸ Medication Admin` → picker → this page.

One record, `2-DEOXY-D-GLUCOSE POWD [25782]`, across **2.3 minutes and 30
frames**. Six of nine sections were opened — still the best-covered activity in the
recording.

---

## The tree — 9 nodes, no scrolling

```
Packaging
⌄ Billing
     Overrides
     Prescription
Equivalency
Identity/ADS
Inventory
Dispense Prep/CNR
Related Information
```

7 top-level, 2 children, 9 total. It fits the panel without scrolling, unlike
brief 03's 26.

`Overrides` and `Prescription` are **children of `Billing`**. Only `Billing`
expands; the other six top-level nodes are leaves.

**Observed — six:** Packaging · Overrides · Prescription · Equivalency ·
Dispense Prep/CNR · Related Information.
**Not opened — three:** `Billing` · `Identity/ADS` · `Inventory`.

`Billing` was never opened. Two frames show `Packaging` selected; the second
(`f_000409`) has a lookup open over it and a second table row inserted, which is
what makes it look like a different section at a glance.

*(`Identity/ADS` does appear later in the recording, but on a different
activity — a `Package` record at 09:37, not this one. Do not borrow it.)*

---

## Footer differs by one label

`Open Another **Medication**`, not `Open Another Hospital/Clinic`. The label
names the activity's record type. Everything else — `Restore` greyed,
`Previous F7`, `Next F8`, `Accept` — matches brief 03.

The positional Previous/Next behaviour is corroborated here: on
`Related Information`, the last node, **`Next F8` is greyed** while `Previous`
is enabled.

---

## Three controls brief 03 does not cover

### 1. Info callout — two of them, plus a third variant

Distinct from brief 03's yellow inline warning. Full panel width, a ⓘ glyph, a
**bold title line**, then a body paragraph. Neutral background, not yellow.

Observed twice: on Packaging (below) and on Prescription as
`Adjudication Timing`. A third case on **Overrides** is yellow like brief 03's
but **full-width at the top of the panel**, not in the right margin —
`Billing Overrides only apply to medical billing.` Treat that as a placement
variant of one component, not a second component.

The Packaging one, verbatim:

> ⓘ **No setting found at ERX.**
> This setting can be overridden at the NDC and NDG level. If the implied unit
> is not set at the ERX/NDC/NDG levels, then the system looks at the package
> unit for the NDC and if it is each, tablet, capsule, suppository, or patch,
> the system uses the package unit as the implied unit, otherwise the system
> uses the entire package.

### 2. Editable table with row actions

Brief 03's tables are read-only with an empty lookup row. This one is editable.

Fieldset `Linked Procedure Override`, columns
`From` · `To` · `Location` · `Department` · `Procedure`. Row 1 is numbered, with
**date inputs carrying calendar glyphs** for From/To and lookup fields for the
other three.

Beneath the table, four buttons: `➕ Insert (F4)` · `➖ Delete (Shift+F4)` ·
`↑ Move Up` · `↓ Move Down`.

**The enable rule is observed, not assumed.** With no row selected all four are
greyed. `f_000409` has a row selected: sampling label ink at p3 across the two
frames gives Insert 104→71 and Delete 102→74 (enabling), while Move Up 104→110
and Move Down 109→114 stay put. So **Insert and Delete enable on selection;
Move Up/Down do not.** Insert's effect is observed too — one table row becomes
two between the frames.

### 2b. Lookups opened over the panel

Three magnifiers were actually opened in this recording, so their contents are
known rather than inferred: a **Department** lookup (6 columns, 13 rows) over
Packaging, and a **SmartText** lookup (2 columns, 11 rows) over
Dispense Prep/CNR. Brief 03 has a third, the Lot/Exp grouper list. Wire each to
the cell whose magnifier opened it; every other magnifier stays inert.

### 3. Card stack — `Related Information`

Not a settings section at all. A stack of cards, each with its title in a
**coloured pill carrying a ⚠ triangle**, then a plain body.

Observed:

| Card title | Body |
| --- | --- |
| ⚠ Duplicate Therapy Class Rules | `No rule found.` |
| ⚠ Active Interval | `For drug-drug interaction checking: 0 hours (from System Definitions)` and `For duplicate therapy checking: 0 hours (from System Definitions)` |
| ⚠ Grouper Records (VCG) | a link: `🔗 ERX PM IP FALLS CHEMICALS [125710]` |

Below the cards, a large heading `Build Inspector Results for Medication Admin`
and a row of three link-styled actions:
`Run Build Inspector` · `Hide OK results` · `Show acknowledged results`.

The panel is scrolled — a partial card sits above `Duplicate Therapy Class
Rules`, cut off by the top edge. **Do not invent it.**

This card shape is what made a brief 03 frame get mis-attributed: card titles
read like section names. Worth building so the resemblance is visible.

---

## Rules carried forward from 01–03

- **Do not manufacture content** to fill the two unopened sections, or to
  complete the partial card. Render them explicitly not captured.
- **Do not complete clipped text.** Seed the legible prefix.
- **Blank is the observed state** for most fields — do not seed values.
- **Render the observed enabled/disabled state.** If a control is enabled in the
  reference, build it enabled and put the undemonstrated behaviour in the
  tooltip. (Correcting brief 03's instruction, which over-disabled.)
- Use the `disabled` + `title="… — not demonstrated"` idiom for behaviour.

---

## Known unknowns

| Unknown | Why |
| --- | --- |
| `Billing`, `Identity/ADS`, `Inventory` contents | never opened on this activity |
| The card above `Duplicate Therapy Class Rules` | scrolled off the top edge |
| What `Run Build Inspector` does | never clicked |
| What `Hide OK results` / `Show acknowledged results` toggle | never clicked |
| What the `Grouper Records` link opens | never clicked |
| Whether `Billing` collapses | shown expanded in every frame |
| What the ⚠ on each card signifies | no card ever showed a non-warning state |

On that last one: the pill, title, triangle and left accent bar all sample
**violet** (accent bar 111,98,149) against a neutral card body of (187,189,192).
So it is card styling rather than a warning colour — which sharpens the unknown
rather than resolving it. Do not render it as a warning.

---

## Definition of done

- Route under the activity, reached from the picker with a record id
- Heading renders `Medication: <record name> [<id>]` from the record
- 9-node tree with `Overrides` and `Prescription` under `Billing`; no scrolling
- The six observed sections render their observed controls
- `Billing`, `Identity/ADS` and `Inventory` render an explicit "not captured" state
- Info callout, editable table with its four row actions, and the card stack
- Footer reads `Open Another Medication`; `Next F8` greyed on the last node
- Every unknown left visibly incomplete and listed when you report back
