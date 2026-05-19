# Phase 9 Runtime Trace-Events Module Slice

PHASE9_SURVEYED_COMMIT=9ca34d1aa5c3031e1126cf951cf7e4bc515fe7b4

This note keeps the owner-facing trace-events pilot-module slice aligned with the narrow current-master packet and its restored family-local survey witness.

## Roadmap anchor

- Linux anchor: `samples/trace_events/trace-events-sample.c`
- required Zigux features: first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity
- recommended Zigux destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

## Current master evidence

Current `master` keeps this narrow direct trace-events runtime packet:

- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- `Documentation/zigux/phase9-runtime-trace-events-survey.md`
- `zigux/tests/runtime_trace_events_manifest.json`
- `zigux/tests/runtime_trace_events_survey.zig`

The direct sample still exposes `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking.
Those cues are still sample-local pilot-module reviewability, not returned shared runtime-loader parity.
The shared `scripts/zigux/check-phase9-trace-events-runtime-packet.py` guard keeps that initialized, selftest_complete, and exited sample-local lifecycle tracking anchored alongside the slice packet.
The direct initialized-stage exit proof in `test "trace-events sample preserves initialized summary across direct exit without selftest"` keeps zero selftest runs explicit, preserves the initialized summary until `exit()` succeeds, and then keeps later lifecycle calls rejected without drift.
The shipped cold-stage guard in `test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity"` also keeps pre-init `runSelftest()` and `exit()` rejection explicit before the module ever reaches `.initialized`, so the packet distinguishes cold-stage fail-closed behavior from the later initialized-stage clean-exit path.
The fail-closed companion keeps unregistered function-thread failures fail-closed.
The exit-rollback companion keeps failed-exit rollback explicit after reusable selftest replay by proving `error.OutstandingRegistration` leaves the selftest_complete summary unchanged until the function thread unregisters and clean exit succeeds.
The registration-reentry companion keeps balanced function-thread registration reusable before and after selftest, including the later duplicate-registration rejection that leaves the summary unchanged.
Its paired initialized-direct-activity proof in `test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest"` keeps one direct main replay plus one function-thread replay explicit, preserves that initialized summary until `exit()` succeeds, and then keeps later lifecycle calls rejected without drift.

## Exact module-slice boundary

Current `master` proves a sample-local cold-stage guard plus init and function-thread registration boundary, not a broader shared runtime-loader registration substrate.

- `init()` still only accepts the cold stage and moves the sample to `.initialized`.
- `runSelftest()` still only accepts `.initialized` and moves the sample to `.selftest_complete`.
- `exit()` still only accepts `.initialized` or `.selftest_complete` with zero registration depth and then moves the sample to `.exited`.
- the direct cold-stage guard in `test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity"` keeps `runSelftest()` and `exit()` rejected before `init()` materializes the module state
- the direct initialized-stage exit proof keeps zero selftest runs explicit and shows that later lifecycle calls stay rejected without changing the exited summary
- the registration-reentry companion's initialized direct-activity exit proof keeps one main replay plus one function-thread replay explicit before clean exit and shows that the same initialized summary survives through exit without any selftest run
- duplicate registration still fails with `error.FunctionThreadAlreadyRegistered`
- unregistered function-thread emission still fails with `error.FunctionThreadNotRegistered`
- failed exit with outstanding registration still fails with `error.OutstandingRegistration`

The paired family-local survey packet through `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` now keeps that pilot-module story directly reviewable under `zigux/tests/runtime_*` again without pretending the wider loader-backed family returned.
That paired survey packet stays adjacent to the shared repo-level rerun guard in `.github/workflows/zigux-bootstrap.yml`, which reruns `zig test samples/zigux/runtime_trace_events.zig`, `zig test samples/zigux/runtime_trace_events_unregistered_gate.zig`, `zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, and `zig test zigux/tests/runtime_trace_events_survey.zig` without turning the workflow into dedicated `phase9-*` build-route proof.
The adjacent `zigux/tests/phase9_build.zig` bundle is now broader than an atomic64-only shard, but it still cannot serve as returned shared-loader proof because its `phase9-runtime-loader-shared-tests` step references missing `samples/zigux/runtime_bitmap_loader.zig` while the shared runtime-loader kernel files remain absent.

## Keep earlier-phase references in their own lanes:

- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references.
- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.
- Those earlier-phase anchors stay adjacent context for the narrow trace-events packet rather than shared runtime-pilot evidence.

## Still Absent

Current `master` still does not expose the broader shared runtime-loader packet:

- the broader shared `zigux/tests/runtime_*` replay family beyond this narrow survey witness
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- dedicated `phase9-*` runtime-pilot routes in `zigux/Makefile`

Current `master` does now expose `zigux/tests/phase9_build.zig`, but the live file is not clean shared-loader evidence: it carries the runtime atomic64 diff replay, the separate bitmap sample and review legs, and `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`, while its `phase9-runtime-loader-shared-tests` step still points at missing `samples/zigux/runtime_bitmap_loader.zig`.
Current `master` therefore no longer carries `samples/zigux/runtime_bitmap_loader.zig` as a live bitmap companion, even though the adjacent build bundle still references that stale leg.

So this slice must keep saying plainly that the broader shared runtime-loader packet remains absent on current `master`, and that the adjacent shared-loader build leg is still blocked evidence until the missing bitmap-loader file returns or the stale leg is rolled back.

## Ownership

1. Keep the trace-events family tied to `samples/trace_events/trace-events-sample.c` and the Phase 9 runtime-pilot roadmap only.
2. Keep the surviving four-file sample family explicit as current sample-local pilot-module proof.
3. Keep `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` paired with this slice as family-local review witnesses.
4. Keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `.github/workflows/zigux-bootstrap.yml`, and the adjacent `zigux/tests/phase9_build.zig` bundle as neighboring shared reminder or build surfaces rather than re-owned here.
5. Keep `zigux/tests/phase9_build.zig` framed as an adjacent mixed runtime bundle with a blocked bitmap-loader leg rather than trace-events packet proof or a returned shared runtime-loader build route.
6. Do not treat the broader shared runtime-loader packet as returned evidence.
7. Do not invent `validate-phase9.py`, a trace-events-only validator, or a loader-backed runtime-substrate claim that current `master` does not expose.

## Next bounded step

Keep the survey note and this module-slice note aligned with the surviving sample family and the blocked shared-loader build leg. If the broader shared runtime-loader family returns later, or if the stale bitmap-loader leg is finally restored or rolled back, reread the exact file family before widening this note back out.
