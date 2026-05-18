# Phase 7 Rbtree Validation Matrix

This note keeps the surviving Phase 7 `rbtree` review anchors honest without implying that the broader helper packet has returned on current `master`.

## Status

- `PHASE7_STATUS=direct_anchor_only`
- `PHASE7_PACKET=rbtree-runtime-leaf`
- lane owner: `P7-L13`
- schedule alias: `P7-Y04 -> P7-L13`
- current direct-readback state: `survey_and_manifest_anchor`
- product boundary: surviving survey-plus-manifest reminder packet only
- freeze posture: stay inside the existing survey, manifest, and owner-map truthfulness packet; do not widen into shared-control, sample, or broader runtime-loader work from this note

## Owned Review Surface

The current directly readable same-lane `rbtree` packet is limited to:

- `Documentation/zigux/phase7-helper-lane-sequencing.md`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase7_rbtree_manifest.json`

The broader helper-local packet still reads missing on current `master`:

- `Documentation/zigux/phase7-rbtree-slice.md`
- `lib/rbtree.zig`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
- `scripts/zigux/check-phase7-rbtree-parity.py`
- `zigux/tests/phase7_build.zig`
- `scripts/zigux/validate-phase7.py`

Readable non-owner evidence that still matters for route truthfulness:

- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

## Validation Surfaces

Current rbtree evidence comes from these surviving or readable surfaces:

| Surface | Current role | What it proves today |
| --- | --- | --- |
| `Documentation/zigux/phase7-helper-lane-sequencing.md` | owner-map reminder | current `master` only directly rereads the survey and manifest anchors for `rbtree`, and same-lane follow-through must stay inside those surviving files until another rbtree companion returns |
| `zigux/tests/phase7_rbtree_survey.zig` | survey gate | roadmap anchor, lane ownership, direct-anchor posture, no-sample boundary, and missing broader-packet paths fail closed together |
| `zigux/tests/phase7_rbtree_manifest.json` | machine-readable packet record | lane ownership, surviving direct-readback state, missing broader-packet files, non-owner route evidence, and next bounded same-lane step stay explicit |
| `zigux/Makefile` | readable non-owner route evidence | the current `phase7-*` wrapper routes are still visible even though the missing helper, dedicated test, checker, and shared build files block any claim that the broader rbtree packet returned |
| `.github/workflows/zigux-bootstrap.yml` | readable non-owner workflow evidence | the workflow still lacks dedicated Phase 7 runtime-helper steps, so build-graph truthfulness must stay split between readable wrapper markers and missing broader-packet files |

## Ownership And Boundary Notes

- This packet is still a runtime-safe leaf-helper lane only.
- The surviving survey-plus-manifest anchor must not be presented as proof that the broader rbtree helper, dedicated test, fixture, checker, or shared build files have returned on current `master`.
- Same-lane follow-through stays inside the surviving survey and manifest anchors until a fresh reread proves another rbtree companion returned on current `master`.
- Cross-helper truthfulness must keep the landed `string_helpers` packet explicit instead of repeating the older blocked-by-missing-string-helper claim.
- Build-graph truthfulness must keep the split non-owner evidence explicit: `zigux/Makefile` now exposes the current `phase7-*` wrapper routes, `.github/workflows/zigux-bootstrap.yml` still lacks dedicated Phase 7 runtime-helper steps, and the missing helper, dedicated test, checker, and shared build files still block any claim that the broader rbtree build packet returned.

## Review Sequence

Use this order when rechecking the current packet:

1. Read `zigux/tests/phase7_rbtree_manifest.json` for the machine-readable direct-anchor state and missing-path inventory.
2. Recheck `zigux/tests/phase7_rbtree_survey.zig` so the survey still exact-requires the same owner-map and missing-path truthfulness.
3. Recheck `Documentation/zigux/phase7-helper-lane-sequencing.md` so the shared owner map still keeps same-lane work anchored to the surviving survey-plus-manifest packet.
4. Recheck `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` only as non-owner route evidence; do not use them alone to imply that the broader rbtree helper packet returned.
5. Recheck `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `scripts/zigux/check-phase7-rbtree-parity.py`, `zigux/tests/phase7_build.zig`, and `scripts/zigux/validate-phase7.py` only if a fresh reread proves those missing files have returned.

## Next Bounded Step

Leave this packet parked unless fresh repo-first inspection finds one more equally small survey-or-manifest truthfulness miss inside the existing `rbtree` review bundle. If `lib/rbtree.zig` or another broader companion file returns on current `master`, reopen the lane from that new direct evidence instead of carrying forward the older missing-helper assumptions.
