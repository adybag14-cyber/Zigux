# Phase 7 Rbtree Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/rbtree.c`.

## Status

- `PHASE7_STATUS=helper_local_slice_note_test_survey_manifest_checker_fixture_harness_anchor`
- `PHASE7_SLICE=rbtree-runtime-leaf`
- `PHASE7_LANE_KEY=P7-L13`
- lane-key note: `P7-L13` keeps the dedicated rbtree packet separate from the broader Phase 7 shared-control lanes; shared docs-root, validator, workflow, and aggregate route reminders stay with those separate follow-ons
- scope: keep the Phase 7 rbtree lane limited to the returned runtime-root helper, the readable legacy tool-root companion, the dedicated slice note, the direct-anchor note, the dedicated replay, the dedicated survey, the dedicated manifest, the dedicated parity checker, the returned JSON fixture, and the returned C harness while the dedicated `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers now stay explicit as returned shared-control evidence and broader shared-control follow-ons remain separate gaps
- lane state: current `master` directly carries `Documentation/zigux/phase7-rbtree-slice.md`, `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`, `scripts/zigux/check-phase7-rbtree-parity.py`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, and `zigux/tests/fixtures/phase7_rbtree_c_harness.c`. Treat those surfaces as the current helper-local packet for this slice. Keep `tools/lib/rbtree.zig` explicit as a readable legacy runtime-family companion and keep `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` explicit as directly readable shared-control build evidence rather than helper-local ownership.

## Why This Slice Exists

Phase 7 is where Zigux starts carrying reusable runtime helper families in product-facing locations.

The current `rbtree` state on `master` now carries a bounded helper-local packet around ordered insertion, ordered and reverse traversal, duplicate-range matching, cached-leftmost promotion, postorder null-stop handling for detached nodes, erase-init ownership boundaries, and fixture-backed checker reviewability while keeping helper-local ownership on the runtime-root implementation and explicit parity companions in both JSON and C-harness form.

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
- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`

3. keep the readable legacy companion and returned parity companions explicit
- `tools/lib/rbtree.zig`
- `zigux/tests/fixtures/phase7_rbtree.json`
- `zigux/tests/fixtures/phase7_rbtree_c_harness.c`

4. keep adjacent Phase 7 families and shared-control surfaces out of this packet unless a fresh reread says otherwise
- do not count `Documentation/zigux/phase7-string-helpers-slice.md`
- do not count `Documentation/zigux/phase7-cmdline-slice.md`
- do not count `Documentation/zigux/phase7-argv-split-slice.md`
- keep `tools/lib/rbtree.zig`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` framed as readable legacy or shared non-owner evidence rather than helper-local ownership

## Current Parity Surface

The current helper-local packet on `master` covers:

- `Node`, `Root`, and `RootCached`
- ordered insertion through `add()`, `findAdd()`, and cached aliases
- ordered and reverse traversal through `first()`, `next()`, `last()`, `prev()`, and duplicate-match helpers
- postorder traversal and detached-node null-stop handling through `firstPostorder()` and `nextPostorder()`
- cached-leftmost insertion, cached replacement, cached non-leftmost erase, singleton cached erase, and cached erase-init helpers
- plain erase-init reset and reseed boundaries after root removal
- dedicated replay, survey, manifest, direct-anchor note, slice note, parity checker, JSON fixture, and C harness reviewability

The current helper-local replay keeps these proofs explicit:

- ordered traversal stays reviewable through the dedicated replay rooted at `zigux/tests/phase7_rbtree.zig`
- reverse traversal aliases and detached-node null-stop handling stay reviewable through the dedicated replay rooted at `zigux/tests/phase7_rbtree.zig`
- postorder aliases stay reviewable through `firstPostorder()`, `nextPostorder()`, and the dedicated replay's detached-node guards
- duplicate-range matching stays reviewable through `findFirst()`, `nextMatch()`, and `matchIterator()`
- cached-leftmost promotion, non-leftmost cached erase, singleton cached erase, and plain erase-init reseed ownership boundaries stay reviewable through the dedicated replay, the parity checker, the returned JSON fixture, and the returned C harness
- the readable legacy companion at `tools/lib/rbtree.zig` now stays reviewable only while its reverse-traversal alias, postorder alias, and plain erase-init markers remain readable beside the direct helper packet
- same-lane truthfulness stays rooted at the returned runtime-root helper, the returned notes, the returned survey, the returned manifest, the returned parity checker, the returned JSON fixture, and the returned C harness

The current helper-local replay also keeps these ownership and boundary rules explicit:

- path truthfulness keeps the returned helper rooted at `lib/rbtree.zig` while the readable legacy companion `tools/lib/rbtree.zig` stays explicit as shared runtime-family evidence rather than helper-local ownership
- same-lane truthfulness keeps the returned slice note, direct-anchor note, parity checker, replay, survey, manifest, JSON fixture, and C harness explicit
- build-graph truthfulness keeps readable non-owner evidence such as `tools/lib/rbtree.zig`, `scripts/zigux/check-phase7-build-wiring.py`, `scripts/zigux/validate-phase7.py`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` separate from this helper-local packet
- public-fallback provenance stays explicit through the now-empty `public_fallback_non_owner_paths` field in `zigux/tests/phase7_rbtree_manifest.json`, because `zigux/tests/phase7_build.zig` and the other listed legacy or shared non-owner surfaces all rematerialized through authenticated rereads in this slot

## Non-goals

This helper-local Phase 7 rbtree slice does not yet claim:

- helper-local ownership of the readable legacy companion at `tools/lib/rbtree.zig`
- broader shared-control routes for `phase7-test` or aggregate `phase7`
- shared workflow steps for Phase 7 runtime-helper gates
- ownership of the shared validators at `scripts/zigux/check-phase7-build-wiring.py` and `scripts/zigux/validate-phase7.py`
- ownership of the shared build file at `zigux/tests/phase7_build.zig`

## Next Bounded Step

Keep same-lane follow-through inside this slice-backed direct-helper packet by leaving `zigux/tests/fixtures/phase7_rbtree.json` and `zigux/tests/fixtures/phase7_rbtree_c_harness.c` reviewable as returned parity evidence, including the non-leftmost cached erase, singleton cached erase, and plain erase-init reseed cases, while keeping the readable legacy `tools/lib/rbtree.zig` companion aligned on the reverse-traversal alias, postorder alias, and plain erase-init markers and keeping the returned `phase7-rbtree-test:` and `phase7-rbtree-survey:` wrappers aligned with `zigux/tests/phase7_build.zig`. Do not widen into workflow-recovery or broader shared-control lanes unless `phase7-test:` or aggregate `phase7:` surfaces actually return.
