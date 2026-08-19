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
  sidebar-tree.jpg                 the whole tree, 3.4x — it fits without scrolling
  section-packaging.jpg            (06:31)
  section-billing.jpg              (06:49)
  section-overrides.jpg            (07:07)
  section-prescription.jpg         (07:20)
  section-equivalency.jpg          (07:50)
  section-dispense-prep-cnr.jpg    (08:19)
  section-related-information.jpg  (08:29)
  detail-info-callout.jpg          the ⓘ callout, 1.9x
  detail-editable-table.jpg        the row-action table, 1.9x
  detail-related-cards.jpg         the card stack, 1.7x
```

**Check each section against the sidebar's accent bar, not against anything in
the panel.** A frame in brief 03 was mis-attributed exactly that way — a card
titled like a section was read as the selection.

---

## What this is

Reached as: hub → `Rx Admin ▸ Medication Admin` → picker → this page.

One record, `2-DEOXY-D-GLUCOSE POWD [25782]`, across **2.3 minutes and 30
frames**. Seven of nine sections were opened — the best-covered activity in the
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

**Observed:** Packaging · Billing · Overrides · Prescription · Equivalency ·
Dispense Prep/CNR · Related Information.
**Not opened:** `Identity/ADS` · `Inventory`.

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

### 1. Info callout

Distinct from brief 03's yellow inline warning. Full panel width, a ⓘ glyph, a
**bold title line**, then a body paragraph. Neutral background, not yellow.

Observed on Packaging, verbatim:

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

Beneath the table, four buttons: `➕ Insert (F4)` · `➖ Remove (Shift+F4)` ·
`↑ Move Up` · `↓ Move Down`. All four appear greyed with no row selected.

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
| `Identity/ADS` and `Inventory` contents | never opened on this activity |
| The card above `Duplicate Therapy Class Rules` | scrolled off the top edge |
| What `Run Build Inspector` does | never clicked |
| What `Hide OK results` / `Show acknowledged results` toggle | never clicked |
| Whether the row-action buttons enable with a selection | no row ever selected |
| What the `Grouper Records` link opens | never clicked |
| Whether `Billing` collapses | shown expanded in every frame |
| What the ⚠ on each card signifies | no card ever showed a non-warning state |

That last one is worth stating plainly: every card carries the same triangle, so
whether it means "attention needed" or is simply the card style is not
determinable from this recording.

---

## Definition of done

- Route under the activity, reached from the picker with a record id
- Heading renders `Medication: <record name> [<id>]` from the record
- 9-node tree with `Overrides` and `Prescription` under `Billing`; no scrolling
- The seven observed sections render their observed controls
- `Identity/ADS` and `Inventory` render an explicit "not captured" state
- Info callout, editable table with its four row actions, and the card stack
- Footer reads `Open Another Medication`; `Next F8` greyed on the last node
- Every unknown left visibly incomplete and listed when you report back
