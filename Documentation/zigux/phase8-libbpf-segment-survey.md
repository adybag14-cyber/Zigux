# Phase 8 Libbpf Segment Survey

This document tracks the bounded Phase 8 userspace-adjacent tooling survey for Zigux around `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=libbpf-segment-survey`
- scope: segment manifest and validation scaffold only
- product boundary:
  - `tools/lib/bpf/zigux_segments/manifest.json`
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

The first three are marked `ready_next`, while the last two stay explicitly deferred as high-risk surfaces until helper-first segments have landed and been validated.

## Gates

1. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig`

2. run the convenience target
- `make -C zigux phase8`

## Non-goals

This survey slice does not yet claim:

- any direct Zig port of `tools/lib/bpf/libbpf.c`
- BTF relocation parity
- ELF loader parity
- perf-buffer runtime behavior
- object-model parity for `bpf_object`, `bpf_map`, or `bpf_program`

## Next bounded step

Stay in `tools/lib/bpf/zigux_segments/` and start one of the `ready_next` helper-first segments, with `logging.zig`, `pin_path.zig`, or `cpu_mask.zig` as the best low-risk entry candidates.
