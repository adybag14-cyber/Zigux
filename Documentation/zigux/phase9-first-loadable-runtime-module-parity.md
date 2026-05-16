# Phase 9 First Loadable Runtime Module Parity

## Status

- `PHASE9_STATUS=shared-atomic-bitmap-parity-survey`
- `PHASE9_SLICE=first-loadable-runtime-module-parity`
- `PHASE9_LANE_KEY=P9-L01`

## Roadmap Anchor

Phase 9 still promises the first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity.

For this bounded survey, keep the direct roadmap anchors to the first two runtime pilot families only:

- `lib/atomic64_test.c`
- `lib/test_bitmap.c`
- recommended destinations: `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

## Current Repo Reality

Current `master` already ships a real starter packet for the atomic64 pilot:

- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`

Current `master` also ships a real starter packet for the bitmap pilot:

- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`

Both families already ride the shared Phase 9 runtime-loader reminder packet through:

- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_loader_selftest_complete_exit_parity.zig`
- `zigux/tests/runtime_loader_lifecycle_boundary_guard.zig`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `zigux/tests/phase9_build.zig`
- `scripts/zigux/check-phase9-build-only-surface.py`
- `make -C zigux phase9-runtime-loader-shared-tests`
- `make -C zigux phase9`

## Honest Parity Read

The truthful current state is:

- atomic64: starter landed, selftest hook visible, family-local module and diff gates present, shared loader-facing handoff packet visible
- bitmap: starter landed, selftest hook visible, family-local module and diff gates present, bitmap-local top-bit contract present, shared loader-facing handoff packet visible
- shared parity blocker: the runtime substrate and publication path are still incomplete, so the repo does not yet ship loadable runtime-module parity for either family

That means the closest current repo reality to the roadmap promise is not “missing Phase 9,” and it is not “loadable parity achieved.” It is “first two pilot families materially staged, but still blocked at the shared runtime-substrate and publication boundary.”

## Blocked Boundary

Keep these surfaces review-only for this shared parity note:

- `.modinfo`
- `MODULE_ALIAS()`
- `modules.alias`
- `modules.order`
- `modules.builtin`
- module install-root state
- `depmod` script, manifest, or alias publication state

Until those shared publication surfaces move from blocked boundary to shipped behavior, the atomic64 and bitmap packets remain starter-parity evidence rather than first-loadable-module parity.

## Next Bounded Step

Keep the next same-lane follow-up inside the smallest shared runtime-loader substrate or reminder-surface repair that improves atomic64-plus-bitmap loadable-module truthfulness without reopening family-local sample, diff, or survey packets.
