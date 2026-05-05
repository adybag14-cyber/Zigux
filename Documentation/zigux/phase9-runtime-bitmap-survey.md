# Phase 9 Runtime Bitmap Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `lib/test_bitmap.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-survey`
- scope: survey manifest, dedicated runtime survey gate, landed sample-backed module starter, landed module gate, landed diff gate, landed loader scaffold, and the lane-level review note that keeps the remaining roadmap blocker explicit without claiming loadable-module parity
- product boundary:
  - `samples/zigux/runtime_bitmap.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `zigux/tests/runtime_bitmap_manifest.json`
  - `zigux/tests/runtime_bitmap_survey.zig`
  - `zigux/tests/runtime_bitmap_module.zig`
  - `zigux/tests/runtime_bitmap_diff.zig`
  - `zigux/tests/phase9_build.zig`
  - `Documentation/zigux/phase9-runtime-bitmap-survey.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/test_bitmap.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo originally needed a survey-shaped review anchor that could record what the runtime bitmap lane had already shipped versus what still depends on a shared runtime substrate. This note stays in place after the bounded starter sample, module gate, diff gate, and loader scaffold landed, so the lane can keep comparing the current pilot-module surface against the roadmap without pretending that Zigux already has a real loadable bitmap module.

This survey note is also not a Phase 5 sample-root approval: `samples/zigux/runtime_bitmap.zig` and `samples/zigux/runtime_bitmap_loader.zig` stay here as the separate Phase 9 runtime bitmap family rooted in `lib/test_bitmap.c`, not as a fifth approved Phase 5 reference idiom under `samples/zigux/`.

## Survey findings

- `lib/test_bitmap.c` is present on `master` at 1567 lines.
- the live Phase 9 bitmap lane already carried dedicated runtime bitmap test files before this survey note landed.
- the live Phase 9 bitmap lane already carried a sample-backed runtime bitmap starter under `samples/zigux/`.
- the live repo already carried shared `zigux/tests/phase9_build.zig` wiring and a bitmap module-slice note before this survey note landed.
- the live repo still keeps that runtime bitmap family outside the four approved Phase 5 reference samples, so this survey packet stays reviewable as later runtime follow-on evidence rather than Phase 5 sample closure.

## Roadmap snapshot

Against the Phase 9 roadmap requirements, the current runtime bitmap lane now records:

- a landed sample-backed runtime starter with selftest-hook metadata under `samples/zigux/runtime_bitmap.zig`
- a landed sample-side loader scaffold in `samples/zigux/runtime_bitmap_loader.zig`
- a landed dedicated module gate in `zigux/tests/runtime_bitmap_module.zig`
- a landed dedicated differential gate in `zigux/tests/runtime_bitmap_diff.zig`
- a remaining blocked live-loader handoff under `zigux/kernel/runtime_loader.zig`, because true runtime-module loading and lifecycle parity still depend on shared runtime substrate pieces that the repo has not started yet

This keeps the survey honest about the difference between the shipped in-memory pilot and the still-missing loadable runtime substrate.

## Direct Sample Checks

The current direct bitmap sample contract is verified through these exact checks:

- summary stability: initializing bits `0`, `5`, `64`, and `70` still yields `first_set=0`, `first_zero=1`, `weight=4`, and `nbits=128`
- descriptor contract: the sample still advertises `name=runtime_bitmap`, `anchor=lib/test_bitmap.c`, `requires_runtime_substrate=true`, and `provides_selftest_hook=true`
- lifecycle and mutation path: the sample still starts cold, rejects selftest before init, records one init run, clears bits `64..65`, adds bits `9..12`, and reaches weight `7` while keeping bit `70`
- copy and selftest path: a second initialized sample can mirror the mutated bitmap, `runSelftest()` still reports the four ordered operation families `clear_set`, `copy`, `parse_and_print`, and `iteration_and_ranges`, and selftest leaves the bitmap summary unchanged
- parse-and-print boundary: the ordered `parse_and_print` selftest family remains a review cue only; the current starter does not claim standalone `initFromBitList()`, `formatSetBits()`, or broader parse/print differential parity on `master`
- exit and error guards: `exit()` still moves the sample to `exited`, later mutation or re-init attempts fail with `InvalidLifecycleTransition`, out-of-range init and range edits fail with `BitRangeOutOfBounds`, zero-length mutations leave the summary unchanged, and `copyFrom()` still rejects cold or exited sources with `InvalidSourceLifecycle`
- diff-gate replay: the bounded parity cases still cover the single-word fill starter, the `79..97` cross-boundary clear cutout, the sparse `10,20,30,40,50,60,80,123` population replay, and the copied `0..108` tail-clear snapshot with `first_zero=109`

## Recorded gaps

The manifest now records:

- the landed `phase9-build-gate`
- the landed `runtime-bitmap-survey-gate`
- the landed `runtime-bitmap-sample-module` starter
- the landed `runtime-bitmap-module-tests`
- the landed `runtime-bitmap-diff-gate`
- the landed `runtime-bitmap-loader-scaffold`
- the still-blocked `runtime-bitmap-live-loader-binding`

This keeps the survey useful after the first starter, module gate, diff gate, and loader scaffold landed without pretending that Zigux already has a loadable runtime bitmap module or a live runtime loader binding waiting behind the blocker.

## Gates

1. run the dedicated Phase 9 survey gate
- `zig build test --build-file zigux/tests/phase9_build.zig`

2. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice still does not claim:

- a loadable Zigux runtime bitmap module implementation
- runtime module lifecycle parity against a real loader path
- a kernel-loadable `samples/zigux/runtime_bitmap.zig` module
- a Phase 5 approved `samples/zigux/` reference idiom
- direct parity for the full `lib/test_bitmap.c` surface beyond the bounded starter and diff gate

## Next bounded step

Stay in the Phase 9 runtime bitmap lane and keep future work narrowly aimed at the remaining runtime loader or lifecycle-parity blocker, rather than reopening already-landed survey, sample, loader-scaffold, module-gate, or diff-gate scaffolding.