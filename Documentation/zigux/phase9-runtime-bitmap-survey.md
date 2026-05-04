# Phase 9 Runtime Bitmap Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `lib/test_bitmap.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-survey`
- `PHASE9_LANE_KEY=P9-Y08`
- `PHASE9_SURVEYED_COMMIT=c0b506e3254e63fe007a72d420bb275846a89093`
- scope: survey manifest, manifest-backed delivery catalog and ownership map, dedicated runtime survey gate, direct `phase9-runtime-bitmap-sample-tests`, `phase9-runtime-bitmap-module-tests`, `phase9-runtime-bitmap-diff-tests`, and `phase9-runtime-bitmap-loader-tests` shared-build legs, landed sample-backed module starter, landed focused top-bit companion replay plus its dedicated sample-side build file, landed module gate, landed diff gate, landed loader scaffold, landed shared loader-request binding, prepared loader-summary snapshot replay, and the lane-level review note that keeps the remaining broader runtime-control blocker explicit without claiming loadable-module parity
- product boundary:
  - `samples/zigux/runtime_bitmap.zig`
  - `samples/zigux/runtime_bitmap_loader.zig`
  - `samples/zigux/runtime_bitmap_top_bit_contract.zig`
  - `samples/zigux/runtime_bitmap_top_bit_build.zig`
  - `zigux/tests/runtime_bitmap_manifest.json`
  - `zigux/tests/runtime_bitmap_survey.zig`
  - `zigux/tests/runtime_bitmap_module.zig`
  - `zigux/tests/runtime_bitmap_diff.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `Documentation/zigux/phase9-runtime-bitmap-survey.md`
  - `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
  - `Documentation/zigux/phase9-runtime-loader-gap-survey.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/test_bitmap.c` as a runtime pilot anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

This survey-shaped review anchor records what the runtime bitmap lane has already shipped versus what still depends on a shared runtime substrate. This note stays in place after the bounded starter sample, direct sample leg, direct module leg, direct diff leg, direct loader leg, focused top-bit companion replay plus its dedicated sample-side build file, module gate, diff gate, loader scaffold, and shared loader-request binding landed, so the lane can keep comparing the current pilot-module surface against the roadmap without pretending that Zigux already has a real loadable bitmap module.

This survey note is also not a Phase 5 sample-root approval: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and `samples/zigux/runtime_bitmap_top_bit_build.zig` stay here as the separate Phase 9 runtime bitmap family rooted in `lib/test_bitmap.c`, not as a fifth approved Phase 5 reference idiom under `samples/zigux/`.

The shared runtime-loader blocker that still governs this bitmap packet also sits underneath the freeze map's study boundary. `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`, so this lane may ship a bounded in-memory starter, sample-side loader scaffold, shared loader-request binding, direct bitmap replay evidence, and the focused top-bit companion replay, but it must not imply workqueue parity, scheduler transport ownership, or any Architecture Council-approved status change for that study-only anchor.

No parity scorecard entry or Architecture Council status-change request is attached to this Phase 9 runtime bitmap lane. The evidence here remains limited to the runtime starter, focused top-bit companion replay, loader scaffold, shared request binding, module and diff gates, and the still-blocked shared loader-control posture that keeps the packet pre-execution.

## Survey findings

- `lib/test_bitmap.c` is present on `master` at 1567 lines.
- the current survey packet is pinned to `master` commit `c0b506e3254e63fe007a72d420bb275846a89093`.
- the live Phase 9 bitmap lane already carried dedicated runtime bitmap test files before this survey note landed.
- the live Phase 9 bitmap lane already carried a sample-backed runtime bitmap starter under `samples/zigux/`.
- the live repo already carried shared `zigux/tests/phase9_build.zig` wiring and a bitmap module-slice note before this survey note landed.
- the live repo still keeps that runtime bitmap family, including the focused top-bit companion replay, outside the four approved Phase 5 reference samples, so this survey packet stays reviewable as later runtime follow-on evidence rather than Phase 5 sample closure.

