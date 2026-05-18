# Phase 1 Closure

This note restores the missing Lane 15 closure record in a current-master-safe form.

## Status

- `PHASE1_STATUS=parked`
- `PHASE1_CLOSURE_RESTORE_STATE=docs_plus_validator`
- `PHASE1_HELPER_COUNT=13`
- manifest: `zigux/tests/fixtures/phase1_helper_manifest.json`
- current authority: the committed helper manifest, this closure note, the narrow closure validator, the shipped bench checker, the live owner-map reminders, and the shared tests-root smoke route remain the trustworthy current-master sources for the closed helper tranche

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
- `scripts/zigux/validate-phase1-closure.py`
- `zigux/tests/README.md`
- `zigux/tests/build.zig`
- `zigux/tests/phase1_host_tools_smoke.zig`
- `zigux/tests/fixtures/phase1_helper_manifest.json`

- `PHASE1_CURRENT_REMINDER_PACKET=Documentation/zigux/phase1-closure.md,Documentation/zigux/phase1-host-helper-lane-sequencing.md,Documentation/zigux/README.md,Documentation/zigux/review-checklist.md,scripts/zigux/README.md,scripts/zigux/check-phase1-string-review-packet.py,scripts/zigux/check-phase1-direct-owner-markers.py,scripts/zigux/check-phase1-bench.py,scripts/zigux/validate-phase1-closure.py,zigux/tests/README.md,zigux/tests/build.zig,zigux/tests/phase1_host_tools_smoke.zig,zigux/tests/fixtures/phase1_helper_manifest.json`

## Current Repo-Reality Gaps

Current `master` still does not directly materialize the older validator-first and replay-side closure companions that earlier reminder surfaces treated as part of the broader closure stack.

- `scripts/zigux/validate-phase1.py`
- `scripts/zigux/check-phase1-parity.py`
- `zigux/tests/phase1_helpers.zig`
- `zigux/tests/phase1_bench.zig`
- `zigux/tests/fixtures/phase1_bench_expectations.json`
- `zigux/tests/fixtures/phase1_helpers_c_harness.c`

- `PHASE1_CURRENT_GAP_PACKET=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zigux/tests/phase1_helpers.zig,zigux/tests/phase1_bench.zig,zigux/tests/fixtures/phase1_bench_expectations.json,zigux/tests/fixtures/phase1_helpers_c_harness.c`

Current `master` does materialize `zigux/Makefile` again, and its live body now exposes the shipped Phase 2 toolchain and kbuild wrappers together with bounded later-lane non-Phase-1 routes across Phase 3, Phase 6, Phase 8, Phase 10, and Phase 12. It still does not expose `make -C zigux phase1-validate`, `make -C zigux phase1-test`, `make -C zigux phase1-bench`, or `make -C zigux phase1`, so treat the returned file as current repo evidence while those older Phase 1 wrapper names remain historical packet members rather than active closure proof.

Restoring this note does not claim that those broader replay routes are back. It restores the Lane 15 closure anchor itself, records the exact repo-reality gap that still separates the closed helper tranche from the older full closure stack, and keeps the already-landed shared tests-root smoke route plus the shipped bench checker visible as part of the narrower packet that current `master` can honestly support.

## Closure Validation

The current shared tests-root closure route is narrow on purpose:

- `zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`

That route keeps a minimal shared import-and-wire smoke check alive for the current helper packet while the dedicated closure validator keeps the restored closure note aligned with the committed helper manifest and the shipped reminder packet on current `master`.

- `PHASE1_CLOSURE_VALIDATOR=python3 scripts/zigux/validate-phase1-closure.py`
- `PHASE1_SHARED_TESTS_ROUTE=zig build phase1-host-tools-smoke --build-file zigux/tests/build.zig`
- `PHASE1_CLOSURE_VALIDATOR_STATE=available_current_master`

## Next Step

The next bounded same-lane follow-through is to sync one shared reminder surface or one helper-family tie-breaker against this restored closure note, the closure validator, the shared tests-root smoke route, and the helper-specific `next_safe_step_note` entries in the committed manifest rather than widening back into the older validator-first or replay-side closure stack.

The current smallest helper-family tie-breaker inside that packet is the bitmap direct-anchor route: keep `tools/lib/bitmap.zig` parked unless a fresh reread finds drift in the manifest-backed fill-tail clamp, copy-alias, cross-word or truncation `scnprintf`, empty-buffer, allocator-reset anchors, or the already-committed bitmap replay fields, and do not reopen the older validator-first or Phase 1 make-route names by default.

- `PHASE1_NEXT_SAFE_STEP=keep tools/lib/bitmap.zig parked unless a fresh reread finds drift in the manifest-backed fill-tail clamp, copy-alias, cross-word or truncation scnprintf, empty-buffer, allocator-reset anchors, or the already-committed bitmap replay fields; do not reopen the older validator-first or Phase 1 make-route names by default`
