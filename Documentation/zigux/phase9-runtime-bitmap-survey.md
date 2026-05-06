# Phase 9 Runtime Bitmap Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `lib/test_bitmap.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-survey`
- `PHASE9_LANE_KEY=P9-L05`
- `PHASE9_SURVEYED_COMMIT=b2dc39dbae0efeacdb7a3ea03c6c95f904a180d9`
- scope: survey manifest, dedicated runtime survey gate, landed sample-backed module starter, landed module gate, landed diff gate, landed loader scaffold, the shared runtime-loader facade and allocator/init-flow contract replay, the focused top-bit companion replay, and the lane-level review note that keeps the remaining roadmap blocker explicit without claiming loadable-module parity
- product boundary:
  - `samples/zigux/runtime_bitmap.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `samples/zigux/runtime_bitmap_top_bit_build.zig`
  - `samples/zigux/runtime_bitmap_top_bit_contract.zig`
  - `zigux/tests/runtime_bitmap_manifest.json`
  - `zigux/tests/runtime_bitmap_survey.zig`
  - `zigux/tests/runtime_bitmap_module.zig`
  - `zigux/tests/runtime_bitmap_diff.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `zigux/kernel/runtime_loader_contract.zig`
  - `zigux/tests/runtime_loader_allocator_init_flow.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/Makefile`
  - `Documentation/zigux/phase9-runtime-bitmap-survey.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/test_bitmap.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo originally needed a survey-shaped review anchor that could record what the runtime bitmap lane had already shipped versus what still depends on a shared runtime substrate. This note stays in place after the bounded starter sample, module gate, diff gate, loader scaffold, shared runtime-loader contract replay, and focused top-bit companion gate landed, so the lane can keep comparing the current pilot-module surface against the roadmap without pretending that Zigux already has a real loadable bitmap module.

This survey note is also not a Phase 5 sample-root approval: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and the focused `samples/zigux/runtime_bitmap_top_bit_{build,contract}.zig` companion replay stay here as the separate Phase 9 runtime bitmap family rooted in `lib/test_bitmap.c`, not as a fifth approved Phase 5 reference idiom under `samples/zigux/`.
The shared sample-root catalog at `samples/zigux/README.md` keeps the approved Phase 5 anchors limited to `bytestream_fifo.zig`, `kobject_example.zig`, `kretprobe_example.zig`, and `trace_events_sample.zig`, while listing the runtime bitmap pair plus the focused top-bit companion replay only under the separate Phase 9 runtime pilot family.

## Survey findings

- `lib/test_bitmap.c` is present on `master` at 1567 lines.
- the live Phase 9 bitmap lane already carried dedicated runtime bitmap test files before this survey note landed.
- the live Phase 9 bitmap lane already carried a sample-backed runtime bitmap starter under `samples/zigux/`.
- the live repo already carried shared `zigux/tests/phase9_build.zig` wiring and a bitmap module-slice note before this survey note landed.
- the shared `zigux/tests/phase9_build.zig` gate still carries the direct `phase9-runtime-bitmap-sample-tests` leg, so the starter sample replay stays explicit beside the bitmap module, diff, loader, and survey gates.
- the shared `zigux/tests/phase9_build.zig` gate now also carries the focused `phase9-runtime-bitmap-top-bit-tests` leg, so the highest-valid-bit replay no longer sits outside the shared Phase 9 runtime bitmap packet.
- the live repo now also carries the shared runtime-loader facade, contract, allocator/init-flow replay, and the focused `phase9-runtime-loader-shared-tests` build step that keep the bitmap loader handoff packet reviewable beside the lane-local sample, module, diff, and top-bit gates.
- the live repo still keeps that runtime bitmap family outside the four approved Phase 5 reference samples, so this survey packet stays reviewable as later runtime follow-on evidence rather than Phase 5 sample closure.
- the shared `samples/zigux/README.md` catalog still lists the runtime bitmap pair plus the focused top-bit companion replay only under the separate Phase 9 runtime pilot family and keeps the four approved Phase 5 anchors explicit.

## Roadmap snapshot

Against the Phase 9 roadmap requirements, the current runtime bitmap lane now records:

- a landed sample-backed runtime starter with selftest-hook metadata under `samples/zigux/runtime_bitmap.zig`
- a landed sample-side loader scaffold in `samples/zigux/runtime_bitmap_loader.zig`
- a landed focused highest-valid-bit boundary replay under `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- a landed dedicated module gate in `zigux/tests/runtime_bitmap_module.zig`
- a landed dedicated differential gate in `zigux/tests/runtime_bitmap_diff.zig`
- a landed shared runtime-loader facade plus allocator/init-flow contract replay under `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/tests/runtime_loader_allocator_init_flow.zig`
- a remaining blocked live runtime substrate binding, because true runtime-module loading and lifecycle parity still depend on shared runtime substrate pieces that the repo has not started yet

