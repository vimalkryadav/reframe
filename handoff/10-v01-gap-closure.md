# Build brief 10 — closing the gaps a second pass over v01 found

**Branch:** `pharmacy-admin` — same branch as 01–09. Same recording, second pass.

**This brief is mostly corrections to screens you have already built, not new
pages.** Five of its seven items change a label, a capture state or a content
list. One is a genuinely new modal. One is three first-run dialogs.

Read [Part C](#part-c--do-not-change-these) before you touch anything. It lists
four places where this pass disagreed with your code and **your code is right** —
the seeds' own notes had already diagnosed two of them. Do not "fix" those.

---

## Where this evidence came from, and what it can and cannot support

The v01 recording was processed twice by `reframe` (the catalogue tool), once at
1 fps and once at 2 fps, all stages, on 2026-08-21. Both runs replayed entirely
from the model cache, so both reproduce earlier runs exactly. Frames here are
*rectified* — the tool detects the monitor in the handheld shot and warps it to a
1600×1000 canonical image.

**Authoritative for:** labels and their exact wording, row and tab order,
nesting, control types, enabled/disabled/selected state, presence and absence,
and which rows a menu panel contains.

**NOT authoritative for geometry.** This is the important one. The source is a
phone pointed at a monitor; rectification removes most perspective but not lens
distortion or the residual homography error, and `reframe`'s DEC-010 forbids the
tool emitting measurements from this corpus for exactly that reason.

That collides with RL_EPIC steps 5 and 6 ("measure, don't eyeball", "≤2px DOM
diff"). **Do not scan these frames for px positions.** Where an item needs
spacing, take it from the equivalent primitive already in this repo
(Reference-This-Repo-First) and say in the comment that geometry is inherited
rather than measured. Wording, order and states come from the frames; numbers do
not.

Frame ids are **not** the same as briefs 01–09's ids. Those came from a 5 fps
extraction; these come from 1 fps and 2 fps passes, so `f_000354` means different
moments in each. Every file below is prefixed with its rate for that reason.

---

## Evidence

```
~/build-evidence/10-v01-gap-closure/
  # A1 — the Rx Admin menu, whole, three independent sightings
  2fps-f_000706-t05m53s--rx-admin-menu-full.jpg
  2fps-f_001029-t08m34s--rx-admin-menu-full.jpg
  1fps-f_000354-t05m54s--rx-admin-menu-full.jpg
  detail-home-infusion-row.jpg          3.2x, both 2 fps frames stacked

  # A2 — Hospital/Clinic Admin ▸ Home Infusion, open
  2fps-f_000455-t03m47s--hc-home-infusion.jpg
  2fps-f_000458-t03m49s--hc-home-infusion.jpg

  # A3 — Related Information at two scroll positions
  2fps-f_000563-t04m41s--hc-related-info-scrolled-up.jpg
  2fps-f_000566-t04m43s--hc-related-info-scrolled-down.jpg

  # A4 — the Find Patients menu, open
  2fps-f_000210-t01m45s--find-patients-menu.jpg
  1fps-f_000105-t01m45s--find-patients-menu.jpg

  # A5 — the Select an Order modal, and what opened it
  1fps-f_000093-t01m33s--select-an-order.jpg
  1fps-f_000096-t01m36s--select-an-order.jpg
  detail-order-hx-hover.jpg             2.6x, 01:31 / 01:32 / 01:33

  # B — the three first-run dialogs
  2fps-f_000096-t00m48s--welcome-to-hyperdrive-qa.jpg
  2fps-f_000105-t00m52s--reminder-added.jpg
  2fps-f_000117-t00m58s--graphs-now-scale.jpg

  # C — frames that prove existing code is correct. Do not change that code.
  1fps-f_000108-t01m48s--report-settings-criteria.jpg
  1fps-f_000115-t01m55s--report-settings-general.jpg
  2fps-f_000673-t05m36s--med-list-four-tabs.jpg
  detail-med-list-tab-row.jpg
  1fps-f_000409-t06m49s--medication-packaging-not-billing.jpg
```

Every filename's trailing label is a claim. Check it against the frame — read the
selected row from its accent bar, not from my label.

---

# PART A — corrections and one new modal

## A1. The Rx Admin menu's 23rd row is `Home Infusion`, and there are exactly 23

**File:** `frontend/components/shell/menuConfig.ts` — `RX_ADMIN_GROUPS`, its
doc comment (~L131–160) and the last item of the last group (~L214–216).

**Now:** the row is carried as
`{ label: "(one more activity, name not legible)", Icon: FileText, disabled: true }`,
and the comment says the list is "AT LEAST 23 ENTRIES, NOT 22 … the menu panel's
own bottom edge is never visible, so there may be more than one … '22' is a
floor".

**The frames settle both open questions.**

1. The row reads **`Home Infusion`** and carries its own submenu chevron. It is
   legible in three independent frames — 1 fps `f_000354` (05:54), 2 fps
   `f_000706` (05:53), 2 fps `f_001029` (08:34) — with a house-outline glyph.
   See `detail-home-infusion-row.jpg`.
2. **The menu panel's bottom border is visible directly beneath it** in
   `f_000706` and `f_001029`, with the OS taskbar below. The panel ends there.
   23 rows, exactly; the count stops being a floor.

**Change:**

- label → `"Home Infusion"`, add `hasMore: true`, keep `disabled: true`.
- Icon → the house glyph. `Home` is exported from `@/components/icons/fluent`
  (`Home24Regular`) and is not currently imported here — add it to the import.
- Rewrite the comment: 23 exactly, row 23 named, both frames that show the panel
  border cited. Keep the existing note that what the chevron opens was never
  seen — that is still true, same state as `Rule Deferral Admin`.
- The "SIX ARE BUILT … the other sixteen, the four submenu entries and the
  unreadable row" sentence needs its arithmetic redone: there is no unreadable
  row any more, so it is seventeen disabled top-level rows plus the four submenu
  entries.

**Do not** infer anything about what `Home Infusion ▸` contains.

**Knock-on:** the inventory exporter reads `menuConfig.ts`, so this replaces the
`(one more activity, name not legible)` entry with `Home Infusion`. That is the
intended effect — the catalogue currently has a placeholder where an activity
name belongs.

---

## A2. `Hospital/Clinic Admin ▸ Home Infusion` was captured after all

**File:** `backend/scripts/seeds/willow_hc_content.py` — the `TREE` entry
`("home-infusion", "Home Infusion", None, True, "not_captured", _NOT_SHIPPED)`,
its module docstring, and `SECTIONS` (which has no `home-infusion` key).

**Now:** marked `not_captured` with `_NOT_SHIPPED` — "The brief lists a frame for
this section, but none was shipped in the evidence set, so its contents are
unknown." That was an accurate statement about the *curated evidence set*. The
recording does contain it.

**What `f_000455` (03:47) and `f_000458` (03:49) show,** with the sidebar row
accent-barred on `Home Infusion` and its children expanded:

- fieldset legend: `Home Infusion`
- field `Supply Mix Definition:` — empty, with a lookup magnifier at its right
- field `Pump Questions Not to Copy Forward:` — empty, with a lookup magnifier
- label `Therapy Type rules for supplies:` above a table
- table columns, left to right: `Grouper`, `Rule`, and a third whose header is
  clipped by the panel's right edge at `Therapy T…`
- one row, numbered `1`, empty; a magnifier in the `Grouper` cell and another in
  the third column
- row-action buttons beneath: `Insert (F4)`, `Remove (Shift+F4)`, `Move Up`,
  `Move Down` — **all four greyed.**

  > **CORRECTED after the build.** This line first claimed Insert and Remove sat
  > at full ink with Move Up / Move Down lighter. That was an eyeball, and it was
  > wrong. Measured 3rd-percentile label ink: 104.9 / 102.9 / 102.4 / 108.3 — a
  > 6-unit spread — against 74.4 for `Open Another Hospital/Clinic` and 83.5 for
  > this section's own field labels in the same frame. All four are greyed, and
  > those numbers match brief 04's measured no-selection values (104/102/104/109)
  > almost exactly, so brief 04's rule already covers this. No code changed.

- the page's own footer is unchanged from the other sections:
  `Open Another Hospital/Clinic`, `Restore`, `Previous F7`, `Next F8`, `Accept`

**Two of the three lookups are open, not none.**

> **CORRECTED after the build.** This section first said "Neither magnifier was
> opened, so what any of the three lookups contain is not captured." That came
> from reading `f_000455` only — `f_000458` was shipped and never opened, which
> is brief 03's shipped-but-unread failure with the halves swapped.
>
> `f_000458` has the **`Pump Questions Not to Copy Forward`** magnifier clicked,
> cursor still on it, its list open over the panel: columns `Grouper Name` /
> `Grouper ID`, eleven visible rows (IDs 112172, 119253, 1726113, 1726137,
> 1765827–1765833), five names cut by the column width, scroll thumb near the top
> and a down-arrow showing more below.
>
> It is a **second, distinct** grouper set, not Lot/Exp's. Lot/Exp's rows are
> `ERX …` medication groupers; these are `LQL …` question groupers with unrelated
> IDs, which is what a field about pump questions should point at. Seeded as
> `pump-question-grouper` and wired to that field.

The other two magnifiers — `Supply Mix Definition` and the two in the rules table
— stay inert: never opened, contents unknown. The third column's full name is not
known either; carry it clipped, the way `NDC_TREE` already carries
`Fill Label and Barcode Scan R`.

**Change:** flip `home-infusion` to `observed`, drop its `_NOT_SHIPPED` note, add
a `SECTIONS["home-infusion"]` entry with the above. Its three children
(`hi-billing`, `hi-dispensing`, `shipment-steps`) keep their current states —
`Shipment Steps` is already `observed`, the other two were still never opened.

**Also correct the docstring.** It currently says "So: 8 observed, 18 not
captured, out of 26 nodes" and that no frame was shipped for **Home Infusion** or
**Dispense Prep**. Home Infusion moves to observed (9 / 17); `Dispense Prep`
stays not-captured and its `_NOT_SHIPPED` note stays true — see C2.

**These frames also confirm the tree you already have.** The sidebar is fully
legible in both, and the order, the nesting of `Gravimetrics` under `Dispense
Prep`, the nesting of `Billing` / `Dispensing` / `Shipment Steps` under `Home
Infusion`, and `Related Information` as the last row all match `TREE` exactly.
The earlier note that an older catalogue got `Shipment Steps`' parent wrong is
worth keeping — this pass independently agrees with the correction.

---

## A3. Related Information has three more cards above the five you have

**File:** `backend/scripts/seeds/willow_hc_content.py` —
`SECTIONS["related-information"]`.

**Now:** five `related_card` controls, in this order — `Calcium Phosphate
Solubility` (collapsed), `Pharmacies With No Parent Hospital`, `Cart Schedule
Summary for {record}`, `Schedule by Cart`, `Build Inspector Results for
Hospital/Clinic Admin`.

**Those five are correct** and match `f_000566` (04:43) exactly, including the
collapsed chevron on the first and the `?` glyph on `Schedule by Cart`. The panel
simply scrolls, and the evidence set only ever had it at the bottom.

`f_000563` (04:41) has it scrolled **up**, showing three cards *above* `Calcium
Phosphate Solubility`:

| order | card | body |
| --- | --- | --- |
| 1 | title not visible — cut off above the viewport | one visible row reading `CC FAMILY PRACTICE`, and `No` / `Admin` column headers to the right |
| 2 | `Pharmacies` | `This hospital does not have any pharmacies.` |
| 3 | `Cart Group and Department Setup` | `This hospital's pharmacies do not run any carts.` |

So the panel holds **at least eight** cards. Add cards 2 and 3 with their body
text. For card 1, follow the pattern `LinksInfoColumn.tsx` already uses for the
Common Links entry below the fold: record it as an explicitly-unnamed card whose
title was never on screen, carrying the one row and two column headers that were.
Do not name it from the row inside it — `CC FAMILY PRACTICE` is a row, and card 2
proves a card here can be titled something else entirely.

Whether more sits above card 1 is unknown; the panel was never scrolled higher.
Say so, the way `STRIP_OVERFLOW_NOTE` does.

---

## A4. `Find Patients` can stop being an inert dropdown

**File:** `frontend/components/shell/moduleChrome.ts` — `WILLOW_TOOLBAR` (~L87),
plus a new groups constant in `menuConfig.ts` beside `RX_ADMIN_GROUPS`.

**Now:** `{ label: "Find Patients", Icon: UsersFilled, dropdown: true }` — no
`groups`, so `TopToolbar` renders the inert "menu not available" button. The
comment above `WILLOW_TOOLBAR` justifies that with "Every dropdown's CONTENTS are
out of scope for brief 01", and the `Rx Admin` line calls itself "The one
dropdown in the app whose contents a reference frame actually shows". **That is
now stale** — there are two.

**What `2fps-f_000210` (01:45) shows,** the menu open under `Find Patients ▾`,
four rows, single column, no dividers:

1. `Today's Patients`
2. `Patient Station`
3. `Status Board`
4. `ED Track Board`

The 1 fps pass caught the same moment (`1fps-f_000105`); its own catalogue then
lost it, because dedupe folded that second into the neighbouring screen and
picked the menu-shut frame as representative. Two independent sightings.

**Change:** add a `FIND_PATIENTS_GROUPS` (one group, four items) and reference it
from `WILLOW_TOOLBAR`. Update both stale comments.

**Which rows navigate.** Match what the repo already knows, don't invent:

- `Patient Station` — already in `MODAL_ACTIVITIES` (`"patient-station"`), so
  label resolution handles it.
- `Status Board` — `nav.ts` maps it to `/status-board`. Note the existing comment
  there that this label collides with the Radiology one; the Willow menu row
  should resolve the same way unless you have evidence it differs, and you do
  not.
- `ED Track Board` — `nav.ts` maps it to `/grand-central/ed-track-board`.
- `Today's Patients` — **not in `nav.ts`, not in the inventory, and its screen
  was never opened.** `disabled: true`, consistent with how the Rx Admin rows
  treat never-observed activities.

One caution: `Today's Patients` also appears as an *Available Reports* row inside
the Report Settings dialog (`f_000108`, `f_000115`). Two different things sharing
a string. Do not wire the menu row to anything on the strength of that.

---

## A5. NEW — the `Select an Order` modal, opened from `Order Hx`

Nothing in this repo matches it. This is the one item that is a build rather than
a correction.

**What `1fps-f_000093` (01:33) and `1fps-f_000096` (01:36) show**, centred over
the Willow Project Team hub, which stays fully visible behind it:

- title `Select an Order`, left-aligned, with an `×` close button at the right
- one label: `Scan barcode, enter Order ID or Rx Number`, followed by a circled
  `?` help glyph
- one single-line text input beneath it, empty, focused (the caret is in it)
- a button row, right-aligned: `✓ Accept` then `✗ Cancel`. **`Accept` is
  disabled** — its check glyph and label are pale against `Cancel`'s full ink and
  red `✗`. That is the empty-input state.
- no grid, no results area, nothing else in the panel

**What opened it** — `detail-order-hx-hover.jpg`, three frames: at 01:31 and
01:32 the cursor sits on the toolbar's `Order Hx` button and the button carries a
hover/focus outline; at 01:33 the outline has cleared and the dialog is up. So
**`Order Hx` opens it.** `Orders`, the button to its left, was never clicked.

**How to build it** (this was decided with the operator):

- Use `frontend/components/shared/DialogShell.tsx` — the repo's Epic modal
  primitive — and **inherit its spacing**. Do not derive px from these frames;
  see the provenance section. Say so in the component comment.
- `width`: match the nearest existing dialog of this shape rather than measuring.
  From the frame it is a small single-field dialog, well under `DialogShell`'s
  600px default — pick by eye against an existing sibling and note that the
  choice is unmeasured.
- Behaviour that IS evidenced: the dialog opens over the hub without navigating,
  the input starts empty and focused, `Accept` is disabled while it is empty,
  `Cancel` and `×` dismiss.
- Behaviour that is NOT evidenced: what a scanned barcode or a typed order id
  does. Nothing was ever entered. Do not build a submit path that navigates
  somewhere — leave `Accept` inert with a title saying it was never exercised,
  the way the disabled toolbar buttons in `MedsScreen` do.

**Wiring — one constraint.** `Order Hx` currently falls through `TopToolbar`'s
dispatch to the final `<Link href={activityHref(label)}>` branch, and since
neither `Order Hx` nor `Orders` is in `nav.ts`, that resolves to the
`/activity/order-hx` catch-all stub. Replacing that with the dialog loses
nothing.

**Do not route it through `MODAL_ACTIVITIES`.** Every member of that map is a
patient/record lookup and its values are `LookupKind`s that open
`PatientLookupModal` with a destination. `Select an Order` is not a lookup — it
is an id-entry box with no grid. Adding a `LookupKind` for it would make the type
mean two different things. A separate branch in `TopToolbar` (or a small
Willow-scoped dialog state) keeps the distinction honest. You own that file —
pick the shape that fits it.

---

## A6. Minor — strengthen the Common Links note

**File:** `frontend/components/WillowProjectTeam/LinksInfoColumn.tsx` (~L134–142).

The comment says an eighth Common Links entry sits below the fold, that the
strokes look like "Content Management", and that the pixels do not settle it —
so it is left as a marked gap. **That judgement is correct; keep the gap.** Two
things can be said more precisely:

- The partial reading is corroborated across **10+ independent hub frames** in
  this pass, not one. Every one clips the row at the same height and every one is
  consistent with `Content Management`. Still the top half of the glyphs, still
  not settled — but no longer a single-frame guess.
- Several of those frames show a `▾` scroll affordance under the list, so **the
  list may be longer than eight** and was never scrolled. Worth recording, since
  the current note implies eight is the total.

No behaviour change. Comment only.

---

# PART B — three first-run dialogs in the chart portion

The operator decided these should be modelled the way
`PatientChart09/MedsScreen.tsx` models `Alternating Row Coloring`: render the
dialog as observed, and be explicit about what it covers.

They are a **sequence**, not three unrelated cards, and that is worth carrying:

```
00:48  Chart Review   "Welcome to Hyperdrive QA"  — a video card; operator takes "Watch Later"
00:52  Chart Review   "Reminder Added"            — confirms it went to the Notification Center;
                                                    the notification badge now reads 2
00:58  Timeline       "Graphs Now Scale Automatically"
```

Note `Reminder Added` names the *consequence* of the choice made in the card
before it. Do not model them as independent.

## B1. `Welcome to Hyperdrive QA` — Chart Review, 00:48

**Frame:** `2fps-f_000096-t00m48s`. Screen behind it is Chart Review with the
`Encounters` tab selected. Rendered by
`frontend/components/ChartReviewActivity/ChartReviewActivityWorkspace.tsx`, not
by `PatientChart09` — Chart Review has no screen component in that folder.

- title `Welcome to Hyperdrive QA`
- body is a **large promotional illustration** — a monitor showing a globe, a
  plant, an Epic-branded coffee mug — with a circular `▶ Watch Now!` control
  overlaid across its lower middle
- beneath the illustration, two inline actions: `More Content Like This` (with a
  small leading glyph) and `✗ I've Watched This`
- bottom left, a bordered button: `Watch Later` (with a leading glyph)
- a `?` and an `×` sit in the activity's own header strip to the right, along
  with a purple notification badge

**The illustration is Epic's own marketing artwork.** Do not draw an
approximation of it — that is inventing reference content, and it is also
someone's art. Render the region as an explicitly-uncaptured image placeholder
carrying its description, and put the real strings (title, `Watch Now!`, the two
actions, `Watch Later`) around it. The controls are the part that matters.

## B2. `Reminder Added` — Chart Review, 00:52. A toast, not a modal.

**Frame:** `2fps-f_000105-t00m52s`.

This one is **not a dialog**. It is a small anchored callout with a pointer tail,
hanging below the purple notification badge in the activity header — the badge
now reads `2` and carries a small video glyph.

- a green circled check, then the title `Reminder Added`
- body, two lines: `We've added a Here's How video reminder to the Notification
  Center.`
- no buttons, no close control visible

Check `frontend/components/common/Toast.tsx` and
`frontend/components/shared/useAnchoredPopover.ts` before building anything —
Reference-This-Repo-First. An anchored popover with a tail is much closer to
this than a modal is.

Behind it, Chart Review's `Encounters` grid **is** visible in this frame
(`When` / `Type` / `With` / `Description` / `Tag` / `Open/Close`, a `5 Years Ago`
group with one selected `12/08/2016 · Anesthesia Event · OBGYN · Line Placement ·
Open` row, and a `10 Years Ago` group with two rows). That is Chart Review's own
brief's territory, not this one's — mentioned only so you know the toast does not
occlude the grid and must not be modelled as if it does.

## B3. `Graphs Now Scale Automatically` — Timeline, 00:58

**Frame:** `2fps-f_000117-t00m58s`. Screen behind it is Timeline with
`Antimicrobial Summary` selected.

- title `Graphs Now Scale Automatically`, with an `×` at the right
- one line of body: `The y-axis range adjusts to show all graphed data.`
- **two side-by-side illustration panels** with a right-pointing arrow between
  them, each a small line chart. Captions beneath:
  - left: `Before, points outside the y-axis scale were not visible.`
  - right: `Now, the graph scales automatically to show all graphed data.`
- bottom right, one button: `✓ Got it!`

Same rule as B1 for the two chart illustrations: they are explanatory artwork.
Carry the captions and the arrow as structure; do not reproduce plotted data —
there is no data, only a diagram.

**One difference from `MedsScreen` worth handling deliberately.** There, the
dialog covers a grid that was never seen, so dismissing it reveals a
not-captured note. Here, **Timeline's body IS captured** — `TimelineScreen.tsx`
is built from `f_000064` (01:04), a frame where this dialog is already gone. So
dismissing this one should reveal the Timeline body you already render, not a
gap note. Model it as open on arrival and dismissible, revealing the real screen.

Seed data goes beside `MEDS_DIALOG_TITLE` / `_LINES` / `_BUTTONS` in
`backend/scripts/seeds/chart09_content.py` for B3. B1 and B2 belong with
whatever seeds `ChartReviewActivity`.

---

# PART C — DO NOT CHANGE THESE

Four places where this pass produced a different answer from your code and **your
code is correct**. Two of them your own seed notes had already diagnosed
precisely. They are listed so nobody "fixes" working code against a bad reading,
and because they say something about how much to trust the catalogue.

## C1. `Calcium Phosphate Solubility` was never opened — the `_MISLABELLED` note is right

The catalogue recorded `section: "Calcium Phosphate Solubility"` at 04:43 with an
accepted confidence of 0.81. **Wrong.** In `f_000566` the sidebar accent bar is
on `Related Information`, at the bottom of the tree; "Calcium Phosphate
Solubility" is the title of the first *card* in that panel. Which is exactly what
`willow_hc_content.py`'s `_MISLABELLED` already says. Keep it `not_captured`.

## C2. `Dispense Prep` was never opened either — keep `_NOT_SHIPPED`

Same failure at 04:41, `section: "Dispense Prep"`, accepted 0.82. In `f_000563`
the accent bar is again on `Related Information` — the same panel, scrolled up.
`Dispense Prep` is merely *expanded* in the sidebar, showing its `Gravimetrics`
child. Keep it `not_captured`.

## C3. `Medication Admin ▸ Billing` was never opened — `_BILLING_NOT_OPENED` is right

The catalogue recorded `section: "Billing"` on Medication Admin at 06:49,
accepted 0.79. In `1fps-f_000409` the accent bar is on **`Packaging`**, with
`Billing` expanded beneath it showing `Overrides` and `Prescription`. Your note
already says "The frame named `section-billing.jpg` is in fact Packaging a second
time — its sidebar accent bar is on the Packaging row." Correct. Keep it.

(That frame also has a department lookup open over the panel — columns `ID`,
`Department`, `Center`, `Specialty`, `Location`, `Service Area` — which is the
`departments` lookup `FieldLookup.tsx` already models.)

## C4. Medication List has four tabs, not five, and Report Settings' tabs are already right

- The catalogue reported an `AQS` tab on Medication List. **There is no such
  tab.** `detail-med-list-tab-row.jpg` shows exactly four: `Medications`, `ADS`,
  `Billing`, `Related Information` — matching `willow_medlist_content.py`'s
  `TABS`.
- The catalogue reported eight tabs on Report Settings. That was two levels
  flattened into one list: three top-level (`Criteria`, `Display`, `General`) and
  five sub-tabs under Criteria (`Appointments`, `Admissions`, `Cases`, `Orders`,
  `Wait Times`). `willow_report_settings_content.py` already has both, in `TABS`
  and `CRITERIA_TABS`, with the right selected states and the
  `Additional Settings`-is-cut note. Nothing to do.

**The pattern in C1–C3:** the catalogue reports an expanded parent row, or a
panel's first card title, instead of the row carrying the selection accent bar —
and it did so at 0.79–0.82 confidence, inside the accept threshold. Treat any
`section` value in the v01 catalogue as a lead to verify against the frame, not
as a fact. Presence of a screen, record identities and menu rows held up well;
`section` and `tabs` did not.

---

## Acceptance

- [ ] `Home Infusion` is row 23 of the Rx Admin menu, disabled, with a chevron;
      no placeholder row remains; the comment claims 23 exactly and cites the two
      frames showing the panel border
- [ ] The inventory export now lists `Home Infusion` and no longer lists
      `(one more activity, name not legible)`
- [ ] `Hospital/Clinic Admin ▸ Home Infusion` renders its two fields, its
      three-column rules table with one empty row, and its four row-action
      buttons (all greyed); the `Pump Questions Not to Copy Forward` lookup is
      seeded from `f_000458` as a distinct question-grouper set, the other two
      lookups stay never-opened; the third column stays clipped
- [ ] `willow_hc_content.py`'s docstring arithmetic matches its `TREE`
- [ ] Related Information renders eight cards, the top one explicitly unnamed,
      and records that the panel may hold more above
- [ ] `Find Patients ▾` opens a real four-row menu; `Today's Patients` is
      disabled; the other three resolve the way `nav.ts` already resolves them
- [ ] Both stale "only Rx Admin's contents are known" comments are gone
- [ ] `Order Hx` opens `Select an Order`; `Accept` is disabled on an empty input
      and inert regardless; the component comment says its geometry is inherited,
      not measured
- [ ] The three first-run dialogs render, the two artwork regions are explicit
      placeholders rather than drawings, `Reminder Added` is an anchored toast,
      and dismissing the Timeline one reveals the real Timeline body
- [ ] Nothing in Part C changed
- [ ] `docs/reference/WILLOW_CAPTURE_GAPS.md` updated — the Home Infusion entry
      at its line ~157 is now closed, and the Common Links note gains the 10-frame
      corroboration and the scroll affordance

## What this brief does not close

Stated so the coverage denominator stays honest:

- **Panel contents for ~15 sections** that `TREE`s mark `observed` were not
  re-verified by this pass — only the trees were. General, Verification,
  Inventory, Lot/Exp, Compounding and Repackaging, Medication Validation System,
  Shipment Steps, Equivalency, Overrides, Prescription, Dispense Prep/CNR,
  Identity/ADS, and the three Workstation sections.
- **20–21 screens per run were never named** — the title band was unreadable.
  Most read as record pickers, which `WillowLaunch` covers; their contents are
  unverified.
- **35–40 frames per run were suppressed by dedupe** and 20 could not be
  rectified, including 00:00–00:09 and 07:04–07:08. Nobody has looked at those
  pixels.
- **Seven toolbar dropdowns were never opened** — `Orders`, `Order Hx`,
  `Inventory Management Admin`, `Pharmacy`, `Inventory`, `Beacon Admin`, `More` —
  nor the submenus behind `Home Infusion`, `Inventory Management Admin` and
  `Rule Deferral Admin`.
- **Data-grid cell contents** are permanently out of scope for this pipeline
  (DEC-011), so no run will ever confirm them.
