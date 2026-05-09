# Phase 8 Libbpf Logging Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around the logging, version, and libbpf-specific errno helpers in `tools/lib/bpf/libbpf.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=libbpf-logging-starter`
- scope: print-level parsing, minimum-level resolution, verbosity gating, version reporting, libbpf-specific error-table lookup, and bounded fallback formatting only
- product boundary:
  - `tools/lib/bpf/zigux_segments/logging.zig`
  - `zigux/tests/phase8_logging.zig`
  - `zigux/tests/phase8_libbpf_segments.zig`
  - `zigux/tests/phase8_libbpf_segments_only_build.zig`
  - `zigux/tests/phase8_build.zig`
  - `tools/lib/bpf/zigux_segments/manifest.json`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/bpf/libbpf.c` as a tooling anchor, and the existing segment survey already marks logging, version reporting, and errno shaping as one of the first safe libbpf entry points.

These helpers are a good early packet because they keep output-stable text behavior reviewable without widening into stderr writes, environment mutation, ELF loading, verifier-facing work, or runtime object ownership.

## Gates

1. run the shared Phase 8 validator route first
- `make -C zigux phase8-validate`

2. run the shared Phase 8 validator self-test
- `python3 scripts/zigux/validate-phase8.py --self-test`

3. run the shared Phase 8 validator
- `python3 scripts/zigux/validate-phase8.py`

4. run the focused Zig module tests
- `zig test tools/lib/bpf/zigux_segments/logging.zig`

5. run the focused libbpf survey wrapper
- `make -C zigux phase8-libbpf-segments-test`
- `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`

6. run the shared Phase 8 tooling replay
- `make -C zigux phase8-test`
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

7. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current starter slice covers:

- case-insensitive `warn`, `info`, and `debug` print-level parsing
- bounded minimum-level resolution that keeps invalid `LIBBPF_LOG_LEVEL`-style text explicit for callers instead of printing directly
- verbosity gating through the same warn-before-info-before-debug ordering the current libbpf packet uses
- compact major, minor, and full version-string helpers for the current `tools/lib/bpf/libbpf_version.h` tuple
- libbpf-specific custom errno text for the bounded helper table in `logging.zig`
- stable fallback formatting for unknown custom codes through `Unknown libbpf error N`

The current tests check:

- warn, info, and debug parsing stays case-insensitive
- invalid print-level text stays explicit while the helper falls back to the default `info` minimum level
- verbosity gating preserves the same ordering as the current libbpf packet
- major, minor, and version-string helpers match the current bounded libbpf tuple
- representative libbpf-specific custom error text stays stable
- unmapped custom error codes fall back cleanly through the bounded formatter

## Non-goals

This slice does not yet claim:

- direct stderr output or print-callback registration
- environment reads or mutation beyond caller-provided level text
- full errno-name coverage outside the bounded libbpf-specific helper table
- loader, relocation, perf-buffer routing, or object-model behavior
- strict-mode policy handling or callback ownership semantics

## Next bounded step

Park `tools/lib/bpf/zigux_segments/logging.zig` unless fresh repo review finds another tiny same-surface wording, gate, or output-shaping gap; keep future libbpf follow-up smaller than direct stderr writes, environment plumbing, loader-facing work, or broader object-model behavior.