This keeps the survey honest about the difference between the shipped in-memory pilot, the landed shared loader-handoff packet, the landed highest-bit boundary replay, and the still-missing live runtime substrate.

## Direct Sample Checks

The current direct bitmap sample contract is verified through these exact checks:

- summary stability: initializing bits `0`, `5`, `64`, and `70` still yields `first_set=0`, `first_zero=1`, `weight=4`, and `nbits=128`
- descriptor contract: the sample still advertises `name=runtime_bitmap`, `anchor=lib/test_bitmap.c`, `requires_runtime_substrate=true`, and `provides_selftest_hook=true`
- lifecycle and mutation path: the sample still starts cold, rejects selftest before init, records one init run, clears bits `64..65`, adds bits `9..12`, and reaches weight `7` while keeping bit `70`
- copy and selftest path: a second initialized sample can mirror the mutated bitmap, `runSelftest()` still reports the four ordered operation families `clear_set`, `copy`, `summary`, and `lifecycle`, and selftest leaves the bitmap summary unchanged
- loader snapshot stability: after `prepare()` captures the `0,5,64,70` bitmap summary, later sample mutation still leaves the pending loader handoff at `first_set=0`, `first_zero=1`, and `weight=4` even while the live sample moves to `first_set=5`, `first_zero=0`, and `weight=7` before `requestRuntimeLoad()`
- shared-loader contract replay: the loader still imports `runtime_loader`, maps initialized and selftest-complete sample stages into the shared handoff flow, fixes `allocator_handoff=.arena`, keeps `init_runs=1` and `exit_runs=0`, and rejects snapshot drift in module name, allocator handoff, handoff stage, or selftest count
- top-bit boundary replay: the focused companion contract still proves that bit `127` is the highest valid bit, keeps `first_set=127`, `first_zero=0`, `weight=1`, and `nbits=128` explicit for the top-bit-only starter, and rejects `setRange(128, 1)` plus `clearRange(128, 1)` as out of bounds
- review-contract boundary: the direct sample still exposes the ordered review focus `descriptor_and_anchor`, `summary_replay`, and `selftest_lifecycle`; it does not claim standalone `initFromBitList()`, `formatSetBits()`, parse/print differential parity, or a loadable runtime bitmap module on `master`
- exit and error guards: `exit()` still moves the sample to `exited`, later mutation or re-init attempts fail with `InvalidLifecycleTransition`, out-of-range init and range edits fail with `BitRangeOutOfBounds`, zero-length mutations leave the summary unchanged, and `copyFrom()` still rejects cold or exited sources with `InvalidSourceLifecycle`
- diff-gate replay: the bounded parity cases still cover the single-word fill starter, the `79..97` cross-boundary clear cutout, the sparse `10,20,30,40,50,60,80,123` population replay, and the copied `0..108` tail-clear snapshot with `first_zero=109`

## Recorded gaps

The manifest now records:

- the landed `phase9-build-gate`
- the landed `runtime-bitmap-survey-gate`
- the landed `runtime-bitmap-sample-module` starter
- the landed `runtime-bitmap-selftest-hook`
- the landed `runtime-bitmap-module-tests`
- the landed `runtime-bitmap-diff-gate`
- the landed `runtime-bitmap-loader-scaffold`
- the landed `runtime-bitmap-top-bit-boundary`
- the still-blocked `runtime-bitmap-live-loader-binding`

This keeps the survey useful after the first starter, selftest-hook surface, module gate, diff gate, loader scaffold, shared loader-contract replay, and top-bit companion gate landed without pretending that Zigux already has a loadable runtime bitmap module or a live runtime loader binding waiting behind the blocker.

## Gates

1. run the dedicated Phase 9 survey gate
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the focused top-bit companion replay
- `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`

3. run the focused shared runtime-loader replay
- `zig build phase9-runtime-loader-shared-tests --build-file zigux/tests/phase9_build.zig`

4. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice still does not claim:

- a loadable Zigux runtime bitmap module implementation
- runtime module lifecycle parity against a real loader path
- a kernel-loadable `samples/zigux/runtime_bitmap.zig` module
- a Phase 5 approved `samples/zigux/` reference idiom
- direct parity for the full `lib/test_bitmap.c` surface beyond the bounded starter and diff gate

## Next bounded step

Stay in the Phase 9 runtime bitmap lane and keep future work narrowly aimed at the remaining shared runtime substrate or lifecycle-parity blocker, rather than reopening already-landed survey, sample, top-bit, loader-scaffold, shared loader-contract, module-gate, or diff-gate scaffolding.
