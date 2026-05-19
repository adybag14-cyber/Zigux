# Phase 9 Runtime Trace-Events Survey

PHASE9_SURVEYED_COMMIT=70542337d15e9f26941f6a247da00077dddcebe8

This survey keeps the Phase 9 runtime trace-events packet aligned with the roadmap after current `master` narrowed down to one direct sample family instead of the older broader loader-backed packet.

## Roadmap anchor

- Linux anchor: `samples/trace_events/trace-events-sample.c`
- required Zigux features: first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity
- recommended Zigux destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

## Current family-local evidence

Current `master` keeps one narrow trace-events runtime sample family:

- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`

Current `master` also now keeps one direct family-local `zigux/tests/runtime_*` witness for that same packet:

- `zigux/tests/runtime_trace_events_manifest.json`
- `zigux/tests/runtime_trace_events_survey.zig`
- `Documentation/zigux/phase9-runtime-trace-events-module-slice.md`

The direct sample still exposes `.provides_selftest_hook = true` together with initialized, selftest_complete, and exited lifecycle tracking.
The direct sample also now keeps initialized-stage clean exit explicit: `test "trace-events sample preserves initialized summary across direct exit without selftest"` proves zero selftest runs stay explicit, the initialized summary stays unchanged until `exit()` succeeds, and later lifecycle calls remain rejected without drift.
The fail-closed companion still keeps unregistered function-thread failures fail-closed.
The exit-rollback companion still keeps failed-exit rollback explicit after reusable selftest replay, including the `error.OutstandingRegistration` guard plus the later post-exit invalid-lifecycle rejections that leave the summary unchanged.
The registration-reentry companion still keeps balanced function-thread registration reusable before and after selftest, including the later duplicate-registration rejection that leaves the summary unchanged.

## Gap Versus Roadmap

This packet is enough to keep one pilot-module review surface honest, but it is not the broader shared runtime-loader story.

Current `master` still does not expose:

- `zigux/tests/phase9_build.zig`
- the broader shared `zigux/tests/runtime_*` replay family beyond this narrow survey witness
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- the older `samples/zigux/runtime_*_loader.zig` scaffolds
- dedicated `phase9-*` runtime-pilot routes in `zigux/Makefile`

So this survey packet closes one bounded roadmap gap by restoring a direct review witness under `zigux/tests/runtime_*`, but it does not claim returned shared loader parity, live `module_init()` or `module_exit()` wiring, depmod-visible registration, or broader runtime-substrate readiness.

## Boundary Rules

- Keep this survey note, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` aligned with the surviving four-file sample family only.
- Keep `Documentation/zigux/phase9-runtime-trace-events-module-slice.md` paired with this survey packet as the family-local pilot-module note.
- Keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` and the shared Phase 9 reminder surfaces adjacent rather than re-owned by this lane.
- Do not invent `validate-phase9.py`, a returned shared loader packet, or extra runtime bitmap or kretprobe evidence here.

## Next Bounded Step

If the trace-events sample family changes again, refresh only the family-local survey note, manifest, survey gate, and module-slice wording needed to keep the narrow pilot-module packet truthful.