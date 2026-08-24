# Build brief 17 — Shortages' `Affected Packages` lookup, which is not empty

**Branch:** `pharmacy-admin`. One item. Corrects brief 13.

**Evidence:** `~/build-evidence/17-v02-shortages-lookup/` — 2 frames.

**Provenance:** rectified handheld footage. Labels, order, column sets, states yes.
Geometry no.

---

## What brief 13 got wrong

Brief 13 described Shortages' filter panel as five lookups, all empty, and its
acceptance closed with:

> No populated grid exists anywhere in this module. Shortages, lots, workqueues and
> par levels are all empty in every frame, so no column set for those tables is
> evidenced. Recorded as one module-wide gap rather than four screens' worth of
> guesses.

**Both halves are wrong.** The `Affected Packages` lookup is open and populated in
two frames, and it is the one populated grid in the Inventory module. The two frames
were in v02's catalogue the whole time as unnamed screens at 01:43 and 01:46 —
nobody had opened them, mine included.

This is the third time this corpus has punished not reading a frame that was
already sitting in the output directory: brief 10 shipped one unread, brief 15 cited
two unshipped, and here two sat unaudited inside the fixture.

---

## What the frames show

Shortages is behind, unchanged from brief 13 — the `Status` chips (`Draft ×`,
`Pending ×`, `Active ×`, `Cleaning Up ×`), `Severity` below it, the balloon empty
state, `Open Shortage` and `× Close`. The cursor rests on the magnifier of the field
directly **above** `Status`, which is `Affected Packages`.

The lookup opens as a wide overlay panel across the upper two thirds of the window.

**Columns:** `NDC Code` · `Associated Medication` · `Status` · `Package Size` ·
`Manufacturer`

`Status` holds no text — only a ⚠ glyph on some rows, blank on others.

**Rows.** The two frames overlap, so this is a contiguous prefix, not two samples.
`f_000103` is at the top of the list; `f_000106` is scrolled down by four rows.

| NDC Code | Associated Medication | ⚠ | Package Size | Manufacturer |
| --- | --- | --- | --- | --- |
| 9999990180 | CEFOTAXIME SODIUM 500 MG IJ SOLR | | | |
| 9999990180 | CEFOTAXIME SODIUM 500 MG IJ SOLR | | | |
| 0000-0001-00 | SULFAMETHOXAZOLE-TRIMETHOPRIM 160 MCG/… | | 1 x 50 mL Vial | FOUNDATION SYSTEM … |
| 0000-0001-01 | SULFAMETHOXAZOLE-TRIMETHOPRIM 16 MCG/M… | | 1 x 10 mL Vial | FOUNDATION SYSTEM … |
| 0000-0001-02 | LC BEADS 70-150 MICROMETER | | 1 x 1 Each | FOUNDATION SYSTEM … |
| 0000-0001-03 | LC BEADS 100-300 MICROMETER | | 1 x 1 Each | FOUNDATION SYSTEM … |
| 0000-0001-04 | LC BEADS 300-500 MICROMETER | | 1 x 1 Each | FOUNDATION SYSTEM … |
| 0000-0001-05 | LC BEADS 500-700 MICROMETER | | 1 x 1 Each | FOUNDATION SYSTEM … |
| 00001-05823 | ETHANOL 95 % SOLN | | 1 x 480 mL Bottle | LAB ALLEY |
| 00001-34957 | ETHANOL 95 % SOLN | | 1 x 480 mL Bottle | LAB ALLEY |
| 00004-405-09 | MIRCERA 200 MCG/0.3ML IJ SOSY | ⚠ | 1 x 0.3 mL Syringe | VIFOR |
| 0002-0152-04 | ZEPBOUND 2.5 MG/0.5ML SC SOLN | | 4 x 0.5 mL Vial | LILLY |
| 0002-0213-01 | HUMULIN R 100 UNIT/ML IJ SOLN | | 1 x 3 mL Vial | LILLY |
| 0002-0243-04 | ZEPBOUND 5 MG/0.5ML SC SOLN | | 4 x 0.5 mL Vial | LILLY |
| 0002-0351-02 | DARVOCET-N 50 50-325 MG PO TABS | ⚠ | 1 x 100 Each Bottle | AAIPHARMA |
| 0002-0353-02 | DARVON-N 100 MG PO TABS | ⚠ | 1 x 100 Each Bottle | AAIPHARMA |
| 0002-0353-03 | DARVON-N 100 MG PO TABS | ⚠ | 1 x 500 Each Bottle | AAIPHARMA |

Seventeen rows. **The scroll thumb sits near the top in both frames, so the list
continues well past `0002-0353-03`** — seed these seventeen and record that it
continues, the way brief 15's Infusion Duration Table handles its twelve.

## Four details worth not smoothing over

**The first row is duplicated.** `9999990180 CEFOTAXIME SODIUM 500 MG IJ SOLR`
appears twice, the first rendered **bold** and the second not, and neither carries a
Package Size or Manufacturer where every later row does. That is what the frame
shows. Do not dedupe it and do not fill the blanks — whether the bold row is a
"currently matched" header, a selected entry, or a genuine duplicate record is
**not** demonstrated. Record the question.

**The NDC code formats are inconsistent** — `9999990180` unpunctuated,
`0000-0001-00` in three groups, `00001-05823` in two, `00004-405-09` in three with
different widths. Transcribe each exactly. A normaliser here would be inventing a
format the source does not use.

**`Status` is glyph-only.** **Four** rows carry ⚠ and the rest are blank — the row
table above is correct and this prose originally said five, twice. Confirmed by an
amber-pixel scan of the Status column across both frames. There is no
text and no legend in frame, so what the warning means is not evidenced.

**Two columns clip, not one.** `FOUNDATION SYSTEM …` is cut on every row that has
it, and **both `SULFAMETHOXAZOLE-TRIMETHOPRIM` medication names are cut too**, with
a visible ellipsis. The row table carries both, so seeding from the table is right;
this callout understated it.

## One cross-video observation, offered as context only

`9999990180 / CEFOTAXIME SODIUM 500 MG IJ SOLR` is the same NDC record v01 caught
in NDC Admin, where its heading read `9999990180 (Active) (CEFOTAXIME SODIUM 500 MG
IJ SOLR) [342577]`. Same record, two videos, two modules. **Do not use this to fill
anything in** — it is a coincidence worth knowing, not evidence about this lookup.
If it tempts you to borrow the `(Active)` status or the `[342577]` id into this
grid, that is exactly the borrowing brief 04's `Identity/ADS` note already refused.

---

## Acceptance

- [ ] Shortages' `Affected Packages` lookup opens as a wide overlay with the five
      columns above, in order
- [ ] Seventeen rows seeded exactly as transcribed, with a note that the list
      continues past the last one
- [ ] The duplicated bold first row is preserved, its blanks left blank, and the
      question of what it is recorded rather than answered
- [ ] NDC codes keep their inconsistent punctuation; no normaliser
- [ ] `Status` renders the ⚠ glyph on the four rows that have it and nothing on the
      rest; what it means is recorded as unevidenced
- [ ] `FOUNDATION SYSTEM …` stays clipped
- [ ] The other four Shortages lookups stay empty — only `Affected Packages` was
      opened
- [ ] Brief 13's "no populated grid exists anywhere in this module" gap is
      **removed** from `WILLOW_CAPTURE_GAPS.md`, replaced by what this frame shows
      and what it still does not
- [ ] No geometry measured from these frames