## Roadmap snapshot

Against the Phase 9 roadmap requirements, the current runtime bitmap lane now records:

- a landed sample-backed runtime starter with selftest-hook metadata under `samples/zigux/runtime_bitmap.zig` plus the focused highest-valid-bit companion replay in `samples/zigux/runtime_bitmap_top_bit_contract.zig` through `samples/zigux/runtime_bitmap_top_bit_build.zig`
- landed direct `phase9-runtime-bitmap-sample-tests`, `phase9-runtime-bitmap-module-tests`, `phase9-runtime-bitmap-diff-tests`, and `phase9-runtime-bitmap-loader-tests` shared-build legs in `zigux/tests/phase9_build.zig` so the sample file's lifecycle replay, the dedicated module and diff checks, and the loader scaffold's request-shape replay now run as first-class shared build evidence
- a landed sample-side loader scaffold in `samples/zigux/runtime_bitmap_loader.zig`
- a landed dedicated module gate in `zigux/tests/runtime_bitmap_module.zig`
- a landed dedicated differential gate in `zigux/tests/runtime_bitmap_diff.zig`
- a landed shared runtime-loader request binding under `zigux/kernel/runtime_loader.zig` that can consume the bitmap loader handoff shape, staged entry and exit symbols, allocator posture, explicit shared command-name preservation, and bitmap payload summary, while keeping the prepared handoff snapshot stable after later sample mutation
- a remaining blocked shared runtime control surface under `zigux/kernel/runtime_loader.zig`, because command-name, argv-policy, and environment-derived activation handling still have no shared owner and true runtime execution or lifecycle parity remains out of scope
- the same shared runtime-loader blocker also stays under the freeze-map study boundary for `kernel/workqueue.c`, so the bitmap packet keeps workqueue parity and any scheduler-facing status change out of scope unless the Architecture Council explicitly reopens that anchor

This keeps the survey honest about the difference between the shipped in-memory pilot and the still-missing loadable runtime substrate.

## Landed sample and exact checks

