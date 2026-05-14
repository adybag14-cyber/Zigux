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
  - `zigux/tests/phase8_kallsyms.zig`
- current read-path state from this environment on 2026-05-14:
  - authenticated GitHub contents reads return `404` for `tools/lib/symbol/kallsyms.zig`
  - authenticated GitHub contents reads return `404` for `zigux/tests/phase8_kallsyms_only_build.zig`
  - raw GitHub URL readback for `tools/lib/symbol/kallsyms.zig` also returns `404`
  - authenticated contents readback and raw GitHub URL readback both serve `zigux/tests/phase8_kallsyms.zig` again on current `master`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

That keeps `kallsyms` in scope as a valid helper-first tooling lane. Current repo evidence is mixed rather than fully missing: the direct helper source and focused build shard are still unreadable from this environment, but the focused test packet is readable again and keeps the parser contract reviewable on current `master`.

The honest same-lane follow-through is therefore to keep the note, validator, and directly coupled reminder surfaces aligned with that mixed readback instead of repeating the older fully missing-file claim or overstating full packet visibility.

## Current repo-read surface

The current lane should be treated as a parked parser-and-wrapper packet with one directly readable focused replay and two still-unreadable helper-local paths from this environment on current `master`.

What this run could verify directly:

- `Documentation/zigux/phase8-kallsyms-slice.md` still exists on current `master`
- `zigux/tests/phase8_kallsyms.zig` is directly readable again on current `master`
- `tools/lib/symbol/kallsyms.zig` is not directly readable through authenticated contents reads or raw GitHub URL readback in this environment
- `zigux/tests/phase8_kallsyms_only_build.zig` is not directly readable through authenticated contents reads in this environment
- the readable focused test keeps one direct `kallsymsParse()` wrapper explicit
- the readable focused test keeps oversized symbol names now truncate to `KSYM_NAME_LEN` explicit
- the readable focused test keeps weak-object `V` and `v` classes still follow the current C header contract explicit
- the readable focused test keeps the parked callback contract, chunked truncation replay, and downstream callback-failure bubbling explicit
- shared reminder surfaces still keep `make -C zigux phase8-help-kallsyms-test` and `make -C zigux phase8-kallsyms-test` visible as the parked focused routes even while the dedicated `phase8_kallsyms_only_build.zig` read path stays unavailable here

Because of that read surface, this note should now describe the following as current parked evidence:

- the roadmap anchor at `tools/lib/symbol/kallsyms.c`
- this slice note plus the readable `zigux/tests/phase8_kallsyms.zig` packet as the directly inspectable same-lane evidence
- the current absence of directly readable `tools/lib/symbol/kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` from this environment on current `master`
- the need to keep shared Phase 8 reminder and validator wording honest until those unreadable helper-local paths return or the checker packet is deliberately narrowed to the mixed-readback reality

## Non-goals

This slice does not currently claim:

- directly readable helper-source coverage from `tools/lib/symbol/kallsyms.zig` on current `master`
- directly readable focused build-shard coverage from `zigux/tests/phase8_kallsyms_only_build.zig` on current `master`
- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the parked helper-first parser-and-wrapper scope

## Next bounded step

Leave the `kallsyms` lane parked unless one of the following happens:

- the helper or focused build route becomes directly readable again on current `master`
- one directly coupled checker, validator, or reminder surface still treats the mixed-readback packet as either fully missing or fully readable and needs one bounded truthfulness repair
- a same-lane helper restoration lands and can be verified through readable current-tree evidence

If the lane reopens, keep it to one helper-local, validator-local, or note-local truthfulness pass at a time, compare the readable `zigux/tests/phase8_kallsyms.zig` packet against the shared reminder routes first, and avoid widening into unrelated Phase 8 tooling work.
