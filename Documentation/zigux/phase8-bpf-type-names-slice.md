# Phase 8 BPF Type-Name Segment

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the exported enum-to-name helpers in `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-type-name-segment`
- scope: dense attach, link, map, and program type string helpers only
- product boundary:
  - `tools/lib/bpf/zigux_segments/type_names.zig`
  - `zigux/tests/phase8_bpf_type_names.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly calls for a segmented rollout under `tools/lib/bpf/zigux_segments/` because `libbpf.c` is too large to treat as one honest starter port.

The exported `libbpf_bpf_{attach,link,map,prog}_type_str()` helpers are a good first segment because they are:

- already part of the libbpf public helper surface
- dense table lookups with stable output behavior
- isolated from ELF parsing, syscalls, perf buffers, and object lifecycle state

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/bpf/zigux_segments/type_names.zig`

2. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig`

3. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current segment covers:

- `libbpf_bpf_attach_type_str()`-adjacent dense name lookup
- `libbpf_bpf_link_type_str()`-adjacent dense name lookup
- `libbpf_bpf_map_type_str()`-adjacent dense name lookup
- `libbpf_bpf_prog_type_str()`-adjacent dense name lookup
- out-of-range rejection that returns `null` for unknown enum values

The current tests check:

- every table entry is reachable through the corresponding helper
- representative late enum ordinals from `tools/include/uapi/linux/bpf.h` still resolve to the expected names
- deprecated-but-still-addressable map ordinals preserve the shipped libbpf names
- out-of-range negative and oversized values are rejected cleanly

## Non-goals

This segment does not yet claim:

- `libbpf_prog_type_by_name()` or section-definition parsing
- BPF object loading, ELF relocation, or feature probing
- perf buffer, ring buffer, link creation, or syscall-backed behavior

## Next bounded step

Park the `type_names` segment unless fresh repo review finds another tiny table-alignment or docs-truthfulness gap; otherwise keep later libbpf follow-up in a different bounded helper-only segment and do not reopen object-loading, syscall-backed, or parser-driven surfaces from this note.
