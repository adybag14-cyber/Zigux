# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- scope: helper-first expansion, output-stable tooling behavior, parser-and-wrapper truthfulness, and one future helper-local reopen cue only
- roadmap anchor:
  - `tools/lib/symbol/kallsyms.c`
- current directly readable same-packet surface from this environment:
  - `Documentation/zigux/phase8-kallsyms-slice.md`
- current read-path state from this environment on 2026-05-14:
  - authenticated GitHub contents reads return `404` for `tools/lib/symbol/kallsyms.zig`
  - authenticated GitHub contents reads return `404` for `zigux/tests/phase8_kallsyms.zig`
  - authenticated GitHub contents reads return `404` for `zigux/tests/phase8_kallsyms_only_build.zig`
  - raw GitHub URL readback for `tools/lib/symbol/kallsyms.zig` also returns `404`
  - repository file search for `kallsyms` and `phase8_kallsyms` returns no current indexed file hits in `adybag14-cyber/Zigux`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

That keeps `kallsyms` in scope as a valid helper-first tooling lane, but the current repo-read truth for this run is a parked reminder packet rather than a directly readable helper-and-test packet. The honest same-lane follow-through is therefore to keep the note, validator, and directly coupled reminder surfaces aligned with the currently missing helper and focused tests instead of repeating the older public-readback recovery claim.

## Current repo-read surface

The current lane should be treated as a parked parser-and-wrapper packet whose helper-local implementation and focused replay files are not directly readable from this environment on current `master`.

What this run could verify directly:

- `Documentation/zigux/phase8-kallsyms-slice.md` still exists on current `master`
- `tools/lib/symbol/kallsyms.zig` is not directly readable through authenticated contents reads or raw GitHub URL readback in this environment
- `zigux/tests/phase8_kallsyms.zig` is not directly readable through authenticated contents reads in this environment
- `zigux/tests/phase8_kallsyms_only_build.zig` is not directly readable through authenticated contents reads in this environment
- repository file search did not surface current indexed `kallsyms` helper or focused test files in `adybag14-cyber/Zigux`
- the next truthful same-lane work therefore lives in reminder-surface, validator, or exact helper-restoration follow-through, not in claiming live parser-local truncation, weak-object classification, carriage-return preservation, or focused replay behavior without a readable current packet

Because of that read surface, this note should now describe the following as current parked evidence:

- the roadmap anchor at `tools/lib/symbol/kallsyms.c`
- this slice note as the directly readable same-lane reminder surface
- the current absence of directly readable `tools/lib/symbol/kallsyms.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig` from this environment on current `master`
- the need to keep shared Phase 8 reminder and validator wording honest until those helper-local files return or the checker packet is narrowed to the missing-file reality

## Non-goals

This slice does not currently claim:

- directly readable parser-local truncation behavior on current `master`
- directly readable weak-object `V` or `v` classification behavior on current `master`
- directly readable carriage-return preservation cues for reader, path, or callback flows on current `master`
- focused `make -C zigux phase8-help-kallsyms-test` or `make -C zigux phase8-kallsyms-test` replay evidence on current `master`
- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the parked helper-first parser-and-wrapper scope

## Next bounded step

Leave the `kallsyms` lane parked unless one of the following happens:

- the helper, focused test, or focused build route becomes directly readable again on current `master`
- one directly coupled checker, validator, or reminder surface still treats the missing helper-and-test packet as live evidence and needs one bounded truthfulness repair
- a same-lane helper restoration lands and can be verified through readable current-tree evidence

If the lane reopens, keep it to one helper-local, validator-local, or note-local truthfulness pass at a time and avoid widening into unrelated Phase 8 tooling work.