# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-starter`
- scope: symbol-type helpers, injected line parsing, chunked reader iteration, thin reader or path adapters, and one direct parse wrapper only
- product boundary:
  - `tools/lib/symbol/kallsyms.zig`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

The live repo already had the parse-first `kallsyms.zig` starter plus the injected chunked reader surface, and the previous bounded follow-up added thin reader-backed and path-backed adapters. The remaining lane-local gap was overlong symbol handling: `kallsyms.c` keeps parsing and passes a bounded name buffer onward, while the Zig starter still raised an explicit length error instead of preserving that output-stable parser flow.

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
- one direct `kallsymsParse()` wrapper that accepts a plain filename plus a C-shaped callback contract while `kallsymsParseInDir()` keeps the narrower injected-dir variant available for tests and callers that need it
- bounded symbol-name truncation that keeps the starter parser inside `KSYM_NAME_LEN` while preserving the same continue-parsing shape as the C helper

The current tests check:

- uppercase and lowercase symbol types map to the same binding and function classifications as the C helper
- valid symbol lines expose the expected address, type, and name slices
- malformed lines are skipped without stopping iteration
- split records still parse correctly when a file-like reader delivers partial lines and CRLF endings across chunk boundaries
- split records also preserve callback-stop behavior unchanged when a failing symbol spans buffered chunk boundaries in the dedicated Phase 8 gate
- the new reader and path adapters preserve the same callback and malformed-line behavior as the lower-level parser
- the direct wrappers preserve both the cwd-based filename contract and the injected-dir contract while presenting a `void *arg` plus null-terminated symbol-name callback shape and preserving non-zero stop codes
- oversized symbol names are truncated to `KSYM_NAME_LEN` in direct, line-by-line, and chunk-reconstructed parsing so the starter slice now matches the C helper's bounded callback contract instead of failing early
- injected callback failures bubble out unchanged so the starter parser does not hide downstream review or tooling errors

## Non-goals

This slice does not yet claim:

- direct `api/io.h` parity for `kallsyms__parse()`
- the exact Linux `open()` or `close()` path instead of Zig std I/O wrappers
- ELF symbol emission or downstream integration with larger symbol tooling

## Next bounded step

Park the `kallsyms` lane unless a fresh parity gap appears; the starter slice now covers bounded overlong-name handling as well as the direct wrappers, so the next honest follow-up should only reopen this lane for another exact parser or callback-contract edge rather than widening into ELF emission or downstream symbol plumbing.
