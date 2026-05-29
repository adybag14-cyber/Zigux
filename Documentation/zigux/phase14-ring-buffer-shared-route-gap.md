# Phase 14 Ring-Buffer Shared Route Gap

This note records the current shared-smoke productization gap for the Phase 14
ring-buffer compile-route checker.

## Status

- `PHASE14_LANE_KEY=P14-L02`
- `PHASE14_GAP=ring-buffer-shared-route-checker-undercount`
- `PHASE14_STATUS=handoff_ready`
- `PHASE14_SCOPE=shared_smoke_route_checker_only`
- `PHASE14_ANCHOR=kernel/trace/ring_buffer.c`
- `PHASE14_BOUNDARY=study_only`
- `PHASE14_REPAIR_TARGET=scripts/zigux/check-phase14-shared-smoke-route.py`
- `PHASE14_VALIDATION_SENTINEL=scripts/zigux/check-phase14-ring-buffer-shared-route-gap.py`

## Current Evidence

The Phase 14 manifest now records that `scripts/zigux/validate-phase14.py` runs
`scripts/zigux/check-phase14-ring-buffer-compile-route.py`, and that the shared
manifest records the ring-buffer compile-route checker. That keeps the
ring-buffer compile row visible beside the shared smoke packet.

The remaining gap is narrower: `scripts/zigux/check-phase14-shared-smoke-route.py`
still fail-closes on the validator-side skbuff and RCU compile-route calls, but
does not yet require the validator-side ring-buffer compile-route call or the two
ring-buffer manifest booleans. This is a shared-smoke route checker undercount,
not a reason to reopen the ring-buffer anchor as implementation work.

## Bounded Repair

The next same-lane repair should teach
`scripts/zigux/check-phase14-shared-smoke-route.py` to require:

- `RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH`
- the validator `run_guardrail_checker(... RING_BUFFER_COMPILE_ROUTE_CHECKER_PATH ...)`
- `survey_summary.phase14_validate_runs_ring_buffer_compile_route_checker == true`
- `survey_summary.shared_manifest_records_ring_buffer_compile_route_checker == true`

After that repair lands, this note and
`scripts/zigux/check-phase14-ring-buffer-shared-route-gap.py` should be retired or
rewritten as closure evidence, rather than left behind as stale gap tracking.
