# Phase 9 Runtime Initcall And Registration Boundary

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-initcall-registration-boundary`
- `PHASE9_LANE_KEY=P9-L18`
- `PHASE9_SURVEYED_COMMIT=2026-05-27-initcall-registration-boundary`
- scope: Phase 9 shared-loader boundary note for initcall metadata exclusion and family-local registration lifecycle ownership

## Current Repo Reality
Trusted current-tree reads on 2026-05-27 show a bounded Phase 9 split:
- the shared runtime-loader boundary in `zigux/kernel/runtime_loader.zig` and `zigux/kernel/runtime_loader_contract.zig` carries `module_name`, anchor, `entry_symbol`, `exit_symbol`, allocator handoff, init-flow counts, and module metadata needed to stage a runtime handoff request
- that shared boundary explicitly keeps `module_init`, `module_exit`, `initcall`, `exitcall`, `register_api`, `unregister_api`, `summary`, and `registration_snapshot` out of the request contract and approved-family contract
- the trace-events and kretprobe families keep registration reentry, duplicate-registration rejection, and fail-closed exit behavior in family-local lifecycle gates instead of moving those summaries into the shared loader request

These shared-loader-facing surfaces are directly readable on current `master`:
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`

These family-local registration-facing surfaces are directly readable on current `master`:
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`

## Boundary Summary
The Phase 9 roadmap target is still first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity, but current `master` reaches that target through a deliberately narrow boundary:
- the shared loader request names `entry_symbol` and `exit_symbol`, but it does not carry Linux-facing initcall metadata or family registration summaries
- the shared loader contract proves that init-flow evidence can be handed off without claiming shipped `module_init` or `module_exit` parity
- the trace-events side keeps function-thread registration depth, duplicate-registration rejection, and outstanding-registration exit guards family-local
- the kretprobe side keeps probe registration reuse, duplicate-registration rejection, outstanding-return guards, and post-exit fail-closed behavior family-local

That means this note must not claim shipped shared initcall parity, shipped shared registration-summary parity, or a shared loader contract that absorbs trace-events or kretprobe registration control.

## Boundaries
Keep this note lane-local and repo-reality-first:
- do not repair family-local trace-events wording here beyond the exact registration-boundary fact pattern
- do not repair family-local kretprobe wording here beyond the exact registration-boundary fact pattern
- do not treat `entry_symbol` and `exit_symbol` as proof that Linux `module_init` or `module_exit` metadata already crosses the shared boundary
- do not infer real depmod publication or end-to-end runtime loading from this boundary note

## Next Bounded Step
If later lanes add a shared Phase 9 survey or build route for this exact boundary, wire this note into that survey instead of broadening the claims here.
