# Build brief 03 — Hospital/Clinic Admin

**Branch:** `pharmacy-admin` — same branch as briefs 01 and 02.
**Verification:** the operator replays the source recording against the built
page. Trust the images over this text — briefs 01 and 02 each had corrections
the build session found at magnification, and it was right every time.

## Evidence

```
~/build-evidence/03-hospital-clinic-admin/
  sidebar-top.jpg                      the nav tree, unscrolled, 2.6x
  sidebar-scrolled.jpg                 the same tree scrolled to the bottom, 2.6x
  header-and-footer.jpg                page header + Jump-to-item, 1.5x
  footer-bar.jpg                       the action bar, 2x
  section-general.jpg                  (02:09)
  section-compounding-repackaging.jpg  (02:41)
  section-lot-exp.jpg                  (03:10)
  section-med-validation-system.jpg    (03:33)
  section-verification.jpg             (03:37)
  section-inventory.jpg                (03:40)
  section-shipment-steps.jpg           (04:10)
  section-related-information.jpg      (04:43) — was mis-named, see below
```

---

## What this is

The first activity reached through the record picker (brief 02), and the first
page whose **sidebar drives the content**. One record — `CC CLINIC [10502]` —
with 26 sections of settings hung off a nav tree.

It is the longest single stretch in the recording: **2.5 minutes, 20 frames**,
the operator walking down the tree section by section.

Reached as: hub → `Rx Admin ▸ Hospital/Clinic Admin` → picker → this page.

---

## Page structure

Four regions below the shell chrome.

### 1. Activity tab strip

`← →` back/forward arrows, then a tab reading `Hospital/Clinic Admin`. On the
right of the same row, `?` help and `✕` close.

Note the workspace tab above it still reads `Pharmacy Admin ✕` — that is the
workspace; this is an activity inside it.

### 2. Page header

- Heading: `Hospital/Clinic: CC CLINIC [10502]` — the activity, then the record
- Right: an input placeholdered `Jump to an item (Alt+F9)`, a `🔍 Search`
  button, and a `⋯` overflow

### 3. Sidebar — a scrolling tree

Not a flat list. Three nodes expand, and **`Shipment Steps` is a child of
`Home Infusion`, not a top-level section** — it reads as top-level in a scrolled
frame, which is how it was first mis-catalogued.

```
General
Intelligent Package Selection
⌄ Charging
     One-Step/Zero-Dollar
     Billing Overrides
Waste
ADT Reporting
Dispensing Information
Hazardous Material Handling
⌄ Dispense Prep
     Gravimetrics
Dispense Check
Compounding and Repackaging
Shared Prep Settings
Workflow Configuration
Beyond-Use Dates
Lot/Exp
Calcium Phosphate Solubility
Medication Validation System
Verification
Inventory
⌄ Home Infusion
     Billing
     Dispensing
     Shipment Steps
Related Information
```

20 top-level nodes, 6 children, **26 in total**. All three groups are shown expanded
in every frame; a collapsed state was never observed.

Selected item: full-width pale highlight plus a solid accent bar on the left
edge. The tree scrolls independently of the content panel.

### 4. Footer action bar

Spans the full width, pinned below both sidebar and content.

- Left: `Open Another Hospital/Clinic`, then `⏮ Restore` (greyed in every frame)
- Right: `↑ Previous F7`, `↓ Next F8`, `✔ Accept`

The bar **does not span the full width** — it starts at the content panel's left
edge, and the sidebar runs full height beside it.

`Previous`/`Next` step the tree, and this is evidenced rather than assumed:
measured against the always-enabled `Open Another` label, on the first node
`Previous` reads 0.56 contrast against `Next`'s 0.92; on the last node it
inverts; in the middle both are enabled.

---

## Content panel — one pattern, repeated

Every observed section is built from the same parts. Learn these once.

**Fieldset** — a legend in bold, followed by a horizontal rule running to the
right edge of the panel. A section may hold several, e.g. Verification has
`Verification Queue Settings` and `Batch Verification Settings`.

**Label + field + magnifier** — a left-aligned label, a text input, and a
magnifier glyph inside the input's right edge. This is the common row.

**Field + Open button** — some rows add a `🔗 Open` or `🔗 Open Record` button to
the right of the input. `Open Record` appears right-aligned on its own line
beneath a group and is greyed when nothing is selected.

**Numbered multi-value control** — a narrow box containing a row number (`1`)
joined to a wide input with a magnifier. Used where a setting takes a list.

**Checkbox** — a square box and a label. A checked one renders as a **filled
accent block with a white tick and light text**, not a tick in an empty box
(see `section-verification.jpg`, `Block HOV/outpatient visit orders from verify
queue`).

**Inline warning** — a yellow banner to the right of a disabled field, e.g.
`ADS console management not enabled` on General. It sits outside the field, in
the panel's right margin.

