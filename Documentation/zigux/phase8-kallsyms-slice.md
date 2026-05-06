# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- scope: symbol-type helpers, injected line parsing, chunked reader iteration, thin reader or path adapters, an already-open-file adapter, and direct parse wrappers only
- product boundary:
  - `tools/lib/symbol/kallsyms.zig`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_kallsyms_only_build.zig`
  - `zigux/tests/phase8_help_kallsyms_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

This parked packet is helper-first expansion inside that `tools/lib/symbol/*.zig` family. Its review surface stays on output-stable tooling behavior rather than downstream symbol plumbing.

The live repo already had the parse-first `kallsyms.zig` surface plus the injected chunked reader path, and the previous bounded follow-ups added thin reader-backed, path-backed, and already-open-file adapters. The parked review surface now includes one direct `kallsymsParseFile()` wrapper for caller-owned open files alongside one direct `kallsymsParse()` wrapper that opens a path, without widening into ELF emission or downstream symbol plumbing.

The live C anchor for this family still concentrates review around `kallsyms2elf_type()`, `kallsyms__is_function()`, and `kallsyms__parse()` on top of `api/io.h`. This parked Zigux packet keeps those symbol-classification and parse-callback cues visible without claiming direct `api/io.h` parity or downstream symbol-emission ownership.

## Gates

1. run the shared validator-first route
- `make -C zigux phase8-validate`

2. run the focused make wrapper
- `make -C zigux phase8-kallsyms-test`

3. run the focused Zig module tests
- `zig test tools/lib/symbol/kallsyms.zig`

4. run the focused shard replay
- `zig build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all`

5. run the focused shared help and symbol gate
- `zig build test --build-file zigux/tests/phase8_help_kallsyms_only_build.zig --summary all`

6. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

7. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current parked parser-and-wrapper slice covers:

- `kallsyms2elf_binding()`-adjacent binding classification
- `kallsyms2elf_type()`-adjacent symbol-type classification
- `kallsyms__is_function()`-adjacent function detection
- injected per-line parsing for `"<hex> <type> <name>"` records with malformed-line skipping
- injected chunked reader iteration that reconstructs split lines before reusing the same parser
- thin reader-backed parsing that reuses the same malformed-line and callback semantics
- thin path-backed parsing that opens a file and feeds the same reader-backed path
- one direct `kallsymsParseFile()` wrapper that accepts an already-open file plus a C-shaped callback contract and stops on the same integer callback result the C helper returns
- one direct `kallsymsParse()` wrapper that accepts a path plus a C-shaped callback contract and stops on the same integer callback result the C helper returns
- a bounded symbol-name length guard that keeps the parked parser honest

The current tests check:

- uppercase and lowercase symbol types map to the same binding and function classifications as the C helper
- valid symbol lines expose the expected address, type, and name slices
- malformed lines are skipped without stopping iteration
- split records still parse correctly when a file-like reader delivers partial lines and CRLF endings across chunk boundaries
- the thin reader, path, and already-open-file adapters preserve the same callback and malformed-line behavior as the lower-level parser
- the direct `kallsymsParseFile()` wrapper keeps an already-open file handle on the same callback-stop contract without reopening path ownership inside the helper
- the direct `kallsymsParse()` wrapper reuses that same path surface while presenting a `void *arg` plus null-terminated symbol-name callback shape and preserving non-zero stop codes
- the focused `phase8_kallsyms_only_build.zig` shard keeps the parked parser-and-wrapper packet reviewable without rerunning the whole Phase 8 bundle
- the focused `phase8_help_kallsyms_only_build.zig` shard keeps the parked help-and-kallsyms packet reviewable without widening into unrelated Phase 8 tooling slices
- oversized symbol names raise an explicit bounded error instead of silently widening the lane
- injected callback failures bubble out unchanged so the parked parser does not hide downstream review or tooling errors

## Non-goals

This slice does not yet claim:

- direct `api/io.h` parity for `kallsyms__parse()`
- the exact Linux `open()` or `close()` path instead of Zig std I/O wrappers
- ELF symbol emission or downstream integration with larger symbol tooling

## Next bounded step

Park the `kallsyms` lane unless a fresh parity gap appears, and prefer the next Phase 8 helper-first follow-up from `tools/lib/subcmd/help.zig` or the next `tools/lib/bpf/zigux_segments/` slice.
