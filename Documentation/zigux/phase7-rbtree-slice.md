# Phase 7 Rbtree Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/rbtree.c`.

## Status

* `PHASE7_STATUS=parked`
* `PHASE7_SLICE=rbtree-runtime-leaf`
* `PHASE7_LANE_KEY=P7-L13`
* scope: first low-risk reviewability, parity, and survey surfaces only
* lane state: helper, dedicated survey, committed manifest packet, committed parity packet, dedicated parity checker, shared validator, shared build-wiring checker, and parked make-wrapper alignment note landed; keep this helper slice parked unless a fresh ownership, parity, or review-surface gap appears inside the existing helper, shared-test, survey, manifest, parity-checker, or shared review packet
* current verification: a bounded 2026-05-13 repo-first inspection confirmed `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, and `scripts/zigux/check-phase7-rbtree-parity.py` remain visible on current `master`, but the broader shared `zigux/tests/phase7_build.zig` replay is not a direct current-master green claim because that build file still imports the missing sibling string-helpers pair `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`
* product boundary:
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`
  * `Documentation/zigux/phase7-helper-lane-sequencing.md`
  * `Documentation/zigux/review-checklist.md`
  * `samples/zigux/README.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/validate-phase7.py`
  * `scripts/zigux/check-phase7-make-wrapper.py`
  * `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
  * `scripts/zigux/check-phase7-rbtree-parity.py`
  * `scripts/zigux/check-phase7-build-wiring.py`
  * `lib/rbtree.zig`
  * `zigux/tests/README.md`
  * `zigux/tests/phase7_rbtree.zig`
  * `zigux/tests/phase7_rbtree_survey.zig`
  * `zigux/tests/phase7_rbtree_manifest.json`
  * `zigux/tests/fixtures/phase7_rbtree.json`
  * `zigux/tests/fixtures/phase7_rbtree_c_harness.c`
  * `zigux/tests/phase7_build.zig`
  * `zigux/Makefile`
  * `.github/workflows/zigux-bootstrap.yml`

## Why this slice exists

Phase 7 explicitly calls out `lib/rbtree.c` as one of the first reusable in-kernel leaf libraries that should move into the Zigux product path.

This current slice keeps the work bounded to the parked reviewability packet that:

* stays inside the helper-local parity, ownership, and survey surface instead of widening into subsystem-owned tree policy
* keeps duplicate-key range traversal, detached-node handoff, linked-node teardown, cached-leftmost state, eraseInit reset, and postorder coverage reviewable beside the committed parity packet and the shared Phase 7 build and validator routes
* records that this slice does not carry an open parity-fixture follow-up on current `master`

Current repo reality is narrower only at the shared bundle level: on `2026-05-13`, direct current `master` reads returned this slice note together with `lib/rbtree.zig`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, and `scripts/zigux/check-phase7-rbtree-parity.py`.
That means the rbtree-local helper packet is still landed, while the broader shared `phase7_build.zig` replay remains parked because the sibling string-helpers helper-plus-test pair is still missing from live `master`.

This is intentionally not a Phase 5 `samples/zigux/` reference-sample lane.
Current `master` still ships no `samples/zigux/*rbtree*` Phase 5 reference sample; keep `rbtree` reviewability under this slice, `Documentation/zigux/README.md`, `Documentation/zigux/phase7-make-wrapper-selftest-alignment.md`, `Documentation/zigux/phase7-helper-lane-sequencing.md`, `lib/rbtree.zig`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase7.py`, `scripts/zigux/check-phase7-make-wrapper.py`, `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`, `scripts/zigux/check-phase7-rbtree-parity.py`, `scripts/zigux/check-phase7-build-wiring.py`, `zigux/tests/README.md`, `zigux/tests/phase7_rbtree.zig`, `zigux/tests/phase7_rbtree_survey.zig`, `zigux/tests/phase7_rbtree_manifest.json`, `zigux/tests/fixtures/phase7_rbtree.json`, `zigux/tests/fixtures/phase7_rbtree_c_harness.c`, `zigux/tests/phase7_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` instead of counting it as a fifth Phase 5 sample.

## Gates

1. keep the dedicated rbtree survey gate reviewable

* `zigux/tests/phase7_rbtree_survey.zig`

2. keep the dedicated parity checker explicit

* `python3 scripts/zigux/check-phase7-rbtree-parity.py`

3. keep the committed manifest and parity packet explicit

* `zigux/tests/phase7_rbtree_manifest.json`
* `zigux/tests/fixtures/phase7_rbtree.json`
* `zigux/tests/fixtures/phase7_rbtree_c_harness.c`

4. keep the shared validator-first packet explicit

* `python3 scripts/zigux/validate-phase7.py`
* `python3 scripts/zigux/check-phase7-make-wrapper.py`
* `python3 scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
* `python3 scripts/zigux/check-phase7-build-wiring.py`
* `make -C zigux phase7-validate`

5. keep the shared Phase 7 helper gate explicit as a parked cross-packet target

The commands below still describe the intended shared replay surface, but they are not a current rbtree-local green claim while the missing sibling imports above remain absent from live `master`.

* `zig build test --build-file zigux/tests/phase7_build.zig --summary all`
* `make -C zigux phase7`

## Current parity surface

The current landed slice covers the bounded `rbtree` review packet under `lib/rbtree.zig`, the dedicated `zigux/tests/phase7_rbtree.zig` helper replay, the dedicated `zigux/tests/phase7_rbtree_survey.zig` survey gate, the committed `zigux/tests/phase7_rbtree_manifest.json` review record, and the committed parity packet under `zigux/tests/fixtures/phase7_rbtree.json` plus `zigux/tests/fixtures/phase7_rbtree_c_harness.c`.

Current `master` still does not expose the full shared Phase 7 helper bundle:

* `lib/string_helpers.zig` currently fails direct current-path reads
* `zigux/tests/phase7_string_helpers.zig` currently fails direct current-path reads

That means the dedicated rbtree helper replay, survey, manifest, and parity packet remain reviewable inside this slice, while the broader shared `phase7_build.zig` route is still a parked cross-packet target rather than a direct rbtree-local green claim.
Shared helper-lane ownership now lives in `Documentation/zigux/phase7-helper-lane-sequencing.md`; keep rbtree-local follow-through under `P7-L13` instead of reusing the shared sequencing lane.

The current tests keep these packet edges explicit:

* `python3 scripts/zigux/check-phase7-rbtree-parity.py` remains the dedicated parity readback route
* `zig build test --build-file zigux/tests/phase7_build.zig --summary all` remains the parked cross-packet replay route for this helper packet; it is not a direct rbtree-local green claim while current `master` still lacks `lib/string_helpers.zig` and `zigux/tests/phase7_string_helpers.zig`
* ordered and duplicate-key traversal stay reviewable through the committed parity packet and the dedicated duplicate-range shared test coverage
* detached-node ownership stays explicit through the clearNode and eraseInit reset paths instead of being left implicit after removal
* linked-node teardown keeps detached ownership state, neighbour relinking, and leftmost continuity reviewable inside the shared Phase 7 packet
* cached-leftmost handoff and final singleton `eraseCached()` state stay explicit in the shared tests instead of being hidden behind the helper implementation alone
* postorder traversal and replacement behavior remain tied back to the committed parity packet rather than drifting into ad hoc helper checks
* this slice does not carry an open parity-fixture follow-up
* the dedicated parity checker, the committed parity packet, the shared validator-first packet, the shared build-wiring checker, the make-wrapper alignment note, the shared helper-lane owner map, and the no-sample boundary note stay reviewable together instead of drifting into separate reminder surfaces

## Non-goals

This slice still does not yet claim:

* augmented-tree, cached-root, or subsystem-owned follow-on helpers beyond the bounded current packet
* a new `samples/zigux/` rbtree reference sample
* widening the slice into broader container or ownership policy beyond the committed parity packet

## Next bounded step

Keep this slice parked unless fresh repo inspection finds one concrete `rbtree` ownership, parity, survey, manifest, fixture, or shared reminder drift inside the current helper packet.
If the family reopens, prefer one tiny same-packet follow-through around the already-landed parity checker, committed parity packet, or shared ownership-review wording before widening into broader tree variants or another lane.

## Footer
