# Phase 1 Closure

This note restores the missing Lane 15 closure record in a current-master-safe form.

## Status

- `PHASE1_STATUS=parked`
- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`
- `PHASE1_HELPER_COUNT=13`
- manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`
- current authority: the committed helper manifest, this closure note, the narrow closure validator, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche, while the route-summary checker stays an adjacent workflow and Makefile guard.

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
- `scripts/zigux/check-phase1-bench.py`
- `scripts/zigux/check-phase1-shared-reminder-packet.py`
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/README.md`
- `zigux/tests/build.zig`
- `zigux/tests/phase1_host_tools_smoke.zig`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/fixtures/phase1_helper_manifest.json`

- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/check-phase1-shared-reminder-packet.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,.github/workflows/zigux-bootstrap.yml,zigux/tests/fixtures/phase1_helper_manifest.json`

## Broader Closure Companions

The older validator-first and replay-side closure companions remain broader closure-stack references rather than active current reminder-packet proof.

- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/check-phase1-parity.py`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/fixtures/phase1_bench_expectations.json`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`

- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`

Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, Phase 12, and Phase 14. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.

This note keeps those broader companions parked as historical closure-stack vocabulary until direct current-master rereads restore them. The already-landed shared tests-root smoke route plus the shipped bench checker and shared reminder checker remain the narrower packet that current `master` can support directly.

## Closure Validation

The current shared tests-root closure route is narrow on purpose:

- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`

That route keeps a minimal shared import-and-wire smoke check alive for the current helper packet while the dedicated closure validator keeps the restored closure note aligned with the committed helper manifest and the shipped reminder packet on current `master`.

The current bootstrap workflow also keeps the adjacent Phase 1 route-summary guard wired beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, and closure-validator checks, replays the route-summary, direct-owner, string-review, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`, and currently keeps the bench checker at self-test coverage only.

Even with that self-test-only posture, the surviving `find_bit` bench guard is still explicit on current `master`: `scripts/zigux/check-phase1-bench.py` hard-codes `PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000` and `PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000`, and it still requires the paired exact checksum keys `PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM` and `PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM` whenever the broader expectations packet returns.

Current `master` also ships `scripts/zigux/check-phase1-find-bit-bench-anchors.py` as a helper-local current-head guard: it exact-checks the inclusive-boundary, past-`nbits` no-read, `clump8` past-end no-read, and tail-clamped `findLastBit()` anchors directly in `tools/lib/find_bit.zig` while the broader expectations packet remains absent.

- `PHASE1_FIND_BIT_BENCH_GUARD=scripts/zigux/check-phase1-bench.py still hard-codes PHASE1_BENCH_FIND_NEXT_BIT_ITERATIONS=20000 and PHASE1_BENCH_FIND_BIT_EDGE_ITERATIONS=20000 and still requires PHASE1_BENCH_FIND_NEXT_BIT_CHECKSUM and PHASE1_BENCH_FIND_BIT_EDGE_CHECKSUM when the broader expectations packet returns`
- `PHASE1_FIND_BIT_BENCH_ANCHOR_GUARD=python3 scripts/zigux/check-phase1-find-bit-bench-anchors.py exact-checks inclusive-boundary, past-nbits no-read, clump8 past-end no-read, and findLastBit tail-clamp anchors directly in tools/lib/find_bit.zig`
- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`
- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`
- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`

## Next Step

The next bounded same-lane follow-through is to sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific `next_safe_step_note` entries in the committed manifest, rather than widening back into the older validator-first or replay-side closure stack.

A current helper-family tie-breaker inside that packet is the `bitmap` direct-anchor route: keep `tools/lib/bitmap.zig` parked unless a fresh reread finds new direct-anchor drift inside the manifest-backed fill-tail clamp, copy-alias, cross-word `scnprintf()`, exact-word-boundary equality fast-path masking, empty-buffer, allocator-reset, zero-bit logical short-circuit, Linux-style alias mirror, caller-window or multiword-tail `xorBits()`/`orBits()` clamp witnesses, or weighted tail-count clamp, or drift in the already-committed bitmap replay fields summarized by the manifest; do not reopen older closure-side or validator-route cue names by default. Current `master` still spells those bitmap-local anchors in `tools/lib/bitmap.zig`, the committed helper manifest, and `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, and the helper-local zero-bit logical test body no longer carries the one-argument `std.testing.expectEqual(...)` compile break that had briefly reopened this packet, so leave the helper parked unless one of those direct anchors or committed replay fields drifts.

A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word, tail-word, or single-word tail inclusive-boundary anchors, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped or tail-inclusive-boundary replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface together with `Documentation/zigux/phase1-host-helper-lane-sequencing.md` keep that helper-local progress review-visible beside the narrower closure validator. That direct packet now also includes the explicit `clump8 past-end scans return without reading bitmap words` no-read anchor, so the byte-clump coverage is not limited to in-range or zero-bit windows. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit`, names the underscore and Linux-style alias anchors `including andnot`, and keeps the dedicated `single-word tail windows keep the last in-range next matches reachable from an inclusive start` proof alongside the head-word and tail-word boundary packet, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts.

A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the dedicated manifest-backed `cached_root_alias_anchor`, the cached-root insert-miss, leftmost-sync, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` still keeps both Linux-style alias proofs named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step.

A third current helper-family tie-breaker inside that packet is the `string` direct-anchor route: keep `tools/lib/string.zig` parked unless a fresh reread finds drift in the helper-local `strscpy()` or `strscpyPad()` copy-and-pad anchors, memparse safety anchors, matched-prefix-length or suffix-boundary anchors, sysfs newline-aware equality or lookup-order anchors through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, C-string list lookup anchors through `matchString()` and `match_string()`, lexical-compare and search-or-length boundary anchors through `strcmp()`, `strlen()`, `strnlen()`, `strchr()`, `strrchr()`, `strchrNul()`, and `strchrnul()`, counted-search anchors through `strpbrk()`, `strcspn()`, `strnchr()`, `strnchrNul()` or `strnchrnul()`, and `strspn()`, embedded-NUL trim preservation, or moving-earliest-dirty-byte `memchrInv()` coverage, or unless committed `replaceChar` parity bytes or current string fixture keys drift; do not reopen missing closure-side validator names by default. Current `master` still keeps that broader string review packet explicit in `tools/lib/string.zig`, the committed manifest, `scripts/zigux/check-phase1-string-review-packet.py`, and `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, so leave string parked unless those direct string review surfaces drift, committed `replaceChar` parity bytes drift, or dedicated shared string fixture keys land.

- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`
- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`