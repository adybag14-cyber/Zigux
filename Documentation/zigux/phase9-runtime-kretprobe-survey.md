# Phase 9 Runtime Kretprobe Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/kprobes/kretprobe_example.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-survey`
- `PHASE9_LANE_KEY=P9-L16`
- `PHASE9_SURVEYED_COMMIT=fe8a43ea2e186da0da152198b571dff57ea3c38c`
- scope: survey manifest, manifest-backed delivery catalog and ownership map, a direct embedded sample replay, dedicated survey and diff gates, the bounded pre-init `configureMaxactive()` starter contract, the bounded loader-handoff scaffold, explicit shared `command_name` preservation, explicit no-substrate rollback evidence, the landed shared loader-request binding, explicit `phase9-runtime-kretprobe-{sample,module,diff,loader,survey}-tests` shared-build legs, and the lane-level note that records the remaining broader runtime-control blocker plus the exact Phase 9 roadmap gap it still leaves open
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
  - `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`
  - `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The roadmap names `samples/kprobes/kretprobe_example.c` twice: first as a Phase 5 sample-reference anchor and later as a Phase 9 runtime pilot anchor. This lane stays strictly inside the Phase 9 reading of that roadmap entry.

This `P9-L16` verification pass keeps the survey artifacts anchored to the current manifest, catalog, and ownership lane for the runtime kretprobe packet after replaying the current sample, module, diff, loader, and survey behavior against `master` head `fe8a43ea2e186da0da152198b571dff57ea3c38c`. That keeps the ownership history honest while still recording the full live review surface.

In other words, the current survey packet is pinned to `master` commit `fe8a43ea2e186da0da152198b571dff57ea3c38c` while this bounded helper-step replay remains under review.

The live repo now has a bounded `runtime_kretprobe` starter, a direct embedded sample replay, dedicated module tests, a dedicated diff gate, a bounded loader-handoff scaffold, a shared loader-request binding under `zigux/kernel/runtime_loader.zig`, and shared Phase 9 build coverage, so this survey note keeps that shipped packet reviewable through a manifest-backed delivery catalog and ownership map instead of leaving the sample and shared-build surface implied.

The shared runtime-loader blocker that still governs this kretprobe packet also sits underneath the freeze map's study boundary. `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`, so this lane may ship a bounded in-memory starter, loader-handoff scaffold, shared loader-request binding, and direct replay evidence, but it must not imply workqueue parity, scheduler transport ownership, or any Architecture Council-approved status change for that study-only anchor.

No parity scorecard entry or Architecture Council status-change request is attached to this Phase 9 kretprobe lane. The evidence here remains limited to the runtime starter, loader scaffold, shared request binding, module and diff gates, and the still-blocked shared loader-control posture that keeps the packet pre-execution.

## Survey findings

- `samples/kprobes/kretprobe_example.c` is present on `master` at 108 lines.
- the Linux sample is module-oriented, centered on `register_kretprobe`, `unregister_kretprobe`, `entry_handler`, `ret_handler`, `maxactive`, and `nmissed`.
- the live repo now ships `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_diff.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, a shared loader-request binding in `zigux/kernel/runtime_loader.zig`, and the shared `zigux/tests/phase9_build.zig` coverage for this lane.
- against the Phase 9 roadmap feature list, the live packet now lands the explicit selftest-hook surface, direct embedded sample replay, and reviewable starter lifecycle transitions, but it still does not satisfy `first loadable Zigux runtime modules` or `runtime module lifecycle parity` because the shared runtime-loader control surface and real `register_kretprobe()` or `unregister_kretprobe()` execution remain blocked.
- the current bounded symbol surface remains sample-side rather than Kconfig-backed: `samples/zigux/runtime_kretprobe.zig` still defaults `symbol_name` to `kernel_clone`, only allows retargeting before init, and does not expose any `CONFIG_` or `Kconfig` gate in this packet.
- the bounded starter now keeps the Linux sample's `maxactive` contract explicit before init: `configureMaxactive()` only accepts values in the starter-owned `1...default_maxactive` range while the module is still `cold`, and the dedicated module plus diff gates keep that pre-init pressure reviewable without implying live module-parameter ownership.
- the bounded starter keeps the Linux sample's fixed `KSYM_NAME_LEN` symbol buffer explicit by rejecting symbol retargets at or above 512 bytes, so the pilot does not silently widen the module-parameter contract while runtime loading is still blocked.
- the bounded starter keeps per-instance private entry timestamps explicit under concurrent active probes, matching the Linux anchor's `struct my_data` shape more closely without claiming real `kretprobe_instance` substrate support.
- the bounded starter exposes a stable `RuntimeKretprobeSummary` surface for lifecycle stage, `init_runs`, `selftest_runs`, `exit_runs`, active-instance state, and the latest bounded probe results, so selftest and post-exit review does not depend on reading sample internals directly.
- the bounded starter now keeps a failed-exit rollback proof explicit: public `runFailedExitRecoveryReplay()` plus `zigux/tests/runtime_kretprobe_module.zig` both show that `OutstandingProbeInstance` leaves lifecycle stage, summary counters, `active_instances`, and `entry_timestamp_armed` unchanged until the pending return path is replayed and exit succeeds.
- the direct embedded sample replay now keeps lifecycle accounting, concurrent timestamp handling, symbol-cap guards, and missed-instance bookkeeping reviewable inside `samples/zigux/runtime_kretprobe.zig`, so the starter packet no longer relies on the separate module gate as its only executable sample evidence.
- the loader scaffold makes the no-substrate rollback path explicit: `releaseSharedRuntimeLoadWithoutSubstrate()` returns the shared runtime-loader request surface in `released_without_substrate` state, so the current fallback path is reviewable without implying live `register_kretprobe()` or `unregister_kretprobe()` execution.
- the sample-side loader and shared request contract still keep symbol or command handling explicit but narrow: `samples/zigux/runtime_kretprobe_loader.zig` and `zigux/kernel/runtime_loader.zig` still carry `register_kretprobe`, `unregister_kretprobe`, the selected `symbol_name`, `requires_runtime_substrate`, `provides_selftest_hook`, a default `command_name = null` handoff for the live starter path, and a synthetic preserved `perf-runtime-kretprobe` command-name replay through `toSharedRequest()` plus `releasedWithoutSubstrate()` instead of any real export-parity or runtime command surface.
- the shared lifecycle-boundary summary in `zigux/kernel/runtime_loader.zig` still forbids live `module_init()` and `module_exit()` handoffs for this packet, so the bounded loader projection remains explicitly pre-execution even while `register_kretprobe()` and `unregister_kretprobe()` stay reviewable as names.
- the shared `zigux/tests/phase9_build.zig` entrypoint now remains explicit about the dedicated `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-diff-tests`, `phase9-runtime-kretprobe-loader-tests`, and `phase9-runtime-kretprobe-survey-tests` legs, so the shipped replay packet is reviewable without reading the build file by eye.
- broader shared runtime-loader controls are still missing, so the starter intentionally stops at bounded lifecycle, bookkeeping, loader-handoff behavior, and a machine-checkable shared request shape rather than claiming real module registration parity; command-name, argv-policy, or environment-derived activation handling still stay blocked in the shared loader-gap note.
- a focused current-head grep across `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/tests/runtime_kretprobe_manifest.json`, `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, and `zigux/tests/phase9_build.zig` still returns no `CONFIG_`, `Kconfig`, `EXPORT_SYMBOL`, or `symbol export` markers, so the honest current evidence is symbol-name plus runtime-substrate metadata only.

## Delivery ownership map

The manifest-backed catalog for this slice now names which file owns each part of the current delivery packet:

- `Documentation/zigux/phase9-runtime-kretprobe-survey.md` owns the roadmap anchor note, shipped review packet summary, explicit shared-build evidence, the freeze-map boundary note, and remaining shared-loader blocker wording
- `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md` owns the bounded starter surface, lifecycle summary, loader handoff wording, and shared-build-leg explanation for the shipped packet
- `zigux/tests/runtime_kretprobe_manifest.json` owns the manifest-backed exact checks, delivery catalog, and ownership map for the current runtime kretprobe packet
- `zigux/tests/runtime_kretprobe_survey.zig` owns the machine-checkable replay of the manifest-backed ownership packet, shared-build legs, and adjacent blocked shared-loader note
- `zigux/tests/runtime_kretprobe_module.zig` owns the bounded starter lifecycle, symbol-cap, and runtime summary replay surface
- `zigux/tests/runtime_kretprobe_diff.zig` owns the bounded differential replay for skip, duration, maxactive pressure, and fixed-symbol-buffer expectations from `samples/kprobes/kretprobe_example.c`
- `zigux/tests/phase9_build.zig` owns the shared Phase 9 runtime entrypoint that replays the dedicated kretprobe sample, module, diff, loader, and survey legs together
- `samples/zigux/runtime_kretprobe.zig` owns the bounded in-memory kretprobe starter contract, direct embedded sample replay, lifecycle staging, per-instance timestamp bookkeeping, public `runFailedExitRecoveryReplay()`, and selftest-hook metadata
- `samples/zigux/runtime_kretprobe_loader.zig` owns the sample-side loader projection, explicit shared `command_name` preservation, waiting_on_runtime_substrate handoff, released_without_substrate fallback, and kretprobe payload summary
- `zigux/kernel/runtime_loader.zig` owns the shared runtime-loader request contract that consumes the kretprobe loader handoff, allocator posture, and staged entry and exit symbols
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` owns the blocked shared command-name, argv-policy, environment-derived activation-control posture that keeps the kretprobe packet pre-execution
- `Documentation/zigux/freeze-map.md` owns the study-only `kernel/workqueue.c` boundary, the no-parity-scorecard posture, and the Architecture Council reopen rule for any scheduler-facing status change tied to this pre-execution kretprobe packet

