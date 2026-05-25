# Phase 9 Initcall And Registration Boundary Survey

This note records the current bounded Phase 9 evidence for the shared runtime-loader initcall boundary and the separate sample-local registration boundary.

## Status

- `PHASE9_LANE_KEY=P9-L15`
- `PHASE9_BOUNDARY_PACKET=initcall_registration_boundary`
- `PHASE9_PROVENANCE_MODE=dated_master_readback`
- surveyed against current-master rereads on `2026-05-25`
- scope: verify current shared-loader initcall staging and sample-local registration guards without reopening runtime execution, publication, depmod, or broader substrate ownership

## Current shared-loader initcall boundary

- shared initcall evidence remains staged through `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, and `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`
- `zigux/kernel/runtime_loader_contract.zig` keeps `entry_symbol` and `exit_symbol` explicit in `LoadPlan` while `InitFlow` stays bounded to `.initialized` and `.selftest_complete`
- `zigux/kernel/runtime_loader.zig` keeps `PreparedRequest.requestRuntimeLoad()` and `PreparedRequest.releaseWithoutSubstrate()` fail-closed on `error.InvalidLoaderState` and `error.PreparedPlanDrift`
- the shared loader packet stays metadata-only: `module_init`, `module_exit`, `register_trace_`, `unregister_trace_`, `register_kretprobe`, `unregister_kretprobe`, `.modinfo`, `MODULE_ALIAS()`, `modules.alias`, `modules.order`, `modules.builtin`, `Module.symvers`, install-root, and depmod surfaces remain blocked-boundary vocabulary rather than active Phase 9 delivery evidence
- `zigux/tests/runtime_loader_allocator_init_flow.zig` keeps initialized-stage and selftest-complete handoff snapshots explicit across bitmap, atomic64, trace-events, and kretprobe request shapes
- `zigux/tests/runtime_trace_events_loader_substrate_drift.zig` keeps prepared-stage and waiting-stage substrate drift fail-closed before loader handoff or release

## Current sample-local registration boundary

- sample-local registration evidence remains in `samples/zigux/runtime_trace_events_unregistered_gate.zig` and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- `samples/zigux/runtime_trace_events_unregistered_gate.zig` keeps unregistered function-thread failures fail-closed with `error.FunctionThreadNotRegistered` and `error.RegistrationUnderflow`
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` keeps reusable registration re-entry explicit with `error.FunctionThreadAlreadyRegistered`
- the same registration-reentry companion also keeps the initialized direct-activity clean-exit proof explicit through `test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest"`

## Shared route evidence

- `zigux/tests/phase9_build.zig` keeps the neighboring shared rerun packet explicit through `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, `phase9-runtime-loader-shared-tests`, and `phase9-runtime-trace-events-loader-substrate-drift-tests`
- those route names are bounded rerun handles, not proof that blocked publication, install-root, or broader runtime-substrate work has returned

## Historical boundary reminder

- `samples/zigux/runtime_trace_events_loader.zig` is not part of the current direct-readback packet for this lane and stays historical wider-family vocabulary unless a fresh repo reread proves it returned
- this note does not treat the absent older loader-gap packet as current proof

## Next bounded step

Keep this packet parked unless a fresh reread changes the shared loader handoff fields, the sample-local registration guards, or the bounded Phase 9 rerun routes tied to this exact boundary.
