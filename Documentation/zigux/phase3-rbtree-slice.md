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
- `PHASE3_RBTREE_SHARED_BOUNDARY_STATUS=shared-root-view-lift-landed`
- `PHASE3_RBTREE_SHARED_BOUNDARY_PACKET=include/zigux/abi.h,zigux/bindings/abi.zig,zigux/tests/phase3_abi.zig,zigux/tests/phase3_abi_dump.zig,zigux/tests/fixtures/phase3_abi/expected.json`
- `PHASE3_RBTREE_SHARED_BOUNDARY_GUARDS=scripts/zigux/check-phase3-abi-layout-packet.py,scripts/zigux/check-phase3-rbtree-shared-lift-contract.py`

## Why this slice exists

The roadmap gap note has been pointing at the missing Phase 3 `rbtree` helper family for a while.

This slice kept the next move deliberately small:

- one helper-local summary view over the existing runtime `rbtree` packet
- one reusable root-view helper around the dedicated Phase 3 binding packet
- bounded node counting with a truncation signal
- explicit first-node and last-node address reporting
- one machine-checked survey packet that records the narrowed remaining gap

That gave Phase 3 a real `zigux/helpers/rbtree_*` foothold without pretending the shared ABI lift had already happened.

This slice already carries both the dedicated `rbtree` boundary packet and the first shared root-view lift into the canonical Phase 3 ABI packet.

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
- a shared `rbtree` root-view record in `include/zigux/abi.h` and `zigux/bindings/abi.zig`
- a shared C-vs-Zig parity replay for the same root view in `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, and `zigux/tests/fixtures/phase3_abi/expected.json`

This slice does not yet claim:

- broader shared `rbtree` node or iterator records beyond the landed root-view packet
- wider shared helper growth beyond the current root-view layout and root-flag contract
- any excuse to widen Phase 3 chrdev-tail churn under the name of `rbtree` progress

The remaining honest Phase 3 `rbtree` gap after this step is broader shared-surface expansion only if a roadmap-backed boundary really needs more than the current root-view packet.

## Next bounded step

The next honest follow-up is to keep the shared `rbtree` packet reviewable and bounded rather than pretending the lane still needs the first lift.

That means:

- keep the dedicated and shared parity fixtures aligned
- keep the slice and survey notes honest about what has already landed
- only widen the shared ABI surface if a concrete roadmap-backed consumer needs more than the current root-view layout and flags
