# Phase 8 File-Path Handle Bridge Slice

This note records the current bounded Phase 8 file-path and handle bridge helper packet against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked_helper_slice`
- `PHASE8_SLICE=file-path-handle-bridge`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-23
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: helper-local fdinfo parsing, reuse-planning, and deferred bridge-boundary truthfulness only

## Current helper packet
Current `master` keeps the dedicated helper packet reviewable through `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, `make -C zigux phase8-file-path-handle-bridge-test`, and `make -C zigux phase8`.

That landed helper packet keeps bounded `"/proc/%d/fdinfo/%d"` pathname shaping, `parseFdinfoLine()` field splitting, `applyFdinfoMapInfoLine()` decoding, `parseFdinfoMapInfo()` line-by-line parsing, and `summarizeFdinfoMapInfo()` completion reporting explicit for `map_type`, `key_size`, `value_size`, `max_entries`, `map_flags`, and `map_extra`.

It also keeps the reused-map-name chooser, helper-only `mapReuseObservationFromFdinfo()` handoff, `summarizeMapReuseCompatibility()`, and `isMapReuseCompatible()` explicit as helper-only comparison surfaces below the broader bridge.

The same packet keeps planning-only `resolveReusePinnedMapAttempt()` gating and planning-only `planTokenPreparation()` gating explicit without promoting direct file or descriptor side effects into landed proof.

## Deferred bridge boundary
This helper packet is intentionally smaller than the remaining file-path and handle bridge.

The deferred boundary still includes no direct procfs reads, no live bpffs opens, no `bpf_obj_get()` reopen flow, no token materialization, and no descriptor replacement, transfer, or close ownership semantics.

That means the helper-first packet stays bounded to pathname shaping, fdinfo text parsing, compatibility observation, and reuse planning while live reopen, token, and ownership behavior remain deferred.

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
Keep this helper slice parked unless the focused helper, its manifest-backed boundary guard, or the shared bridge-boundary survey drifts again around the landed helper-only packet versus the deferred file-path and handle bridge.
