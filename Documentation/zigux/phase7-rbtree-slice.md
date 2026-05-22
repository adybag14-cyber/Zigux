# Phase 7 Rbtree Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/rbtree.c`.

## Status

- `PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_anchor`
- `PHASE7_SLICE=rbtree-runtime-leaf`
- `PHASE7_LANE_KEY=P7-L13`
- lane-key note: `P7-L13` keeps the dedicated rbtree packet separate from the broader Phase 7 shared-control lanes; shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate follow-ons
- scope: keep the Phase 7 rbtree lane limited to the returned runtime-root helper, the readable legacy tool-root companion, the dedicated slice note, the direct-anchor note, the dedicated replay, the dedicated survey, the dedicated manifest, and the dedicated parity checker
- lane state: current `master` directly carries `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `scripts/zigux/check-phase7-rbtree-parity.py`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, and `zigux/tests/phase7_rbtree_manifest.json`. Treat those surfaces as the current helper-local packet for this slice. Keep `tools/lib/rbtree.zig` explicit as a readable legacy runtime-family companion and keep `zigux/tests/fixtures/phase7_rbtree.json` plus `zigux/tests/fixtures/phase7_rbtree_c_harness.c` explicit as still-missing same-family follow-ons unless a fresh reread proves they have rematerialized on current `master`. Keep `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` explicit as directly readable shared-control build evidence rather than helper-local ownership; in this runtime `zigux/tests/phase7_build.zig` needed public blob/raw fallback after the authenticated contents bridge returned `404`, so keep that one path framed as returned shared non-owner evidence without overstating authenticated whole-file coverage.

## Why This Slice Exists

Phase 7 is where Zigux starts carrying reusable runtime helper families in product-facing locations.

The current `rbtree` state on `master` now carries a bounded helper-local packet around ordered insertion, ordered and reverse traversal, duplicate-range matching, cached-leftmost promotion, postorder null-stop handling for detached nodes, erase-init ownership boundaries, and checker-backed reviewability while keeping helper-local ownership on the runtime-root implementation and the dedicated fixture pair outside this same helper family.

This slice must stay truthful about the current direct helper path. The helper-local implementation now remains rooted at `lib/rbtree.zig`, while the older tool-root `tools/lib/rbtree.zig` stays readable as legacy runtime-family companion evidence rather than proof that helper-local ownership still lives there.

## Gates

1. keep the returned helper-local implementation explicit
- `lib/rbtree.zig`

2. keep the returned helper-local review packet explicit
- `Documentation/zigux/phase7-rbtree-slice.md`
- `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`
- `scripts/zigux/check-phase7-rbtree-parity.py`
- `zigux/tests/phase7_rbtree.zig`
- `zigux/tests/phase7_rbtree_survey.zig`
- `zigux/tests/phase7_rbtree_manifest.json`

3. keep the readable legacy companion explicit and keep the dedicated fixture follow-ons explicit as still missing until they really materialize
- `tools/lib/rbtree.zig`
- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`

4. keep adjacent Phase 7 families and shared-control surfaces out of this packet unless a fresh reread says otherwise
- do not count `Documentation/zigux/phase7-string-helpers-slice.md`
- do not count `Documentation/zigux/phase7-cmdline-slice.md`
- do not count `Documentation/zigux/phase7-argv-split-slice.md`
- keep `tools/lib/rbtree.zig`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` framed as readable legacy or shared non-owner evidence rather than helper-local ownership; in this runtime `zigux/tests/phase7_build.zig` needed public blob/raw fallback after the authenticated contents bridge returned `404`, while the other listed non-owner surfaces still materialized through authenticated rereads

## Current Parity Surface

The current helper-local packet on `master` covers:

- `Node`, `Root`, and `RootCached`
- ordered insertion through `add()`, `findAdd()`, and cached aliases
- ordered and reverse traversal through `first()`, `next()`, `last()`, `prev()`, and duplicate-match helpers
- postorder traversal and detached-node null-stop handling through `firstPostorder()` and `nextPostorder()`
- cached-leftmost insertion, cached replacement, and cached erase-init helpers
- dedicated replay, survey, manifest, direct-anchor note, slice note, and parity checker reviewability

The current helper-local replay keeps these proofs explicit:

- ordered traversal stays reviewable through the dedicated replay rooted at `zigux/tests/phase7_rbtree.zig`
- reverse traversal aliases and detached-node null-stop handling stay reviewable through the dedicated replay rooted at `zigux/tests/phase7_rbtree.zig`
- postorder aliases stay reviewable through `firstPostorder()`, `nextPostorder()`, and the dedicated replay's detached-node guards
- duplicate-range matching stays reviewable through `findFirst()`, `nextMatch()`, and `matchIterator()`
- cached-leftmost promotion and erase-init ownership boundaries stay reviewable through the dedicated replay and the parity checker
- same-lane truthfulness stays rooted at the returned runtime-root helper, the returned notes, the returned survey, the returned manifest, and the returned parity checker

The current helper-local replay also keeps these ownership and boundary rules explicit:

- path truthfulness keeps the returned helper rooted at `lib/rbtree.zig` while the readable legacy companion `tools/lib/rbtree.zig` stays explicit as shared runtime-family evidence rather than helper-local ownership
- same-lane truthfulness keeps the returned slice note, direct-anchor note, parity checker, replay, survey, and manifest explicit without claiming the dedicated fixture pair as returned
- cross-helper truthfulness keeps the landed `string_helpers` packet explicit while keeping the `cmdline`, `argv_split`, and `rbtree` packets distinct instead of collapsing them into one shared reminder claim
- build-graph truthfulness keeps readable non-owner evidence such as `tools/lib/rbtree.zig`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` separate from this helper-local packet; in this runtime `zigux/tests/phase7_build.zig` was confirmed through public blob/raw fallback after the authenticated contents bridge returned `404`, `tools/lib/rbtree.zig` came back through authenticated rereads as readable legacy companion evidence, and the dedicated fixture pair still does not directly materialize on current `master`

## Non-goals

This helper-local Phase 7 rbtree slice does not yet claim:

- helper-local ownership of the readable legacy companion at `tools/lib/rbtree.zig`
- the dedicated fixture pair at `zigux/tests/fixtures/phase7_rbtree.json` and `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
- dedicated Makefile wrapper routes for `phase7-rbtree-test`, `phase7-rbtree-survey`, `phase7-test`, or aggregate `phase7`
- shared workflow steps for Phase 7 runtime-helper gates
- ownership of the shared validators at `scripts/zigux/check-phase7-build-wiring.py` and `scripts/zigux/validate-phase7.py`
- ownership of the shared build file at `zigux/tests/phase7_build.zig`

## Next Bounded Step

Keep same-lane follow-through inside this slice-backed direct-helper packet by rereading `zigux/tests/phase7_rbtree_survey.zig` and `zigux/tests/phase7_rbtree_manifest.json` against this note so the returned `lib/rbtree.zig` helper path stays explicit, the already-landed public-fallback provenance for shared non-owner build evidence stays explicit, and `tools/lib/rbtree.zig` remains framed as readable legacy companion evidence rather than current helper-local ownership. Do not widen into dedicated make-wrapper, workflow-recovery, or fixture-recovery lanes unless one more concrete still-missing companion surface such as `zigux/tests/fixtures/phase7_rbtree.json` or `zigux/tests/fixtures/phase7_rbtree_c_harness.c` rematerializes on current `master`.