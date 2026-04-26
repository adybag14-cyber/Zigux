# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=kallsyms-reader-path-adapter`
- scope: symbol-type helpers, injected line parsing, chunked reader iteration, and thin reader or path adapters only
- product boundary:
  - `tools/lib/symbol/kallsyms.zig`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

The live repo already had the parse-first `kallsyms.zig` starter plus the injected chunked reader surface, so the honest next lane-local step was not another survey pass. The real remaining gap was the thin adapter layer that turns existing parser behavior into something reader-backed and filename-backed, closer to the C helper's file-oriented shape, without widening into ELF emission or downstream symbol plumbing.

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
- injected chunked reader iteration that reconstructs split lines before reusing the same parser
- thin reader-backed parsing that reuses the same malformed-line and callback semantics
- thin path-backed parsing that opens a file and feeds the same reader-backed path
- a bounded symbol-name length guard that keeps the starter parser honest

The current tests check:

- uppercase and lowercase symbol types map to the same binding and function classifications as the C helper
- valid symbol lines expose the expected address, type, and name slices
- malformed lines are skipped without stopping iteration
- split records still parse correctly when a file-like reader delivers partial lines and CRLF endings across chunk boundaries
- the new reader and path adapters preserve the same callback and malformed-line behavior as the lower-level parser
- oversized symbol names raise an explicit bounded error instead of silently widening the lane
- injected callback failures bubble out unchanged so the starter parser does not hide downstream review or tooling errors

## Non-goals

This slice does not yet claim:

- direct `api/io.h` parity for `kallsyms__parse()`
- a C-shaped filename wrapper with the exact Linux callback signature
- ELF symbol emission or downstream integration with larger symbol tooling

## Next bounded step

Stay in `tools/lib/symbol/kallsyms.zig` and add one direct `kallsyms__parse()`-adjacent wrapper that accepts a path plus a C-shaped callback contract while continuing to reuse the existing path and reader adapters underneath.
