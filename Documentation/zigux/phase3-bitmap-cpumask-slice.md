# Phase 3 bitmap/cpumask Slice

This note records the current helper-local Phase 3 bitmap and cpumask starter packet on this branch.

## Current Status

- `PHASE3_BITMAP_CPUMASK_SLICE_FILE_COUNT=11`
- `PHASE3_BITMAP_CPUMASK_SLICE_SCOPE=helper-local bitmap summary and cpumask membership replay`
- `PHASE3_BITMAP_CPUMASK_NEXT_SAFE_STEP=keep the bitmap and cpumask helper family bounded to manifest-backed replay and truthful validator-support wording before widening into the fixture-backed parity packet or broader Phase 3 closure claims`

## Current Slice

- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `Documentation/zigux/phase3-validator-support-surface.md`
- `include/zigux/bitmap_cpumask.h`
- `zigux/uapi/bitmap_cpumask.zig`
- `zigux/bindings/bitmap_cpumask.zig`
- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py`

## Bounded Contract

The helper family stays intentionally small:

- `zigux/helpers/bitmap_view.zig` only models bounded bitmap word traversal, last-word masking, first-set and first-zero search, and weight summaries over the shared layout surface.
- `zigux/helpers/cpumask_view.zig` only layers bounded CPU-membership helpers over that same bitmap view without widening into scheduler or topology behavior.
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig` keeps the helper-local header, UAPI, bindings, helper behavior, and version linkage reviewable as one manifest-backed starter packet.

## Current Replay Surface

The current helper-local packet stays intentionally narrow:

- `zigux/tests/phase3_bitmap_cpumask_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py`
- `python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py`
- `zig build phase3-bitmap-cpumask-starter-packet-test --build-file zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`

The separate fixture-backed parity packet remains the next same-lane follow-up rather than part of this restack:

- `zigux/tests/phase3_bitmap_cpumask_dump.zig`
- `zigux/tests/phase3_bitmap_cpumask_dump_build.zig`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`
- `zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask.py`

## Current Gap

This is still not the broader Phase 3 ABI, export/UAPI, catalog, or low-level-wrapper packet that older reminder surfaces still name. It is one helper-local interop proof layered beside the current `dev_t`, `err_ptr` / `xarray`, and policy slices.

Shared reminder follow-up still belongs in the separate broader Phase 3 truthfulness lane:

- `Documentation/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`

Those surfaces should stay separate from this helper-local packet instead of being treated as proof that the wider validator or export-boundary routes already ship.

## Scope

This note is limited to the helper-local bitmap and cpumask starter boundary. It does not claim scheduler semantics, topology state, broader UAPI layout support, IDR or IDA coverage, or any shared `phase3` replay route.