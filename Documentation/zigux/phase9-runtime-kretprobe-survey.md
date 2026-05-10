# Phase 9 Runtime Kretprobe Survey
This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/kprobes/kretprobe_example.c`.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-survey`
- `PHASE9_SURVEYED_COMMIT=2a1851e145a648f0792e2bba2fee100e9884a1de`
- lane: `P9-L13`
- scope: survey manifest, starter sample, dedicated module, survey, and diff gates, the bounded loader-handoff scaffold, the focused `phase9-runtime-kretprobe-tests` build step, and explicit adjacency to the separate shared runtime-loader lane that owns the facade, contract, allocator/init-flow replay, focused shared runtime-loader shard, and the workflow-backed `make -C zigux phase9` route
- product boundary:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
  - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`

The Phase 9 roadmap explicitly names `samples/kprobes/kretprobe_example.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live Phase 9 runtime kretprobe packet also stays separate from the already-approved non-runtime Phase 5 reference-sample packet: `samples/zigux/runtime_kretprobe.zig` and `samples/zigux/runtime_kretprobe_loader.zig` remain the separate runtime family rooted in `samples/kprobes/kretprobe_example.c`, not a second owner for the already-approved `samples/zigux/kretprobe_example.zig` cue under `Documentation/zigux/phase5-kretprobe-sample-survey.md`.

The shared sample-root catalog at `samples/zigux/README.md` keeps the approved Phase 5 anchor explicit through `samples/zigux/kretprobe_example.zig` while listing the runtime kretprobe pair only under the separate Phase 9 runtime pilot family.

## Survey findings
- `samples/kprobes/kretprobe_example.c` is present on `master` at 108 lines.
- the live repo now ships `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_diff.zig`, `zigux/tests/runtime_kretprobe_survey.zig`, and the shared `zigux/tests/phase9_build.zig` coverage for this lane.
- the landed loader scaffold keeps `register_kretprobe` and `unregister_kretprobe` explicit as metadata-only labels inside a pre-execution handoff plan.
- explicit init and exit symbol names remain review-only handoff data, so this packet still does not claim live `module_init()`, `module_exit()`, or kernel initcall-order parity.
- the loader handoff now refuses to prepare a shared request while an entry timestamp is still armed or a probe instance is still active, keeping the metadata-only registration snapshot idle before the shared runtime-loader request begins.
- the bounded runtime kretprobe sample and dedicated module tests now also keep failed-exit state explicit: if `exit()` is attempted while an active probe is still armed, the initialized or selftest-complete stage stays intact until the active probe drains instead of silently widening into a partial teardown.
- the loader handoff also keeps the loader-owned prepared handoff snapshot explicit: once `prepare()` or `prepareSharedRequest()` captures an idle registration snapshot, later sample mutation or late selftest activity can be inspected separately but must not rewrite that parked handoff plan before runtime-substrate review.
- the loader handoff now also fail-closes prepared shared-request selftest-hook drift plus direct initialized-stage and selftest-complete shared-plan selftest-hook drift before any live registration claim, and it keeps loader-versus-shared-request release state synchronized when `releaseSharedWithoutSubstrate()` is attempted before the shared request reaches `waiting_on_runtime_substrate`.
- the live repo also carries `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, and the focused `phase9-runtime-loader-shared-tests` build step, so allocator handoff, init-flow counts, release-without-substrate behavior, and shared-request drift stay reviewable beside the kretprobe starter packet instead of hiding only inside the shared build.
- the newer `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` now keeps those shared `runtime_loader`, `runtime_loader_contract`, `runtime_loader_allocator_init_flow`, and `phase9-runtime-loader-shared-tests` surfaces under the separate shared loader lane rather than inside the kretprobe pilot lane.
- the shared `zigux/kernel/runtime_loader.zig` facade remains a review-only Phase 9 packet under the freeze map's study-only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` boundary, so this lane keeps the kretprobe handoff reviewable without claiming scheduler-facing substrate closure or a freeze-map status change.
- runtime substrate work is still missing, so the starter intentionally stops at bounded lifecycle, bookkeeping, metadata-only registration labels, review-only init and exit symbol evidence, idle registration snapshot checks, failed-exit state retention until the active probe drains, loader-owned prepared handoff snapshot checks, and loader-handoff behavior rather than claiming real module registration parity.

## Roadmap gap vs current pilot
- the Phase 9 roadmap asks for first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`.
- the landed kretprobe packet satisfies the bounded selftest-hook and lifecycle-evidence part of that roadmap, but it does not yet satisfy the loadable-module part.
- the honest current state is `starter_landed_without_loadable_runtime_substrate`.
- the missing capability is a shared runtime substrate that can turn the bounded `register_kretprobe()` and `unregister_kretprobe()` handoff plan into a real loadable module path.
- the blocked deliverable is loadable Phase 9 runtime kretprobe pilot module parity.

## Recorded gaps
The survey manifest now records:
- the landed `phase9-build-gate`
- the landed `runtime-kretprobe-survey-gate`
- the landed `runtime-kretprobe-sample-module`
- the landed `runtime-kretprobe-module-tests`
- the landed `runtime-kretprobe-diff-gate`
- the landed `runtime-kretprobe-loader-plan`
- the landed `runtime-kretprobe-loader-contract`
- the landed `runtime-kretprobe-loader-init-flow`
- the still-blocked shared runtime substrate handoff

## Next bounded step
Stay in the Phase 9 runtime kretprobe lane and keep broader work blocked until a shared runtime loader substrate can consume the bounded `register_kretprobe()` and `unregister_kretprobe()` handoff plan.

## Gates
1. run the focused shared runtime-loader shard
   - `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`
2. run the focused shared runtime-loader convenience target
   - `make -C zigux phase9-runtime-loader-shared-tests`
3. run the focused runtime kretprobe lane step
   - `zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig`
4. run the focused runtime kretprobe convenience target
   - `make -C zigux phase9-runtime-kretprobe-test`
5. run the dedicated Phase 9 build
   - `zig build test --build-file zigux/tests/phase9_build.zig`
6. run the convenience target
   - `make -C zigux phase9`
