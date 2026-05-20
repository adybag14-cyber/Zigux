# Phase 9 Runtime Trace-Events Survey

PHASE9_SURVEYED_COMMIT=9ca34d1aa5c3031e1126cf951cf7e4bc515fe7b4

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
The direct sample also keeps cold-stage fail-closed behavior explicit: `test "trace-events sample keeps selftest replay-summary continuity explicit after direct pilot activity"` proves pre-init `runSelftest()` and `exit()` stay rejected before `init()` moves the module into `.initialized`.
The direct sample also now keeps initialized-stage clean exit explicit: `test "trace-events sample preserves initialized summary across direct exit without selftest"` proves zero selftest runs stay explicit, the initialized summary stays unchanged until `exit()` succeeds, and later lifecycle calls remain rejected without drift.
The fail-closed companion still keeps unregistered function-thread failures fail-closed.
The exit-rollback companion still keeps failed-exit rollback explicit after reusable selftest replay: `error.OutstandingRegistration` leaves the selftest_complete summary unchanged, one later main replay plus one later function-thread replay stay explicit before unregister, and the later post-exit invalid-lifecycle rejections still leave the exited summary unchanged.
The registration-reentry companion still keeps balanced function-thread registration reusable before and after selftest, including the later duplicate-registration rejection that leaves the summary unchanged.
Its paired initialized direct-activity proof in `test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest"` keeps one direct main replay plus one function-thread replay explicit, preserves that initialized summary until `exit()` succeeds, and then keeps later lifecycle calls rejected without drift.

## Gap Versus Roadmap

This packet is enough to keep one pilot-module review surface honest, but it is not the broader shared runtime-loader publication story. The adjacent shared allocator/init-flow review packet has returned on current `master`; this lane still treats that returned packet as neighboring evidence rather than family-local trace-events proof.

Current `master` still does not expose, inside this family-local trace-events proof packet:

- the broader shared `zigux/tests/runtime_*` replay family beyond this narrow survey witness
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- the older `samples/zigux/runtime_*_loader.zig` scaffolds
- dedicated `phase9-*` runtime-pilot routes in `zigux/Makefile`

Current `master` does now expose `zigux/tests/phase9_build.zig`, but the live file is still a bounded Phase 9 build bundle rooted in `runtime_atomic64_diff.zig` together with the separate runtime bitmap sample, module, diff, loader, survey, and top-bit targets rather than a broader shared runtime-loader or trace-events build packet.

The returned shared allocator/init-flow packet now lives separately through `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and the `samples/zigux/runtime_*_loader.zig` scaffolds, but those shared surfaces still stop short of proving broader runtime publication or loadable-runtime-complete substrate work.

Current `master` does still keep the separate Phase 9 runtime bitmap reminder packet explicit through `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the bounded `zigux/tests/phase9_build.zig` bundle, so the absent-loader wording above is about the older trace-events loader-backed packet rather than proof that any direct bitmap sample-family file has returned.

So this survey packet closes one bounded roadmap gap by restoring a direct review witness under `zigux/tests/runtime_*`, but it does not claim returned shared loader parity, live `module_init()` or `module_exit()` wiring, depmod-visible registration, or broader runtime-substrate readiness.

## Boundary Rules

- Keep this survey note, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` aligned with the surviving four-file sample family only.
- Keep `Documentation/zigux/phase9-runtime-trace-events-module-slice.md` paired with this survey packet as the family-local pilot-module note.
- Keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` and the shared Phase 9 reminder surfaces adjacent rather than re-owned by this lane.
- Do not invent `validate-phase9.py`, a returned shared loader packet, or extra runtime bitmap or kretprobe evidence here.

## Next Bounded Step

If the trace-events sample family changes again, refresh only the family-local survey note, manifest, survey gate, and module-slice wording needed to keep the narrow pilot-module packet truthful.
