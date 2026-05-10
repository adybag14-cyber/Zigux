# Phase 8 File-Path Handle Bridge Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the procfs fdinfo pathname, fdinfo text-parsing helpers, and planning-only reuse gates adjacent to `bpf_get_map_info_from_fdinfo()` in `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-file-path-handle-bridge`
- scope: exact `"/proc/%d/fdinfo/%d"` assembly, bounded fdinfo text parsing for `map_type`, `key_size`, `value_size`, `max_entries`, `map_flags`, and `map_extra`, helper-only fdinfo-to-reuse observation handoff, planning-only reuse-pinned-map attempt gating, and planning-only token-preparation gating only
- product boundary:
  - `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
  - `zigux/tests/phase8_file_path_handle_bridge.zig`
  - `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap still calls for a segmented libbpf rollout under `tools/lib/bpf/zigux_segments/`, and the current survey packet now treats this helper family as a landed adjacent review surface while still keeping the broader file-path-and-handle resource boundary parked.

`bpf_get_map_info_from_fdinfo()` stayed the right starter because it keeps the landed work inside reviewable path formatting, fdinfo text parsing, helper-only reuse compatibility planning, and planning-only token gating without widening into direct procfs reads, live bpffs opens, actual pinned-map reopen flow, token materialization, or object-loader state.

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
- bounded line splitting for libbpf-style `field:	value` fdinfo text
- numeric parsing for `map_type`, `key_size`, `value_size`, `max_entries`, `map_flags`, and `map_extra`
- `map_flags` parsing that keeps decimal, octal, and hex prefixes explicit
- compact summary state that tells callers whether all five legacy fdinfo fields were parsed and whether `map_extra` was present
- ignored unrelated fdinfo lines so the helper stays smaller than direct file reads
- helper-only `mapReuseObservationFromFdinfo()` handoff from parsed fdinfo fields into bounded reuse planning
- planning-only `resolveReusePinnedMapAttempt()` gating that keeps pinned path emptiness, fdinfo-derived compatibility, and truncated-name reuse checks explicit without reopening anything yet
- planning-only `planTokenPreparation()` gating that keeps token-path readiness attached to a ready reuse plan without materializing a token or opening one

The current tests check:

- valid procfs fdinfo path rendering
- explicit invalid pid, invalid fd, and path overflow failures
- trimmed field-name and field-value parsing
- complete five-field legacy fdinfo parsing with ignored unrelated lines
- explicit `map_extra` parsing, including uppercase hex input
- repeated field handling that keeps the latest parsed value
- explicit malformed line and malformed integer failures
- helper-only map reuse observation, reuse-attempt planning, and token-preparation planning outcomes
- focused build wiring for the Phase 8 helper packet
- shared build wiring for the active stable-output Phase 8 tooling packet

## Non-goals

This slice does not yet claim:

- no direct procfs reads
- no `fopen()` or `fgets()` parity
- no `bpf_map_get_info_by_fd()` fallback control flow
- no live bpffs opens
- no `bpf_obj_get()` reopen flow
- no token materialization or capability handoff
- no fd duplication or `F_DUPFD_CLOEXEC` handling
- no descriptor replacement, transfer, or close ownership semantics

## Next bounded step

Park `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` unless fresh repo review finds another tiny same-family helper or docs-truthfulness gap inside this helper packet; if the lane reopens, keep the shared `make -C zigux phase8-validate` route aligned with this landed planning surface and keep the next step smaller than direct procfs reads, live bpffs opens, actual reopen flow, token materialization, fd duplication, or broader object-model work.
