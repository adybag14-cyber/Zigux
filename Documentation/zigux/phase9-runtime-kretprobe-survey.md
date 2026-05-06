# Phase 9 Runtime Kretprobe Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/kprobes/kretprobe_example.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-survey`
- `PHASE9_SURVEYED_COMMIT=248bfeaa7f2beddc283c3e398fc36fec3c841242`
- scope: survey manifest, starter sample, dedicated module, survey, and diff gates, the bounded loader-handoff scaffold, the shared runtime-loader facade, allocator/init-flow contract replay, and shared-request bridge with landed selftest-hook parity, shared Phase 9 build wiring, and the lane-level note that now records the landed runtime starter plus the remaining substrate blocker
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`
  - `zigux/tests/runtime_loader_allocator_init_flow.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`

## Why this slice exists

The roadmap names `samples/kprobes/kretprobe_example.c` twice: first as a Phase 5 sample-reference anchor and later as a Phase 9 runtime pilot anchor. This lane stays strictly inside the Phase 9 reading of that roadmap entry.

The survey artifacts now stay anchored to the active `P9-L17` packet while still recording the full live runtime kretprobe review surface. That keeps the packet identity honest after the landed starter, dedicated module tests, diff gate, shared-request bridge, and loader-handoff scaffold all moved this pilot beyond the older survey-only footing.

The live repo now has a bounded `runtime_kretprobe` starter, dedicated module tests, a dedicated diff gate, a bounded loader-handoff scaffold, the shared runtime-loader facade and allocator/init-flow replay, and shared Phase 9 build coverage, so this survey note should reflect the landed pilot review surface instead of still reading like the lane is waiting on sample-level differential checks.

## Survey findings

- `samples/kprobes/kretprobe_example.c` is present on `master` at 108 lines.
- the Linux sample is module-oriented, centered on `register_kretprobe`, `unregister_kretprobe`, `entry_handler`, `ret_handler`, `maxactive`, and `nmissed`.
- the live repo now ships `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_diff.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, and the shared `zigux/tests/phase9_build.zig` coverage for this lane.
- the landed loader scaffold keeps `register_kretprobe` and `unregister_kretprobe` explicit as metadata-only labels inside a pre-execution handoff plan, together with the retargeted symbol name and private-data size, rather than claiming live initcall or runtime registration behavior.
- the loader handoff now refuses to prepare a shared request while an entry timestamp is still armed or a probe instance is still active, keeping the metadata-only registration snapshot idle before the shared runtime-loader request begins.
- the bounded runtime kretprobe sample and dedicated module tests now also keep failed-exit state explicit: if `exit()` is attempted while an active probe is still armed, the initialized or selftest-complete stage stays intact until the active probe drains instead of silently widening into a partial teardown.
- the shared runtime-loader packet is now live on `master`: `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, the focused `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig` shard, and `make -C zigux phase9` all keep selftest-hook parity on pending load plans, allocator handoff, init-flow counts, the release-without-substrate path, and shared request-surface proof explicit for the shipped four-pilot bundle.
- runtime substrate work is still missing, so the starter intentionally stops at bounded lifecycle, bookkeeping, metadata-only registration labels, idle registration snapshot checks, failed-exit state retention until the active probe drains, and loader-handoff behavior rather than claiming real module registration parity.

## Recorded gaps

The survey manifest now records:

- the landed `phase9-build-gate`
- the landed `runtime-kretprobe-survey-gate`
- the landed `runtime-kretprobe-sample-module`
- the landed `runtime-kretprobe-module-tests`
- the landed `runtime-kretprobe-diff-gate`
- the landed `runtime-kretprobe-loader-plan`
- the still-blocked shared runtime substrate handoff

This keeps the lane concrete without pretending that Zigux already has real `register_kretprobe()` substrate support.

## Gates

1. run the focused shared runtime-loader shard
- `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

2. run the dedicated Phase 9 survey gate
- `zig build test --build-file zigux/tests/phase9_build.zig`

3. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice does not yet claim:

- a side-by-side Phase 5 `samples/zigux/kretprobe_example.zig` reference port
- architecture-specific `pt_regs` handling or real return-value extraction parity
- loadable-module init and exit parity for kretprobes inside Zigux

## Next bounded step

Stay in the Phase 9 runtime kretprobe lane and keep broader work blocked until a shared runtime loader substrate can consume the bounded `register_kretprobe()` and `unregister_kretprobe()` handoff plan.
