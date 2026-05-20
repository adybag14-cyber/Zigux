# Phase 1 Closure

This note restores the missing Lane 15 closure record in a current-master-safe form.

## Status

- `PHASE1_STATUS=parked`
- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`
- `PHASE1_HELPER_COUNT=13`
- manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`
- current authority: the committed helper manifest, this closure note, the narrow closure validator, the shipped bench checker, the shipped shared reminder checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche, while the route-summary checker stays an adjacent workflow and Makefile guard.

The bounded Phase 1 helper tranche is still the same thirteen helper ports named in the committed manifest, but the broader closure-side validator and replay stack is not fully materialized on current `master`.

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

## Current Repo-Reality Gaps

Current `master` still does not directly materialize the older validator-first and replay-side closure companions that earlier reminder surfaces treated as part of the broader closure stack.

- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/check-phase1-parity.py`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/fixtures/phase1_bench_expectations.json`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`

- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`

Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 4, Phase 6, Phase 8, Phase 10, and Phase 12. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.

Restoring this note does not claim that those broader replay routes are back. It restores the Lane 15 closure anchor itself, records the exact repo-reality gap that still separates the closed helper tranche from the older full closure stack, and keeps the already-landed shared tests-root smoke route plus the shipped bench checker and shared reminder checker visible as part of the narrower packet that current `master` can honestly support, while the route-summary checker stays an adjacent workflow and Makefile guard.

## Closure Validation

The current shared tests-root closure route is narrow on purpose:

- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`

That route keeps a minimal shared import-and-wire smoke check alive for the current helper packet while the dedicated closure validator keeps the restored closure note aligned with the committed helper manifest and the shipped reminder packet on current `master`.

The current bootstrap workflow also replays the adjacent Phase 1 route-summary guard beside that same live reminder packet: `.github/workflows/zigux-bootstrap.yml` self-tests and replays the directly readable Phase 1 direct-owner, string-review, route-summary, bench, shared-reminder, closure-validator, and shared tests-root smoke steps on current `master`.

- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`
- `PHASE1_ROUTE_SUMMARY_GUARD=python3 scripts/zigux/check-phase1-route-summary-counts.py`
- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`

## Next Step

The next bounded same-lane follow-through is to sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific `next_safe_step_note` entries in the committed manifest, rather than widening back into the older validator-first or replay-side closure stack.

A current helper-family tie-breaker inside that packet is the `find_bit` direct-anchor route: keep `tools/lib/find_bit.zig` parked unless a fresh reread finds drift in the manifest-backed same-word start-mask, head-word or tail-word inclusive-boundary, zero-window, zero-sized short-circuit, past-`nbits`, `clump8`, `getValue8()`, `findLastBit()`, underscore-alias, Linux-style alias, or tail-word skip anchors, or drift in the already-committed tail-clamped replay fields, and do not reopen older validator-first cues or neighboring helper families by default. Current `master` still keeps the helper-local byte-clump, backward-scan, alias, and shipped `find_*andnot*` entry-point packet directly in `tools/lib/find_bit.zig`, and the manifest-backed review surface still records those anchors as shipped helper-local coverage even though the narrower `next_safe_step_note` keeps them parked unless the direct-anchor or committed replay packet itself drifts. Current `master` also now spells the lead direct anchor as `find first and next set bits across words, with andnot gaps explicit` and names the underscore and Linux-style alias anchors `including andnot`; the manifest and the current closure validator keep that helper-local progress review-visible, so leave `find_bit` parked unless one of those direct anchors or committed replay fields drifts.

A second current helper-family tie-breaker inside that packet is the `rbtree` direct-anchor route: keep `tools/lib/rbtree.zig` parked unless a fresh reread finds drift in the helper-local ordered Linux-style alias proof, the dedicated manifest-backed `low_level_alias_anchor`, the cached-root insert-miss, leftmost-sync, cached-root alias, singleton-erase, replacement, detach, or reseed anchors, or drift in the already-committed duplicate-search replay fields or exact `cached_leftmost_return_serials` witness. Current `master` still keeps that low-level Linux-style alias proof named explicitly in `zigux/tests/fixtures/phase1_helper_manifest.json`, while the shared host-tools smoke route and committed Phase 1 fixture already recheck duplicate-range iteration plus the exact cached-leftmost-return packet, so leave rbtree parked unless one of those helper-local anchors or committed replay fields drifts and do not batch a second cached-root widening into the same reopen step.

A third current helper-family tie-breaker inside that packet is the `string` direct-anchor route: keep `tools/lib/string.zig` parked unless a fresh reread finds drift in the helper-local `strscpy()` or `strscpyPad()` copy-and-pad anchors, memparse safety, matched-prefix or suffix boundaries, sysfs newline-aware equality or lookup order through `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`, `matchString()` or `match_string()` C-string lookup order, counted-search `strnchr()`, accepted-prefix `strspn()`, or `strnchrNul()` boundary behavior, embedded-NUL trim preservation, or moving earliest-dirty-byte `memchrInv()` coverage, or drift in the already-committed `replaceChar` parity fields and current string fixture keys. Current `master` still keeps the helper-local sysfs review anchors explicit in `tools/lib/string.zig`, the committed manifest, and `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, so leave string parked unless those direct surfaces drift or dedicated shared sysfs fixture keys land.

- `PHASE1_STRING_SYSFS_REVIEW=helper-local string sysfs newline-aware equality and lookup-order anchors stay explicit through the direct string tests and the Phase 1 helper manifest because the shared Phase 1 replay still carries no dedicated sysfs fixture keys`
- `PHASE1_NEXT_SAFE_STEP=sync one shared reminder surface or one helper-family tie-breaker against the restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific next_safe_step_note entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.`
