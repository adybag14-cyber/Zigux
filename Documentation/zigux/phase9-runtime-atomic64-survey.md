# Phase 9 Runtime Atomic64 Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `lib/atomic64_test.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-survey`
- `PHASE9_LANE_KEY=P9-L04`
- `PHASE9_SURVEYED_COMMIT=d46fb91493e6e9126d5111bf0e5b21184e0ec1d1`
- scope: survey manifest, manifest-backed delivery catalog and ownership map, dedicated runtime survey gate, direct `phase9-runtime-atomic64-sample-tests`, `phase9-runtime-atomic64-module-tests`, `phase9-runtime-atomic64-diff-tests`, and `phase9-runtime-atomic64-loader-tests` shared-build legs, landed sample-backed module starter, landed module gate, landed diff gate, landed loader scaffold with prepared counter-summary snapshot replay, landed shared loader-request binding, and the lane-level review note that keeps the remaining roadmap blocker explicit without claiming loadable-module parity
- product boundary:
  - `samples/zigux/runtime_atomic64.zig`
  - `samples/zigux/runtime_atomic64_loader.zig`
  - `zigux/tests/runtime_atomic64_manifest.json`
  - `zigux/tests/runtime_atomic64_survey.zig`
  - `zigux/tests/runtime_atomic64_module.zig`
  - `zigux/tests/runtime_atomic64_diff.zig`
  - `zigux/tests/phase9_build.zig`
  - `zigux/kernel/runtime_loader.zig`
  - `Documentation/zigux/phase9-runtime-atomic64-survey.md`
  - `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
  - `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
  - `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/atomic64_test.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo originally carried the Linux atomic64 runtime test without any dedicated Phase 9 review gate, `runtime_*` Zigux tests, or `samples/zigux/` pilot-module scaffold. This survey note stays in place as the lane history and review anchor after the bounded starter sample, direct sample-test leg, direct module-test leg, direct diff-test leg, direct loader-test leg, module gate, diff gate, loader scaffold, and shared loader-request binding landed, so Phase 9 can keep recording what is shipped versus what still depends on the runtime substrate.

The shared runtime-loader blocker that still governs this atomic64 packet also sits underneath the freeze map's study boundary. `Documentation/zigux/freeze-map.md` keeps `kernel/workqueue.c` in `Study / Boundary Only`, so this lane may ship a bounded in-memory starter, sample-side loader scaffold, and shared loader-request binding, but it must not imply workqueue parity, scheduler transport ownership, or any Architecture Council-approved status change for that study-only anchor.

That blocked shared-loader packet now spans both `Documentation/zigux/phase9-runtime-loader-gap-survey.md` and `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`. This atomic64 survey therefore keeps both notes in the same reviewable boundary packet whenever the adjacent loader-stage vocabulary, without-substrate fallback posture, or shared handoff wording changes under the same study-only `kernel/workqueue.c` rule.

No parity scorecard entry or Architecture Council status-change request is attached to this Phase 9 atomic64 lane. The evidence here remains limited to the runtime starter, loader scaffold, shared request binding, the module-slice note that describes the starter packet, the paired loader-gap and loader-substrate-plan notes that describe the still-blocked shared loader packet, and the still-blocked shared loader-control posture that keeps the packet pre-execution.

## Survey findings

- `lib/atomic64_test.c` is present on `master` at 277 lines.
- the current survey packet is pinned to `master` commit `d46fb91493e6e9126d5111bf0e5b21184e0ec1d1`.
- the repo had zero `zigux/tests/runtime_*` files before this survey landed.
- the repo had no `samples/zigux/` directory before this survey landed.
- the repo had no `zigux/tests/phase9_build.zig` gate, no dedicated Phase 9 runtime note, and no dedicated atomic64 module-slice note before this survey landed.

## Latest verification snapshot

On inspected `master` commit `d46fb91493e6e9126d5111bf0e5b21184e0ec1d1`, focused Phase 9 replay still passed with the attached Zig toolchain across the dedicated atomic64 and bitmap sample, module, diff, loader, and survey legs, keeping the bounded lifecycle, selftest, and pre-execution runtime-pilot packet green without widening into unrelated shared runtime-loader control work.

## Roadmap snapshot

Against the Phase 9 roadmap requirements, the current runtime atomic64 lane now records:

- a landed sample-backed runtime starter with selftest-hook metadata under `samples/zigux/runtime_atomic64.zig`
- a landed direct `phase9-runtime-atomic64-sample-tests` shared-build leg in `zigux/tests/phase9_build.zig` so the sample file's own lifecycle and summary replay now runs as first-class shared build evidence
- a landed direct `phase9-runtime-atomic64-loader-tests` shared-build leg in `zigux/tests/phase9_build.zig` so the loader scaffold's request-shape replay stays equally first-class instead of being implied through the broader shared loader checks
- a landed sample-side loader scaffold in `samples/zigux/runtime_atomic64_loader.zig` that snapshots the prepared four-field counter summary before later sample mutation
- the atomic64 loader scaffold now keeps a synthetic non-null shared `command_name` reviewable through both `toSharedRequest()` and `releasedWithoutSubstrate()` so field preservation is explicit even while the broader shared runtime command surface remains blocked
- a landed dedicated module gate in `zigux/tests/runtime_atomic64_module.zig`
- a landed dedicated differential gate in `zigux/tests/runtime_atomic64_diff.zig`
- a landed shared runtime-loader request binding under `zigux/kernel/runtime_loader.zig` that can consume the atomic64 loader handoff shape, staged entry and exit symbols, allocator posture, and the four-field atomic64 payload summary while preserving that prepared snapshot through both `waiting_on_runtime_substrate` and `released_without_substrate` review paths
- the differential gate now includes the bounded arithmetic, bitwise, swap, compare-swap, and guard-return families from `lib/atomic64_test.c`, including `or`, `and`, `xor`, `andnot`, `add_unless`, `inc_not_zero`, and `dec_if_positive`
- a remaining blocked shared runtime control surface under `zigux/kernel/runtime_loader.zig`, because command-name, argv-policy, and environment-derived activation handling still have no shared owner and true runtime execution or lifecycle parity remains out of scope
- the same shared runtime-loader blocker also stays under the freeze-map study boundary for `kernel/workqueue.c`, so the atomic64 packet keeps workqueue parity and any scheduler-facing status change out of scope unless the Architecture Council explicitly reopens that anchor

This keeps the survey honest about the difference between the shipped in-memory pilot and the still-missing loadable runtime substrate.

## Delivery ownership map

The manifest-backed ownership packet for this slice now keeps the current delivery surfaces explicit:

- `Documentation/zigux/phase9-runtime-atomic64-survey.md` owns the roadmap anchor note, shipped starter scope, ownership packet summary, and remaining shared-loader blocker wording
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md` owns the bounded starter surface, loader handoff wording, prepared counter-summary snapshot replay, and shared-build-leg explanation for the shipped packet
- `zigux/tests/runtime_atomic64_manifest.json` owns the exact checks plus the delivery catalog and ownership map for the current runtime atomic64 packet
- `zigux/tests/runtime_atomic64_survey.zig` owns the machine-checkable replay of that ownership packet and the adjacent blocked shared-loader note
- `zigux/tests/runtime_atomic64_module.zig` owns the bounded starter lifecycle, selftest, and guard-path replay surface
- `zigux/tests/runtime_atomic64_diff.zig` owns the bounded differential replay for arithmetic, bitwise, swap, compare-swap, and guard-return expectations
- `zigux/tests/phase9_build.zig` owns the shared Phase 9 replay entrypoint for the direct atomic64 sample, module, diff, and loader legs plus the survey and shared runtime-loader checks
- `samples/zigux/runtime_atomic64.zig` owns the bounded in-memory atomic64 starter contract, lifecycle staging, and selftest-hook metadata
- `samples/zigux/runtime_atomic64_loader.zig` owns the sample-side loader projection, explicit shared `command_name` preservation, prepared counter-summary snapshot replay, `waiting_on_runtime_substrate` handoff, `released_without_substrate` fallback, and atomic64 payload summary
- `zigux/kernel/runtime_loader.zig` owns the shared runtime-loader request contract that consumes the atomic64 loader handoff, allocator posture, staged entry and exit symbols, and prepared counter-summary snapshot replay
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md` owns the still-blocked shared command-name, argv-policy, and environment-derived activation-control posture that keeps this atomic64 packet pre-execution
- `Documentation/zigux/phase9-runtime-loader-substrate-plan.md` owns the shared loader-stage vocabulary and the adjacent atomic64 handoff-alignment note that keep this packet coupled to the still-blocked shared loader review surface
- `Documentation/zigux/freeze-map.md` owns the study-only `kernel/workqueue.c` boundary and the Architecture Council reopen rule that keep this atomic64 packet out of scheduler-facing parity claims

## Recorded gaps

The manifest now records both the ownership packet and the current gap posture:

- the landed `phase9-build-gate`, including the direct `phase9-runtime-atomic64-sample-tests`, `phase9-runtime-atomic64-module-tests`, `phase9-runtime-atomic64-diff-tests`, and `phase9-runtime-atomic64-loader-tests` shared-build legs
- the landed `runtime-atomic64-survey-gate`
- the landed `runtime-atomic64-sample-module` starter
- the landed `runtime-atomic64-module-tests`
- the landed `runtime-atomic64-diff-gate`
- the landed `runtime-atomic64-loader-scaffold`
- the landed `runtime-atomic64-live-loader-binding`
- the still-blocked `runtime-atomic64-shared-loader-controls`

This keeps the survey useful after the first starter, direct sample-test leg, direct module-test leg, direct diff-test leg, direct loader-test leg, module gate, diff gate, loader scaffold, and shared loader-request binding landed without pretending that Zigux already has a loadable runtime module or the full shared runtime control surface needed for real execution. It also keeps ownership for the shipped evidence packet explicit so the survey note, module-slice note, manifest, survey gate, module gate, diff gate, sample-side loader, prepared counter-summary snapshot replay, shared loader contract, and shared Phase 9 replay entrypoint cannot drift independently by eye.

## Gates

1. run the dedicated Phase 9 survey gate
- `zig test zigux/tests/runtime_atomic64_survey.zig`

2. run the shared Phase 9 runtime survey bundle
- `zig build test --build-file zigux/tests/phase9_build.zig`
- this shared build now includes the direct `phase9-runtime-atomic64-sample-tests`, `phase9-runtime-atomic64-module-tests`, `phase9-runtime-atomic64-diff-tests`, and `phase9-runtime-atomic64-loader-tests` legs alongside the atomic64 survey, module, diff, loader, and shared runtime-loader checks

3. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice still does not claim:

- a loadable Zigux runtime module implementation
- runtime module lifecycle parity against a real loader path
- a kernel-loadable `samples/zigux/runtime_atomic64.zig` module
- direct parity for the full `lib/atomic64_test.c` surface beyond the bounded starter and diff gate
- shared runtime-loader command-name, argv-policy, or environment-activation controls
- parity or ownership for `kernel/workqueue.c`
- any freeze-map status change for the scheduler-facing workqueue boundary without an Architecture Council decision

## Next bounded step

Stay in the Phase 9 runtime atomic64 lane and keep future work narrowly aimed at the remaining runtime substrate handoff or lifecycle-parity blocker, rather than reopening already-landed survey, sample, loader-scaffold, shared binding, module-gate, or diff-gate scaffolding, while keeping the separate `kernel/workqueue.c` freeze-map boundary in study-only status unless the Architecture Council explicitly reopens it.