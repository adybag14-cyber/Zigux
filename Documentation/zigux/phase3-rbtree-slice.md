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
- `PHASE3_RBTREE_SHARED_BOUNDARY_STATUS=shared-root-view-lift-landed-shared-replay-present`
- `PHASE3_RBTREE_SHARED_BOUNDARY_GAP=shared-phase3-abi-note-and-marker-alignment-still-needed`
- `PHASE3_RBTREE_SHARED_BOUNDARY_GUARDS=scripts/zigux/check-phase3-abi-layout-packet.py,scripts/zigux/check-phase3-rbtree-shared-lift-contract.py`

## Why this slice exists

The roadmap gap note had been pointing at the missing Phase 3 `rbtree` helper family for a while.

This slice kept the next move deliberately small:

- one helper-local summary view over the existing runtime `rbtree` packet
- one reusable root-view helper around the dedicated Phase 3 binding packet
- bounded node counting with a truncation signal
- explicit first-node and last-node address reporting
- one machine-checked survey packet that records the narrowed remaining gap

That gave Phase 3 a real `zigux/helpers/rbtree_*` foothold without widening into balancing logic or unrelated boundary growth.

This slice now carries both the dedicated `rbtree` boundary packet and the landed shared Phase 3 ABI root-view lift.

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
- a shared Phase 3 ABI replay in `zigux/tests/phase3_abi.zig`, `zigux/tests/phase3_abi_dump.zig`, and `zigux/tests/fixtures/phase3_abi/phase3_abi_c_harness.c` that now uses the curated shared header and binding path for `zigux_rbtree_root_view`
- the shared ABI manifest now catalogs both that dedicated packet and the shared ABI replay plus the shared-lift guards, so the outstanding same-family work is note and marker alignment rather than missing shared code

This slice does not yet claim:

- broader shared `rbtree` node or iterator records beyond the current root-view packet
- wider shared helper growth beyond the current root-view layout and root-flag contract
- any excuse to widen Phase 3 chrdev-tail churn under the name of `rbtree` progress

The remaining honest Phase 3 `rbtree` gap after this step is the broader shared ABI note-and-marker alignment, not the absence of a dedicated or shared boundary packet.

## Next bounded step

The next honest follow-up is one bounded shared-note alignment pass:

- align the broader shared ABI note and marker packet with the landed shared root-view lift
- keep the dedicated packet, shared replay, and shared-lift guards explicit
- reuse the existing dedicated `zigux_rbtree_root_view` layout and flag constants unchanged
