# Phase 9 Runtime Trace-Events Survey

PHASE9_SURVEYED_COMMIT=184cd984461917f4d56bf5d7b6d6ba246c94ba23

This survey keeps the Phase 9 runtime trace-events packet aligned with the roadmap after current `master` narrowed down to one direct sample family plus an adjacent shared loader-handoff build shard instead of the older broader loader-backed packet.

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
The direct sample also keeps rejected re-selftest rollback explicit: `test "trace-events sample keeps rejected re-selftest rollback explicit"` proves retrying `runSelftest()` after both the selftest_complete and exited stages returns `error.InvalidLifecycleTransition` without changing either summary.
The fail-closed companion still keeps unregistered function-thread failures fail-closed.
The exit-rollback companion still keeps failed-exit rollback explicit after reusable selftest replay: `error.OutstandingRegistration` leaves the selftest_complete summary unchanged, one later main replay plus one later function-thread replay stay explicit before unregister, and the later post-exit invalid-lifecycle rejections still leave the exited summary unchanged.
The same exit-rollback companion also keeps initialized-stage failed-exit rollback explicit before selftest replay: `error.OutstandingRegistration` leaves the initialized summary unchanged, the later unregister stays explicit, and the module can still reach the selftest_complete summary without drift.
The same exit-rollback companion also keeps initialized-stage direct-activity failed-exit rollback explicit before selftest replay: `error.OutstandingRegistration` leaves the initialized direct-activity summary unchanged after one main replay plus one function-thread replay, the later unregister stays explicit, and the module can still reach the selftest_complete summary without drift.
The registration-reentry companion still keeps balanced function-thread registration reusable before and after selftest, including the later duplicate-registration rejection that leaves the summary unchanged.
Its paired initialized direct-activity proof in `test "phase9 trace-events sample preserves initialized direct-activity summary across exit without selftest"` keeps one direct main replay plus one function-thread replay explicit, preserves that initialized summary until `exit()` succeeds, and then keeps later lifecycle calls rejected without drift.

Current `master` also now keeps an adjacent shared loader-handoff build shard in `zigux/tests/phase9_build.zig`: the live file names `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, aggregate `phase9-runtime-loader-shared-tests`, and the broader `phase9-first-loadable-runtime-module-parity-survey-tests` route, but those steps remain shared-owner evidence rather than family-local trace-events proof.

## Gap Versus Roadmap

This packet is enough to keep one pilot-module review surface honest, but it is not the broader shipped runtime publication story. The adjacent shared allocator/init-flow review packet has returned on current `master`; this lane still treats that returned packet and the shared loader-handoff build shard as neighboring evidence rather than family-local trace-events proof.

Current `master` still does not expose, inside this family-local trace-events proof packet itself:

- a dedicated trace-events-only build route in `zigux/tests/phase9_build.zig`
- a family-local loader parity witness inside `zigux/tests/runtime_*` beyond the adjacent shared allocator/init-flow and command/environment boundary packet
- shipped runtime publication, install-root, or depmod-visible proof for the broader loader family

Current `master` now exposes the shared loader-backed surfaces `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`, and the separate returned `samples/zigux/runtime_bitmap_loader.zig` scaffold through the adjacent `phase9-runtime-loader-shared-tests` shard in `zigux/tests/phase9_build.zig`, but that shard still stays neighboring shared-owner evidence instead of a returned family-local trace-events packet.

Current `master` still keeps the separate Phase 9 runtime bitmap reminder packet explicit through `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_survey.zig`, and the bounded `zigux/tests/phase9_build.zig` bundle, so the family-local boundary above is about avoiding trace-events overclaim rather than proof that the bitmap family is complete.

So this survey packet closes one bounded roadmap gap by restoring a direct review witness under `zigux/tests/runtime_*`, but it does not claim dedicated trace-events build-route ownership, shipped broader runtime publication parity, live `module_init()` or `module_exit()` wiring beyond the current sample family, or loadable-runtime-complete substrate work.

## Boundary Rules

- Keep this survey note, `zigux/tests/runtime_trace_events_manifest.json`, and `zigux/tests/runtime_trace_events_survey.zig` aligned with the surviving four-file sample family only.
- Keep `Documentation/zigux/phase9-runtime-trace-events-module-slice.md` paired with this survey packet as the family-local pilot-module note.
- Keep the adjacent shared loader-handoff shard in `zigux/tests/phase9_build.zig` explicit without promoting it into family-local trace-events proof.
- Keep `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` and the other shared Phase 9 reminder surfaces adjacent rather than re-owned by this lane.
- Do not invent `validate-phase9.py`, a returned trace-events-only loader packet, or extra runtime bitmap or kretprobe evidence here.

## Next Bounded Step

If the trace-events sample family changes again, refresh only the family-local survey note, manifest, survey gate, and module-slice wording needed to keep the narrow pilot-module packet truthful while leaving the shared loader-handoff shard as neighboring evidence unless it is explicitly promoted by the owning shared Phase 9 lane.