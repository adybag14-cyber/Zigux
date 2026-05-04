# Phase 9 Runtime Kretprobe Module Slice

This document tracks the first bounded Phase 9 runtime kretprobe starter under `samples/zigux/`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-module-starter`
- `PHASE9_LANE_KEY=P9-L16`
- `PHASE9_SURVEYED_COMMIT=fe8a43ea2e186da0da152198b571dff57ea3c38c`
- scope: lifecycle starter, bounded return-probe bookkeeping, direct embedded sample replay, the bounded pre-init `configureMaxactive()` starter contract, explicit `phase9-runtime-kretprobe-{sample,module,diff,loader,survey}-tests` shared-build legs, a manifest-backed survey packet, a loader-handoff scaffold, explicit shared `command_name` preservation, a landed shared loader-request binding, and survey-manifest closure only
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
  - `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `samples/kprobes/kretprobe_example.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already had runtime pilot starters for atomic64, bitmap, and trace-events, but it still had no kretprobe lane foothold. This slice lands the smallest honest kretprobe follow-on step: a sample-backed lifecycle scaffold that models bounded per-instance private entry timestamps, return values, duration, missed-instance bookkeeping, a direct embedded sample replay, and the loader handoff plan plus shared loader-request binding without claiming `register_kretprobe()` or loadable-module parity.

The same shared runtime-loader blocker that still governs the bounded kretprobe packet also sits underneath the freeze map's study boundary. `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`, so this slice may document the pre-execution handoff, rollback, and shared request facts, but it must not imply workqueue parity, scheduler transport ownership, or any Architecture Council-approved status change for that study-only anchor.

No parity scorecard entry or Architecture Council status-change request is attached to this lane. The shipped evidence remains limited to the bounded starter, loader handoff, shared binding, and survey-manifest closure packet while the broader runtime loader stays pre-execution.

## Landed starter surface

- module descriptor metadata naming the `samples/kprobes/kretprobe_example.c` anchor
- guarded lifecycle transitions for `cold`, `initialized`, `selftest_complete`, and `exited`
- a retargetable symbol-name starter that defaults to `kernel_clone`, matches the Linux sample's module parameter, and rejects retargets at or above the fixed `KSYM_NAME_LEN`-style 512-byte ceiling
- a pre-init `configureMaxactive()` starter contract that keeps `maxactive` reviewable as bounded starter-owned state, accepts only `1...default_maxactive` before init, and rejects post-init retunes so the pilot does not imply live module-parameter mutation
- bounded entry-handler skip behavior for kernel-thread-like contexts, bounded per-instance private entry-timestamp tracking across concurrent active probes, return-value and duration bookkeeping, and explicit `nmissed` tracking
- a stable `RuntimeKretprobeSummary` view exposing lifecycle stage, `init_runs`, `selftest_runs`, `exit_runs`, active-instance state, and the latest bounded probe results without requiring direct field access on the sample
- a direct post-selftest replay proof that `selftest_complete` still permits bounded entry-timestamp, return-value, duration, and `nmissed` replay while `RuntimeKretprobeSummary` stays explicit until exit
- a failed-exit rollback proof that public `runFailedExitRecoveryReplay()` keeps `OutstandingProbeInstance` from mutating lifecycle stage, summary counters, `active_instances`, or `entry_timestamp_armed` until the outstanding return path is replayed and exit succeeds
- a direct embedded sample replay in `samples/zigux/runtime_kretprobe.zig` that keeps lifecycle accounting, concurrent timestamp handling, symbol-cap guards, and no-substrate bookkeeping reviewable without routing every starter check through the separate module gate
- a dedicated `runtime_kretprobe_diff` gate that replays skip, elapsed-time, and missed-instance expectations from `samples/kprobes/kretprobe_example.c`
- a bounded `runtime_kretprobe_loader` scaffold that makes the planned `register_kretprobe()` and `unregister_kretprobe()` lifecycle, entry or exit symbol names, and per-instance private-data size explicit while the runtime substrate remains unavailable
- a bounded shared `command_name` preservation check in `samples/zigux/runtime_kretprobe_loader.zig` that keeps a synthetic non-null `perf-runtime-kretprobe` loader request reviewable through both `waiting_on_runtime_substrate` and `released_without_substrate` without claiming live argv policy or runtime execution
- the same loader scaffold keeps the no-substrate rollback path explicit through `releaseSharedRuntimeLoadWithoutSubstrate()` and the shared `released_without_substrate` request state, so fallback review does not rely on prose alone
- a landed shared runtime-loader request binding under `zigux/kernel/runtime_loader.zig` that consumes the kretprobe loader handoff through explicit allocator posture, staged entry and exit symbols, and a machine-checkable kretprobe payload
- dedicated Phase 9 tests and manifest coverage wired into the shared `zigux/tests/phase9_build.zig` gate through the explicit `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-diff-tests`, `phase9-runtime-kretprobe-loader-tests`, and `phase9-runtime-kretprobe-survey-tests` legs plus the manifest-backed survey packet

## Non-goals

This slice does not yet claim:

- a kernel-loadable Zigux kretprobe module
- real `register_kretprobe()` or `unregister_kretprobe()` parity
- architecture-specific register extraction parity for `regs_return_value()`
- shared runtime-loader command-name, argv-policy, or environment-derived activation controls
- parity or ownership for `kernel/workqueue.c`
- any freeze-map status change for the scheduler-facing workqueue boundary without an Architecture Council decision

## Gates

1. run the focused kretprobe survey replay
- `zig test zigux/tests/runtime_kretprobe_survey.zig`
- `make -C zigux phase9-kretprobe-survey`
- this focused replay keeps the manifest-backed kretprobe survey packet reviewable beside the direct sample, module, diff, and loader legs without implying shared runtime-loader controls or loadable-module parity

2. run the dedicated Phase 9 build
- `zig build test --build-file zigux/tests/phase9_build.zig --summary all`
- this shared build keeps the dedicated kretprobe sample, module, diff, loader, and survey legs explicit through `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-diff-tests`, `phase9-runtime-kretprobe-loader-tests`, and `phase9-runtime-kretprobe-survey-tests`

3. run the convenience target
- `make -C zigux phase9`

## Next bounded step

Stay in the Phase 9 runtime kretprobe lane and keep broader work blocked until the shared runtime-loader control surface grows a real owner for command-name, argv-policy, or environment-derived activation handling, rather than reopening already-landed sample, survey, manifest, loader, module, or diff scaffolding, while keeping `kernel/workqueue.c` in study-only status unless the Architecture Council explicitly reopens that anchor.
