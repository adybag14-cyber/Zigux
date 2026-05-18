# Phase 3 Bitmap Cpumask Gap

This note records the current bounded Lane 27 gap on `master`.

## Current Status

- `PHASE3_BITMAP_CPUMASK_GAP=current master still lacks the bounded bitmap/cpumask helper-local slice while the adjacent dev_t, err_ptr/xarray, policy, low-level-wrapper, and focused export/UAPI reminder surfaces already ship`
- `PHASE3_BITMAP_CPUMASK_GAP_DETAIL=direct current-head readback still returns missing for Documentation/zigux/phase3-bitmap-cpumask-slice.md, include/zigux/bitmap_cpumask.h, zigux/uapi/bitmap_cpumask.zig, zigux/bindings/bitmap_cpumask.zig, zigux/helpers/bitmap_view.zig, zigux/helpers/cpumask_view.zig, zigux/tests/phase3_bitmap_cpumask_starter_packet.zig, zigux/tests/phase3_bitmap_cpumask_dump.zig, scripts/zigux/check-phase3-bitmap-cpumask.py, and the combined zig build phase3-bitmap-cpumask --build-file zigux/tests/build.zig route, so current reminder surfaces should keep that packet framed as an unlanded same-lane slice rather than folding it into the shipped helper-local or shared-route inventory`
- `PHASE3_BITMAP_CPUMASK_NEXT_STEP=land or replay the bounded helper-local bitmap/cpumask packet, then refresh the shared reminder surfaces so they promote this slice from tracked gap to shipped Phase 3 evidence`

## Sampled Missing Lane 27 Members

- `Documentation/zigux/phase3-bitmap-cpumask-slice.md`
- `include/zigux/bitmap_cpumask.h`
- `zigux/uapi/bitmap_cpumask.zig`
- `zigux/bindings/bitmap_cpumask.zig`
- `zigux/helpers/bitmap_view.zig`
- `zigux/helpers/cpumask_view.zig`
- `zigux/tests/phase3_bitmap_cpumask_starter_packet.zig`
- `zigux/tests/phase3_bitmap_cpumask_dump.zig`
- `scripts/zigux/check-phase3-bitmap-cpumask.py`
- `zig build phase3-bitmap-cpumask --build-file zigux/tests/build.zig`

## Shared Reminder Boundary

- Keep the current docs-root, tests-root, validator-support, and scripts-root Phase 3 reminder surfaces explicit about the shipped `dev_t`, `err_ptr` / `xarray`, policy, low-level-wrapper, and focused export/UAPI layout packet.
- Keep the bitmap/cpumask slice separate from that shipped packet until direct current-`master` readback returns the helper-local, UAPI, binding, dump, and route surfaces above.
- Do not use the adjacent low-level-wrapper reminder packet or focused export/UAPI layout replay pair as evidence that the bitmap/cpumask slice already landed.

## Scope

This note is limited to the current Lane 27 reminder gap on live `master`. It records the missing bitmap/cpumask helper-local slice, names representative absent files and route surfaces, and keeps the next same-lane step pointed at landing or replaying the bounded packet before any broader reminder-surface promotion.