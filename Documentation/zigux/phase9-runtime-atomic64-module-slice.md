# Phase 9 Runtime Atomic64 Module Slice

This note tracks the current bounded Phase 9 runtime atomic64 review packet on `master`.

## Status

- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-atomic64-review-packet`
- `PHASE9_LANE_KEY=P9-L04`
- scope: atomic64 family-local loader scaffold, manifest-backed reminder surfaces, and adjacent shared loader-handoff evidence only

## Current review surface

Current `master` keeps these atomic64 family-local surfaces visible:

- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `zigux/tests/runtime_atomic64_manifest.json`
- `samples/zigux/runtime_atomic64_loader.zig`

Current `master` also keeps the adjacent shared loader-facing packet visible:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/phase9_build.zig`
- `zigux/Makefile`
- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`

Direct atomic64 starter files do not currently materialize on `master`:

- `samples/zigux/runtime_atomic64.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`

That means the honest current slice is a partial atomic64 reminder packet plus the shared loader-handoff packet, not a fully materialized atomic64 sample, module, diff, and survey bundle.

## Why this slice exists

The Phase 9 roadmap still uses `lib/atomic64_test.c` as the atomic64 pilot anchor and still expects first loadable Zigux runtime modules, selftest hooks, and runtime module lifecycle parity under `samples/zigux/runtime_*` and `zigux/tests/runtime_*`.

Current `master` does not close that full starter yet. The family-local proof that remains visible is the bounded loader scaffold plus the manifest-backed reminder surfaces, while the broader shared runtime-loader substrate is still the real blocker for loadable runtime parity.

This note exists to keep that smaller review packet explicit without pretending that the missing direct starter files or the live runtime substrate are already landed.

## Truthfulness rules

1. Keep the atomic64 family described as a partial Phase 9 review packet, not as completed loadable runtime module parity.
2. Keep the shared loader-facing packet adjacent but separate. If `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, `zigux/tests/runtime_loader_allocator_init_flow.zig`, `zigux/tests/phase9_build.zig`, or the shared sequencing note drift, record that in the shared Phase 9 loader lane instead of claiming the atomic64 family covers it alone.
3. Do not claim that the direct atomic64 sample, module, diff, or survey files are present on `master` until those files can be read directly again.
4. Do not invent a dedicated `validate-phase9.py` route, a separate atomic64-only validator, or a cleared runtime-substrate handoff on current `master`.

## Active blocker posture

The family-local blocker on current `master` is still the missing direct atomic64 starter packet.

The loader scaffold, manifest, and reminder notes are present, but the direct atomic64 sample, module gate, diff gate, and dedicated survey gate do not currently materialize. Until they do, this slice should stay described as partial atomic64 review evidence only.

The broader shared runtime substrate also remains blocked. Until that shared substrate lands, the atomic64 family should stay framed as loader-handoff evidence rather than completed runtime module lifecycle parity.

## Next bounded step

Keep future follow-through literal and lane-local: either restore one missing direct atomic64 starter file at a time or continue trimming overstated atomic64 wording so each family-local note matches the live repo packet exactly.
