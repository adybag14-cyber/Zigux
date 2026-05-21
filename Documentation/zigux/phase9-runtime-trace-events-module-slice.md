# Phase 9 Runtime Trace-Events Module Slice

PHASE9_SURVEYED_COMMIT=184cd984461917f4d56bf5d7b6d6ba246c94ba23

This note keeps the owner-facing trace-events pilot-module slice aligned with the narrow current-master packet and its adjacent shared loader-handoff build shard.

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
Those cues are still sample-local pilot-module reviewability, not promoted family-local runtime-loader parity.
The shared `scripts/zigux/check-phase9-trace-events-runtime-packet.py` guard keeps that initialized, selftest_complete, and exited sample-local lifecycle tracking anchored alongside the slice packet.
The direct initialized-stage exit proof in `test "trace-events sample preserves initialized summary across direct exit without selftest"` keeps zero selftest runs explicit, preserves the initialized summary until `exit()` succeeds, and then keeps later lifecycle calls rejected without drift.
The direct sample also keeps rejected re-selftest rollback explicit: `test "trace-events sample keeps rejected re-selftest rollback explicit"` proves `runSelftest()` stays rejected after both the selftest_complete and exited summaries without drift.
The shipped cold-stage guard in `test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity"` also keeps pre-init `runSelftest()` and `exit()` rejection explicit before the module ever reaches `.initialized`, so the packet distinguishes cold-stage fail-closed behavior from the later initialized-stage clean-exit path.
The fail-closed companion keeps unregistered function-thread failures fail-closed.
The exit-rollback companion keeps failed-exit rollback explicit after reusable selftest replay by proving `error.OutstandingRegistration` leaves the selftest_complete summary unchanged until the function thread unregisters and clean exit succeeds.
The same companion also keeps initialized-stage failed-exit rollback explicit before selftest replay by proving `error.OutstandingRegistration` leaves the initialized summary unchanged until unregister and the later `runSelftest()` replay succeeds without drift.
The same exit-rollback companion also keeps initialized-stage direct-activity failed-exit rollback explicit before selftest replay by proving `error.OutstandingRegistration` leaves one main replay plus one function-thread replay unchanged until unregister and the later `runSelftest()` replay succeeds without drift.
The registration-reentry companion keeps balanced function-thread registration reusable before and after selftest, including the later duplicate-registration rejection that leaves the summary unchanged.
Its paired initialized-direct-activity proof in `test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest"` keeps one main replay plus one function-thread replay explicit, preserves that initialized summary until `exit()` succeeds, and then keeps later lifecycle calls rejected without drift.

## Exact module-slice boundary

Current `master` proves a sample-local cold-stage guard plus init and function-thread registration boundary, not a broader shipped runtime-loader registration substrate.

- `init()` still only accepts the cold stage and moves the sample to `.initialized`.
- `runSelftest()` still only accepts `.initialized` and moves the sample to `.selftest_complete`.
- `exit()` still only accepts `.initialized` or `.selftest_complete` with zero registration depth and then moves the sample to `.exited`.
- the direct cold-stage guard in `test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity"` keeps `runSelftest()` and `exit()` rejected before `init()` materializes the module state
- the direct initialized-stage exit proof keeps zero selftest runs explicit and shows that later lifecycle calls stay rejected without changing the exited summary
- the direct rejected re-selftest rollback proof keeps `runSelftest()` fail-closed after both the selftest_complete and exited summaries so later selftest retries cannot mutate either lifecycle checkpoint
- the registration-reentry companion's initialized direct-activity exit proof keeps one main replay plus one function-thread replay explicit before clean exit and shows that the same initialized summary survives through exit without any selftest run
- duplicate registration still fails with `error.FunctionThreadAlreadyRegistered`
- unregistered function-thread emission still fails with `error.FunctionThreadNotRegistered`
- failed exit with outstanding registration still fails with `error.OutstandingRegistration`

The paired family-local survey packet through `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` now keeps that pilot-module story directly reviewable under `zigux/tests/runtime_*` again without pretending the wider loader-backed family returned.
That paired survey packet stays adjacent to the shared repo-level rerun guard in `.github/workflows/zigux-bootstrap.yml`, which reruns `zig test samples/zigux/runtime_trace_events.zig`, `zig test samples/zigux/runtime_trace_events_unregistered_gate.zig`, `zig test samples/zigux/runtime_trace_events_exit_rollback_guard.zig`, `zig test samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, and `zig test zigux/tests/runtime_trace_events_survey.zig` without turning the workflow into dedicated family-local loader parity proof.
The adjacent shared build shard in `zigux/tests/phase9_build.zig` now names `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-trace-events-loader-substrate-drift-tests`, aggregate `phase9-runtime-loader-shared-tests`, and the broader `phase9-first-loadable-runtime-module-parity-survey-tests` route, but those loader-backed and cross-family rerun routes remain neighboring shared-owner evidence instead of expanding this module slice into returned family-local runtime-loader parity.

## Keep earlier-phase references in their own lanes:

- `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references.
- `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.
- Those earlier-phase anchors stay adjacent context for the narrow trace-events packet rather than shared runtime-pilot evidence.

## Still Absent

Current `master` still does not expose, inside this family-local trace-events proof packet itself:

- a dedicated trace-events-only build route in `zigux/tests/phase9_build.zig`
- a family-local loader parity witness beyond the adjacent shared `zigux/tests/runtime_trace_events_loader_substrate_drift.zig` handoff check
- shipped runtime publication, install-root, or depmod-visible proof for the broader loader family

Current `master` does now expose the shared loader-backed surfaces `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the `samples/zigux/runtime_*_loader.zig` scaffolds through the adjacent `phase9-runtime-loader-shared-tests` shard in `zigux/tests/phase9_build.zig`, but that shard still stays neighboring shared-owner evidence rather than returned family-local trace-events proof.
Current `master` still keeps the separate Phase 9 runtime bitmap reminder packet visible through `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and the bounded `zigux/tests/phase9_build.zig` bundle, while `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, and `zigux/tests/runtime_bitmap_manifest.json` remain trusted-contents gaps. So the family-local boundary above is about avoiding trace-events overclaim rather than proof that every bitmap-side loader or manifest companion returned.

So this slice must keep saying plainly that the broader shared runtime-loader packet remains adjacent shared evidence rather than family-local trace-events proof on current `master`.

## Ownership

1. Keep the trace-events family tied to `samples/trace_events/trace-events-sample.c` and the Phase 9 runtime-pilot roadmap only.
2. Keep the surviving four-file sample family explicit as current sample-local pilot-module proof.
3. Keep `Documentation/zigux/phase9-runtime-trace-events-survey.md`, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` paired with this slice as family-local review witnesses.
4. Keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `.github/workflows/zigux-bootstrap.yml`, and the adjacent shared loader shard in `zigux/tests/phase9_build.zig` as neighboring reminder, workflow, or build surfaces rather than re-owned here.
5. Keep `zigux/tests/phase9_build.zig` framed as a shared Phase 9 loader-handoff shard plus bounded bitmap and atomic64 rerun bundle rather than trace-events packet proof or a returned family-local runtime-loader build route.
6. Do not treat the broader shared runtime-loader packet as returned family-local trace-events evidence.
7. Do not invent `validate-phase9.py`, a trace-events-only validator, or a loader-backed runtime-substrate claim that current `master` does not expose.

## Next bounded step

Keep the survey note and this module-slice note aligned with the surviving sample family while naming the adjacent shared loader shard truthfully. If the broader shared runtime-loader family widens again, reread the exact file family before widening this note back out.