# Phase 8 File-Path Handle Bridge Slice

This note records the current bounded Phase 8 file-path and handle bridge helper packet against the roadmap's `tools/lib/bpf/libbpf.c` anchor.

## Status
- `PHASE8_STATUS=parked_helper_slice`
- `PHASE8_SLICE=file-path-handle-bridge`
- survey checkpoint: refreshed against inspected current `master` readback on 2026-05-26
- roadmap anchor: `tools/lib/bpf/libbpf.c`
- intended Zigux destination family: `tools/lib/bpf/zigux_segments/`
- scope: helper-local pathname shaping, fdinfo line splitting, reused-map-name retention, and deferred bridge-boundary truthfulness only

## Current helper packet
Current `master` keeps the dedicated helper packet reviewable through `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_file_path_handle_boundary_guard.zig`, `zigux/tests/phase8_file_path_handle_bridge_manifest_sync.zig`, `zigux/tests/phase8_build.zig`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, `make -C zigux phase8-file-path-handle-bridge-test`, and `make -C zigux phase8`.

That landed helper packet keeps bounded `"/proc/%d/fdinfo/%d"` pathname shaping through `validateProcFdinfoRoot()` and `buildProcFdinfoPath()`, `parseFdinfoLine()` field splitting, `summarizeReusedMapName()` retained-name summaries, and `resolveReusedMapName()` plus errno-shaped wrappers explicit without claiming direct file reads, numeric fdinfo map-info decoding, or reuse-comparison side effects.

The landed `fdinfo-path-and-reuse-name-footholds` slice therefore now mirrors the manifest rationale exactly: This materializes the shared bridge destination with side-effect-free pathname shaping and bounded reused-map name retention while keeping procfs reads, full fdinfo map-info parsing, and reuse comparison logic deferred.

The neighboring `fdinfo-map-info-helpers` slice now stays explicit as queued groundwork rather than landed bridge proof: the shared bridge destination is materialized for helper-only proc-fdinfo pathname shaping, but the fdinfo line parser, numeric map-info decoder, and completion summary helpers still need their own follow-through before that slice can be reported as fully landed.

The sibling `map-reuse-compatibility` slice likewise stays explicit as queued groundwork rather than landed bridge proof: current helper source retains reused-map names, but helper-only compatibility observation, flag normalization, and mismatch reporting still need follow-through before that slice can be reported as fully landed.

## Deferred bridge boundary
This helper packet is intentionally smaller than the remaining file-path and handle bridge.

The deferred boundary still covers direct procfs reads, live bpffs opens, `bpf_obj_get()` reopen flow, token materialization, and descriptor replacement, transfer, or close ownership semantics.

That means the helper-first packet stays bounded to pathname shaping, line splitting, retained-name summaries, and deferred-boundary truthfulness while live reopen, token, and ownership behavior remain deferred.

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
Keep this helper slice parked unless the focused helper, its manifest-backed boundary guard, or the shared bridge-boundary survey drifts again around the landed foothold versus the queued helper groundwork and deferred file-path bridge boundary.
