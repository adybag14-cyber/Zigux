# Phase 9 Runtime Atomic64 Survey

This document tracks the bounded Phase 9 runtime pilot-module survey around `lib/atomic64_test.c`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-survey`
- scope: survey manifest, dedicated runtime survey gate, direct `phase9-runtime-atomic64-sample-tests` shared-build leg, landed sample-backed module starter, landed module gate, landed diff gate, landed loader scaffold, landed shared loader-request binding, and the lane-level review note that keeps the remaining roadmap blocker explicit without claiming loadable-module parity
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

## Why this slice exists

The Phase 9 roadmap explicitly names `lib/atomic64_test.c` as a runtime pilot-module anchor and recommends `zigux/tests/runtime_*` plus `samples/zigux/runtime_*` as the bounded Zigux destinations.

The live repo originally carried the Linux atomic64 runtime test without any dedicated Phase 9 review gate, `runtime_*` Zigux tests, or `samples/zigux/` pilot-module scaffold. This survey note stays in place as the lane history and review anchor after the bounded starter sample, direct sample-test leg, module gate, diff gate, loader scaffold, and shared loader-request binding landed, so Phase 9 can keep recording what is shipped versus what still depends on the runtime substrate.

## Survey findings

- `lib/atomic64_test.c` is present on `master` at 277 lines.
- the repo had zero `zigux/tests/runtime_*` files before this survey landed.
- the repo had no `samples/zigux/` directory before this survey landed.
- the repo had no `zigux/tests/phase9_build.zig` gate and no dedicated Phase 9 runtime note before this survey landed.

## Roadmap snapshot

Against the Phase 9 roadmap requirements, the current runtime atomic64 lane now records:

- a landed sample-backed runtime starter with selftest-hook metadata under `samples/zigux/runtime_atomic64.zig`
- a landed direct `phase9-runtime-atomic64-sample-tests` shared-build leg in `zigux/tests/phase9_build.zig` so the sample file's own lifecycle and summary replay now runs as first-class shared build evidence
- a landed sample-side loader scaffold in `samples/zigux/runtime_atomic64_loader.zig`
- a landed dedicated module gate in `zigux/tests/runtime_atomic64_module.zig`
- a landed dedicated differential gate in `zigux/tests/runtime_atomic64_diff.zig`
- a landed shared runtime-loader request binding under `zigux/kernel/runtime_loader.zig` that can consume the atomic64 loader handoff shape, staged entry and exit symbols, allocator posture, and the four-field atomic64 payload summary
- the differential gate now includes the bounded arithmetic, bitwise, swap, compare-swap, and guard-return families from `lib/atomic64_test.c`, including `or`, `and`, `xor`, `andnot`, `add_unless`, `inc_not_zero`, and `dec_if_positive`
- a remaining blocked shared runtime control surface under `zigux/kernel/runtime_loader.zig`, because command-name, argv-policy, and environment-derived activation handling still have no shared owner and true runtime execution or lifecycle parity remains out of scope

This keeps the survey honest about the difference between the shipped in-memory pilot and the still-missing loadable runtime substrate.

## Recorded gaps

The manifest now records:

- the landed `phase9-build-gate`, including the direct `phase9-runtime-atomic64-sample-tests` shared-build leg
- the landed `runtime-atomic64-survey-gate`
- the landed `runtime-atomic64-sample-module` starter
- the landed `runtime-atomic64-module-tests`
- the landed `runtime-atomic64-diff-gate`
- the landed `runtime-atomic64-loader-scaffold`
- the landed `runtime-atomic64-live-loader-binding`
- the still-blocked `runtime-atomic64-shared-loader-controls`

This keeps the survey useful after the first starter, direct sample-test leg, module gate, diff gate, loader scaffold, and shared loader-request binding landed without pretending that Zigux already has a loadable runtime module or the full shared runtime control surface needed for real execution.

## Gates

1. run the dedicated Phase 9 survey gate
- `zig build test --build-file zigux/tests/phase9_build.zig`
- this shared build now includes the direct `phase9-runtime-atomic64-sample-tests` leg alongside the atomic64 survey, module, diff, loader, and shared runtime-loader checks

2. run the convenience target
- `make -C zigux phase9`

## Non-goals

This survey slice still does not claim:

- a loadable Zigux runtime module implementation
- runtime module lifecycle parity against a real loader path
- a kernel-loadable `samples/zigux/runtime_atomic64.zig` module
- direct parity for the full `lib/atomic64_test.c` surface beyond the bounded starter and diff gate
- shared runtime-loader command-name, argv-policy, or environment-activation controls

## Next bounded step

Stay in the Phase 9 runtime atomic64 lane and keep future work narrowly aimed at the remaining runtime substrate handoff or lifecycle-parity blocker, rather than reopening already-landed survey, sample, loader-scaffold, shared binding, module-gate, or diff-gate scaffolding.
