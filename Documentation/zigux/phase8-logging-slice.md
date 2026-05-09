# Phase 8 Logging Segment

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the logging, version, and libbpf-specific errno helpers in `tools/lib/bpf/libbpf.c` and `tools/lib/bpf/libbpf_utils.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-logging-segment`
- scope: print-level parsing, verbosity gating, version reporting, and libbpf-specific custom error text only
- product boundary:
  - `tools/lib/bpf/zigux_segments/logging.zig`
  - `zigux/tests/phase8_logging.zig`
  - `zigux/tests/phase8_build.zig`
  - `tools/lib/bpf/zigux_segments/manifest.json`

## Why this slice exists

The Phase 8 roadmap explicitly calls for a segmented rollout under `tools/lib/bpf/zigux_segments/` because `tools/lib/bpf/libbpf.c` is too large to treat as one honest starter port.

The bounded logging helpers are a good parked helper-first segment because they stay inside stable text and severity behavior:

- `parsePrintLevel()` and `resolveMinPrintLevel()` keep the `LIBBPF_LOG_LEVEL`-style parsing surface explicit without touching real environment reads
- `shouldPrint()` makes the warn-info-debug gating order reviewable without printing directly to stderr
- `libbpfMajorVersion()`, `libbpfMinorVersion()`, and `libbpfVersionString()` expose the current version tuple without widening into loader or feature-probe work
- `libbpfCustomErrorMessage()` and `formatErrorString()` keep the libbpf-specific error table and unknown-code fallback explicit without claiming full libc strerror parity

## Gates

1. run the shared Phase 8 validator route first
- `make -C zigux phase8-validate`

2. run the shared Phase 8 validator self-test
- `python3 scripts/zigux/validate-phase8.py --self-test`

3. run the shared Phase 8 validator
- `python3 scripts/zigux/validate-phase8.py`

4. run the focused Zig module tests
- `zig test tools/lib/bpf/zigux_segments/logging.zig`

5. run the dedicated Phase 8 tooling gate
- `make -C zigux phase8-test`
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

6. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current parked helper covers:

- case-insensitive `warn`, `info`, and `debug` print-level parsing
- explicit invalid-value reporting while defaulting unresolved log levels back to `info`
- bounded warn-info-debug gating through `shouldPrint()`
- the current libbpf major, minor, and compact version-string tuple
- the libbpf-specific custom errno table for bounded helper-owned messages
- stable `Unknown libbpf error N` fallback formatting for unmapped custom codes

The current tests check:

- the helper imports cleanly into the dedicated Phase 8 logging packet
- warn, info, and debug resolution stays case-insensitive
- invalid log-level text stays explicit while callers still receive the default `info` minimum level
- the bounded version helpers still report the current `v1.8` tuple
- representative libbpf-specific custom errors such as the verifier failure text stay stable
- unknown or unmapped custom codes still fall back to the stable `Unknown libbpf error N` formatter

## Non-goals

This segment does not yet claim:

- direct environment reads, stderr output, or print callbacks
- full errno-name coverage or libc `strerror()` parity
- object loading, ELF relocation, token handling, or verifier-facing behavior
- perf-buffer, file-path bridge, or syscall-backed runtime behavior

## Next bounded step

Park `tools/lib/bpf/zigux_segments/logging.zig` unless fresh repo review finds another tiny same-surface truthfulness or helper-local text-parity gap; if this segment reopens, keep it bounded to logging-level, version-tuple, or libbpf-specific error-text behavior and do not widen into environment reads, stderr output, loader state, or the heavier file-path and perf-buffer packets.
