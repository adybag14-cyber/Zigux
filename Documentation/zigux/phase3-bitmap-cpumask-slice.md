# Phase 3 bitmap/cpumask Slice

This note records the current helper-local Phase 3 bitmap and cpumask interop slice on `master`.

## Current Status

- `PHASE3_BITMAP_CPUMASK_SLICE_FILE_COUNT=current master now carries one bounded bitmap/cpumask helper slice with a shared header, Zig UAPI and bindings, two helper-local views, one machine-readable manifest, and one focused replay route`
- `PHASE3_BITMAP_CPUMASK_SLICE_SCOPE=this slice proves bounded bitmap word traversal and cpumask membership decoding without widening into the older dump fixture, C harness, or broader Phase 3 validator stack`
- `PHASE3_BITMAP_CPUMASK_NEXT_SAFE_STEP=keep bitmap and cpumask helper coverage bounded to manifest-backed replay and truthful validator-support wording before widening into the older dump-style packet or shared Phase 3 closure claims`

## Files Present On Master

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
- `python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py --self-test`
- `python3 scripts/zigux/check-phase3-bitmap-cpumask-starter-packet.py`

## Current Gap

This is not the older broader Phase 3 bitmap/cpumask replay packet named in the bootstrap ledger. It does not claim that `zigux/tests/phase3_bitmap_cpumask_dump.zig`, `zigux/tests/fixtures/phase3_bitmap_cpumask/phase3_bitmap_cpumask_c_harness.c`, `zigux/tests/fixtures/phase3_bitmap_cpumask/expected.json`, or `zigux/tests/fixtures/phase3_bitmap_cpumask_manifest.json` already ship on current `master`.

The current slice only proves that the shared header layout, Zig UAPI surface, bindings offsets, bounded bitmap summary helpers, and cpumask membership helpers stay reviewable together under one manifest-backed replay route.

## Scope

This note is limited to the helper-local bitmap and cpumask interop family. It records the directly readable header, the Zig-facing layout surfaces, the helper-local summary and membership decoders, the dedicated replay route, and the machine-readable manifest. It does not claim the older dump fixture, C harness parity, or broader shared Phase 3 validator completion.