## Recorded gaps

The survey manifest now records:

- the landed `phase9-build-gate`, including the dedicated `phase9-runtime-kretprobe-sample-tests` shared-build leg
- the landed `phase9-build-gate`, including the dedicated `phase9-runtime-kretprobe-module-tests` shared-build leg
- the landed `phase9-build-gate`, including the dedicated `phase9-runtime-kretprobe-diff-tests` shared-build leg
- the landed `phase9-build-gate`, including the dedicated `phase9-runtime-kretprobe-loader-tests` shared-build leg
- the landed `phase9-build-gate`, including the dedicated `phase9-runtime-kretprobe-survey-tests` shared-build leg
- the landed `runtime-kretprobe-survey-gate`
- the landed `runtime-kretprobe-sample-module`
- the landed `runtime-kretprobe-module-tests`
- the landed `runtime-kretprobe-diff-gate`
- the landed `runtime-kretprobe-loader-scaffold`
- the landed `runtime-kretprobe-live-loader-binding`
- the still-blocked `runtime-kretprobe-shared-loader-controls`

This keeps the lane concrete without pretending that Zigux already has real `register_kretprobe()` substrate support or the broader shared runtime-loader controls needed for execution.

It also keeps the roadmap comparison explicit: this packet now has the landed selftest-hook marker, direct sample replay, and starter lifecycle evidence, but the `first loadable Zigux runtime modules` and `runtime module lifecycle parity` steps remain open until the broader shared runtime-loader controls can drive a real registration path.

