# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling survey lane for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-roadmap-reminder-packet`
- scope: roadmap-backed symbol-lane reminder work, exact repo-read truthfulness, and one future helper-first reopen cue only
- roadmap anchor:
  - `tools/lib/symbol/kallsyms.c`
- current directly readable same-packet surface from this environment:
  - `Documentation/zigux/phase8-kallsyms-slice.md`
- current repo-read gaps from this environment:
  - `tools/lib/symbol/kallsyms.zig`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_kallsyms_only_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

That keeps `kallsyms` in scope as a valid helper-first tooling lane, but the current exact GitHub file reads available in this run do not expose the helper or focused test packet paths that older reminder text described as already landed. The honest Phase 8 follow-through in this lane is therefore note truthfulness first, not speculative parser claims.

## Current repo-read surface

The current lane should be treated as a roadmap-backed reminder packet rather than as direct evidence of a landed parser-and-wrapper helper family.

What this run could verify directly:

- the roadmap still keeps `tools/lib/symbol/kallsyms.c` inside Phase 8 userspace-adjacent tooling expansion
- this slice note is still present on current `master`
- exact GitHub contents reads from this environment still return `404` for `tools/lib/symbol/kallsyms.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig`

Because of that read surface, this note must not describe the following as current landed evidence:

- a live `kallsyms` Zig parser implementation
- a focused `phase8_kallsyms` replay packet
- direct CRLF behavior as a current repo-visible parser fact
- callable `make -C zigux phase8-kallsyms-test` parity evidence tied to files this run could not read

## Non-goals

This slice does not currently claim:

- direct `kallsyms__parse()` parity
- a shipped `tools/lib/symbol/kallsyms.zig` helper on current repo-read evidence
- focused `zigux/tests/phase8_kallsyms*.zig` shard coverage on current repo-read evidence
- ELF emission or downstream symbol-tooling integration

## Next bounded step

Leave the `kallsyms` lane parked unless one of the following happens:

- `tools/lib/symbol/kallsyms.zig` and its focused `zigux/tests/phase8_kallsyms*.zig` companions become directly readable again from one consistent source
- a same-packet reminder surface drifts and starts overstating current `kallsyms` helper visibility again

If the helper and focused test files become directly readable again, reopen this lane with one bounded helper-local or note-local truthfulness pass instead of widening into unrelated Phase 8 tooling work.
