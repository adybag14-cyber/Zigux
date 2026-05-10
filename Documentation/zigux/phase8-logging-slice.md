# Phase 8 Libbpf Logging Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the print-level, version, and custom libbpf errno helpers in `tools/lib/bpf/libbpf.c`.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-logging-segment`
- scope: bounded print-level parsing, verbosity gating, version reporting, custom libbpf error text, and stable unknown-error formatting only
- product boundary:
  - `tools/lib/bpf/zigux_segments/logging.zig`
  - `zigux/tests/phase8_logging.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap still calls for a segmented libbpf rollout under `tools/lib/bpf/zigux_segments/` because `tools/lib/bpf/libbpf.c` is too large to port honestly as one helper packet.

The logging starter stays small and reviewable because it focuses on stable text and enum behavior around libbpf's print-level, version, and custom errno helpers without widening into environment reads, stderr output, or broader object-loading flow.

## Gates
1. run the shared Phase 8 validator route first
   - `make -C zigux phase8-validate`
2. run the shared Phase 8 validator self-test
   - `python3 scripts/zigux/validate-phase8.py --self-test`
3. run the shared Phase 8 validator
   - `python3 scripts/zigux/validate-phase8.py`
4. run the shared Phase 8 tooling replay
   - `make -C zigux phase8-test`
   - `zig build test --build-file zigux/tests/phase8_build.zig --summary all`
5. run the convenience target
   - `make -C zigux phase8`

## Current parity surface

The current bounded helper covers:
- case-insensitive `warn`, `info`, and `debug` print-level parsing
- default `info` minimum-level resolution when the caller leaves the environment value unset
- explicit invalid-value preservation when the caller provides unknown print-level text
- `shouldPrint()` ordering that keeps `warn <= info <= debug` reviewable without direct printing side effects
- bounded `libbpfMajorVersion()`, `libbpfMinorVersion()`, and `libbpfVersionString()` helpers
- compact custom libbpf errno-to-message coverage for the current landed helper table
- stable `"Unknown libbpf error N"` fallback formatting for unmapped custom codes

The current tests check:
- warn, info, and debug parsing stays case-insensitive
- invalid print-level text stays explicit while callers still fall back to the default `info` minimum
- print gating preserves the current libbpf verbosity ordering
- the version tuple still reports the landed `1.8` major, minor, and string helpers
- representative custom libbpf error messages stay stable across positive and negative errno-shaped inputs
- unmapped custom codes still fall back to the compact unknown-error formatter instead of inventing broader strerror coverage

## Non-goals

This slice does not yet claim:
- direct environment reads such as `getenv("LIBBPF_LOG_LEVEL")`
- stderr output, callback wiring, or any live print side effects
- full `strerror_r()` parity for non-libbpf errno values
- object loading, verifier logs, ELF relocation, or feature probing
- broader error catalog ownership outside the current landed custom libbpf table

## Next bounded step

Park `tools/lib/bpf/zigux_segments/logging.zig` unless fresh repo review finds another tiny same-surface truthfulness or helper-table drift. If this lane reopens, keep the next step smaller than direct environment reads, print callbacks, broader errno catalogs, or object-loading behavior.
