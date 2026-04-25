# Phase 8 Libbpf Segment Survey

This document tracks the bounded Phase 8 userspace-adjacent tooling survey for Zigux around `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=libbpf-segment-survey`
- scope: segment manifest plus one landed helper-first starter slice
- product boundary:
  - `tools/lib/bpf/zigux_segments/manifest.json`
  - `tools/lib/bpf/zigux_segments/cpu_mask.zig`
  - `zigux/tests/phase8_cpu_mask.zig`
  - `zigux/tests/phase8_libbpf_segments.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/bpf/libbpf.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/bpf/zigux_segments/` as the bounded Zigux destination for a segmented rollout.

The live repo already carried the full C libbpf tree, but it still had no `tools/lib/bpf/zigux_segments/` scaffold and no Phase 8 libbpf note to explain how Zigux should enter this surface without exploding into mirror-tree churn. The highest-value lane-local step was to close that planning gap with a concrete, testable segment catalog before any direct libbpf port work starts.

## Survey findings

- `tools/lib/bpf/libbpf.c` is still the dominant anchor at 14771 lines.
- companion C leaves such as `btf.c`, `linker.c`, `bpf.c`, `features.c`, `ringbuf.c`, `netlink.c`, `nlattr.c`, and `libbpf_utils.c` confirm that Phase 8 needs a segmented rollout instead of a single-file port attempt.
- before this survey landed, the repo had no `tools/lib/bpf/zigux_segments/` directory and no dedicated Phase 8 libbpf review note.
- the first realistic Zigux entry points are helper-first clusters with stable text or path behavior, not the BTF relocation or program-load core.

## Segment catalog

The manifest currently records six bounded segments:

- `logging-version-and-errno`
- `pin-path-helpers`
- `cpu-mask-parsing`
- `skeleton-population`
- `object-and-elf-loader`
- `btf-relocation-and-program-load`

`cpu-mask-parsing` has now moved from `ready_next` to a landed starter slice under `tools/lib/bpf/zigux_segments/cpu_mask.zig`, while `logging-version-and-errno` and `pin-path-helpers` remain the next two low-risk `ready_next` segments. The last two stay explicitly deferred as high-risk surfaces until more helper-first segments have landed and been validated.

## Current landed segment progress

The current starter implementation stays deliberately bounded:

- `cpu_mask.zig` ports the string-parsing core of `parse_cpu_mask_str()`
- the segment now includes an injected chunk-reader interface for sysfs-style buffered input without claiming direct file-descriptor parity
- the starter exposes dense `[]bool` mask output plus set-bit counting for future perf-buffer and feature-probe callers
- delimiter skipping accepts the newline-terminated `/sys/devices/system/cpu/possible` style input without widening into real file I/O
- malformed ranges still fail fast instead of silently stretching the segment into broader object or verifier-facing work

The current tests check:

- mixed single-CPU and `start-end` ranges expand into the expected dense mask
- repeated delimiters and newline-terminated inputs still parse cleanly
- chunked reader input can split ranges and delimiters across scratch-buffer boundaries
- the bounded set-bit counter matches the parsed mask contents
- empty and malformed ranges report explicit errors
- reader contract failures stay explicit instead of silently truncating input

## Gates

1. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig`

2. run the convenience target
- `make -C zigux phase8`

## Non-goals

This survey slice does not yet claim:

- any direct Zig port of `tools/lib/bpf/libbpf.c`
- `parse_cpu_mask_file()` parity or direct file reads
- BTF relocation parity
- ELF loader parity
- perf-buffer runtime behavior
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`

## Next bounded step

Stay in `tools/lib/bpf/zigux_segments/` and start the next `ready_next` helper-first segment in `logging.zig` or `pin_path.zig` now that the cpu-mask reader interface is in place.
