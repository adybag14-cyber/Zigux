# Phase 9 Runtime Bitmap Module Slice

This document tracks the current bounded runtime bitmap slice.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-partial-slice`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=2026-05-22-runtime-bitmap-diff-returned`
- scope: partial runtime bitmap reminder packet, direct sample proof, direct direct-init companion proof, direct cold-stage guard proof, direct loader proof, direct module proof, direct diff proof, manifest-backed ownership packet, top-bit and active-word-boundary companion proof, bounded build-bundle vocabulary, and no broader shared runtime-loader claim

## Current visible slice
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `zigux/tests/runtime_bitmap_manifest.json`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/phase9_build.zig`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_direct_init_contract.zig`
- `samples/zigux/runtime_bitmap_cold_stage_guard.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`

## Repo-reality gaps inside the bitmap family
- none on the trusted current-tree read path

## Adjacent shared-owner evidence outside this bitmap reminder packet
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`
- the bounded `phase9-runtime-loader-allocator-init-flow-tests`, `phase9-runtime-loader-shared-tests`, `phase9-runtime-loader-command-env-boundary-guard-tests`, and `phase9-first-loadable-runtime-module-parity-survey-tests` routes inside `zigux/tests/phase9_build.zig`

## Historical wider-family shared loader vocabulary still missing on trusted direct reads
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
- `zigux/tests/runtime_loader_gap_manifest.json`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- the broader shared `zigux/tests/runtime_*` replay family beyond the returned allocator/init-flow and command/environment boundary packet

## Why This Slice Exists

The runtime bitmap lane still needs a family-local note that keeps the visible reminder packet explicit without turning it into false proof that every broader shared runtime-loader surface returned too.

The current visible packet includes the direct bitmap sample, direct-init normalization companion, direct cold-stage guard companion, direct loader companion, direct module proof, direct diff proof, focused top-bit and active-word-boundary companion, manifest-backed ownership packet, survey note, module-slice note, survey gate, and bounded build bundle. The shared `zigux/tests/phase9_build.zig` bundle reruns the direct sample, direct-init companion, cold-stage guard, loader, module, survey, diff gate, and top-bit companion through the dedicated `phase9-runtime-bitmap-direct-init-contract-tests`, `phase9-runtime-bitmap-cold-stage-guard-tests`, and `phase9-runtime-bitmap-top-bit-tests` routes plus the aggregate `phase9-runtime-bitmap-tests` handle. The neighboring shared loader packet also survives through allocator/init-flow, command/environment boundary guard, the bounded loader-shared routes, and the broader `phase9-first-loadable-runtime-module-parity-survey-tests` handle, but those adjacent shared-owner surfaces still do not prove the broader runtime bitmap packet has reached loadable pilot-module parity.

The diff leg is directly readable again on the trusted path, but the older wider-family loader-gap survey and manifest vocabulary still does not return there, so this slice must stay bitmap-local while keeping that narrower returned shared loader packet distinct from the still-missing wider-family loader backlog.

## Roadmap Gap

- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap packet is still `partial_packet_with_diff_but_without_broader_runtime_loader_parity`: the survey note, module-slice note, manifest-backed ownership packet, survey gate, bounded build bundle, direct sample, direct-init normalization companion, direct cold-stage guard companion, direct loader companion, direct module proof, direct diff proof, and top-bit plus active-word-boundary companion are visible, but the broader shared runtime-loader family remains only partially returned on the trusted path
- the blocked follow-through remains `broader shared runtime-loader family completion plus loadable Phase 9 runtime bitmap pilot module parity`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig test zigux/tests/runtime_bitmap_module.zig`
3. `zig test zigux/tests/runtime_bitmap_diff.zig`
4. `zig build phase9-runtime-bitmap-direct-init-contract-tests --build-file zigux/tests/phase9_build.zig`
5. `zig build phase9-runtime-bitmap-loader-tests --build-file zigux/tests/phase9_build.zig`
6. `zig build phase9-runtime-bitmap-module-tests --build-file zigux/tests/phase9_build.zig`
7. `zig build phase9-runtime-bitmap-diff-tests --build-file zigux/tests/phase9_build.zig`
8. `zig build phase9-runtime-bitmap-cold-stage-guard-tests --build-file zigux/tests/phase9_build.zig`
9. `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`
10. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`

Treat the shared `zigux/tests/phase9_build.zig` bitmap route names as rerun handles for the visible sample, direct-init companion, cold-stage guard, loader, module, survey, diff, and top-bit packet only; they do not prove the broader shared runtime-loader family returned beyond the narrower allocator/init-flow, command/environment boundary, and cross-family parity-survey packet.

## Next Bounded Step

Advance only to the next bitmap-local compile or note mismatch that a fresh `phase9-runtime-bitmap-tests` replay exposes, and widen only when a coherent broader shared runtime-loader packet is directly readable again.
