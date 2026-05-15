# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- scope: helper-first expansion, output-stable tooling behavior, parser-and-wrapper truthfulness, and one future helper-local reopen cue only
- product boundary:
  - `tools/lib/symbol/kallsyms.zig`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_kallsyms_only_build.zig`
  - `zigux/tests/phase8_help_kallsyms_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

This lane keeps the parked `kallsyms` starter slice aligned with the helper-first parser-and-wrapper packet that Zigux can validate honestly today: one direct `kallsymsParse()` wrapper, output-stable tooling behavior, chunked discard-after-boundary handling, and the bounded `kallsyms__parse()` callback-wrapper contract. That smaller packet is still the honest product surface here, rather than broader ELF emission, procfs, loader-facing ownership, or downstream symbol-tooling integration.

## Gates

1. run the shared validator-first route
   - `make -C zigux phase8-validate`
2. run the focused make wrappers
   - `make -C zigux phase8-help-kallsyms-test`
   - `make -C zigux phase8-kallsyms-test`
3. run the focused Zig module tests
   - `zig test tools/lib/symbol/kallsyms.zig`
4. run the focused shard replay
   - `zig build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all`
5. run the focused shared help-and-symbol replay
   - `zig build test --build-file zigux/tests/phase8_help_kallsyms_only_build.zig --summary all`
6. run the dedicated Phase 8 tooling gate
   - `zig build test --build-file zigux/tests/phase8_build.zig --summary all`
7. run the convenience target
   - `make -C zigux phase8`

## Current parity surface

The current starter slice covers:

- direct line parsing through `parseLine()` with the same address, symbol-type, and symbol-name extraction boundary as the parked helper packet
- one direct `kallsymsParse()` wrapper that preserves the current callback shape while stopping on downstream non-zero callback returns
- chunked reader handling that keeps discard-after-boundary behavior explicit when oversized lines spill across read buffers
- output-stable symbol truncation where oversized symbol names now truncate to `KSYM_NAME_LEN`
- weak-object `V` and `v` classes still follow the current C header contract instead of drifting into function classification
- callback-failure bubbling that leaves downstream parser-consumer errors unchanged

The current tests check:

- the slice note still names the parked parser contract, the helper-first expansion boundary, and the focused `make -C zigux phase8-help-kallsyms-test` route
- direct parser truncation keeps the current `KSYM_NAME_LEN` name boundary explicit
- chunked parser truncation keeps the same oversized-name boundary explicit even when the symbol name spans multiple chunks
- weak-object `V` and `v` classes still follow the current C header contract
- the segmented reader path bubbles callback failures unchanged
- the parked wrapper path preserves the current callback contract without widening into downstream symbol-tooling claims
- the focused `phase8_kallsyms_only_build.zig` shard keeps the direct parser packet reviewable without rerunning unrelated Phase 8 tooling slices
- the shared `phase8_help_kallsyms_only_build.zig` shard keeps the parked help-and-symbol packet reviewable beside the dedicated symbol shard

## Non-goals

This slice does not yet claim:

- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the parked helper-first parser-and-wrapper packet
- a wider userspace symbol pipeline beyond the bounded parser and callback-wrapper contract

## Next bounded step

Leave the `kallsyms` lane parked unless one directly coupled review, checker, or focused replay surface drifts away from this bounded parser packet again. If the lane reopens, keep it to one helper-local, checker-local, or slice-note truthfulness pass at a time and avoid widening into unrelated Phase 8 tooling work.
