# Build brief 16 — the `More ▾` cascade, and the Relationship Builder welcome panel

**Branch:** `pharmacy-admin`. Small brief, two items, and it exists because of a
mistake in brief 15.

Brief 15 cited both of these — `Troubleshooting Tools` in §7, the welcome card in
§4 — and **shipped no frames for either**, so the build session correctly recorded
them as unbuildable. Both frames exist and both are fully legible. That is the
mirror of brief 10's failure: there a frame was shipped and not read, here frames
were cited and not shipped. Same root cause, opposite direction.

**Evidence:** `~/build-evidence/16-v02-more-menu/` — 2 frames.

**Provenance:** rectified handheld footage. Labels, order, nesting, state yes.
Geometry no.

---

## 1. `More ▾` — a third toolbar menu, with a three-level cascade

`more-menu-build-tools-cascade-f_000576` (09:36). This is the last frame of v02
and it is one of the most valuable in either recording: `More ▾` is one of the
seven dropdowns v01's coverage boundary listed as never opened.

### The `More ▾` panel itself — four rows

| # | label | submenu |
| --- | --- | --- |
| 1 | Troubleshooting Tools | ▸ |
| 2 | Build Tools | ▸ |
| 3 | Content Management | — |
| 4 | Record Viewer | — |

Row 1 carries the hover highlight. **Check the panel's bottom border before
claiming four is the total** — brief 12's two menus were exact because the border
was visible under the last row, and that is the test to apply here too. If the
border is not visible, four is a floor and must be recorded as one.

### The expanded flyout — 20 rows

```
Rule Editor                        Grouper Editor
Property Editor                    Data Courier
Scoring System Editor              Compare Record
Column Editor                      Content Management
Medication Warnings Admin      ▸   Category List Maintenance
Medication Management          ▸   User Security
Medication Display Name Replacer   Security Class Editor
Frequency Editor                   Second Sign Editor - Full Access
Order-Specific Question Editor     Workflow Engine Rule
OurPractice Advisory               Report/HTML Assistance
```

Read as a single column top-to-bottom in that order — the two columns above are
this document's layout, not the menu's.

**CORRECTED: the flyout has seven separators, and this listing omitted them.**
Measured after the fact — a 15–36 point dark dip at each, against +2 to +3 for
ordinary row gaps, with row pitch widening to 43–45px from 38–41px at exactly the
same seven boundaries. Ink and layout agreeing on the same positions, and the dips
confined to the panel rather than crossing it, which rules out a scanline or
gradient artifact.

Rules fall after rows 7, 9, 10, 11, 14, 15 and 19, giving eight groups:

```
Rule Editor · Property Editor · Scoring System Editor · Column Editor ·
Medication Warnings Admin ▸ · Medication Management ▸ · Medication Display Name Replacer
———
Frequency Editor · Order-Specific Question Editor
———
OurPractice Advisory
———
Grouper Editor
———
Data Courier · Compare Record · Content Management · Category List Maintenance
———
User Security
———
Security Class Editor · Second Sign Editor - Full Access · Workflow Engine Rule
———
Report/HTML Assistance
```

Four of the eight groups are singletons, which looks odd and is idiomatic here:
`RX_ADMIN_GROUPS` already has three — `Medication List Admin`, `Merchandise and Fee
Admin` and `Cart Admin` each sit alone. No defence needed.