The manifest-backed review prompts for this lane now also keep one rollback question explicit: does the current packet still name the no-substrate fallback path, or did a code change silently turn the bounded handoff into an implied live loader?

## Latest verification snapshot

- verified against `master` head `fe8a43ea2e186da0da152198b571dff57ea3c38c`
- direct sample replay in the lane-local scratch packet passed: `zig test samples/zigux/runtime_kretprobe.zig`
- formatting stayed clean for the shipped sample: `zig fmt --check samples/zigux/runtime_kretprobe.zig`
- the dedicated survey packet stays directly replayable through the shipped standalone survey gate: `zig test zigux/tests/runtime_kretprobe_survey.zig`
- the shared Phase 9 runtime build still passes the dedicated `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-diff-tests`, `phase9-runtime-kretprobe-loader-tests`, and `phase9-runtime-kretprobe-survey-tests` legs inside `zig build test --build-file zigux/tests/phase9_build.zig --summary all`, but the broader entrypoint is currently red outside this lane because `phase9-runtime-loader-non-owner-boundary-survey-tests` hits `error.StreamTooLong`
- observed current bounded behavior stayed unchanged where this packet owns behavior: the sample selftest path still reaches `selftest_complete`, the failed-exit rollback path keeps lifecycle state and summary facts stable until the outstanding return path is replayed, the pre-init `configureMaxactive()` surface still rejects zero, over-cap, and post-init retunes, the loader still hands off through `waiting_on_runtime_substrate` plus `released_without_substrate`, the synthetic `perf-runtime-kretprobe` command name still survives the shared handoff unchanged, and the broader shared runtime-loader control surface remains the only blocker to real execution

## Gates

1. run the dedicated Phase 9 survey gate
- `zig test zigux/tests/runtime_kretprobe_survey.zig`
- `make -C zigux phase9-kretprobe-survey`
- the dedicated make target wraps the same standalone survey gate so the focused ownership packet stays reviewable without requiring the broader shared build

2. run the shared runtime packet replay
- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`
- this shared build now includes the dedicated `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-diff-tests`, `phase9-runtime-kretprobe-loader-tests`, and `phase9-runtime-kretprobe-survey-tests` legs

3. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice does not yet claim:

- a side-by-side Phase 5 `samples/zigux/kretprobe_example.zig` reference port
- architecture-specific `pt_regs` handling or real return-value extraction parity
- loadable-module init and exit parity for kretprobes inside Zigux
- shared runtime-loader command-name, argv-policy, or environment-derived activation controls
- true runtime execution or lifecycle parity through a shared loader path
- parity or ownership for `kernel/workqueue.c`
- any freeze-map status change for the scheduler-facing workqueue boundary without an Architecture Council decision

## Next bounded step

Stay in the Phase 9 runtime kretprobe lane and keep future work narrowly aimed at the remaining shared runtime-loader control blocker, rather than reopening already-landed sample, survey, manifest, loader-scaffold, shared binding, module-gate, or diff-gate scaffolding, while keeping `kernel/workqueue.c` in study-only status unless the Architecture Council explicitly reopens that anchor.
