# Phase 8 Libbpf CPU Mask Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the CPU mask helpers in `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-cpu-mask-starter`
- scope: injected CPU-mask string parsing, chunk-reader ingestion, and set-bit counting only
- product boundary:
  - `tools/lib/bpf/zigux_segments/cpu_mask.zig`
  - `zigux/tests/phase8_cpu_mask.zig`
  - `zigux/tests/phase8_build.zig`
  - `tools/lib/bpf/zigux_segments/manifest.json`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/bpf/libbpf.c` as a tooling anchor, and the existing segment survey already marked CPU mask parsing as one of the first safe libbpf entry points.

`parse_cpu_mask_str()` is a small, self-contained helper with stable text semantics, no ELF coupling, and no verifier-facing behavior. That makes it the right first real segment to land after the survey scaffold.

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/bpf/zigux_segments/cpu_mask.zig`

2. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig`

3. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current starter slice covers:

- `parse_cpu_mask_str()`-adjacent parsing for `N` and `N-M` fragments
- repeated comma and newline delimiter skipping for sysfs-style CPU mask strings
- explicit rejection of carriage-return-delimited fragments that the live helper does not skip
- an injected chunk-reader interface that can assemble buffered sysfs-style input without touching real file descriptors
- dense `[]bool` mask materialization for future tooling callers
- counted possible-CPU reporting over the parsed mask

The current tests check:

- mixed single-value and ranged fragments
- newline-terminated and repeated-delimiter inputs
- chunked reader input that splits ranges and delimiters across buffer boundaries
- sparse masks with unset gaps preserved
- explicit error handling for empty and malformed ranges
- direct and chunked carriage-return regression cases that must stay rejected
- reader contract failures such as zero-length chunks, oversized counts, injected read errors, and empty scratch buffers

## Non-goals

This slice does not yet claim:

- direct `parse_cpu_mask_file()` parity
- real file-descriptor I/O
- `libbpf_num_possible_cpus()` caching or `READ_ONCE`/`WRITE_ONCE` behavior
- perf-buffer or feature-probe integration

## Next bounded step

Park `tools/lib/bpf/zigux_segments/cpu_mask.zig` unless fresh repo review finds another tiny same-surface truthfulness or parity gap; otherwise keep later libbpf follow-up in sibling helper-only segments and do not reopen file I/O, caching, perf-buffer, or feature-probe behavior from this note.
