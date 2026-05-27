# Phase 8 File-Path Handle Bridge Slice

This note records the current bounded Phase 8 file-path and handle bridge helper packet against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=active_helper_slice`
- `PHASE8_SLICE=file-path-handle-bridge`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-27
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: helper-local pathname shaping, fdinfo map-info parsing, reused-map compatibility planning, and deferred bridge-boundary truthfulness only

## Current helper packet
Current `master` keeps the dedicated helper packet reviewable through `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, `make -C zigux phase8-file-path-handle-bridge-test`, and `make -C zigux phase8`.

That landed helper packet keeps bounded `"/proc/%d/fdinfo/%d"` pathname shaping through `validateProcFdinfoRoot()`, `buildProcFdinfoPath()`, and `buildCurrentProcessFdinfoPath()`, `parseFdinfoLine()` field splitting, `applyFdinfoMapInfoLine()` numeric field decoding, `parseFdinfoMapInfo()` compact fdinfo summary parsing, `summarizeFdinfoMapInfo()` completion reporting, `summarizeReusedMapName()` retained-name summaries, and `resolveReusedMapName()` plus errno-shaped wrappers explicit without claiming no direct procfs reads, no live bpffs opens, and no `bpf_obj_get()` reopen flow.

The helper packet also now keeps helper-only `mapReuseObservationFromFdinfo()` handoff, `summarizeMapReuseCompatibility()` and `isMapReuseCompatible()` reviewable, while `resolveReusePinnedMapAttempt()` stays explicit as planning-only `resolveReusePinnedMapAttempt()` gating and `planTokenPreparation()` stays explicit as planning-only `planTokenPreparation()` gating.

The focused helper proof now also keeps terminated-prefix and truncated-fixed-width retained-name dispositions explicit, along with incomplete-fdinfo reuse planning that must fail closed before any reopen or token step.

Those planning-only helpers remain bounded: no live bpffs opens, no descriptor replacement, transfer, or close ownership semantics, no token materialization, and no direct file-open bridge-heavy behavior.

## Deferred bridge boundary
This helper packet is intentionally smaller than the remaining file-path and handle bridge.

The deferred boundary still covers direct procfs reads, live bpffs opens, `bpf_obj_get()` reopen flow, token materialization, and descriptor replacement, transfer, or close ownership semantics.

That means the helper-first packet stays bounded to pathname shaping, line splitting, map_type/key_size/value_size/max_entries/map_flags/map_extra parsing, helper-only reuse planning, and deferred-boundary truthfulness while live reopen, token, and ownership behavior remain deferred.

## Non-goals
This slice does not yet claim:
- direct procfs reads or descriptor ownership flow
- live bpffs opens
- `bpf_obj_get()` reopen flow
- token materialization
- descriptor replacement, transfer, or close ownership semantics
- direct file-open bridge-heavy behavior
- any direct Zig port of the full `tools/lib/bpf/libbpf.c` bridge-heavy setup path

## Next bounded step
Keep this helper slice parked unless the focused helper, its manifest-backed boundary guard, or the shared bridge-boundary survey drifts again around the landed fdinfo parser and planning helpers versus the still-deferred file-path bridge boundary.
