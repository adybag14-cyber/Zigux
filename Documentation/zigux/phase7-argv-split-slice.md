# Phase 7 Argv Split Slice

This document tracks the bounded Phase 7 runtime leaf-helper slice for Zigux around `lib/argv_split.c`.

## Status

- `PHASE7_STATUS=helper_local_test_packet_landed`
- `PHASE7_SLICE=argv-split-runtime-leaf`
- `PHASE7_LANE_KEY=P7-L09`
- lane-key note: `P7-L09` keeps the dedicated argv-split packet separate from the broader Phase 7 shared-control lanes; shared docs-root, validator, Makefile, workflow, and build-route reminders stay with those separate follow-ons
- scope: keep the Phase 7 argv-split lane limited to the current helper-local slice anchor, dedicated replay, dedicated fixture vectors, and the no-standalone-argv-sample boundary
- lane state: current `master` directly carries `Documentation/zigux/phase7-argv-split-slice.md`, `lib/argv_split.zig`, `zigux/tests/phase7_argv_split.zig`, `zigux/tests/phase7_argv_split_survey.zig`, `zigux/tests/phase7_argv_split_manifest.json`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `scripts/zigux/check-phase7-argv-split-packet.py`, and `samples/zigux/README.md`. Treat those surfaces as the current helper-local packet for this slice and keep same-lane follow-through inside that returned fixture-backed packet.

## Why This Slice Exists

Phase 7 is where Zigux starts carrying reusable runtime helper families in product-facing locations.

The current `argv_split` state on `master` now carries a bounded helper-local packet around argument counting, copied-storage tokenization, sentinel-terminated argv views, empty-input sentinel reuse, teardown ownership, allocator-failure cleanup, overflow rejection, and fixture-backed packet reviewability while keeping broader shared-control follow-ons outside this same helper family.

This is intentionally not a Phase 5 `samples/zigux/` delivery lane. Current `master` still ships no standalone `samples/zigux/*argv*` reference sample, so the dedicated boundary reminder should keep that separation explicit while the Phase 7 argv-split helper stays reviewable through helper-local surfaces only.

## Gates

1. keep the helper-local implementation explicit
- `lib/argv_split.zig`

2. keep the current helper-local review packet explicit
- `Documentation/zigux/phase7-argv-split-slice.md`
- `zigux/tests/phase7_argv_split.zig`
- `zigux/tests/phase7_argv_split_survey.zig`
- `zigux/tests/phase7_argv_split_manifest.json`
- `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
- `scripts/zigux/check-phase7-argv-split-packet.py`

3. keep the no-standalone-argv-sample boundary explicit
- `samples/zigux/README.md`

4. keep adjacent Phase 7 families and shared-control surfaces out of this packet unless a fresh reread says otherwise
- do not count `Documentation/zigux/phase7-string-helpers-slice.md`
- do not count `Documentation/zigux/phase7-cmdline-slice.md`
- do not count `Documentation/zigux/phase7-rbtree-slice.md`
- do not count shared validator, Makefile, workflow, or build-route reminders here even when they are readable as non-owner evidence

## Current Parity Surface

The current helper-local packet on `master` covers:

- `countArgc()`
- `argvSplit()`
- `argvSplitWithArgc()`
- `argvFree()`
- `ArgvSplitResult.deinit()`
- `ArgvSplitResult.cArgv()`

The current helper-local replay keeps these proofs explicit:

- exact whitespace-delimited token counting through the first exported C-string boundary
- copied-storage tokenization that zeroes whitespace separators in the owned storage copy instead of mutating caller input
- blank-input handling that keeps empty storage and sentinel argv views explicit
- first-NUL truncation that keeps ignored tails outside the owned storage copy and sentinel-terminated argv view
- caller-owned teardown, idempotent release behavior, and argc-preservation on allocation failure
- dedicated helper-local replay, fixture-vector, survey, and checker coverage rooted at `zigux/tests/phase7_argv_split.zig`, `zigux/tests/fixtures/phase7_argv_split_vectors.zig`, `zigux/tests/phase7_argv_split_survey.zig`, and `scripts/zigux/check-phase7-argv-split-packet.py`

The current helper-local replay also keeps these ownership and boundary rules explicit:

- `argvSplit()` duplicates the caller input before tokenizing so returned tokens stay inside helper-owned storage
- `countArgc()`, `cStringPrefix()`, `nextArgSpan()`, and `nextSplitArgSpan()` keep token counting and separator zeroing bounded to the exported C-string prefix
- blank-input results reuse exported empty storage and argv sentinel views without widening beyond the returned packet
- whitespace-before-first-NUL input still reuses the canonical blank storage and exported argv sentinels without allocator space
- `deinit()`, `argvFree()`, allocator-failure cleanup, and overflow rejection keep release ownership explicit without widening beyond the returned argv packet
- the no-standalone-argv sample boundary stays helper-local only while `samples/zigux/README.md` keeps `*argv*` listed among the no-extra-sample reminders

## Non-goals

This helper-local Phase 7 argv-split slice does not yet claim:

- any standalone `samples/zigux/*argv*` sample-root delivery
- the separate `cmdline`, `string_helpers`, or `rbtree` helper families
- shared validator, Makefile, workflow, or tests-root reminder ownership
- widened shell-style quoting or escape semantics beyond the current whitespace-delimited helper packet

## Next Bounded Step

Keep same-lane follow-through limited to the returned fixture-backed helper-local survey-manifest-checker truthfulness packet or one bounded vector-backed replay proof.
Route shared validator, Makefile, workflow, tests-root, and broader docs-root follow-through to the separate Phase 7 shared-control lanes.
