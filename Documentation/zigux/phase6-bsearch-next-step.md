# Phase 6 bsearch next step

## Scope

This note is limited to the `lib/bsearch.zig` helper lane.

## Current current-master evidence

- `lib/bsearch.zig` is already a substantial Phase 6 helper, not an empty scaffold. It ships typed and raw search helpers, lower-bound and upper-bound helpers, equal-range helpers, native comparator handling, C ABI comparator handling, and inline tests for duplicate spans, insertion points, comparison-budget behavior, and mutable aliasing.
- `zigux/tests/phase6_build.zig` already wires helper-local replay for `phase6-bsearch-test`, `phase6-bsearch-perf`, `phase6-bsearch-index-range-accessors-tests`, `phase6-bsearch-lower-bound-c-abi-tests`, and `phase6-bsearch-c-abi-budget-tests`.
- `zigux/Makefile` already exposes `make -C zigux phase6-bsearch-test` and `make -C zigux phase6-bsearch-perf` on current `master`.
- `scripts/zigux/validate-phase6.py` already treats bsearch as part of the live Phase 6 packet through `scripts/zigux/check-phase6-bsearch-corpus-evidence.py`, `scripts/zigux/check-phase6-bsearch-c-parity.py`, and the shared perf-marker surfaces.
- The broader reminder surfaces checked in this lane run do not currently carry a helper-local bsearch summary even though the helper, replay routes, parity checker, and perf gate are already present.

## Closure correction

The helper-local repo reality is ahead of the broad reminder surfaces. For `lib/bsearch.zig`, the honest correction is to treat the helper as an already-materialized Phase 6 packet with a reminder-surface gap, not as a missing implementation lane.

## Bounded next safe step

The next safe helper-only follow-up is a reminder-surface correction that threads this exact bsearch packet through the shared review surfaces without reopening other Phase 6 helpers:

- `lib/bsearch.zig`
- `zigux/tests/phase6_bsearch.zig`
- `zigux/tests/phase6_bsearch_perf.zig`
- `scripts/zigux/check-phase6-bsearch-c-parity.py`
- `make -C zigux phase6-bsearch-test`
- `make -C zigux phase6-bsearch-perf`

Keep that follow-up limited to `bsearch` so the lane stays on the current helper packet instead of expanding into `base64`, `checksum`, or `hexdump` churn.
