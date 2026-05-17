# Phase 3 bitmap/cpumask Slice

This note records the current helper-local Phase 3 bitmap and cpumask interop slice on the Lane 27 branch.

## Current Slice

- `include/zigux/bitmap_cpumask.h`
- `zigux/uapi/bitmap_cpumask.zig`
- `zigux/bindings/bitmap_cpumask.zig`
- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_build.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py`
- `zigux/tests/phase3_bitmap_cpumask_dump.zig`
- `zigux/tests/phase3_bitmap_cpumask_dump_build.zig`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`
- `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`
- `zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`
- `scripts/zigux/check-phase3-bitmap-cpumask.py`

## Bounded Contract

The helper family stays intentionally small:

- `zigux/helpers/bitmap_view.zig` only models bounded bitmap word traversal, last-word masking, first-set and first-zero search, and weight summaries over the shared layout surface
- `zigux/helpers/cpumask_view.zig` only layers bounded CPU-membership helpers over that same bitmap view without widening into scheduler or topology behavior
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig` keeps the helper-local header, UAPI, bindings, and version linkage reviewable as one manifest-backed starter packet

## Current Replay Surface

The current helper-local packet now has two bounded replay layers:

- one manifest-backed starter packet:
  - `zigux/tests/phase3_bitmap_cpumask_starter_packet_manifest.json`
  - `scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py`
  - `python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py --self-test`
  - `python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py`
- one fixture-backed parity packet:
  - `zigux/tests/phase3_bitmap_cpumask_dump.zig`
  - `zigux/tests/phase3_bitmap_cpumask_dump_build.zig`
  - `zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`
  - `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`
  - `zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json`
  - `scripts/zigux/check-phase3-bitmap-cpumask.py`
  - `python3 scripts/zigux/check-phase3-bitmap-cpumask.py --self-test`
  - `python3 scripts/zigux/check-phase3-bitmap-cpumask.py --repo-root . --zig zig --cc gcc`
  - `zig build phase3-bitmap-cpumask-dump --build-file zigux/tests/phase3_bitmap_cpumask_dump_build.zig`

That fixture-backed parity packet keeps one tiny bitmap-and-cpumask C-vs-Zig comparison explicit without reopening the broader shared tests root.

## Current Gap

This is still not the broader Phase 3 ABI, export/UAPI, catalog, or low-level-wrapper packet that older reminder surfaces still name. It is one helper-local interop proof layered beside the current `dev_t`, `err_ptr` / `xarray`, and policy slices.

Current shared reminder follow-up still belongs to the broader Phase 3 truthfulness pass:

- `Documentation/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/review-checklist.md`

Those surfaces should stay separate from this helper-local packet instead of being treated as proof that the wider validator or export-boundary routes already ship.

## Scope

This note is limited to the helper-local bitmap and cpumask boundary plus one tiny fixture-backed parity dump. It does not claim scheduler semantics, topology state, broader UAPI layout support, IDR or IDA coverage, or any shared `phase3` replay route.
