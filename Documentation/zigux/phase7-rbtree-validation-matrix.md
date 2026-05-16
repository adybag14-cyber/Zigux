# Phase 7 Rbtree Validation Matrix

This note keeps the current Phase 7 `rbtree` helper packet reviewable without widening into new helper behavior.

## Status

- `PHASE7_STATUS=landed`
- `PHASE7_PACKET=rbtree-runtime-leaf`
- lane owner: `P7-L13`
- schedule alias: `P7-Y04 -> P7-L13`
- product boundary: parked helper-local parity and review packet only
- freeze posture: stay inside existing runtime-safe leaf-helper validation, ownership, and parity evidence; do not widen into shared-control, sample, or broader runtime-loader work from this note

## Owned Review Surface

The current helper-local `rbtree` packet is limited to these landed review surfaces:

- `Documentation/zigux/phase7-rbtree-slice.md`
- `lib/rbtree.zig`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase7_rbtree_manifest.json`
- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
- `scripts/zigux/check-phase7-rbtree-parity.py`

Shared reminder surfaces stay outside this packet and remain owned by the shared Phase 7 lanes:

- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `samples/zigux/README.md`
- `zigux/Makefile`
- `scripts/zigux/validate-phase7.py`
- `scripts/zigux/check-phase7-build-wiring.py`
- `scripts/zigux/check-phase7-build-inventory.py`
- `scripts/zigux/check-phase7-make-wrapper.py`
- `zigux/tests/phase7_build.zig`

## Validation Surfaces

Helper-local parity and ownership evidence currently comes from these surfaces:

| Surface | Current role | What it proves today |
| --- | --- | --- |
| `lib/rbtree.zig` | implementation plus helper-local unit tests | cached-tree, linked-node, erase-init, match-search, and replacement entrypoints stay explicit inside the parked helper packet |
| `zigux/tests/phase7_rbtree.zig` | dedicated Phase 7 helper replay | the reusable runtime leaf packet stays reviewable through direct Phase 7 tests rather than only through the shared build bundle |
| `zigux/tests/phase7_rbtree_survey.zig` | survey gate | roadmap anchor, helper-lane ownership, no-sample boundary, shared review surfaces, manifest wording, build inventory, slice-note wording, and parity-checker routes fail closed together |
| `zigux/tests/phase7_rbtree_manifest.json` | machine-readable packet record | lane ownership, parity packet contents, detached-node and replacement-node ownership claims, and parked posture stay explicit |
| `zigux/tests/fixtures/phase7_rbtree.json` | serialized parity fixture | the bounded replay packet keeps deterministic parity inputs visible |
| `zigux/tests/fixtures/phase7_rbtree_c_harness.c` | C-side parity harness | the parked parity packet keeps the Linux-facing comparison surface explicit |
| `scripts/zigux/check-phase7-rbtree-parity.py` | dedicated checker | shared docs, tests, samples, validator, Makefile, manifest, helper, fixture, and parity anchors stay aligned with the landed helper-local packet |

## Ownership And Boundary Notes

- This packet is still a runtime-safe leaf-helper lane only.
- There is no standalone `samples/zigux/*rbtree*` reference sample in the current Phase 7 packet.
- The shared `zigux/tests/phase7_build.zig` route remains reviewable evidence, but it is not the only proof surface for this helper family.
- Helper-local follow-up should prefer one-file survey, checker, manifest, fixture, or slice-note truthfulness repairs before any new helper behavior.

## Review Sequence

Use this order when rechecking the landed packet:

1. Read `Documentation/zigux/phase7-rbtree-slice.md` for current scope, lane ownership, and non-goals.
2. Read `zigux/tests/phase7_rbtree_manifest.json` for machine-readable packet ownership and parity claims.
3. Recheck `zigux/tests/phase7_rbtree_survey.zig` so the survey still exact-requires the shared reminder surfaces and helper-local ownership markers.
4. Recheck `scripts/zigux/check-phase7-rbtree-parity.py` so the checker still fail-closes on the live helper, fixture, manifest, and shared packet anchors.
5. Recheck `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/fixtures/phase7_rbtree.json`, and `zigux/tests/fixtures/phase7_rbtree_c_harness.c` only if one of the earlier review surfaces drifted.

## Next Bounded Step

Leave this packet parked unless fresh repo-first inspection finds one more equally small helper-local truthfulness miss inside the existing `rbtree` review bundle. If it reopens, prefer one-file survey, checker, manifest, fixture, or slice-note fail-closed repair before widening helper behavior or touching shared Phase 7 control surfaces.
