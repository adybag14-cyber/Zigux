# Phase 9 Initcall and Registration Boundary Survey

This note records the exact Phase 9 initcall and registration boundary currently visible on trusted current-tree reads.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_LANE_KEY=P9-L15`
- `PHASE9_SURVEYED_COMMIT=2026-05-23-initcall-registration-boundary-shared-loader-survives`
- scope: surviving shared runtime-loader initcall evidence, sample-local trace-events registration evidence, bounded rerun handles, and no live runtime execution or shared registration-path claim

## Current repo reality
- trusted current-tree contents reads on 2026-05-23 do materialize `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`, `samples/zigux/runtime_trace_events_unregistered_gate.zig`, `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`, `samples/zigux/README.md`, and `zigux/tests/phase9_build.zig`
- the shared initcall boundary is still staged metadata only: `LoadPlan` carries `entry_symbol` and `exit_symbol`, `InitFlow.readyForRuntimeLoad()` requires exactly one init and zero exits before handoff, and `PreparedRequest` only moves through `.prepared`, `.waiting_on_runtime_substrate`, and `.released_without_substrate`
- the shared request contract still keeps `register_api`, `unregister_api`, `summary`, and `registration_snapshot` out of `LoadPlan`, and the shared loader still keeps publication and depmod surfaces out of `PreparedRequest`
- current sample-root runtime trace-events registration evidence is local to the sample packet: `registration_depth`, `last_register_label`, and `last_unregister_label` are exercised through `runtime_trace_events_unregistered_gate.zig` and `runtime_trace_events_registration_reentry_gate.zig`
- current sample-root readback still does not materialize `samples/zigux/runtime_trace_events_loader.zig`; the surviving shared-loader evidence is the shared kernel-side packet plus the sample-local registration guards instead

## Exact evidence
- `zigux/kernel/runtime_loader_contract.zig` proves the staged initcall boundary through `entry_symbol`, `exit_symbol`, `requires_runtime_substrate`, `provides_selftest_hook`, and `init_flow`, and by fail-closing extra `init_runs`, `selftest_runs`, or `exit_runs`
- `zigux/kernel/runtime_loader.zig` proves there is still no executable initcall or shared registration path here: request handoff is bounded to `requestRuntimeLoad()` and `releaseWithoutSubstrate()`, and the file still contains no `module_init(`, `module_exit(`, `register_kretprobe(`, or `unregister_kretprobe(` calls
- `zigux/tests/runtime_loader_allocator_init_flow.zig` and `zigux/tests/runtime_trace_events_loader_substrate_drift.zig` keep the staged init and release counters fail-closed across bitmap, kretprobe, atomic64, and trace-events loader plans
- `samples/zigux/runtime_trace_events_unregistered_gate.zig` keeps `OutstandingRegistration`, `FunctionThreadNotRegistered`, and `RegistrationUnderflow` fail-closed while preserving initialized and selftest-complete summaries
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig` keeps duplicate registration fail-closed with `FunctionThreadAlreadyRegistered` and records `foo_bar_reg` / `foo_bar_unreg` as sample-local labels rather than shared loader fields
- `zigux/tests/phase9_build.zig` keeps the bounded rerun handles `phase9-runtime-loader-shared-tests`, `phase9-runtime-trace-events-unregistered-gate-tests`, and `phase9-runtime-trace-events-registration-reentry-gate-tests` visible for this packet

## Boundaries
- keep shared initcall evidence in `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, and `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`
- keep trace-events registration evidence sample-local in `samples/zigux/runtime_trace_events_unregistered_gate.zig` and `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- do not present sample-local `foo_bar_reg` / `foo_bar_unreg` labels as shared loader registration APIs
- do not claim a live runtime init invocation, a direct `module_init` / `module_exit` path, or a returned `runtime_trace_events_loader.zig` companion
- do not reopen depmod, publication, or broader runtime substrate ownership

## Roadmap gap
- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- current repo evidence is still a split boundary: staged shared initcall metadata plus sample-local registration guards, without a live runtime substrate or shared executable registration path
- the blocked deliverable remains `real runtime initcall execution and shared registration-path parity`

## Gates
1. `zig test zigux/tests/runtime_initcall_registration_boundary.zig`
2. `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`
3. `zig build phase9-runtime-trace-events-unregistered-gate-tests --build-file zigux/tests/phase9_build.zig`
4. `zig build phase9-runtime-trace-events-registration-reentry-gate-tests --build-file zigux/tests/phase9_build.zig`

## Next bounded step

Reread this packet only when current `master` changes the surviving shared runtime-loader or sample-local trace-events registration files; if it reopens, tighten the same evidence packet before widening into new runtime behavior.
