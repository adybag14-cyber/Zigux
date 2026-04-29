# Phase 9 Runtime Kretprobe Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/kprobes/kretprobe_example.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-survey`
- `PHASE9_LANE_KEY=P9-L16`
- `PHASE9_SURVEYED_COMMIT=9c4fb93b29fd1b1c5dabb4cff3017a9ad5d9f1be`
- surveyed inspected `master` head: `9c4fb93b29fd1b1c5dabb4cff3017a9ad5d9f1be`
- scope: survey manifest, manifest-backed delivery catalog and ownership map, a direct embedded sample replay, dedicated survey and diff gates, the bounded loader-handoff scaffold, explicit no-substrate rollback evidence, the landed shared loader-request binding, explicit `phase9-runtime-kretprobe-{sample,module,diff,loader,survey}-tests` shared-build legs, and the lane-level note that records the remaining broader runtime-control blocker plus the exact Phase 9 roadmap gap it still leaves open
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
  - `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`
  - `Documentation/zigux/phase9-runtime-loader-gap-survey.md`

## Why this slice exists

The roadmap names `samples/kprobes/kretprobe_example.c` twice: first as a Phase 5 sample-reference anchor and later as a Phase 9 runtime pilot anchor. This lane stays strictly inside the Phase 9 reading of that roadmap entry.

The survey artifacts now advance to `P9-L16` because the live packet has grown beyond the original `P9-L13` survey-only shape: `master` now carries the `runtime_kretprobe` starter, the direct embedded sample replay, dedicated module tests, diff gate, loader-handoff scaffold, and the shared runtime-loader request binding. This keeps the roadmap-aligned review history honest while recording the full live packet that reviewers actually ship.

The live repo now has a bounded `runtime_kretprobe` starter, a direct embedded sample replay, dedicated module tests, a dedicated diff gate, a bounded loader-handoff scaffold, a shared loader-request binding under `zigux/kernel/runtime_loader.zig`, and shared Phase 9 build coverage, so this survey note keeps that shipped packet reviewable through a manifest-backed delivery catalog and ownership map instead of leaving the sample and shared-build surface implied.

## Survey findings

- `samples/kprobes/kretprobe_example.c` is present on `master` at 108 lines.
- the Linux sample is module-oriented, centered on `register_kretprobe`, `unregister_kretprobe`, `entry_handler`, `ret_handler`, `maxactive`, and `nmissed`.
- the live repo now ships `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_diff.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, a shared loader-request binding in `zigux/kernel/runtime_loader.zig`, and the shared `zigux/tests/phase9_build.zig` coverage for this lane.
- against the Phase 9 roadmap feature list, the live packet now lands the explicit selftest-hook surface, direct embedded sample replay, and reviewable starter lifecycle transitions, but it still does not satisfy `first loadable Zigux runtime modules` or `runtime module lifecycle parity` because the shared runtime-loader control surface and real `register_kretprobe()` or `unregister_kretprobe()` execution remain blocked.
- the current bounded symbol surface remains sample-side rather than Kconfig-backed: `samples/zigux/runtime_kretprobe.zig` still defaults `symbol_name` to `kernel_clone`, only allows retargeting before init, and does not expose any `CONFIG_` or `Kconfig` gate in this packet.
- the bounded starter keeps the Linux sample's fixed `KSYM_NAME_LEN` symbol buffer explicit by rejecting symbol retargets at or above 512 bytes, so the pilot does not silently widen the module-parameter contract while runtime loading is still blocked.
- the bounded starter keeps per-instance private entry timestamps explicit under concurrent active probes, matching the Linux anchor's `struct my_data` shape more closely without claiming real `kretprobe_instance` substrate support.
- the bounded starter exposes a stable `RuntimeKretprobeSummary` surface for lifecycle stage, `init_runs`, `selftest_runs`, `exit_runs`, active-instance state, and the latest bounded probe results, so selftest and post-exit review does not depend on reading sample internals directly.
- the direct embedded sample replay now keeps lifecycle accounting, concurrent timestamp handling, symbol-cap guards, and missed-instance bookkeeping reviewable inside `samples/zigux/runtime_kretprobe.zig`, so the starter packet no longer relies on the separate module gate as its only executable sample evidence.
- the loader scaffold makes the no-substrate rollback path explicit: `releaseSharedRuntimeLoadWithoutSubstrate()` returns the shared runtime-loader request surface in `released_without_substrate` state, so the current fallback path is reviewable without implying live `register_kretprobe()` or `unregister_kretprobe()` execution.
- the sample-side loader and shared request contract still keep symbol or command handling explicit but narrow: `samples/zigux/runtime_kretprobe_loader.zig` and `zigux/kernel/runtime_loader.zig` still carry `register_kretprobe`, `unregister_kretprobe`, the selected `symbol_name`, `requires_runtime_substrate`, `provides_selftest_hook`, and an explicit `command_name = null` handoff instead of any real export-parity or runtime command surface.
- the shared `zigux/tests/phase9_build.zig` entrypoint now remains explicit about the dedicated `phase9-runtime-kretprobe-sample-tests`, `phase9-runtime-kretprobe-module-tests`, `phase9-runtime-kretprobe-diff-tests`, `phase9-runtime-kretprobe-loader-tests`, and `phase9-runtime-kretprobe-survey-tests` legs, so the shipped replay packet is reviewable without reading the build file by eye.
- broader shared runtime-loader controls are still missing, so the starter intentionally stops at bounded lifecycle, bookkeeping, loader-handoff behavior, and a machine-checkable shared request shape rather than claiming real module registration parity; command-name, argv-policy, or environment-derived activation handling still stay blocked in the shared loader-gap note.
- a focused current-head grep across `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/tests/runtime_kretprobe_manifest.json`, `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, and `zigux/tests/phase9_build.zig` still returns no `CONFIG_`, `Kconfig`, `EXPORT_SYMBOL`, or `symbol export ¶»§q«^