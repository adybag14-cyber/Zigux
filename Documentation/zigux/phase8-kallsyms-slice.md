# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- legacy validator alias: `PHASE8_SLICE=kallsyms-parse-wrapper-starter`
- scope: symbol-type helpers, injected line parsing, chunked reader iteration, thin reader, file, or path adapters, and direct callback wrappers over contents, reader-backed parsing, file-backed parsing, and plain filename parsing only
- product boundary:
  - `tools/lib/symbol/kallsyms.zig`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_kallsyms_only_build.zig`
  - `zigux/tests/phase8_help_kallsyms_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche. That same roadmap says Phase 8 should prove Zigux inside serious repo-hosted tooling, not just tiny helpers, so the phase-level packet should stay focused on the integrated parser-and-wrapper surface that reviewers actually need to inspect.

This parked packet therefore keeps `tools/lib/symbol/kallsyms.zig` framed as helper-first expansion inside the recommended `tools/lib/symbol/*.zig` family and keeps its review surface centered on output-stable tooling behavior rather than downstream symbol plumbing.

The live repo already has the parse-first `kallsyms.zig` parked slice, the injected chunked reader surface, thin reader-backed, file-backed, and path-backed adapters, the bounded discard-after-boundary behavior for oversized symbol names, and direct callback wrappers across caller-provided contents, injected readers, open files, and plain filename parsing. The lane-local drift is no longer about broad symbol-tooling expansion; it is about keeping that bounded callback-wrapper surface explicit and machine-checked while still framing the tranche as a parser-and-wrapper packet rather than a broader symbol-tooling port.

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/symbol/kallsyms.zig`

2. run the focused shared kallsyms gate
- `zig build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all`

3. run the focused shared help and symbol gate
- `zig build test --build-file zigux/tests/phase8_help_kallsyms_only_build.zig --summary all`

4. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

5. run the convenience targets
- `make -C zigux phase8-kallsyms-test`
- `zig build test --build-file zigux/tests/phase8_help_kallsyms_only_build.zig --summary all`
- `make -C zigux phase8`

## Current parity surface

The current parked slice covers:

- `kallsyms2elf_binding()`-adjacent binding classification
- `kallsyms2elf_type()`-adjacent symbol-type classification
- `kallsyms__is_function()`-adjacent function detection
- injected per-line parsing for `"<hex> <type> <name>"` records with malformed-line skipping
- injected chunked reader iteration that reconstructs split lines before reusing the same parser
- thin reader-backed parsing that reuses the same malformed-line and callback semantics
- thin file-backed parsing that reuses the same malformed-line and callback semantics over an already open file plus caller-owned scratch storage
- thin path-backed parsing that opens a file and feeds the same reader-backed path
- one direct `kallsymsParseContents()` wrapper that replays the same C-shaped callback contract over caller-provided contents
- one direct `kallsymsParseReader()` wrapper that replays the same C-shaped callback contract over an injected reader plus caller-owned scratch storage
- one direct `kallsymsParseFile()` wrapper that replays the same C-shaped callback contract over an already open file plus caller-owned scratch storage
- one direct `kallsymsParse()` wrapper that accepts a plain filename plus the same callback contract while `kallsymsParseInDir()` keeps the narrower injected-dir variant available for tests and callers that need it
- bounded symbol-name truncation that keeps the parked parser inside `KSYM_NAME_LEN` while preserving the same continue-parsing shape as the C helper
- chunked overlong-line handling that now stops buffering after the bounded callback surface is full, discards the remainder of that one line until newline, and still reaches the next symbol record the same way the fixed-size C buffer does

The current tests check:

- helper-local `tools/lib/symbol/kallsyms.zig` tests own the direct binding, type, `parseLine()`, per-line malformed-record skipping, EOF-finish, and callback-stop matrix
- the focused `zigux/tests/phase8_kallsyms.zig` replay stays on the integrated review packet: chunked reconstruction, chunked callback-stop behavior, thin reader, file, and path adapters, direct callback wrappers, the parked note itself, and the live C helper anchors
- split records still parse correctly when a file-like reader delivers partial lines and CRLF endings across chunk boundaries
- split records also preserve callback-stop behavior unchanged when a failing symbol spans buffered chunk boundaries in the dedicated Phase 8 gate
- the new reader, file, and path adapters preserve the same callback and malformed-line behavior as the lower-level parser
- the direct wrappers preserve the same callback-stop contract across caller-provided contents, injected readers, already open files, the cwd-based filename entrypoint, and the injected-dir contract while presenting a `void *arg` plus null-terminated symbol-name callback shape
- oversized symbol names are truncated to `KSYM_NAME_LEN` in chunk-reconstructed parsing, with explicit helper and dedicated Phase 8 test coverage for the chunked discard path, so the parked slice now matches the C helper's bounded callback contract without buffering the whole overlong line first

## Non-goals

This slice does not yet claim:

- direct `api/io.h` parity for `kallsyms__parse()`
- the exact Linux `open()` or `close()` path instead of Zig std I/O wrappers
- ELF symbol emission or downstream integration with larger symbol tooling

## Next bounded step

Park the `kallsyms` lane unless a fresh parity gap appears; the parked slice now covers the integrated parser-and-wrapper packet while the helper-local matrix stays owned by `tools/lib/symbol/kallsyms.zig`, and the new shared `phase8_help_kallsyms_only_build.zig` shard keeps the parked help-plus-symbol packet reviewable without rerunning the full Phase 8 bundle. The next honest follow-up should only reopen this lane for another exact parser or callback-contract edge rather than widening into ELF emission or downstream symbol plumbing.