**Sub-heading + table** — a plain bold heading above a column-headed table with
an empty lookup row (see `Shipment Steps`).

**Horizontal scrollbar** — the content panel scrolls horizontally as well as
vertically; General shows one at the bottom.

---

## Observed section contents

**Eight** of 26 sections were opened, not ten.

Two frames I listed have no image shipped (`Dispense Prep`, `Home Infusion`), and
one is mislabelled: the file named for `Calcium Phosphate Solubility` is actually
**`Related Information`** — its sidebar accent bar is on the last row, and the
panel holds cards, one of which is *titled* "Calcium Phosphate Solubility". That
is where the wrong name came from. `Calcium Phosphate Solubility` itself was
never opened.

Treat every `section` label in this brief as a claim to check against the
sidebar's highlighted row, not against anything in the panel. Transcribe from the images — the fields below
are what is legible, not necessarily all of them.

**General** — `Hospital/Clinic formulary:` (= `EPIC HOSPITAL FORMULARY`, + Open) ·
`Main pharmacy:` (= `EHS CLINIC MEDICATION ROOM`, + Open) ·
`ADS console management formulary:` (empty, disabled, + Open, yellow warning
`ADS console management not enabled`) · `High-risk medication ADS override pull
grouper:` · `High-risk medication ADS override pull alert extensions:`
(numbered) · `Track ADS inventory:` · ☐ `Disable formulary checks` ·
`Default preference list for mixture section types:` ·
`Default outpatient preference list:` ·
☐ `Allow documenting PTA meds as patient supplied` · *(continues below fold)*

**Verification** — fieldset `Verification Queue Settings`:
☑ `Block HOV/outpatient visit orders from verify queue` ·
`Orders needing review on Ord Rec transfer:` ·
`Send on-the-fly orders for pharmacy review:` ·
`Autoverified orders to send for pharmacy review:` (numbered) · `Open Record`
(greyed). Fieldset `Batch Verification Settings`: ☐ `Enable batch verification` ·
`Orders to exclude from batch verification:` (numbered) · `Open Record` (greyed).

**Shipment Steps** — fieldset `Shipment Steps`. Sub-heading
`Scanning Requirements` above a table with columns `Shipment Step` ·
`Scanning Requirements` · `Allow Save and Resume?` and one empty lookup row.
Then `Disable scanning requirement for these medications:` (+ Open) ·
`Disable scanning requirement for these supplies:` (+ Open) · sub-heading
`Allowed Reasons to Override Scanning Requirements` with a field · sub-heading
`Workflow Toggles` with a field · sub-heading `Combined Workflows` with a field.

The remaining seven — Compounding and Repackaging, Lot/Exp, Medication
Validation System, Inventory, Home Infusion, Dispense Prep, Calcium Phosphate
Solubility — each have one frame. Read the fields off the images rather than
from a summary here; that is the point of shipping them.

---

## Rules carried forward

**Do not manufacture content to fill a section.** Eighteen sections were never
opened. Render them as empty with an explicit note, not with plausible settings.
The same rule the session applied to the picker's row counts applies here, and
it matters more: an invented pharmacy setting reads as configuration someone
might act on.

**Do not complete clipped text.** Where a label runs past the frame edge, seed
the legible prefix.

**Use the `disabled` + `title="… — not demonstrated"` idiom** established in
brief 01 for anything never exercised.

---

## Known unknowns

| Unknown | Why |
| --- | --- |
| 18 of 26 sections' contents | never opened in the recording |
| Whether tree groups collapse | all three shown expanded in every frame |
| What `Previous F7` / `Next F8` step through | never pressed |
| What `Accept` commits, and whether it closes | never pressed |
| What `Restore` does | greyed in every frame |
| What `Open` / `Open Record` navigate to | never clicked |
| Whether `Jump to an item` filters the tree or the panel | never used |
| What the `⋯` overflow holds | never clicked |
| Whether the record can be changed in-place | `Open Another Hospital/Clinic` never clicked |
| Field values for every setting left blank | genuinely blank in the reference, not unread |

That last row matters: most fields on this page are **empty in the reference**.
Blank is the observed state, not missing information — do not seed values into
them.

---

## Definition of done

- Route under the activity, reached from the picker with a record id
- Header shows `Hospital/Clinic: <record name> [<id>]` from the record, not a literal
- Full 26-node tree with the three groups nested correctly, `Shipment Steps`
  under `Home Infusion`
- Tree scrolls independently; selection shows highlight + left accent bar
- The ten observed sections render their observed controls
- The eighteen unobserved sections render an explicit "not captured" state
- Footer bar with all five controls, `Restore` greyed
- Checkbox checked-state matches the reference (filled block, white tick)
- Yellow inline warning on General's disabled field
- Every unknown above left visibly incomplete, and listed when you report back
