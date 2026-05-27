# Phase 1 Closure

This note restores the missing Lane 15 closure record in a current-master-safe form.

## Status

- `PHASE1_STATUS=parked`
- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`
- `PHASE1_HELPER_COUNT=13`
- manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`
- current authority: the committed helper manifest, this closure note, the narrow closure validator, the direct-anchor manifest gate, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche, while the route-summary checker stays an adjacent workflow and Makefile guard.

The bounded Phase 1 helper tranche is still the same thirteen helper ports named in the committed manifest, but the broader closure-side validator and replay stack is only partially promoted into the narrow current reminder packet on current `master`.

## Current Reminder Packet

The currently reviewable Phase 1 reminder packet is:

- `Documentation/zigux/phase1-closure.md`
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase1-string-review-packet.py`
- `scripts/zigux/check-phase1-direct-owner-markers.py`
- `scripts/zigux/check-phase1-direct-anchor-manifest-gate.py`
- `scripts/zigux/check-phase1-bench.py`
- `scripts/zigux/check-phase1-shared-reminder-packet.py`
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/README.md`
- `zigux/tests/build.zig`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_helpers_build.zig`
- `zigux/tests/phase1_host_tools_smoke.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/fixtures/phase1_helper_manifest.json`

- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-direct-anchor-manifest-gate.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_helpers_build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`

## Helper-Local Direct Anchor Reminder

For `tools/lib/bitmap.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass. The shipped direct anchors already cover whole-word range edges, raw copy and tail-clearing behavior, zero and aligned `copyAndExtend()` handling, zero-sized destination-view no-op behavior, exact-word-boundary equality masking, out-of-range tail masking for predicates and weights, caller-window `xor` and `or` clamping including multiword tails, complement tail clamping, cross-word `scnprintf()` merging, empty-bitmap caller-buffer preservation, Linux-style alias mirrors, and allocator optional-reset coverage.

This helper should only reopen if a fresh reread finds drift in those direct anchors or in the committed shared bitmap parity fields carried by `zigux/tests/phase1_helpers.zig` and `zigux/tests/fixtures/phase1_helper_manifest.json`; do not widen this helper-local reminder into older closure-side validator names by default.

For `tools/lib/find_bit.zig`, current `master` still justifies a parked helper-local follow-up rather than a reopened closure pass. The shipped direct anchors already cover same-word start-mask scans, head-word and tail-word inclusive-boundary starts, single-word tail inclusive-boundary reachability, zero-window and past-`nbits` short-circuit behavior, tail-word set, zero, and shared-bit skip behavior, byte-aligned `clump8` forward-skip behavior, final-word last-aligned-byte isolation for both `clump8` and `getValue8()`, `findLastBit()` tail clamping, and the public, Linux-style, and underscore alias surfaces including the shipped `andnot` scan entry points.

This helper should only reopen if a fresh reread finds drift in those direct anchors or in the committed shared find-bit parity fields carried by `zigux/tests/phase1_helpers.zig` and `zigux/tests/fixtures/phase1_helper_manifest.json`; do not widen this helper-local reminder into older closure-side validator names by default.

A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` keep that helper-local progress review-visible beside the narrower closure validator. That direct packet now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts.

A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` still keeps both Linux-style alias proofs named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step.

Current `master` also keeps the companion `cached_root_transition_serials` witness shared instead of helper-local only: `zigux/tests/fixtures/phase1_helpers.json` still records the exact cached-root erase, replacement, and detach transition packet, and `zigux/tests/phase1_host_tools_smoke.zig` already rechecks the same `[0, 0, 4, 2]` sequence beside the parked `cached_leftmost_return_serials` witness. Treat that transition packet as landed shared closure evidence for future cached-root rereads, while still leaving the remaining insert-miss, leftmost-sync, alias, singleton-erase, replacement, detach, and reseed anchors helper-local until another broader replay field lands.

## Broader Closure Companions

The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.

- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/check-phase1-parity.py`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/fixtures/phase1_bench_expectations.json`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`

- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`

Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.

This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them. The already-landed shared tests-root smoke route plus the shipped bench checker and shared reminder checker remain the narrower packet that current `master` can support directly.

## Closure Validation

The current shared tests-root closure route is narrow on purpose:

- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
- `zig build phase1-helpers --build-file zigux/tests/phase1_helpers_build.zig`

Those routes keep a minimal shared import-and-wire smoke check plus a focused fixture-backed helper replay anchor alive for the current helper packet while the dedicated closure validator keeps the restored closure note aligned with the committed helper manifest and the shipped reminder packet on current `master`.

- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`
- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`
- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`
- `PHASE1_BITMAP_DIRECT_REVIEW=helper-local bitmap direct anchors stay explicit through the closure packet because the shared Phase 1 replay still only owns allocator sizing, zero-filled allocation words, scnprintf output, truncation, tiny-buffer handling, and partial-window xor replay, so current master keeps fill-tail clamp, raw copy alias, tail-clearing and extension semantics, zero and aligned copyAndExtend handling, zero-sized destination-view no-op coverage, zero-bit logical short-circuit coverage, exact-word-boundary equality fast-path masking, tail-masked predicate behavior, caller-window xor and or clamping, multiword-tail xor and or clamp witnesses, weighted tail-count clamping, complement-tail masking, terminator-only and zero-length caller-view formatting, empty-bitmap caller-buffer preservation, Linux-style alias mirror coverage, and allocator optional-reset coverage review-visible at the helper surface`
- `PHASE1_BITMAP_UNIT_REVIEW=bitmap multiword-tail xorBits behavior still lets callers clamp the last word without leaking out-of-range bits into the asserted view`
- `PHASE1_BITMAP_EMPTY_UNIT_REVIEW=bitmap_scnprintf leaves a non-empty caller buffer untouched when no bits are set, matching both the direct Zig unit test and the committed parity fixture`
- `PHASE1_BITMAP_FINAL_PARTIAL_WORD_REVIEW=helper-local bitmap final partial-word proof stays explicit through the direct bitmap test anchor so setRange and clearRange clamp trailing partial-word masks to the requested tail window instead of spilling work beyond it`
- `PHASE1_BITMAP_LINUX_ALIAS_REVIEW=helper-local bitmap Linux-style alias proof stays explicit through the direct bitmap test anchor and the Phase 1 helper manifest so the Linux-style bitmap alloc/free, zero/fill, predicate, mutation, and render aliases remain behaviorally locked to the primary helper surface`
- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`
- `PHASE1_STRING_REVIEW_GUARD=python3 scripts/zigux/check-phase1-string-review-packet.py exact-checks helper-local string anchors plus the committed replaceChar and current string fixture packet across the helper, closure note, lane note, manifest, and fixture`
Current `master` now also spells the helper-local `memtostr()`, `memtostrPad()`, and `memtostr_pad()` anchors directly in the shipped manifest-backed string review packet beside the `memcpyAndPad()`, `memcpy_and_pad()`, `strtomem()`, and `strtomem_pad()` byte-copy anchors. Keep those byte-copy and pad tests helper-local review evidence rather than shared-fixture or validator-owned requirements until dedicated fixture keys land.
- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`
- `PHASE1_RBTREE_BENCH_GUARD=scripts/zigux/check-phase1-bench.py now hard-codes PHASE1_BENCH_RBTREE_ITERATIONS=4000 and exact-checks PHASE1_BENCH_RBTREE_CHECKSUM, PHASE1_BENCH_RBTREE_POSTORDER_SAFE_CHECKSUM, PHASE1_BENCH_FIND_ADD_CHECKSUM, PHASE1_BENCH_RBTREE_DUPLICATE_CHECKSUM, and PHASE1_BENCH_RBTREE_CACHED_CHECKSUM when the broader expectations packet returns`
- `PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`
- `PHASE1_FIND_BIT_REVIEW_GUARD=python3 scripts/zigux/check-phase1-find-bit-review-packet.py exact-checks helper-local find_bit anchors plus the committed tail-clamped and tail-inclusive-boundary replay packet across the helper, closure note, lane note, manifest, and fixture`
- `PHASE1_RBTREE_REVIEW_GUARD=python3 scripts/zigux/check-phase1-rbtree-review-packet.py exact-checks helper-local rbtree anchors plus the committed duplicate-search and cached-leftmost replay packet across the helper, closure note, lane note, manifest, fixture, and shared smoke route`
- `PHASE1_DIRECT_ANCHOR_MANIFEST_GATE=python3 scripts/zigux/check-phase1-direct-anchor-manifest-gate.py exact-checks the current direct-anchor helper manifest packet for bitmap, find_bit, rbtree, and string and then reruns the dedicated rbtree direct-anchor checker`
- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`