# Phase 9 Runtime Loader Initcall and Registration Boundary Survey

This note tracks the shared Phase 9 runtime-loader boundary that keeps initcall and registration evidence explicit without claiming a live loadable-module path on current `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-loader-initcall-registration-boundary`
- `PHASE9_LANE_KEY=P9-L13`
- `PHASE9_SURVEYED_COMMIT=2026-05-24-runtime-loader-initcall-registration-boundary`
- scope: shared runtime-loader initcall metadata, registration boundary, lifecycle-readiness evidence, and roadmap-gap wording only

## Current Shared Boundary Packet

Current `master` keeps these shared Phase 9 surfaces readable for this boundary:

- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/phase9_build.zig`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`

The contract is still metadata-only. `LoadPlan` keeps `entry_symbol` and `exit_symbol` explicit, `InitFlow.readyForRuntimeLoad()` keeps the staged readiness rule explicit, and `PreparedRequest` keeps the shared request state bounded to `prepared`, `waiting_on_runtime_substrate`, and `released_without_substrate`.

The lifecycle evidence is still counted handoff evidence rather than executable initcall or registration control. Current shared tests only accept `.initialized` with zero selftest runs or `.selftest_complete` with one selftest run while `exit_runs` stays zero, and they reject drift before the shared request can move forward.

The dedicated shared boundary guard also keeps live initcall and runtime registration out of the current shared loader packet. Current guard coverage rejects bleed-through from:

- `module_init(`
- `module_exit(`
- `register_kretprobe(`
- `unregister_kretprobe(`
- `register_trace_`
- `unregister_trace_`
- `tracepoint_probe_register(`
- `tracepoint_probe_unregister(`

## Gap Versus Roadmap

Phase 9 still requires first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`.

Current `master` has enough shared evidence to review the initcall and registration boundary honestly:

- staged entry and exit symbol names remain explicit
- lifecycle readiness remains explicit through `initialized` and `selftest_complete`
- drifted plans and out-of-order shared loader transitions still fail closed
- live initcall and runtime registration APIs remain explicitly absent from the shared loader packet

Current `master` still does not have, inside this shared boundary packet itself:

- executable `module_init()` or `module_exit()` wiring
- runtime registration or unregistration callback control paths
- end-to-end runtime module lifecycle parity through a live shared loader path

So this survey packet records a truthful roadmap gap: the shared loader boundary is reviewable, but it is still a metadata-only and pre-execution boundary rather than a shipped loadable-runtime path.

## Boundary Rules

1. Keep this packet focused on the shared loader boundary, not the family-local trace-events, bitmap, atomic64, or kretprobe sample packets.
2. Keep `entry_symbol`, `exit_symbol`, staged readiness, and blocked live registration markers explicit together.
3. Keep `zigux/tests/runtime_loader_allocator_init_flow.zig` and `zigux/tests/phase9_build.zig` adjacent evidence rather than proof that lifecycle parity is already complete.
4. Do not treat the absence checks for `module_init(`, `module_exit(`, or runtime registration APIs as proof that the missing execution path has landed somewhere else.

## Next Bounded Step

If the shared runtime-loader contract grows new initcall or registration-facing fields, refresh only this survey note, `zigux/tests/runtime_loader_initcall_registration_manifest.json`, and `zigux/tests/runtime_loader_initcall_registration_survey.zig` so the Phase 9 roadmap gap stays explicit without reopening family-local runtime sample packets.