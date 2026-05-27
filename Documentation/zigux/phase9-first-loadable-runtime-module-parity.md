# Phase 9 First Loadable Runtime Module Parity

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=first-loadable-runtime-module-parity`
- `PHASE9_LANE_KEY=P9-L01`
- `PHASE9_SURVEYED_COMMIT=2026-05-25-first-loadable-parity-bitmap-direct-init-readback`
- scope: cross-family repo-reality survey for the returned atomic64 and kretprobe direct packets with their family-local loader companions, the still-partial bitmap reminder packet with returned direct-init companion, restored cold-stage guard, module, and diff proof, and the narrower shared loader reminder packet only

## Current Repo Reality
Trusted current-tree reads on 2026-05-25 now show a four-part Phase 9 pilot picture: the atomic64 and kretprobe sides return direct packets with family-local loader companions, the bitmap side remains partial but now includes the returned direct-init companion, direct cold-stage guard, module, and diff proof, and the narrower shared loader reminder packet is readable without proving shipped loader parity.

These atomic64-facing surfaces are directly readable on current `master`:
- `Documentation/zigux/phase9-runtime-atomic64-survey.md`
- `Documentation/zigux/phase9-runtime-atomic64-module-slice.md`
- `samples/zigux/runtime_atomic64.zig`
- `samples/zigux/runtime_atomic64_loader.zig`
- `zigux/tests/runtime_atomic64_module.zig`
- `zigux/tests/runtime_atomic64_diff.zig`
- `zigux/tests/runtime_atomic64_survey.zig`
- `zigux/tests/runtime_atomic64_manifest.json`

Current `master` now directly materializes the atomic64 sample, family-local loader companion, survey, and manifest packet beside the already readable module, diff, and family-local note surfaces.

These kretprobe-facing surfaces are directly readable on current `master`:
- `samples/zigux/runtime_kretprobe.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`
- `zigux/tests/runtime_kretprobe_module.zig`
- `zigux/tests/phase9_build.zig`

Current `master` now directly materializes the kretprobe sample, family-local loader companion, and module lifecycle packet beside the shared Phase 9 build shard, but that returned loader companion still does not close the broader shared loader or shipped loader parity proof.

These bitmap-facing surfaces are directly readable on current `master`:
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_direct_init_contract.zig`
- `samples/zigux/runtime_bitmap_cold_stage_guard.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`

Current `master` now directly materializes the bitmap direct-init companion beside the visible sample, cold-stage guard, loader, top-bit, survey, manifest, module, and diff packet while broader shared loader completion remains blocked.

These shared runtime-loader-facing surfaces are directly readable on current `master`:
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`

## Cross-Family Parity
The Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`.

Current `master` does not yet materialize that target as a coherent cross-family packet:
- the atomic64 side now exposes a direct trusted-path packet around the sample, family-local loader companion, module, diff, survey, manifest, and family-local notes, but that returned loader companion still stops short of broader shared loader proof or shipped loader parity
- the kretprobe side now exposes a direct trusted-path packet around the sample, family-local loader companion, module-boundary lifecycle replay, and shared build shard, but that returned loader companion still stops short of broader shared loader proof or shipped loader parity
- the bitmap side still exposes only a partial trusted-path packet around the direct sample, direct-init normalization companion, cold-stage guard companion, loader, top-bit companion, manifest-backed ownership packet, survey gate, bounded build bundle, and restored module and diff proof while broader shared loader completion remains blocked
- the directly readable shared runtime-loader allocator/init-flow, note, contract, and command/environment boundary surfaces still stop short of shipped install-root, depmod, or end-to-end lifecycle parity proof
- the shared `zigux/tests/phase9_build.zig` bundle still proves `phase9-runtime-atomic64-diff`, the build-local `phase9-runtime-atomic64-loader-tests` route name, the build-local `phase9-runtime-atomic64-module-tests` route name, the build-local `phase9-runtime-atomic64-sample-tests` route name, the build-local `phase9-runtime-kretprobe-sample-tests` route name, the build-local `phase9-runtime-kretprobe-loader-tests` route name, the build-local `phase9-runtime-kretprobe-module-tests` route name, the aggregate `phase9-runtime-kretprobe-tests` route name, the build-local `phase9-runtime-bitmap-direct-init-contract-tests` route name, the bounded bitmap sample, direct-init companion, cold-stage guard, loader, survey, top-bit, module, and diff routes, the build-local `phase9-runtime-loader-allocator-init-flow-tests` route name, the build-local `phase9-runtime-loader-command-env-boundary-guard-tests` route name, the build-local `phase9-runtime-loader-shared-tests` route name, and the shared `phase9-first-loadable-runtime-module-parity-survey-tests` handle; because broader shared loader completion surfaces still remain absent on the same trusted path, those surviving shared-loader and cross-family route names are reminder vocabulary rather than proof that the underlying Phase 9 parity target shipped

That means this note must not claim shipped cross-family loader parity, shipped runtime-loader handoff parity, or shipped end-to-end module lifecycle parity on current `master`.

## Boundaries
Keep this note lane-local and repo-reality-first:
- do not repair atomic64 family-local survey, loader-companion, module-slice, manifest, or direct-sample wording here; hand that work back to the owning atomic64 family lane
- do not repair kretprobe family-local sample, loader-companion, or module-boundary wording here; hand that work back to the owning kretprobe family lane if that direct packet changes
- do not repair bitmap family-local survey, module-slice, manifest, or direct-sample wording here; hand that work back to the owning bitmap family lane
- do not treat broader shared reminder, checklist, or scripts-root truthfulness work as owned here
- do not infer real runtime execution, depmod publication, or live registration control from the currently readable partial pilot packet

## Next Bounded Step
Leave `P9-L01` parked unless a fresh live reread finds another exact cross-family parity-summary mismatch between this note, the shared survey gate, the shared build shard, the returned atomic64 and kretprobe direct packets with their family-local loader companions, and the still-partial bitmap reminder packet with returned direct-init companion, restored cold-stage guard, module, and diff proof but without broader shared runtime-loader parity.
If only one family gains or loses trusted-path coverage, hand the repair back to that owning family lane.
If the shared runtime-loader substrate returns more than the visible allocator/init-flow, note, contract, and command/environment boundary packet, hand the loader-side proof back to the shared loader lane before reviving cross-family parity claims here.
