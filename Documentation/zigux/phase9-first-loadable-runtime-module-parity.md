# Phase 9 First Loadable Runtime Module Parity

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=first-loadable-runtime-module-parity`
- `PHASE9_LANE_KEY=P9-L01`
- scope: cross-family repo-reality survey for the bounded atomic64 and bitmap runtime pilot packets only

## Current Repo Reality
Trusted current-tree reads on 2026-05-20 show a mixed partial Phase 9 pilot picture rather than either of the older extremes.

These atomic64-facing surfaces are directly readable on current `master`:
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`

These atomic64-facing surfaces are not directly readable on the same trusted path:
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`

These bitmap-facing surfaces are directly readable on current `master`:
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/phase9_build.zig`

These bitmap-facing surfaces are not directly readable on the same trusted path:
- `samples/zigux/runtime_bitmap_loader.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_bitmap_manifest.json`

The broader shared runtime-loader substrate is also still absent on the trusted read path:
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`

## Cross-Family Parity
The Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`.

Current `master` does not yet materialize that target as a coherent cross-family packet:
- the atomic64 side still exposes only a partial trusted-path packet around module and diff evidence plus family-local notes
- the bitmap side still exposes only a partial trusted-path packet around the direct sample, top-bit companion, survey gate, and bounded build bundle
- the shared runtime-loader substrate remains absent on the trusted path
- the shared `zigux/tests/phase9_build.zig` bundle currently proves only `phase9-runtime-atomic64-diff` plus the bounded bitmap sample, survey, and top-bit routes; it does not prove a matched pair of first-loadable runtime modules

That means this note must not claim shipped cross-family loader parity, shipped runtime-loader handoff parity, or shipped end-to-end module lifecycle parity on current `master`.

## Boundaries
Keep this note lane-local and repo-reality-first:
- do not repair atomic64 family-local survey, module-slice, manifest, or direct-sample wording here; hand that work back to the owning atomic64 family lane
- do not repair bitmap family-local survey, module-slice, manifest, or direct-sample wording here; hand that work back to the owning bitmap family lane
- do not treat broader shared reminder, checklist, or scripts-root truthfulness work as owned here
- do not infer real runtime execution, depmod publication, or live registration control from the currently readable partial pilot packet

## Next Bounded Step
Leave `P9-L01` parked after this shared note refresh unless a fresh live reread proves that both families return to a directly readable first-loadable packet shape at the same time.
If only one family gains or loses trusted-path coverage, hand the repair back to that owning family lane.
If the shared runtime-loader substrate returns, hand the loader-side proof back to the shared loader lane before reviving cross-family parity claims here.