The repo already carries the bounded runtime starter in `samples/zigux/runtime_bitmap.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit through `RuntimeBitmapSample.descriptor()`
- it uses a bounded two-word bitmap backing store instead of claiming a larger runtime-owned allocation surface
- it models only lifecycle staging, range mutation, copy, summary, and selftest-facing review behavior in memory
- it keeps the shared runtime-loader surface separate through the adjacent loader scaffold and shared loader note rather than pretending the sample itself can execute through a real runtime path

The same runtime bitmap family also carries a focused companion replay under `samples/zigux/runtime_bitmap_top_bit_contract.zig` plus `samples/zigux/runtime_bitmap_top_bit_build.zig` so the highest valid bit stays reviewable as a small sample-side check without widening this lane into another approved Phase 5 idiom.

The exact checks now recorded in `zigux/tests/runtime_bitmap_manifest.json` and exercised through `zigux/tests/phase9_build.zig` are:

- the descriptor advertises `runtime_bitmap`, anchor `lib/test_bitmap.c`, `requires_runtime_substrate = true`, and `provides_selftest_hook = true`
- initializing bits `0`, `5`, `64`, and `70` yields `first_set = 0`, `first_zero = 1`, `weight = 4`, and `nbits` equal to the bounded two-word bitmap width
- clearing bits `64` and `65` then setting range `9` through `12` yields `weight = 7`, keeps bit `70` set, sets bit `12`, and preserves the same summary through `copyFrom()` on an initialized mirror sample
- `runSelftest()` moves the sample to `selftest_complete`, records exactly four operation families in order: `clear_set`, `copy`, `parse_and_print`, and `iteration_and_ranges`, and leaves the summary unchanged
- the direct sample leg replays sparse `nthSetBit()` iteration across bits `10`, `20`, `30`, `40`, `50`, `60`, `80`, and `123`, then returns `null` once the ordered set-bit sequence is exhausted
- after `runSelftest()` reaches `selftest_complete`, `clearRange(64, 2)` plus `setRange(9, 4)` still yields `first_set = 0`, `first_zero = 1`, and `weight = 7`, keeps bit `70` set, sets bit `12`, and preserves that replay through `copyFrom()` on an initialized mirror sample before exit
- `exit()` moves the sample to `exited`, keeps the final bitmap snapshot reviewable, and later `setRange()`, `runSelftest()`, `exit()`, or re-init calls fail with `InvalidLifecycleTransition`
- out-of-bounds init, `setRange()`, and `clearRange()` requests stay explicit `BitRangeOutOfBounds` errors at the bitmap tail
- zero-length `setRange()` and `clearRange()` calls leave the summary unchanged, and `copyFrom()` rejects cold or exited sources with `InvalidSourceLifecycle`
- `initFromBitList()` rejects trailing or doubled separators, rejects out-of-bounds bit lists, normalizes duplicate bit lists to the canonical `0,5,64,70` replay, preserves empty parse-and-print replay as an empty string plus `null` first `nthSetBit()`, blocks repeat parse initialization with `InvalidLifecycleTransition` once the first parse succeeds, and keeps failed parsed or direct init attempts cold and empty so a clean follow-up init can still succeed
- the focused top-bit companion replay keeps bit `127` reviewable as the highest valid bounded bit through direct init, parse, summary, `nthSetBit()`, single-bit range counting, and canonical formatting under `samples/zigux/runtime_bitmap_top_bit_contract.zig` plus `samples/zigux/runtime_bitmap_top_bit_build.zig`
- the loader scaffold keeps entry symbol `zigux_runtime_bitmap_init`, exit symbol `zigux_runtime_bitmap_exit`, `waiting_on_runtime_substrate` handoff, `released_without_substrate` fallback, `helper_owned` allocator flow, explicit shared command-name preservation, and the seven-field bitmap payload summary machine-checkable through the shared runtime-loader request surface
- preparing the loader handoff snapshots the current bitmap summary, and later sample mutations do not rewrite the pending `waiting_on_runtime_substrate` request or `released_without_substrate` fallback summary or counters
- the shared Phase 9 build keeps the dedicated `phase9-runtime-bitmap-sample-tests`, `phase9-runtime-bitmap-module-tests`, `phase9-runtime-bitmap-diff-tests`, and `phase9-runtime-bitmap-loader-tests` legs together so the sample, module, diff, and loader review evidence stays explicit inside one shared build entrypoint
- the diff gate replays a 9-bit fill-from-zero case with `first_set = 0`, `first_zero = 9`, `weight = 9`, bits `0` and `8` set, and later bits clear
- the diff gate replays a full-set then `clearRange(79, 19)` cutout with `first_zero = 79`, weight `bitmap_nbits - 19`, and bits `79` through `97` cleared while bit `98` and the last bit stay set
- the diff gate replays a sparse population at bits `10`, `20`, `30`, `40`, `50`, `60`, `80`, and `123` plus a 109-bit copy case whose copied summary is `first_set = 0`, `first_zero = 109`, and `weight = 109`

## Delivery ownership map

The manifest-backed ownership packet for this slice now keeps the current delivery surfaces explicit:

- `Documentation/zigux/phase9-runtime-bitmap-survey.md` owns the roadmap anchor note, shipped starter scope, ownership packet summary, and remaining shared-loader blocker wording
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md` owns the bounded starter surface, loader handoff wording, and shared-build-leg explanation for the shipped bitmap packet
- `zigux/tests/runtime_bitmap_manifest.json` owns the exact checks plus the delivery catalog and ownership map for the current runtime bitmap packet
- `zigux/tests/runtime_bitmap_survey.zig` owns the machine-checkable replay of that ownership packet and the adjacent blocked shared-loader note
- `zigux/tests/runtime_bitmap_module.zig` owns the bounded starter lifecycle, sparse `nthSetBit()` replay, selftest, range-mutation, and copy surface
- `zigux/tests/runtime_bitmap_diff.zig` owns the bounded differential replay for first-set, first-zero, weight, sparse nth-bit iteration, cutout, and copy expectations
- `zigux/tests/phase9_build.zig` owns the shared Phase 9 replay entrypoint for the direct bitmap sample, module, diff, and loader legs plus the survey and shared runtime-loader checks
- `samples/zigux/runtime_bitmap.zig` owns the bounded two-word in-memory bitmap starter contract, lifecycle staging, sparse iteration, summary, and selftest-hook metadata
- `samples/zigux/runtime_bitmap_loader.zig` owns the sample-side loader projection, `waiting_on_runtime_substrate` handoff, `released_without_substrate` fallback, explicit shared command-name preservation, prepared-summary snapshot replay, and bitmap payload summary
- `samples/zigux/runtime_bitmap_top_bit_contract.zig` owns the focused highest-valid-bit replay that keeps direct init, parse, summary, `nthSetBit()`, range counting, and canonical formatting reviewable at the bounded bitmap tail
- `samples/zigux/runtime_bitmap_top_bit_build.zig` owns the dedicated sample-side build wrapper that replays the focused top-bit contract without widening the shared Phase 9 build or implying a Phase 5 approval change
- `zigux/kernel/runtime_loader.zig` owns the shared runtime-loader request contract that consumes the bitmap loader handoff, allocator posture, staged entry and exit symbols, and explicit command-name preservation
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` owns the still-blocked shared command-name, argv-policy, and environment-derived activation-control posture that keeps this bitmap packet pre-execution
- `Documentation/zigux/freeze-map.md` owns the study-only `kernel/workqueue.c` boundary and the Architecture Council reopen rule that keep this bitmap packet out of scheduler-facing parity claims

## Contributor refresh prompts

When a contributor updates `samples/zigux/runtime_bitmap.zig` or its directly coupled Phase 9 review files, keep these prompts explicit:

- does the descriptor still keep the Linux anchor path explicit, leave `requires_runtime_substrate = true` while `provides_selftest_hook = true`, and still name the bounded two-word bitmap backing?
- does the survey note still say plainly that `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_bitmap_top_bit_contract.zig`, and `samples/zigux/runtime_bitmap_top_bit_build.zig` are the separate Phase 9 runtime bitmap family rather than a fifth approved Phase 5 reference idiom under `samples/zigux/`?
- do the manifest-backed delivery catalog and ownership map still keep `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`, `zigux/tests/runtime_bitmap_manifest.json`, `zigux/tests/runtime_bitmap_survey.zig`, `zigux/tests/runtime_bitmap_module.zig`, `zigux/tests/runtime_bitmap_diff.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `zigux/kernel/runtime_loader.zig`, and the direct `phase9-runtime-bitmap-sample-tests`, `phase9-runtime-bitmap-module-tests`, `phase9-runtime-bitmap-diff-tests`, and `phase9-runtime-bitmap-loader-tests` shared-build legs describing one exact lifecycle, summary, sparse `nthSetBit()` replay, post-selftest mutation replay, copy, loader handoff, explicit shared command-name preservation, prepared-summary snapshot replay, and diff-case packet run through `zigux/tests/phase9_build.zig`?
- if the runtime bitmap sample behavior changes, is the manifest updated alongside the module and diff checks instead of leaving reviewers to infer the new contract from code alone?
- if the focused top-bit companion replay changes, do `samples/zigux/runtime_bitmap_top_bit_contract.zig` and `samples/zigux/runtime_bitmap_top_bit_build.zig` still keep the highest-valid-bit proof explicit without implying that the Phase 5 approved idiom set widened?
- if `initFromBitList()` or `initWithSetBits()` changes separator parsing, out-of-bounds handling, duplicate-normalization replay, empty parse-and-print replay, repeat-init lifecycle guards, or transactional failed-init behavior, is that stricter direct-sample contract refreshed in the manifest-backed exact checks instead of being left implicit in code?
- if the loader scaffold changes, does the manifest-backed evidence still say clearly that prepare snapshots the current summary and later sample mutation cannot silently rewrite the `waiting_on_runtime_substrate` or `released_without_substrate` replay?
- does the review packet still keep this bounded starter visibly separate from the still-blocked shared runtime-loader control surface rather than implying a loadable module or real command-path parity?
- do the docs and tests still say clearly that real runtime execution, shared loader controls, and full `lib/test_bitmap.c` parity remain out of scope, with `Documentation/zigux/phase9-runtime-loader-gap-survey.md` still owning the blocked command-name, argv-policy, and environment-derived activation-control posture?
- does the bitmap packet still treat `Documentation/zigux/freeze-map.md` as authoritative for the study-only `kernel/workqueue.c` boundary, with no parity scorecard entry or Architecture Council status-change request attached to this scheduler-facing anchor?

