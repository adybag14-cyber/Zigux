# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- scope: helper-first expansion, output-stable tooling behavior, direct parser-and-wrapper truthfulness, and one future helper-local reopen cue only
- roadmap anchor:
  - `tools/lib/symbol/kallsyms.c`
- current directly readable same-packet surface from this environment:
  - `Documentation/zigux/phase8-kallsyms-slice.md`
  - `tools/lib/symbol/kallsyms.zig`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_kallsyms_only_build.zig`
- current read-path caution from this environment:
  - authenticated contents reads for the same helper-and-test packet still remain intermittent, so truthful Phase 8 wording should prefer the successful public raw readback over older contents-route `404` snapshots

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

That keeps `kallsyms` in scope as a valid helper-first tooling lane, and current public raw readback now serves the helper and focused build packet again. The honest same-lane follow-through is therefore to keep the note aligned with the visible parser-and-wrapper packet rather than to keep repeating the older unreadable-file warning.

## Current repo-read surface

The current lane should be treated as a parked parser-and-wrapper packet with directly readable helper and focused-test evidence from one consistent public source.

What this run could verify directly:

- public raw readback on 2026-05-13 serves `tools/lib/symbol/kallsyms.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig` again
- the helper-first packet keeps one direct `kallsymsParse()` wrapper alongside the bounded `parseLine()`, `forEachParsedChunked()`, `forEachParsedReader()`, `forEachParsedFile()`, and `kallsymsParseFile()` parser helpers
- oversized symbol names now truncate to `KSYM_NAME_LEN`
- weak-object `V` and `v` classes still follow the current C header contract
- `make -C zigux phase8-help-kallsyms-test` and `make -C zigux phase8-kallsyms-test` remain the focused replay routes that keep the parked symbol packet reviewable beside the shared Phase 8 validator lane

Because of that read surface, this note should now describe the following as current parked evidence:

- the directly readable `tools/lib/symbol/kallsyms.zig` helper packet
- the focused `zigux/tests/phase8_kallsyms.zig` replay packet
- the focused `zigux/tests/phase8_kallsyms_only_build.zig` build route
- the current parser-local truncation and weak-object classification contract

## Non-goals

This slice does not currently claim:

- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the current helper-first parser-and-wrapper packet
- behavior beyond the current bounded parse, truncation, callback, and focused replay surface

## Next bounded step

Leave the `kallsyms` lane parked unless one of the following happens:

- a same-packet reminder surface drifts and starts understating the currently readable helper-and-test packet again
- a consistent reread from one source shows a new helper-local parser contract drift that still fits inside the parked packet

If the lane reopens, keep it to one helper-local or note-local truthfulness pass at a time and avoid widening into unrelated Phase 8 tooling work.
