# Phase 7 Rbtree Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/rbtree.c`.

## Status

- `PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_anchor`
- `PHASE7_SLICE=rbtree-runtime-leaf`
- `PHASE7_LANE_KEY=P7-L13`
- lane-key note: `P7-L13` keeps the dedicated rbtree packet separate from the broader Phase 7 shared-control lanes; shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate follow-ons
- scope: keep the Phase 7 rbtree lane limited to the returned tool-root helper, the readable roadmap-path companion, the dedicated slice note, the direct-anchor note, the dedicated replay, the dedicated survey, the dedicated manifest, and the dedicated parity checker
- lane state: current `master` directly carries `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `scripts/zigux/check-phase7-rbtree-parity.py`, `tools/lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_rbtree_manifest.json`. Treat those surfaces as the current helper-local packet for this slice. Keep `lib/rbtree.zig` explicit as a directly readable roadmap-path companion and keep `zigux/tests/fixtures/phase7_rbtree.json` plus `zigux/tests/fixtures/phase7_rbtree_c_harness.c` explicit as still-missing same-family follow-ons unless a fresh reread proves they have rematerialized on current `master`. Keep `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` explicit as directly readable shared-control build evidence rather than helper-local ownership; in this runtime `zigux/tests/phase7_build.zig` needed public blob/raw fallback after the authenticated contents bridge returned `404`, so keep that one path framed as returned shared non-owner evidence without overstating authenticated whole-file coverage.

## Why This Slice Exists

Phase 7 is where Zigux starts carrying reusable runtime helper families in product-facing locations.

The current `rbtree` state on `master` now carries a bounded helper-local packet around ordered insertion, ordered traversal, duplicate-range matching, cached-leftmost promotion, erase-init ownership boundaries, and checker-backed reviewability while keeping helper-local ownership on the tool-root implementation and the dedicated fixture pair outside this same helper family.

This slice must stay truthful about the current direct helper path. The helper-local implementation remains rooted at `tools/lib/rbtree.zig`, while the roadmap destination `lib/rbtree.zig` now rematerializes as readable runtime-family companion evidence rather than proof that helper-local ownership has moved off the tool-root packet.

## Gates

1. keep the returned helper-local implementation explicit
- `tools/lib/rbtree.zig`

2. keep the returned helper-local review packet explicit
- `Documentation/zigux/phase7-rbtree-slice.md`
- `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`
- `scripts/zigux/check-phase7-rbtree-parity.py`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase7_rbtree_manifest.json`

3. keep the readable roadmap-path companion explicit and keep the dedicated fixture follow-ons explicit as still missing until they really materialize
- `lib/rbtree.zig`
- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`

4. keep adjacent Phase 7 families and shared-control surfaces out of this packet unless a fresh reread says otherwise
- do not count `Documentation/zigux/phase7-string-helpers-slice.md`
- do not count `Documentation/zigux/phase7-cmdline-slice.md`
- do not count `Documentation/zigux/phase7-argv-split-slice.md`
- keep `lib/rbtree.zig`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` framed as readable roadmap-aligned or shared non-owner evidence rather than helper-local ownership; in this runtime `zigux/tests/phase7_build.zig` needed public blob/raw fallback after the authenticated contents bridge returned `404`, while the other listed non-owner surfaces still materialized through authenticated rereads

## Current Parity Surface

The current helper-local packet on `master` covers:

- `Node`, `Root`, and `RootCached`
- ordered insertion through `add()`, `findAdd()`, and cached aliases
- ordered traversal through `first()`, `next()`, and duplicate-match helpers
- cached-leftmost insertion, cached replacement, and cached erase-init helpers
- dedicated replay, survey, manifest, direct-anchor note, slice note, and parity checker reviewability

The current helper-local replay keeps these proofs explicit:

- ordered traversal stays reviewable through the dedicated replay rooted at `zigux/tests/phase7_rbtree.zig`
- duplicate-range matching stays reviewable through `findFirst()`, `nextMatch()`, and `matchIterator()`
- cached-leftmost promotion and erase-init ownership boundaries stay reviewable through the dedicated replay and the parity checker
- same-lane truthfulness stays rooted at the returned tool-root helper, the returned notes, the returned survey, the returned manifest, and the returned parity checker

The current helper-local replay also keeps these ownership and boundary rules explicit:

- path truthfulness keeps the returned helper rooted at `tools/lib/rbtree.zig` while the readable roadmap destination `lib/rbtree.zig` stays explicit as shared runtime-family companion evidence rather than helper-local ownership
- same-lane truthfulness keeps the returned slice note, direct-anchor note, parity checker, replay, survey, and manifest explicit without claiming the dedicated fixture pair as returned
- cross-helper truthfulness keeps the landed `string_helpers` packet explicit while keeping the `cmdline`, `argv_split`, and `rbtree` packets distinct instead of collapsing them into one shared reminder claim
- build-graph truthfulness keeps readable non-owner evidence such as `lib/rbtree.zig`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` separate from this helper-local packet; in this runtime `zigux/tests/phase7_build.zig` was confirmed through public blob/raw fallback after the authenticated contents bridge returned `404`, `lib/rbtree.zig` came back through authenticated rereads as readable roadmap-path companion evidence, and the dedicated fixture pair still does not directly materialize on current `master`

## Non-goals

This helper-local Phase 7 rbtree slice does not yet claim:

- helper-local ownership of the readable roadmap-path companion at `lib/rbtree.zig`
- the dedicated fixture pair at `zigux/tests/fixtures/phase7_rbtree.json` and `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
- dedicated Makefile wrapper routes for `phase7-rbtree-test`, `phase7-rbtree-survey`, `phase7-test`, or aggregate `phase7`
- shared workflow steps for Phase 7 runtime-helper gates
- ownership of the shared validators at `scripts/zigux/check-phase7-build-wiring.py` and `scripts/zigux/validate-phase7.py`
- ownership of the shared build file at `zigux/tests/phase7_build.zig`

## Next Bounded Step

Keep same-lane follow-through inside this slice-backed direct-helper packet by rereading `zigux/tests/phase7_rbtree_survey.zig` and `zigux/tests/phase7_rbtree_manifest.json` against this note so the already-landed public-fallback provenance for shared non-owner build evidence stays explicit and the returned `lib/rbtree.zig` roadmap-path companion stays framed as readable shared runtime-family evidence rather than proof that helper-local ownership has moved out of the tool-root packet. Do not widen into dedicated make-wrapper, workflow-recovery, or fixture-recovery lanes unless one more concrete still-missing companion surface such as `zigux/tests/fixtures/phase7_rbtree.json` or `zigux/tests/fixtures/phase7_rbtree_c_harness.c` rematerializes on current `master`.
