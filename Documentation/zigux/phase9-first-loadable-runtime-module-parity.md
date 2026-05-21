# Phase 9 First Loadable Runtime Module Parity

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=first-loadable-runtime-module-parity`
- `PHASE9_LANE_KEY=P9-L02`
- `PHASE9_SURVEYED_COMMIT=2026-05-21-first-loadable-parity-atomic64-direct-packet`
- scope: cross-family repo-reality survey for the bounded atomic64 direct packet, the partial bitmap reminder packet, and the shared loader contract surfaces only

## Current Repo Reality
Trusted current-tree reads on 2026-05-21 now show a split Phase 9 pilot picture: the atomic64 side returns a direct packet, the bitmap side remains partial, and the shared loader contract surfaces are readable without proving shipped loader parity.

These atomic64-facing surfaces are directly readable on current `master`:
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`

Current `master` now directly materializes the atomic64 sample, loader, survey, and manifest packet beside the already readable module, diff, and family-local note surfaces.

These bitmap-facing surfaces are directly readable on current `master`:
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/phase9_build.zig`

These bitmap-facing surfaces are not directly readable on the same trusted path:
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`

These shared runtime-loader-facing surfaces are directly readable on current `master`:
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`

## Cross-Family Parity
The Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`.

Current `master` does not yet materialize that target as a coherent cross-family packet:
- the atomic64 side now exposes a direct trusted-path packet around the sample, loader, module, diff, survey, manifest, and family-local notes
- the bitmap side still exposes only a partial trusted-path packet around the direct sample, loader, top-bit companion, manifest-backed ownership packet, survey gate, and bounded build bundle
- the directly readable shared runtime-loader note and contract files still stop short of shipped install-root, depmod, or end-to-end lifecycle parity proof
- the shared `zigux/tests/phase9_build.zig` bundle still proves `phase9-runtime-atomic64-diff`, the build-local `phase9-runtime-atomic64-module-tests` route name, the build-local `phase9-runtime-atomic64-sample-tests` route name, the bounded bitmap sample, loader, survey, and top-bit routes, the build-local `phase9-runtime-loader-shared-tests` route name, and the shared `phase9-first-loadable-runtime-module-parity-survey-tests` handle; because the bitmap module/diff legs and broader shared loader completion surfaces still remain absent on the same trusted path, those surviving shared-loader and cross-family route names are reminder vocabulary rather than proof that the underlying Phase 9 parity target shipped

That means this note must not claim shipped cross-family loader parity, shipped runtime-loader handoff parity, or shipped end-to-end module lifecycle parity on current `master`.

## Boundaries
Keep this note lane-local and repo-reality-first:
- do not repair atomic64 family-local survey, module-slice, manifest, or direct-sample wording here; hand that work back to the owning atomic64 family lane
- do not repair bitmap family-local survey, module-slice, manifest, or direct-sample wording here; hand that work back to the owning bitmap family lane
- do not treat broader shared reminder, checklist, or scripts-root truthfulness work as owned here
- do not infer real runtime execution, depmod publication, or live registration control from the currently readable partial pilot packet

## Next Bounded Step
Leave `P9-L02` parked unless a fresh live reread finds another exact cross-family parity-summary mismatch between this note, the shared survey gate, the shared build shard, the visible atomic64 direct packet, and the still-partial bitmap reminder packet.
If only one family gains or loses trusted-path coverage, hand the repair back to that owning family lane.
If the shared runtime-loader substrate returns more than the visible note-and-contract pair, hand the loader-side proof back to the shared loader lane before reviving cross-family parity claims here.
