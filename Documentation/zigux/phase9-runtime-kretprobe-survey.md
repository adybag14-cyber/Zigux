# Phase 9 Runtime Kretprobe Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/kprobes/kretprobe_example.c`.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-survey`
- `PHASE9_LANE_KEY=P9-L13`
- `PHASE9_SURVEYED_AT=2026-05-12`
- scope: survey manifest, dedicated runtime survey gate, directly readable module and loader packet, focused shared-request lifecycle proof, failed-exit retention until drain, maxactive-overflow retention until drain, and the lane-level review note that keeps the still-unlanded shared runtime-loader substrate explicit without claiming loadable-module parity while current direct contents reads still fail to confirm the dedicated sample root and diff gate named by the broader build packet
- product boundary:
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
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

The live repo still directly exposes a bounded `runtime_kretprobe` review packet through the manifest, the dedicated module test, the sample-side loader scaffold, and the shared request-surface proofs. Direct current-`master` contents reads from this environment do not currently confirm `samples/zigux/runtime_kretprobe.zig` or `zigux/tests/runtime_kretprobe_diff.zig`, so this survey note exists to keep the family honest about the lifecycle and handoff evidence that is directly readable today and the tracing-proof slice that still needs restoration.

`Documentation/zigux/freeze-map.md` keeps the shared Phase 9 runtime-loader packet review-only beside `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`, so this survey may describe the bounded in-memory handoff plan, the sample-side loader scaffold, and the shared runtime-loader facade plus allocator/init-flow contract replay, but it must not imply live `register_kretprobe` parity, scheduler-facing substrate closure, or any freeze-map status change.

## Survey Findings
- `samples/kprobes/kretprobe_example.c` remains the Phase 9 runtime pilot anchor for this lane.
- the live repo still directly exposes `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_manifest.json`, the focused `zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig` replay, the matching `make -C zigux phase9-runtime-kretprobe-test` convenience route, and the shared `zigux/tests/phase9_build.zig` coverage for this lane.
- direct current-`master` contents reads from this environment do not currently confirm `samples/zigux/runtime_kretprobe.zig` or `zigux/tests/runtime_kretprobe_diff.zig`, so the dedicated tracing-proof portion of this lane should be treated as blocked review debt instead of claimed as directly readable landed proof.
- the currently readable packet still keeps selftest-hook behavior, skipped-kernel-thread accounting, missed-instance accounting, duration tracking, and lifecycle transitions reviewable through the dedicated module test, the loader scaffold, and the shared allocator/init-flow replay without claiming a real loadable runtime module.
- the landed module packet keeps failed-exit state explicit until the active probe drains, and it keeps maxactive-overflow state explicit until the active probe drains, so the current directly readable module packet does not overstate exit or pressure recovery behavior.
- the bounded sample-side loader scaffold now keeps both initialized-stage and selftest-complete shared-request handoff snapshots explicit, including the proof that an initialized prepared request stays pinned even if later sample selftest activity runs before the shared runtime-loader handoff.
- the same loader packet also keeps the selftest-complete prepared snapshot explicit across later exit activity, along with prepared selftest-hook drift rejection, prepared shared-plan drift rejection, and release-without-substrate behavior.
- `zigux/tests/runtime_loader_allocator_init_flow.zig` now keeps the shared allocator/init-flow replay explicit for the kretprobe family beside the other landed runtime pilot families.
- the shared `zigux/kernel/runtime_loader.zig` facade and `zigux/kernel/runtime_loader_contract.zig` contract remain a review-only Phase 9 packet under the freeze map's study-only boundary, so this lane keeps the handoff proof explicit without claiming scheduler-facing substrate closure or a freeze-map status change.
- runtime substrate work is still missing, so the lane intentionally stops at bounded lifecycle and loader-handoff behavior rather than claiming real `register_kretprobe` or `unregister_kretprobe` execution parity.

## Roadmap Gap Vs Current Pilot
- the Phase 9 roadmap asks for first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`.
- the directly readable kretprobe packet now satisfies the bounded selftest-hook and lifecycle-evidence part of that roadmap through the manifest-backed module, loader, and shared allocator/init-flow proofs.
- the manifest-backed intended state still reads as `starter_landed_without_loadable_runtime_substrate`, but the directly readable current-`master` packet is narrower because `samples/zigux/runtime_kretprobe.zig` and `zigux/tests/runtime_kretprobe_diff.zig` are not currently confirmed through contents reads from this environment.
- the immediate packet-local follow-through is restoring that directly readable sample-root and diff-gate tracing packet before this survey switches back to broader landed wording.
- the next shared blocker after that remains the runtime-loader substrate that could turn the bounded `register_kretprobe` and `unregister_kretprobe` handoff plan into a real loadable runtime-module path.

## Footer
