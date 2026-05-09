# Phase 8 Pin-Path Segment

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the pure pathname and bpffs pin-name helpers in `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-pin-path-segment`
- scope: pathname joining, default bpffs-root selection, dot sanitization, and explicit pin-name or root-path validation only
- product boundary:
  - `tools/lib/bpf/zigux_segments/pin_path.zig`
  - `zigux/tests/phase8_pin_path.zig`
  - `zigux/tests/phase8_build.zig`
  - `tools/lib/bpf/zigux_segments/manifest.json`

## Why this slice exists

The Phase 8 roadmap explicitly calls for a segmented rollout under `tools/lib/bpf/zigux_segments/` because `tools/lib/bpf/libbpf.c` is too large to treat as one honest starter port.

The bounded pin-path helpers are a good parked helper-first segment because they keep Phase 8 inside stable pathname behavior:

- `pathname_concat()`-adjacent output shaping is pure text assembly
- `build_map_pin_path()`-adjacent default-root handling is reviewable without touching the filesystem
- `sanitize_pin_path()` keeps libbpf's dot-to-underscore bpffs naming rule explicit for callers
- the current helper can reject malformed names and roots without widening into `mkdir()`, `statfs()`, `unlink()`, or `bpf_obj_pin()` side effects

## Gates

1. run the shared Phase 8 validator route first
- `make -C zigux phase8-validate`

2. run the shared Phase 8 validator self-test
- `python3 scripts/zigux/validate-phase8.py --self-test`

3. run the shared Phase 8 validator
- `python3 scripts/zigux/validate-phase8.py`

4. run the focused Zig module tests
- `zig test tools/lib/bpf/zigux_segments/pin_path.zig`

5. run the dedicated Phase 8 tooling gate
- `make -C zigux phase8-test`
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

6. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current parked helper covers:

- `pathname_concat()`-adjacent path joining for caller-provided roots and names
- `build_map_pin_path()`-adjacent default-root selection for `/sys/fs/bpf`
- `sanitize_pin_path()` dot-to-underscore rewriting across both the root and map-name portions of the assembled path
- explicit pin-name validation for empty, slash-bearing, or NUL-bearing map names
- explicit root-path validation for relative roots and trailing-slash roots
- explicit `NameTooLong` failures when bounded output buffers cannot hold the assembled pin path

The current tests check:

- default and caller-provided pin roots join cleanly with map names
- dot sanitization keeps bpffs-style `_` rewriting explicit for both roots and map names
- validated pin-path helpers reject empty names, slash-bearing names, embedded NUL bytes, relative roots, and trailing-slash roots
- validated sanitized assembly still returns the expected bounded full path on valid input
- overflow failures stay explicit instead of silently truncating output

## Non-goals

This segment does not yet claim:

- direct `mkdir()`, `statfs()`, `unlink()`, or `bpf_obj_pin()` parity
- bpffs mount validation or filesystem probing
- pinned-object reopen flow, procfs reads, or descriptor ownership behavior
- object loading, verifier interaction, token handling, or broader file-path-and-handle bridge work

## Next bounded step

Park `tools/lib/bpf/zigux_segments/pin_path.zig` unless fresh repo review finds another tiny same-surface pathname, validation, or docs-truthfulness gap; if this helper reopens, keep it bounded to helper-local path-shape behavior and do not widen it into filesystem side effects, reopen flow, or shared Phase 8 wording work.
