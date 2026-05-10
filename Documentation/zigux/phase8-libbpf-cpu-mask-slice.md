# Phase 8 Libbpf CPU Mask Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the CPU mask helpers in `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-cpu-mask-starter`
- scope: injected CPU-mask string parsing, chunk-reader ingestion, counted possible-CPU reporting, bounded perf-buffer auto-CPU sizing, and pure online-CPU eligibility planning only
- product boundary:
  - `tools/lib/bpf/zigux_segments/cpu_mask.zig`
  - `zigux/tests/phase8_cpu_mask.zig`
  - `zigux/tests/phase8_cpu_mask_only_build.zig`
  - `zigux/tests/phase8_build.zig`
  - `tools/lib/bpf/zigux_segments/manifest.json`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/bpf/libbpf.c` as a tooling anchor, and the existing segment survey already marked CPU mask parsing as one of the first safe libbpf entry points.

`parse_cpu_mask_str()` is a small, self-contained helper with stable text semantics, no ELF coupling, and no verifier-facing behavior. That makes it the right first real segment to land after the survey scaffold while still leaving the deferred `perf-buffer-online-cpu-routing` packet parked behind an interrupt-routing-sensitive timing boundary.

## Gates

1. run the shared Phase 8 validator route first
- `make -C zigux phase8-validate`

2. run the shared Phase 8 validator self-test
- `python3 scripts/zigux/validate-phase8.py --self-test`

3. run the shared Phase 8 validator
- `python3 scripts/zigux/validate-phase8.py`

4. run the focused Zig module tests
- `zig test tools/lib/bpf/zigux_segments/cpu_mask.zig`

5. run the focused cpu-mask build shard
- `make -C zigux phase8-cpu-mask-test`
- `zig build test --build-file zigux/tests/phase8_cpu_mask_only_build.zig --summary all`

6. run the dedicated Phase 8 tooling gate
- `make -C zigux phase8-test`
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

7. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current starter slice covers:

- `parse_cpu_mask_str()`-adjacent parsing for `N` and `N-M` fragments
- `+N` and `+N-+M` signed-decimal token forms when the decoded values stay non-negative, matching the C helper's bounded signed parsing surface
- repeated comma and newline delimiter skipping for sysfs-style CPU mask strings
- anchor-faithful acceptance of carriage returns, tabs, and other ASCII whitespace that `parse_cpu_mask_str()` reaches through `sscanf()`-driven range parsing
- an injected chunk-reader interface that can assemble buffered sysfs-style input without touching real file descriptors
- dense `[]bool` mask materialization for future tooling callers
- counted possible-CPU reporting over the parsed mask
- a bounded auto-CPU count clamp that mirrors libbpf's perf-buffer map-budget sizing
- a pure online-CPU eligibility predicate that mirrors libbpf's automatic-budget offline skip rule
- bounded perf-buffer auto-CPU sizing that stays reviewable as helper-only planning instead of widening into per-CPU perf-buffer routing

The current tests check:

- mixed single-value and ranged fragments
- newline-terminated and repeated-delimiter inputs
- direct and chunked carriage-return or tab-delimited fragments that must keep matching the live libbpf helper
- chunked reader input that splits ranges and delimiters across buffer boundaries
- sparse masks with unset gaps preserved
- explicit error handling for empty and malformed ranges
- reader contract failures such as zero-length chunks, oversized counts, injected read errors, and empty scratch buffers
- helper-local bounded perf-buffer auto-CPU sizing and pure online-CPU eligibility planning without widening into `perf_buffer__new()` side effects

## Non-goals

This slice does not yet claim:

- direct `parse_cpu_mask_file()` parity
- real file-descriptor I/O
- `libbpf_num_possible_cpus()` caching or `READ_ONCE`/`WRITE_ONCE` behavior
- direct `/sys/devices/system/cpu/online` reads
- direct `/sys/devices/system/cpu/possible` caching
- `perf_buffer__new()` online CPU selection
- per-CPU perf-buffer routing
- deferred `perf-buffer-online-cpu-routing` setup or the broader interrupt-routing-sensitive timing boundary
- `perf_buffer__poll(timeout_ms)` timeout handling
- standalone timer helper behavior
- standalone clockevent helper behavior
- perf-buffer or feature-probe integration

## Next bounded step

Park `tools/lib/bpf/zigux_segments/cpu_mask.zig` unless fresh repo review finds another tiny same-surface truthfulness or parity gap; otherwise keep later libbpf follow-up in sibling helper-only segments, keep the shared `make -C zigux phase8-validate` route aligned with this parked cpu-mask packet plus the explicit deferred routing boundary, and do not reopen file I/O, caching, `perf_buffer__new()` online CPU selection, per-CPU perf-buffer routing, `perf_buffer__poll(timeout_ms)` timeout handling, timer or clockevent behavior, or feature-probe work from this note.
