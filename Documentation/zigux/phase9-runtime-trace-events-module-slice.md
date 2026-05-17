# Phase 9 Runtime Trace-Events Module Slice

This note keeps the owner-facing module-slice surface aligned with the narrow Phase 9 runtime packet still visible on current `master`.

PHASE9_SURVEYED_COMMIT=39e19ef4419df76af18f2461d225c15e1318c44f

This note keeps the last reviewed packet checkpoint explicit without treating older manifest-backed or loader-backed companions as shipped current-`master` evidence.

## Roadmap anchor

Phase 9 is the runtime pilot tranche.

  * Linux anchor: `samples/trace_events/trace-events-sample.c`
  * required Zigux features: first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity
  * recommended Zigux destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

This module-slice note stays review-first. It records what the live repository still proves, what remains absent on current `master`, and which shared reminder files own the next bounded follow-through.

## Current master evidence

Current `master` keeps only a narrow direct trace-events runtime packet in this family-local slice:
  * `samples/zigux/runtime_trace_events.zig`
  * `samples/zigux/runtime_trace_events_unregistered_gate.zig`
  * `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/check-phase9-trace-events-runtime-packet.py`
  * `zigux/tests/README.md`

The direct sample keeps the roadmap-facing pilot contract concrete through `RuntimeTraceEventsSample.descriptor()` and `.provides_selftest_hook = true`, together with initialized, selftest_complete, and exited lifecycle tracking.
The same direct sample also keeps rejected re-selftest and failed-exit rollback cues explicit inside the shipped file, so the surviving packet still carries one real runtime selftest plus bounded lifecycle-rollback proof on current `master`.
The fail-closed companion keeps the unregistered function-thread boundary explicit both immediately after `init()` and after the direct selftest replay, so the surviving packet still carries one real runtime selftest and companion-boundary proof on current `master`.

## Exact init and registration evidence

Current `master` proves a sample-local init and function-thread registration boundary, not a broader shared runtime-loader registration substrate.

  * `RuntimeTraceEventsSample.descriptor()` sets `.requires_runtime_substrate = true` and `.provides_selftest_hook = true`.
  * `init()` only accepts the `.cold` stage, resets registration depth, counters, labels, and cached payloads, increments `init_runs`, and moves `stage_state` to `.initialized`.
  * `registerFunctionThread()` only runs through `ensureMutable()` while the sample is still `.initialized` or `.selftest_complete`; if `registration_depth != 0` it returns `error.FunctionThreadAlreadyRegistered`, otherwise it sets `registration_depth = 1` and `last_register_label = "foo_bar_reg"`.
  * `emitFunctionIteration()` rejects use without prior registration with `error.FunctionThreadNotRegistered`.
  * `runSelftest()` is only accepted from `.initialized`; it replays `emitMainIteration(0)`, `registerFunctionThread()`, `emitFunctionIteration(1)`, and `unregisterFunctionThread()` before incrementing `selftest_runs` and moving the sample to `.selftest_complete`.
  * `unregisterFunctionThread()` fails closed with `error.RegistrationUnderflow` when the depth is already zero, and `exit()` rejects nonzero registration depth with `error.OutstandingRegistration` before allowing the `.exited` stage.
  * `samples/zigux/runtime_trace_events_unregistered_gate.zig` keeps the same boundary explicit both immediately after `init()` and after the selftest replay by asserting `error.FunctionThreadNotRegistered` plus `error.RegistrationUnderflow`, then checking the summary stays stable.
  * The shipped duplicate-registration test in `samples/zigux/runtime_trace_events.zig` confirms that a second `registerFunctionThread()` call preserves the prior summary and fails with `error.FunctionThreadAlreadyRegistered`.

Current `master` does not currently expose the broader shared runtime-loader packet that older Phase 9 reminder surfaces described. Fresh repo-first rereads did not find `zigux/tests/phase9_build.zig`, the shared `zigux/tests/runtime_*` replay family, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/Makefile`, or the older `samples/zigux/runtime_*_loader.zig` scaffolds on `master`.

No current family-local trace-events packet should therefore describe `samples/zigux/runtime_trace_events_loader.zig`, `zigux/tests/runtime_trace_events_module.zig`, `zigux/tests/runtime_trace_events_diff.zig`, `zigux/tests/runtime_trace_events_loader_substrate_drift.zig`, `zigux/tests/runtime_trace_events_survey.zig`, or `zigux/tests/runtime_trace_events_manifest.json` as shipped current-`master` evidence unless a fresh repo reread proves they have returned.

## What this slice owns

1. Keep the Phase 9 trace-events family tied to `samples/trace_events/trace-events-sample.c` and the runtime-pilot roadmap only.
2. Keep the surviving direct sample plus its rejected re-selftest and failed-exit rollback cues explicit as real current-packet lifecycle proof.
3. Keep the surviving fail-closed companion explicit as the same packet's function-thread boundary proof.
4. Keep the exact init and registration evidence above tied to the shipped sample pair instead of inferring broader loader behavior that current `master` does not expose.
5. Keep the real blocker explicit: the broader shared runtime-loader, build, kernel, and multi-file runtime replay packet is absent on current `master`, so this note must not borrow evidence from older missing paths.
6. Do not invent `validate-phase9.py`, a trace-events-only validator, or a returned loader family.
7. Keep earlier-phase references in their own lanes: `scripts/zigux/kconfig/conf_bridge.zig` and `scripts/zigux/kconfig/confdata_bridge.zig` remain Phase 2 references, while `rust/exports.c` and `zigux/kernel/export_shim.zig` remain Phase 3 export-boundary references.

## Review posture

- the current direct runtime proof is the narrow sample pair made of `samples/zigux/runtime_trace_events.zig` and `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- the direct sample still exposes `.provides_selftest_hook = true` plus initialized, selftest_complete, and exited lifecycle tracking
- the direct sample also keeps rejected re-selftest and failed-exit rollback cues explicit inside the shipped file
- the direct sample now has exact recorded evidence for `init()`, `registerFunctionThread()`, `emitFunctionIteration()`, `runSelftest()`, `unregisterFunctionThread()`, and `exit()` behavior inside this slice note
- the fail-closed companion keeps unregistered function-thread rejection explicit after `init()` and after the direct selftest replay
- the shared reminder packet is checker-backed through `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase9-trace-events-runtime-packet.py`
- broader loader, build, kernel, and `zigux/tests/runtime_*` replay surfaces remain backlog references until a fresh reread proves they have returned

## Next bounded step

Keep this module-slice note aligned with the surviving direct sample pair, including the exact init and registration evidence plus the rejected re-selftest and failed-exit rollback cues already shipped in `samples/zigux/runtime_trace_events.zig`. If the broader shared runtime-loader family returns later, reread the exact file family before widening this note back out.
