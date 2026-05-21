# Phase 9 Runtime Bitmap Module Slice

This document tracks the current bounded runtime bitmap slice.

## Status
- `PHASE9_STATUS=active`
- `PHASE9_SLICE=runtime-bitmap-partial-slice`
- `PHASE9_LANE_KEY=P9-L08`
- `PHASE9_SURVEYED_COMMIT=2026-05-21-runtime-bitmap-manifest-restored`
- scope: partial runtime bitmap reminder packet, direct sample proof, direct loader proof, manifest-backed ownership packet, top-bit companion proof, bounded build-bundle vocabulary, and no broader shared runtime-loader claim

## Current visible slice
- `Documentation/zigux/phase9-runtime-bitmap-survey.md`
- `Documentation/zigux/phase9-runtime-bitmap-module-slice.md`
- `zigux/tests/runtime_bitmap_manifest.json`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/phase9_build.zig`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`

## Repo-reality gaps inside the bitmap family
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`

## Adjacent shared-owner evidence outside this bitmap reminder packet
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`
- the bounded `phase9-runtime-loader-shared-tests` and `phase9-runtime-loader-command-env-boundary-guard-tests` routes inside `zigux/tests/phase9_build.zig`

## Historical wider-family shared loader vocabulary still missing on trusted direct reads
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`
- `zigux/tests/runtime_loader_gap_manifest.json`
- `zigux/tests/runtime_loader_gap_survey.zig`
- `samples/zigux/runtime_trace_events_loader.zig`
- the broader shared `zigux/tests/runtime_*` replay family beyond the returned allocator/init-flow and command/environment boundary packet

## Why This Slice Exists

The runtime bitmap lane still needs a family-local note that keeps the visible reminder packet explicit without turning it into false proof that every broader shared runtime-loader surface returned too.

The current visible packet includes the direct bitmap sample, direct loader companion, focused top-bit companion, manifest-backed ownership packet, survey note, module-slice note, survey gate, and bounded build bundle. The shared `zigux/tests/phase9_build.zig` bundle reruns the direct sample, loader, survey gate, and top-bit companion; the neighboring shared loader packet also survives through allocator/init-flow, command/environment boundary guard, and bounded loader-shared routes, but those adjacent shared-owner surfaces still do not prove that the broader runtime bitmap module or diff packet returned.

The module and diff legs are still absent on the trusted read path, and the older wider-family loader-gap survey and manifest vocabulary still does not return there either, so this slice must stay bitmap-local while keeping that narrower returned shared loader packet distinct from the still-missing wider-family loader backlog.

## Roadmap Gap

- the Phase 9 roadmap target is still `first loadable Zigux runtime modules with selftest hooks and runtime module lifecycle parity`
- the current runtime bitmap packet is still `partial_packet_without_module_and_diff_follow_through`: the survey note, module-slice note, manifest-backed ownership packet, survey gate, bounded build bundle, direct sample, direct loader companion, and top-bit companion are visible, but the module gate and diff gate are not, and the broader shared runtime-loader family remains only partially returned on the trusted path
- the blocked follow-through remains `bitmap module-and-diff parity plus broader shared runtime-loader family completion`

## Gates
1. `zig test zigux/tests/runtime_bitmap_survey.zig`
2. `zig build phase9-runtime-bitmap-loader-tests --build-file zigux/tests/phase9_build.zig`
3. `zig build phase9-runtime-bitmap-top-bit-tests --build-file zigux/tests/phase9_build.zig`
4. `zig build phase9-runtime-bitmap-tests --build-file zigux/tests/phase9_build.zig`

Treat the shared `zigux/tests/phase9_build.zig` bitmap route names as rerun handles for the visible sample, loader, survey, and top-bit packet only while the module and diff surfaces stay absent on the trusted path; they do not prove the broader shared runtime-loader family returned beyond the narrower allocator/init-flow and command/environment boundary packet.

## Next Bounded Step

Advance the next same-lane surface inside the module-side runtime bitmap family, starting with `zigux/tests/runtime_bitmap_module.zig`, and widen only when a coherent module-side packet is directly readable again.
