# Phase 9 Runtime Kretprobe Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/kprobes/kretprobe_example.c`.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-survey`
- `PHASE9_LANE_KEY=P9-L13`
- `PHASE9_SURVEYED_AT=2026-05-11`
- scope: survey manifest, dedicated runtime survey gate, landed sample-backed module starter, landed module and diff gates, the bounded sample-side loader scaffold, the shared runtime-loader facade plus allocator/init-flow contract replay, initialized-stage shared-request snapshot stability, selftest-complete shared-request snapshot stability across later exit activity, prepared selftest-hook and shared-plan drift proofs, failed-exit retention until drain, maxactive-overflow retention until drain, and the lane-level review note that keeps the still-unlanded shared runtime-loader substrate explicit without claiming loadable-module parity
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`
  - `zigux/tests/runtime_loader_allocator_init_flow.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
  - `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`
  - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`

## Why This Slice Exists

The Phase 9 roadmap explicitly names `samples/kprobes/kretprobe_example.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo already ships a bounded `runtime_kretprobe` starter, dedicated module tests, a dedicated diff gate, and a sample-side loader scaffold with shared request-surface proofs. This survey note exists so the current review packet stays explicit on `master` instead of reading like the lane still stops before the landed lifecycle, selftest-hook, and shared-request evidence.

`Documentation/zigux/freeze-map.md` keeps the shared Phase 9 runtime-loader packet review-only beside `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`, so this survey may describe the bounded in-memory pilot, the sample-side loader scaffold, and the shared runtime-loader facade plus allocator/init-flow contract replay, but it must not imply live `register_kretprobe` parity, scheduler-facing substrate closure, or any freeze-map status change.

## Survey Findings
- `samples/kprobes/kretprobe_example.c` remains the Phase 9 runtime pilot anchor for this lane.
- the live repo now ships `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_diff.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, the focused `zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig` replay, the matching `make -C zigux phase9-runtime-kretprobe-test` convenience route, and the shared `zigux/tests/phase9_build.zig` coverage for this lane.
- the bounded starter keeps selftest-hook behavior, skipped-kernel-thread accounting, missed-instance accounting, duration tracking, and lifecycle transitions reviewable without claiming a real loadable runtime module.
- the landed module packet keeps failed-exit state explicit until the active probe drains, and it keeps maxactive-overflow state explicit until the active probe drains, so the current sample and module packet does not overstate exit or pressure recovery behavior.
- the bounded sample-side loader scaffold now keeps both initialized-stage and selftest-complete shared-request handoff snapshots explicit, including the proof that an initialized prepared request stays pinned even if later sample selftest activity runs before the shared runtime-loader handoff.
- the same loader packet also keeps the selftest-complete prepared snapshot explicit across later exit activity, along with prepared selftest-hook drift rejection, prepared shared-plan drift rejection, and release-without-substrate behavior.
- `zigux/tests/runtime_loader_allocator_init_flow.zig` now keeps the shared allocator/init-flow replay explicit for the kretprobe family beside the other landed runtime pilot families.
- the shared `zigux/kernel/runtime_loader.zig` facade and `zigux/kernel/runtime_loader_contract.zig` contract remain a review-only Phase 9 packet under the freeze map's study-only boundary, so this lane keeps the handoff proof explicit without claiming scheduler-facing substrate closure or a freeze-map status change.
- runtime substrate work is still missing, so the lane intentionally stops at bounded lifecycle, selftest-hook, differential, and loader-handoff behavior rather than claiming real `register_kretprobe` or `unregister_kretprobe` execution parity.

## Roadmap Gap Vs Current Pilot
- the Phase 9 roadmap asks for first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`.
- the landed kretprobe packet now satisfies the bounded selftest-hook and lifecycle-evidence part of that roadmap, including prepared shared-request stability at both initialized and selftest-complete handoff points.
- the honest current state is still `starter_landed_without_loadable_runtime_substrate`.
- the next real blocker remains the shared runtime-loader substrate that could turn the bounded `register_kretprobe` and `unregister_kretprobe` handoff plan into a real loadable runtime-module path.

## Footer
