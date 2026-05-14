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
  - `tools/lib/symbol/kallsyms.zig`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_kallsyms_only_build.zig`
- current read-path state from this environment on 2026-05-14:
  - authenticated GitHub contents reads still return `404` for `tools/lib/symbol/kallsyms.zig`
  - authenticated GitHub contents reads still return `404` for `zigux/tests/phase8_kallsyms_only_build.zig`
  - raw GitHub URL readback now serves `tools/lib/symbol/kallsyms.zig`
  - raw GitHub URL readback now serves `zigux/tests/phase8_kallsyms_only_build.zig`
  - authenticated contents readback and raw GitHub URL readback both serve `zigux/tests/phase8_kallsyms.zig` again on current `master`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

That keeps `kallsyms` in scope as a valid helper-first tooling lane. Current repo evidence is still mixed rather than fully stable across every read path, but it is broader than the older missing-file cue: the direct helper source and focused build shard are raw-readable again, while the focused test packet remains directly readable and keeps the parser contract reviewable on current `master`.

The honest same-lane follow-through is therefore to keep the note, validator, and directly coupled reminder surfaces aligned with that mixed readback instead of repeating the older fully missing-file claim or overstating contents-route stability.

## Current repo-read surface

The current lane should be treated as a parked helper-first parser-and-wrapper packet with three directly readable same-packet files through mixed raw and authenticated readback on current `master`.

What this run could verify directly:

- `Documentation/zigux/phase8-kallsyms-slice.md` still exists on current `master`
- `tools/lib/symbol/kallsyms.zig` is directly readable again through raw GitHub URL readback on current `master`
- `zigux/tests/phase8_kallsyms.zig` is directly readable again on current `master`
- `zigux/tests/phase8_kallsyms_only_build.zig` is directly readable again through raw GitHub URL readback on current `master`
- the readable focused test keeps one direct `kallsymsParse()` wrapper explicit
- the readable focused test keeps oversized symbol names now truncate to `KSYM_NAME_LEN` explicit
- the readable focused test keeps weak-object `V` and `v` classes still follow the current C header contract explicit
- the readable focused test keeps the parked callback contract, chunked truncation replay, and downstream callback-failure bubbling explicit
- shared reminder surfaces still keep `make -C zigux phase8-help-kallsyms-test` and `make -C zigux phase8-kallsyms-test` visible as the parked focused routes

Because of that read surface, this note should now describe the following as current parked evidence:

- the roadmap anchor at `tools/lib/symbol/kallsyms.c`
- this slice note, the raw-readable `tools/lib/symbol/kallsyms.zig` helper, the readable `zigux/tests/phase8_kallsyms.zig` packet, and the raw-readable `zigux/tests/phase8_kallsyms_only_build.zig` shard as the directly inspectable same-lane evidence
- the current contents-route instability for `tools/lib/symbol/kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` from this environment on current `master`
- the need to keep shared Phase 8 reminder and validator wording honest until the authenticated contents route matches the broader raw-readable packet or the checker packet is deliberately narrowed to a smaller read-path contract

## Non-goals

This slice does not currently claim:

- stable authenticated-contents coverage for `tools/lib/symbol/kallsyms.zig` on current `master`
- stable authenticated-contents coverage for `zigux/tests/phase8_kallsyms_only_build.zig` on current `master`
- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the parked helper-first parser-and-wrapper packet

## Next bounded step

Leave the `kallsyms` lane parked unless one of the following happens:

- the authenticated contents route for the helper or focused build shard becomes stable again on current `master`
- one directly coupled checker, validator, or reminder surface still treats the raw-readable helper and focused build shard as unreadable and needs one bounded truthfulness repair
- a same-lane helper restoration lands and can be verified through readable current-tree evidence

If the lane reopens, keep it to one helper-local, validator-local, or note-local truthfulness pass at a time, compare the raw-readable `tools/lib/symbol/kallsyms.zig` helper plus the readable `zigux/tests/phase8_kallsyms.zig` packet against the shared reminder routes first, and avoid widening into unrelated Phase 8 tooling work.