## Recorded gaps

The manifest now records:

- the landed `phase9-build-gate`, including the direct `phase9-runtime-bitmap-sample-tests`, `phase9-runtime-bitmap-module-tests`, `phase9-runtime-bitmap-diff-tests`, and `phase9-runtime-bitmap-loader-tests` shared-build legs
- the landed `runtime-bitmap-survey-gate`
- the landed `runtime-bitmap-sample-module` starter
- the landed `runtime-bitmap-module-tests`
- the landed `runtime-bitmap-diff-gate`
- the landed `runtime-bitmap-loader-scaffold`
- the landed `runtime-bitmap-live-loader-binding`
- the still-blocked `runtime-bitmap-shared-loader-controls`

This keeps the survey useful after the first starter, direct sample leg, direct module leg, direct diff leg, direct loader leg, focused top-bit companion replay, module gate, diff gate, loader scaffold, and shared loader-request binding landed without pretending that Zigux already has a loadable runtime bitmap module or the full shared runtime control surface needed for real execution. It also keeps ownership for the shipped evidence packet explicit so the survey note, module-slice note, manifest, survey gate, module gate, diff gate, sample-side loader, shared loader contract, and shared Phase 9 replay entrypoint cannot drift independently by eye.

## Gates

1. run the dedicated Phase 9 survey gate
- `zig test zigux/tests/runtime_bitmap_survey.zig`
- this dedicated gate keeps the manifest-backed ownership packet, exact checks, and adjacent blocked shared-loader note reviewable without requiring the broader shared build

