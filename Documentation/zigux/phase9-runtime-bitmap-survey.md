# Phase 9 Runtime Bitmap Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `lib/test_bitmap.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-survey`
- scope: survey manifest, dedicated runtime survey gate, landed sample-backed module starter, landed module gate, landed diff gate, landed loader scaffold, landed shared loader-request binding, and the lane-level review note that keeps the remaining broader runtime-control blocker explicit without claiming loadable-module parity
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

The live repo originally needed a survey-shaped review anchor that could record what the runtime bitmap lane had already shipped versus what still depends on a shared runtime substrate. This note stays in place after the bounded starter sample, module gate, diff gate, loader scaffold, and shared loader-request binding landed, so the lane can keep comparing the current pilot-module surface against the roadmap without pretending that Zigux already has a real loadable bitmap module.

## Survey findings

- `lib/test_bitmap.c` is present on `master` at 1567 lines.
- the live Phase 9 bitmap lane already carried dedicated runtime bitmap test files before this survey note landed.
- the live Phase 9 bitmap lane already carried a sample-backed runtime bitmap starter under `samples/zigux/`.
- the live repo already carried shared `zigux/tests/phase9_build.zig` wiring and a bitmap module-slice note before this survey note landed.

## Roadmap snapshot

Against the Phase 9 roadmap requirements, the current runtime bitmap lane now records:

- a landed sample-backed runtime starter with selftest-hook metadata under `samples/zigux/runtime_bitmap.zig`
- a landed sample-side loader scaffold in `samples/zigux/runtime_bitmap_loader.zig`
- a landed dedicated module gate in `zigux/tests/runtime_bitmap_module.zig`
- a landed dedicated differential gate in `zigux/tests/runtime_bitmap_diff.zig`
- a landed shared runtime-loader request binding under `zigux/kernel/runtime_loader.zig` that can consume the bitmap loader handoff shape, staged entry and exit symbols, allocator posture, and bitmap payload summary
- a remaining blocked shared runtime control surface under `zigux/kernel/runtime_loader.zig`, because command-name, argv-policy, and environment-derived activation handling still have no shared owner and true runtime execution or lifecycle parity remains out of scope

This keeps the survey honest about the difference between the shipped in-memory pilot and the still-missing loadable runtime substrate.

## Landed sample and exact checks

The repo already carries the bounded runtime starter in `samples/zigux/runtime_bitmap.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit through `RuntimeBitmapSample.descriptor()`
- it uses a bounded two-word bitmap backing store instead of claiming a larger runtime-owned allocation surface
- it models only lifecycle staging, range mutation, copy, summary, and selftest-facing review behavior in memory
- it keeps the shared runtime-loader surface separate through the adjacent loader scaffold and shared loader note rather than pretending the sample itself can execute through a real runtime path

The exact checks now recorded in `zigux/tests/runtime_bitmap_manifest.json` and exercised through `zigux/tests/phase9_build.zig` are:

- the descriptor advertises `runtime_bitmap`, anchor `lib/test_bitmap.c`, `requires_runtime_substrate = true`, and `provides_selftest_hook = true`
- initializing bits `0`, `5`, `64`, and `70` yields `first_set = 0`, `first_zero = 1`, `weight = 4`, and `nbits` equal to the bounded two-word bitmap width
- clearing bits `64` and `65` then setting range `9` through `12` yields `weight = 7`, keeps bit `70` set, sets bit `12`, and preserves the same summary through `copyFrom()` on an initialized mirror sample
- `runSelftest()` moves the sample to `selftest_complete`, records exactly four operation families in order: `clear_set`, `copy`, `parse_and_print`, and `iteration_and_ranges`, and leaves the summary unchanged
- `exit()` moves the sample to `exited`, keeps the final bitmap snapshot reviewable, and later `setRange()`, `runSelftest()`, `exit()`, or re-init calls fail with `InvalidLifecycleTransition`
- out-of-bounds init, `setRange()`, and `clearRange()` requests stay explicit `BitRangeOutOfBounds` errors at the bitmap tail
- zero-length `setRange()` and `clearRange()` calls leave the summary unchanged, and `copyFrom()` rejects cold or exited sources with `InvalidSourceLifecycle`
- the diff gate replays a 9-bit fill-from-zero case with `first_set = 0`, `first_zero = 9`, `weight = 9`, bits `0` and `8` set, and later bits clear
- the diff gate replays a full-set then `clearRange(79, 19)` cutout with `first_zero = 79`, weight `bitmap_nbits - 19`, and bits `79` through `97` cleared while bit `98` and the last bit stay set
- the diff gate replays a sparse population at bits `10`, `20`, `30`, `40`, `50`, `60`, `80`, and `123` plus a 109-bit copy case whose copied summary is `first_set = 0`, `first_zero = 109`, and `weight = 109`

## Contributor refresh prompts

When a contributor updates `samples/zigux/runtime_bitmap.zig` or its directly coupled Phase 9 review files, keep these prompts explicit:

- does the descriptor still keep the Linux anchor path explicit, leave `requires_runtime_substrate = true` while `provides_selftest_hook = true`, and still name the bounded two-word bitmap backing?
- do `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_module.zig`, and `zigux/tests/runtime_bitmap_diff.zig` still describe the exact lifecycle, summary, range-mutation, copy, and diff-case contract run through `zigux/tests/phase9_build.zig`?
- if the runtime bitmap sample behavior changes, is the manifest updated alongside the module and diff checks instead of leaving reviewers to infer the new contract from code alone?
- does the review packet still keep this bounded starter visibly separate from the still-blocked shared runtime-loader control surface rather than implying a loadable module or real command-path parity?
- do the docs and tests still say clearly that real runtime execution, shared loader controls, and full `lib/test_bitmap.c` parity remain out of scope?

## Recorded gaps

The manifest now records:

- the landed `phase9-build-gate`
- the landed `runtime-bitmap-survey-gate`
- the landed `runtime-bitmap-sample-module` starter
- the landed `runtime-bitmap-module-tests`
- the landed `runtime-bitmap-diff-gate`
- the landed `runtime-bitmap-loader-scaffold`
- the landed `runtime-bitmap-live-loader-binding`
- the still-blocked `runtime-bitmap-shared-loader-controls`

This keeps the survey useful after the first starter, module gate, diff gate, loader scaffold, and shared loader-request binding landed without pretending that Zigux already has a loadable runtime bitmap module or the full shared runtime control surface needed for real execution.

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
- direct parity for the full `lib/test_bitmap.c` surface beyond the bounded starter and diff gate
- shared runtime-loader command-name, argv-policy, or environment-activation controls

## Next bounded step

Stay in the Phase 9 runtime bitmap lane and keep future work narrowly aimed at the remaining broader shared runtime-loader control surface or real lifecycle-parity blocker, rather than reopening already-landed survey, sample, loader-scaffold, shared binding, module-gate, or diff-gate scaffolding.
