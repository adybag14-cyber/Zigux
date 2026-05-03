# Phase 3 Rbtree Interop Helper Slice

This document records the first bounded Phase 3 helper packet around the roadmap's `lib/rbtree.c` anchor.

## Status

- `PHASE3_STATUS=active`
- `PHASE3_SLICE=rbtree-helper-interop`
- scope: first bounded `zigux/helpers/rbtree_*` helper packet only
- product boundary:
  - `zigux/helpers/rbtree_view.zig`
  - `zigux/helpers/rbtree_root_view.zig`
  - `Documentation/zigux/phase3-rbtree-slice.md`
  - `zigux/tests/phase3_rbtree_survey.zig`
  - `zigux/tests/phase3_rbtree_root_view_survey.zig`
  - `zigux/tests/phase3_rbtree_manifest.json`
- `PHASE3_RBTREE_DEDICATED_BOUNDARY_PARITY=zigux/tests/fixtures/phase3_rbtree/expected.json,zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c`
- `PHASE3_RBTREE_SHARED_BOUNDARY_GAP=shared-abi-root-view-lift-still-missing`
- `PHASE3_RBTREE_SHARED_BOUNDARY_TARGET=include/zigux/abi.h,zigux/bindings/abi.zig,zigux/tests/fixtures/phase3_abi/`

## Why this slice exists

The roadmap gap note has been pointing at the missing Phase 3 `rbtree` helper family for a while.

This slice keeps the next move deliberately small:

- one helper-local summary view over the existing runtime `rbtree` packet
- one reusable root-view helper around the dedicated Phase 3 binding packet
- bounded node counting with a truncation signal
- explicit first-node and last-node address reporting
- one machine-checked survey packet that records the narrowed remaining gap

That gives Phase 3 a real `zigux/helpers/rbtree_*` foothold without pretending the shared ABI lift is already complete.

## Gates

1. run the helper-local Zig tests
- `zig test zigux/helpers/rbtree_view.zig`
- `zig test zigux/helpers/rbtree_root_view.zig`

2. keep the survey packet machine-checked
- `zig test zigux/tests/phase3_rbtree_survey.zig`
- `zig test zigux/tests/phase3_rbtree_root_view_survey.zig`

3. keep the shared Phase 3 slice contract aligned
- `python3 scripts/zigux/validate-phase3.py`
- `zig build phase3-test --build-file zigux/tests/build.zig`
- `python3 scripts/zigux/run-phase3-checks.py --slug rbtree`

- `PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py`
- `PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig`
- `PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug rbtree`

## Boundary

This slice already carries:

- a dedicated `rbtree` root-view record in `include/zigux/rbtree.h` and `zigux/bindings/rbtree.zig`
- a dedicated C-vs-Zig parity replay in `zigux/tests/fixtures/phase3_rbtree/expected.json` and `zigux/tests/fixtures/phase3_rbtree/phase3_rbtree_c_harness.c`

This slice does not yet claim:

- a shared `rbtree` record in `include/zigux/abi.h`
- a matching shared `zigux/bindings/abi.zig` layout type
- a shared `zigux/tests/fixtures/phase3_abi/` parity replay for the `rbtree` root view

The remaining honest Phase 3 `rbtree` gap after this step is the shared ABI lift, not the absence of a dedicated boundary packet.

## Next bounded step

The next honest follow-up is one curated shared Phase 3 `rbtree` root-view lift:

- one shared header-and-binding shape
- one shared parity fixture
- one validator-backed survey refresh

That keeps the roadmap-backed `rbtree` anchor moving without widening into more char-device planning churn.
