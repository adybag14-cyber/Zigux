# Phase 8 Libbpf CPU Mask Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the CPU mask helpers in `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=libbpf-cpu-mask-starter`
- scope: injected CPU-mask string parsing, chunk-reader ingestion, set-bit counting, bounded perf-buffer auto-CPU sizing, pure online-CPU eligibility checks, pure caller-supplied explicit perf-buffer target planning, bounded sequential positive-CPU fallback planning, and pure auto-selected CPU planning from already-injected masks only
- product boundary:
  - `tools/lib/bpf/zigux_segments/cpu_mask.zig`
  - `zigux/tests/phase8_cpu_mask.zig`
  - `zigux/tests/phase8_build.zig`
  - `tools/lib/bpf/zigux_segments/manifest.json`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/bpf/libbpf.c` as a tooling anchor, and the existing segment survey already marked CPU mask parsing as one of the first safe libbpf entry points.

`parse_cpu_mask_str()` is a small, self-contained helper with stable text semantics, no ELF coupling, and no verifier-facing behavior. That makes it the right first real segment to land after the survey scaffold.

## Gates

The shared review path now fail-closes through the broader Phase 8 validator and the dedicated docs-index/tests-index alignment checker before the focused helper and shared build replays run, so this cpu-mask slice stays tied to the same docs-root, tests-root, Makefile, workflow, and deferred interrupt-routing boundary packet that current `master` already ships.

1. run the shared Phase 8 validator self-test
- `python3 scripts/zigux/validate-phase8.py --self-test`

2. run the shared Phase 8 docs-index/tests-index alignment self-test
- `python3 scripts/zigux/check-phase8-tests-readme-alignment.py --self-test`

3. run the shared Phase 8 validator
- `python3 scripts/zigux/validate-phase8.py`

4. run the shared Phase 8 docs-index/tests-index alignment checker
- `python3 scripts/zigux/check-phase8-tests-readme-alignment.py`

5. run the focused Zig module tests
- `zig test tools/lib/bpf/zigux_segments/cpu_mask.zig`

6. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

7. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current starter slice covers:

- `parse_cpu_mask_str()`-adjacent parsing for `N` and `N-M` fragments
- `+N` and `+N-+M` signed-decimal token forms that libbpf's `%d` parsing already accepts, while still rejecting negative CPU indices
- C-style whitespace immediately after the range dash when the second `%d` parse consumes the trailing CPU index, without widening into standalone whitespace-delimiter behavior
- repeated comma and newline delimiter skipping for sysfs-style CPU mask strings
- leading `sscanf()`-style token whitespace, including vertical tab, form feed, and carriage return, only where the C helper's `%d` token parsing already consumes them, without widening into standalone whitespace-delimiter behavior
- an injected chunk-reader interface that can assemble buffered sysfs-style input without touching real file descriptors
- the same fixed-width CPU-mask read ceiling that libbpf enforces before widening into real file-descriptor or `/sys` reads
- dense `[]bool` mask materialization for future tooling callers
- counted possible-CPU reporting over the parsed mask
- a bounded auto-CPU count clamp that mirrors libbpf's perf-buffer map-budget sizing without widening into `/sys` reads, online CPU filtering, perf-event-array updates, epoll-backed perf FD registration, or timeout-driven `perf_buffer__poll(timeout_ms)` waits that return ready-buffer counts
- a pure online-CPU eligibility predicate that mirrors libbpf's automatic-budget offline skip rule without claiming direct `/sys/devices/system/cpu/online` reads, perf-event-array updates, or interrupt-routing ownership
- a pure caller-supplied perf-buffer target planner that keeps the explicit positive-branch `cpus[]` and `map_keys[]` pairs aligned without claiming perf-event-array updates, epoll registration, or interrupt-routing ownership
- a bounded sequential positive-CPU fallback planner for synthetic callers that only need a pure CPU index list without claiming raw perf-buffer option parity
- a pure auto-selected CPU planner that consumes already-injected possible and online masks, caps selection to the bounded auto-CPU budget, and keeps sparse or truncated mask handling explicit without claiming `/sys` reads, perf-event-array updates, or epoll-backed routing behavior

The current tests check:

- mixed single-value and ranged fragments
- `+`-prefixed single-value and ranged fragments that stay non-negative
- newline-terminated, repeated-delimiter, and `sscanf()`-style token-leading whitespace inputs, including vertical tab, form feed, and carriage return cases
- C-style whitespace immediately after range dashes for the second parsed CPU index
- chunked reader input that splits `+`-prefixed ranges, post-dash whitespace, delimiters, and leading `sscanf()`-style whitespace across buffer boundaries
- explicit rejection once chunked reader input exceeds libbpf's fixed-width CPU-mask buffer ceiling
- sparse masks with unset gaps preserved
- explicit error handling for empty, malformed, and trailing-whitespace-only ranges
- reader contract failures such as zero-length chunks, oversized counts, and injected read errors
- the bounded auto-CPU count clamp keeps possible-CPU sizing inside the map entry budget while still treating zero as the uncapped case
- explicit online-mask eligibility behavior for zero-or-negative automatic CPU budgets versus positive caller-pinned CPU budgets
- explicit caller-supplied CPU and map-key planning keeps pair ordering, count mismatches, and negative targets explicit without widening into perf-buffer routing
- the synthetic sequential positive-CPU fallback remains available for pure non-routing callers that only need a bounded CPU index list
- auto-selected CPU planning keeps only online possible CPUs, respects the bounded map-entry budget, and treats truncated injected online masks as offline instead of widening into direct sysfs reads

## Non-goals

This slice does not yet claim:

- direct `parse_cpu_mask_file()` parity
- real file-descriptor I/O
- `libbpf_num_possible_cpus()` caching or `READ_ONCE`/`WRITE_ONCE` behavior
- `perf_buffer__new()` online CPU selection, perf-event-array population, or interrupt-routing behavior across the interrupt-routing-sensitive timing boundary
- direct `perf_buffer__poll(timeout_ms)` timeout handling or ready-buffer count parity
- no standalone timer helper and no standalone clockevent helper for perf-buffer polling
- perf-buffer or feature-probe integration

## Next bounded step

Keep the landed parser helper bounded, and leave the neighboring `perf-buffer-online-cpu-routing` survey segment deferred until Zigux has a smaller reviewed substrate for `/sys` cpu-mask reads, online CPU filtering, per-CPU perf-buffer routing, and the interrupt-routing-sensitive timing boundary around `perf_buffer__poll(timeout_ms)` than the current libbpf boundary.