2. run the shared Phase 9 runtime survey bundle
- `zig build test --build-file zigux/tests/phase9_build.zig`
- this shared build now includes the direct `phase9-runtime-bitmap-sample-tests`, `phase9-runtime-bitmap-module-tests`, `phase9-runtime-bitmap-diff-tests`, and `phase9-runtime-bitmap-loader-tests` legs alongside the bitmap survey, module, diff, loader, and shared runtime-loader checks

3. run the focused top-bit companion replay
- `zig build test --build-file samples/zigux/runtime_bitmap_top_bit_build.zig --summary all`
- this companion build keeps the highest-valid-bit boundary explicit as later Phase 9 follow-on evidence without implying a fifth approved Phase 5 reference sample

4. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice still does not claim:

- a loadable Zigux runtime bitmap module implementation
- runtime module lifecycle parity against a real loader path
- a kernel-loadable `samples/zigux/runtime_bitmap.zig` module
- direct parity for the full `lib/test_bitmap.c` surface beyond the bounded starter, focused top-bit companion replay, and diff gate
- shared runtime-loader command-name, argv-policy, or environment-activation controls
- parity or ownership for `kernel/workqueue.c`
- any freeze-map status change for the scheduler-facing workqueue boundary without an Architecture Council decision

## Next bounded step

Stay in the Phase 9 runtime bitmap lane and keep the next step on the remaining broader shared runtime-loader control surface or real lifecycle-parity blocker, rather than inventing another bitmap-local binding surface now that `zigux/kernel/runtime_loader.zig` already consumes the current handoff plan, while keeping the focused top-bit companion replay and the separate `kernel/workqueue.c` freeze-map boundary in study-only status unless the Architecture Council explicitly reopens it.
