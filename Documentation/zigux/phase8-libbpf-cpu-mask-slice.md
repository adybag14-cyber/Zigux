# Phase 8 Libbpf CPU Mask Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the CPU mask helpers in `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=libbpf-cpu-mask-starter`
- scope: injected CPU-mask string parsing, chunk-reader ingestion, set-bit counting, and bounded perf-buffer auto-CPU sizing only
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
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

3. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current starter slice covers:

- `parse_cpu_mask_str()`-adjacent parsing for `N` and `N-M` fragments
- `+N` and `+N-+M` signed-decimal token forms that libbpf's `%d` parsing already accepts, while still rejecting negative CPU indices
- repeated comma and newline delimiter skipping for sysfs-style CPU mask strings
- leading horizontal whitespace and carriage-return acceptance only where the C helper's `sscanf()` token parsing already consumes them, without widening into standalone whitespace-delimiter behavior
- an injected chunk-reader interface that can assemble buffered sysfs-style input without touching real file descriptors
- dense `[]bool` mask materialization for future tooling callers
- counted possible-CPU reporting over the parsed mask
- a bounded auto-CPU count clamp that mirrors libbpf's perf-buffer map-budget sizing without widening into `/sys` reads, online CPU filtering, perf-event-array updates, epoll-backed perf FD registration, or timeout-driven `perf_buffer__poll(timeout_ms)` waits that return ready-buffer counts

The current tests check:

- mixed single-value and ranged fragments
- `+`-prefixed single-value and ranged fragments that stay non-negative
- newline-terminated, repeated-delimiter, and leading-whitespace-at-token-start inputs
- chunked reader input that splits `+`-prefixed ranges, delimiters, and leading `sscanf()`-style whitespace across buffer boundaries
- sparse masks with unset gaps preserved
- explicit error handling for empty, malformed, and trailing-whitespace-only ranges
- reader contract failures such as zero-length chunks, oversized counts, and injected read errors
- the bounded auto-CPU count clamp keeps possible-CPU sizing inside the map entry budget while still treating zero as the uncapped case

## Non-goals

This slice does not yet claim:

- direct `parse_cpu_mask_file()` parity
- real file-descriptor I/O
- `libbpf_num_possible_cpus()` caching or `READ_ONCE`/`WRITE_ONCE` behavior
- `perf_buffer__new()` online CPU selection, perf-event-array population, or interrupt-routing-sensitive timing boundary behavior
- direct `perf_buffer__poll(timeout_ms)` timeout handling or ready-buffer count parity
- any standalone timer helper or standalone clockevent helper for perf-buffer polling
- perf-buffer or feature-probe integration

## Next bounded step

Keep the landed parser helper bounded, and leave the neighboring `perf-buffer-online-cpu-routing` survey segment deferred until Zigux has a smaller reviewed substrate for `/sys` cpu-mask reads, online CPU filtering, per-CPU perf-buffer routing, and the interrupt-routing-sensitive timing boundary around `perf_buffer__poll(timeout_ms)` than the current libbpf boundary.
