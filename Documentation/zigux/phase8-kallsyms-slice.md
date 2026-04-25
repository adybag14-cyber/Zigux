# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=kallsyms-parse-starter`
- scope: symbol-type helpers and injected line parsing only
- product boundary:
  - `tools/lib/symbol/kallsyms.zig`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

The live repo still lacked any sibling Zig slice under `tools/lib/symbol/`, so the highest-value lane-local step was to start with the low-risk parsing surface that can be validated without widening into file descriptors, ELF emission, or the larger symbol toolchain.

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/symbol/kallsyms.zig`

2. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig`

3. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current starter slice covers:

- `kallsyms2elf_binding()`-adjacent binding classification
- `kallsyms2elf_type()`-adjacent symbol-type classification
- `kallsyms__is_function()`-adjacent function detection
- injected per-line parsing for `"<hex> <type> <name>"` records with malformed-line skipping
- a bounded symbol-name length guard that keeps the starter parser honest

The current tests check:

- uppercase and lowercase symbol types map to the same binding and function classifications as the C helper
- valid symbol lines expose the expected address, type, and name slices
- malformed lines are skipped without stopping iteration
- oversized symbol names raise an explicit bounded error instead of silently widening the lane
- injected callback failures bubble out unchanged so the starter parser does not hide downstream review or tooling errors

## Non-goals

This slice does not yet claim:

- direct file-descriptor or `api/io.h` parity for `kallsyms__parse()`
- callback-driven file parsing from a real `kallsyms` file
- ELF symbol emission or downstream integration with larger symbol tooling

## Next bounded step

Stay in `tools/lib/symbol/kallsyms.zig` and add an injected reader surface that can iterate file-like chunks with the same malformed-line skipping semantics before attempting real file I/O parity.
