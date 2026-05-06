# Phase 8 File-Path Handle Bridge Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the procfs fdinfo pathname and text-parsing helpers adjacent to `bpf_get_map_info_from_fdinfo()` in `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-file-path-handle-bridge`
- scope: `"/proc/%d/fdinfo/%d"` assembly plus bounded fdinfo text parsing for `map_type`, `key_size`, `value_size`, `max_entries`, `map_flags`, and `map_extra`, with bounded reuse-pinned-map attempt planning kept reviewable without performing direct bpffs reopen work
- product boundary:
  - `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
  - `zigux/tests/phase8_file_path_handle_bridge.zig`
  - `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap still calls for a segmented libbpf rollout under `tools/lib/bpf/zigux_segments/`, and the current survey packet now treats the bounded fdinfo bridge helper plus the helper-only reused-map compatibility packet as landed adjacent review surface while keeping the broader bridge follow-through queued.

`bpf_get_map_info_from_fdinfo()` stayed the right starter because it keeps the landed work inside reviewable path formatting, fdinfo text parsing, helper-only reused-map compatibility checks, and planning-only reuse gating without widening into direct procfs reads, pinned-map reopen flow, or object-loader state.

## Gates

1. run the shared Phase 8 validator route first
- `make -C zigux phase8-validate`

2. run the shared Phase 8 validator self-test
- `python3 scripts/zigux/validate-phase8.py --self-test`

3. run the shared Phase 8 validator
- `python3 scripts/zigux/validate-phase8.py`

4. run the focused Phase 8 file-path handle bridge shard
- `make -C zigux phase8-file-path-handle-bridge-test`
- `zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all`

5. run the shared Phase 8 replay
- `make -C zigux phase8-test`
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

6. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current bounded helper covers:

- exact `"/proc/%d/fdinfo/%d"` pathname assembly for a caller-provided pid and fd
- bounded line splitting for libbpf-style `field:\tvalue` fdinfo text
- numeric parsing for `map_type`, `key_size`, `value_size`, `max_entries`, `map_flags`, and `map_extra`
- `map_flags` parsing that keeps decimal, octal, and hex prefixes explicit
- compact summary state that tells callers whether all five legacy fdinfo fields were parsed and whether `map_extra` was present
- ignored unrelated fdinfo lines so the helper stays smaller than direct file reads
- reused-map name resolution that keeps truncated kernel names tied back to the object-side name when the libbpf-compatible `BPF_OBJ_NAME_LEN` boundary is hit
- bounded compatibility checks for map type, key size, value size, max entries, map flags, and `map_extra`, including the devmap readonly-prog exception that libbpf tolerates
- planning-only reopen-attempt disposition that requires a non-empty pinned path plus compatible fdinfo-derived map info before any real map reopen can be considered

The current tests check:

- valid procfs fdinfo path rendering
- explicit invalid pid, invalid fd, and path overflow failures
- trimmed field-name and field-value parsing
- complete five-field legacy fdinfo parsing with ignored unrelated lines
- explicit `map_extra` parsing, including uppercase hex input
- repeated field handling that keeps the latest parsed value
- explicit malformed line and malformed integer failures
- truncated-name reuse resolution and devmap readonly-prog compatibility normalization
- planning-only reopen-attempt classification for missing path, missing observation, incompatible name, incompatible map definition, and compatible ready-to-reopen outcomes
- focused build wiring for the new Phase 8 helper packet
- shared build wiring for the active stable-output Phase 8 tooling packet

## Non-goals

This slice does not yet claim:

- no direct procfs reads
- no `fopen()` or `fgets()` parity
- no `bpf_map_get_info_by_fd()` fallback control flow
- no actual bpffs opens or `bpf_obj_get()` reopen calls
- no fd duplication or `F_DUPFD_CLOEXEC` handling
- no token materialization or handle transfer

## Next bounded step

Park `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` unless fresh repo review finds another tiny reuse-planning or docs-truthfulness gap inside this same helper packet; if the lane reopens, keep the shared `make -C zigux phase8-validate` route aligned with this fdinfo-plus-planning surface and keep the next step smaller than actual procfs reads, bpffs opens, `bpf_obj_get()` reopen flow, fd duplication, or broader object-model work.
