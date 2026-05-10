# Phase 9 Runtime Kretprobe Survey
This document tracks the bounded Phase 9 runtime pilot-module survey around `samples/kprobes/kretprobe_example.c`.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-kretprobe-survey`
- `PHASE9_SURVEYED_COMMIT=2a1851e145a648f0792e2bba2fee100e9884a1de`
- lane: `P9-L13`
- scope: dedicated Phase 9 runtime kretprobe survey truthfulness, explicit adjacency to the separate shared runtime-loader lane, and blocked-state evidence for initcall and metadata-only registration parity while current repo reality stays below a loadable runtime substrate claim
- live reminder surfaces:
  - `Documentation/zigux/phase9-runtime-kretprobe-survey.md`
  - `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`
  - `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- planned Phase 9 anchors when the starter packet returns on current `master`:
  - `samples/zigux/runtime_kretprobe.zig`
  - `samples/zigux/runtime_kretprobe_loader.zig`
  - `zigux/tests/runtime_kretprobe_module.zig`
  - `zigux/tests/runtime_kretprobe_manifest.json`
  - `zigux/tests/runtime_kretprobe_survey.zig`
  - `zigux/tests/runtime_kretprobe_diff.zig`
  - `zigux/tests/phase9_build.zig`

The Phase 9 roadmap explicitly names `samples/kprobes/kretprobe_example.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The Phase 9 runtime kretprobe family also stays separate from the already-approved non-runtime Phase 5 reference-sample packet: any later return of `samples/zigux/runtime_kretprobe.zig` and `samples/zigux/runtime_kretprobe_loader.zig` would still belong to the separate runtime family rooted in `samples/kprobes/kretprobe_example.c`, not to the approved `samples/zigux/kretprobe_example.zig` cue under `Documentation/zigux/phase5-kretprobe-sample-survey.md`.

## Survey findings
- `samples/kprobes/kretprobe_example.c` is present on current `master` at 108 lines.
- current contents reads for `samples/zigux/runtime_kretprobe.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, `zigux/tests/runtime_kretprobe_module.zig`, `zigux/tests/runtime_kretprobe_manifest.json`, `zigux/tests/runtime_kretprobe_survey.zig`, `zigux/tests/runtime_kretprobe_diff.zig`, and `zigux/tests/phase9_build.zig` now return not found on current `master`.
- current contents reads for the adjacent shared loader packet `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, and the focused shared replay route also return not found on current `master`.
- because those pilot-local and shared-loader files are currently missing, this survey must not claim a landed loader scaffold, landed prepared-request lifecycle proof, live `register_kretprobe()` or `unregister_kretprobe()` handoff review, or a runnable shared `make -C zigux phase9` replay route from present repo evidence.
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` is the current truthful shared owner map: it records the missing shared runtime-loader family as a repo-reality blocker and keeps later reminder-surface narrowing ordered one shared note at a time.
- the honest current review state is reminder-only: the docs packet still records what this lane is supposed to prove, but current `master` does not expose the dedicated kretprobe starter or shared loader files needed to claim that the bounded lifecycle, bookkeeping, metadata-only registration labels, or init and exit handoff cues are presently landed.

## Roadmap gap vs current pilot
- the Phase 9 roadmap still asks for first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`.
- current repo reality does not presently expose the dedicated runtime kretprobe starter or the shared runtime-loader packet that earlier reminder surfaces described.
- the honest current state is `phase9_kretprobe_and_shared_loader_packet_missing_on_current_master`.
- the missing capability is not just a shared runtime substrate; it is first the return of the concrete kretprobe and shared-loader review packet on current `master`, and then the later shared substrate that could turn the bounded `register_kretprobe()` and `unregister_kretprobe()` handoff plan into a real loadable module path.
- the blocked deliverable remains loadable Phase 9 runtime kretprobe pilot module parity.

## Recorded gaps
This survey currently records:
- the Phase 9 roadmap anchor under `samples/kprobes/kretprobe_example.c`
- the still-visible reminder packet under `Documentation/zigux/phase9-runtime-kretprobe-survey.md`, `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`, and `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- the missing dedicated runtime kretprobe starter family on current `master`
- the missing shared runtime-loader family on current `master`
- the blocked loadable runtime substrate follow-through

## Next bounded step
Stay in the Phase 9 runtime kretprobe lane family and keep broader work blocked until current `master` either restores the dedicated runtime kretprobe and shared runtime-loader file family or narrows the remaining shared reminder surfaces so they stop presenting those missing paths as landed replay evidence.

## Gates
1. current truthfulness gate
   - keep this survey, `Documentation/zigux/phase9-runtime-kretprobe-module-slice.md`, and `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md` aligned on the same missing-file reality
2. shared loader follow-up, only if the shared file family returns
   - `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`
   - `make -C zigux phase9-runtime-loader-shared-tests`
3. pilot-family follow-up, only if the dedicated kretprobe packet returns
   - `zig build phase9-runtime-kretprobe-tests --build-file zigux/tests/phase9_build.zig`
   - `make -C zigux phase9-runtime-kretprobe-test`
4. bundled Phase 9 replay, only if the shared build file returns
   - `zig build test --build-file zigux/tests/phase9_build.zig`
   - `make -C zigux phase9`