Two things to settle while building: whether seven is the **total or a floor** (a
rule clipped at the flyout's top or bottom edge would change the grouping — same
border test as the `More ▾` panel's four rows), and whether the dip and the pitch
signals ever **disagree**. If any boundary has one without the other it is weaker
than the other six and should be recorded that way rather than averaged in.

This is the second time a menu's separators were missing from one of my listings —
brief 12's Beacon menu was the first. Menu transcriptions should record group
boundaries as a matter of course, not as an afterthought.

`Medication Warnings Admin ▸` and `Medication Management ▸` carry their own
chevrons and **were not expanded**. Give them `hasMore: true` and no children, as
brief 12 did for `SmartForms` and `SmartTool Editors`.

Three rows appear to carry **no icon** — `Medication Display Name Replacer`,
`Frequency Editor`, `Second Sign Editor - Full Access`. Verify against the frame
and transcribe the absence rather than filling it, the way brief 12 handled the
four unglyphed Beacon rows.

### RESOLVED: `Build Tools` owns the flyout

**This section previously reserved the parentage as unresolvable. That was wrong,
and it was wrong because of a defect in my own reading.** Recorded here rather
than deleted, because the reason matters more than the answer.

What I claimed: the flyout aligns with `Build Tools`, but the highlight box sits on
`Troubleshooting Tools`, so the two arguments conflict and the frame cannot decide.

What measurement shows. Per-row background sampled as **blue-minus-red**, chosen
because a selection tint raises blue relative to red while a lighting gradient
moves all channels together:

| row | b−r | luminance |
| --- | --- | --- |
| Troubleshooting Tools | −5.0 | 229.0 |
| **Build Tools** | **+11.0** | 201.3 |
| Content Management | −3.0 | 210.0 |
| Record Viewer | −4.0 | 205.0 |
| flyout background, y200 / y400 / y700 | −5.0 / −5.0 / −5.0 | 184.7 → 179.7 |

Two independent confirmations beyond the 16-unit separation:

1. **The metric's invariance is demonstrated on this frame.** The flyout background
   holds b−r = −5.0 across a 500px span while luminance drifts 184.7 → 179.7. So
   the +11.0 on `Build Tools` is chromatic, not illumination.
2. **The blue plateau spans y78–120 — one 41px row pitch, bracketing `Build
   Tools`.** Extent corroborates magnitude.

And the confound is identified: `Troubleshooting Tools` is the **brightest** band in
the panel (lum 229, R 230) while chromatically neutral. I read the brightest row as
the highlighted row. That is a luminance artifact of handheld footage — the same
error class as brief 13's Lot and Expiration controls, which looked washed out and
measured enabled.

So the positional and highlight arguments **agree**: attach the 20 rows to
`Build Tools`.

`Troubleshooting Tools` keeps `hasMore: true` with **no children** — its submenu
genuinely was never expanded. It simply is not this flyout's parent.

**Why this overrides "do not resolve by inference".** That instruction bars
guessing from meaning — the "these look like build tools" argument, which remains
inadmissible. Measurement on an illumination-invariant metric, corroborated by
plateau extent, is not inference. The same method correctly reported brief 14's
toolbar greyed states as *undecided* when it turned out to be glyph-confounded; a
method that reports its own failures is one to trust when it reports a result.

**Exporter consequence.** As `Build Tools` children the 20 rows now reach
`inventory.json` with `module` = the toolbar button's label, `More`, per brief 12's
decision. The entry count will move well past 300 — state the new total so the jump
is explained rather than discovered later.

### `Security Class Editor` appears here too

Note row 17 of the flyout. Brief 14 built a `Security Class Editor` reached from
`Beacon Admin ▾ ▸ Beacon Security`, and the same label is a `More ▾` descendant.
Whether they are one activity reachable two ways or two different editors is
**not** settled by this frame. Do not merge them, and do not route this row to
brief 14's page.

### Bonus: the hub in detail

This frame also shows the Willow Project Team hub more completely than brief 10's
frames did — `Interface Error Workqueue Summary` with a populated table
(`Willow Inpatient Interface Errors` and `Device Integration Interface Errors`,
both `Total Errors 0`, `Added Today 0`, `Last Accessed Never`), and
`Rx Project Team Reports` with five named reports each `Ready to run`. Out of
scope for this brief; worth a note in the gaps doc as newly-available hub
evidence.

---

## 2. `Welcome to the Relationship Builder`

`welcome-relationship-builder-f_000433` (07:13). A first-run **panel**, docked at
the right over the Relationship Builder grid — not a centred modal. The builder's
own footer (`Context:`, `Release`, `Save`, `Accept`, `Cancel`) stays visible
beneath it, and its `Group 2` columns are occluded rather than the whole screen.

Title: `Welcome to the Relationship Builder`

Intro paragraph, verbatim:

> Relationships define logical dependencies between SmartData elements. Unlike
> scripting, which is form-specific, relationships affect data across all
> SmartForms in a context. A relationship consists of implications and exclusions.

Section `Implications`:

> An implication defines a group of trigger SmartData elements which imply a
> certain value for a result SmartData element.
>
> For example, a relationship could contain an implication where the trigger
> elements each document a specific kind of abdominal pain and the result element
> documents abdominal pain in general. If a user enters a positive finding for any
> specific kind of abdominal pain, the positive finding for general abdominal pain
> is also automatically selected. Conversely, if the user clears the positive
> finding for general abdominal pain, then the positive findings for any specific
> kinds of abdominal pain are also cleared.

Section `Exclusions`:

> An exclusion defines two groups of SmartData elements which are mutually
> exclusive.
>
> For example, a relationship could contain an exclusion where one group contains
> the SmartData element "Nose Normal" and the other group contains elements such
> as "Congestion," "Nasal Tenderness," and "Epistaxis" (nosebleed). If the user
> initially selects a "Nose Normal" checkbox on one of your facility's SmartForms,
> but later documents that the patient has congestion or a nosebleed, the "Nose
> Normal" checkbox is cleared automatically. Conversely, if a user documents a
> specific symptom, and then marks the nose as normal, the previously documented
> symptom is cleared.

No visible close control, no buttons, no dismissal affordance in frame. There is a
small glyph pair at the panel's top-left edge that may be a collapse control —
verify before modelling it as one. **Nothing was ever clicked on this panel**, so
whether and how it dismisses is not demonstrated: render it open, and if you give
it a dismiss path, say in the comment that the path is unevidenced.

---

## Acceptance

- [ ] `More ▾` opens a real menu; its row count is stated as exact **only** if the
      panel's bottom border is visible under `Record Viewer`, otherwise recorded
      as a floor
- [ ] The 20 flyout rows are transcribed in order and attached to **`Build
      Tools`**, per the resolved measurement; `Troubleshooting Tools` keeps
      `hasMore: true` with no children
- [ ] The flyout renders **eight groups** separated by seven rules, in the
      positions above; seven is stated as exact or as a floor per the edge check
- [ ] `Medication Warnings Admin ▸` and `Medication Management ▸` have chevrons
      and no children
- [ ] Unglyphed rows are transcribed as unglyphed
- [ ] The `More ▾ ▸ Security Class Editor` row is **not** routed to brief 14's
      page, and the question of whether they are the same activity is recorded
      rather than answered
- [ ] The welcome panel renders as a docked right-hand panel over the Relationship
      Builder grid, not a centred modal, with all four passages verbatim
- [ ] Its dismissal behaviour is either absent or commented as unevidenced
- [ ] The exporter picks up whatever new labels this adds, per brief 12's decision
- [ ] `WILLOW_CAPTURE_GAPS.md` records: `More ▾`'s parentage ambiguity, the two
      unexpanded flyout submenus, the `Security Class Editor` duplicate-label
      question, and the newly-available hub detail in `f_000576`
