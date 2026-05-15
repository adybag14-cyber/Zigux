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
  - `zigux/tests/phase8_kallsyms_only_build.zig`
- current read-path state from this environment on 2026-05-15:
  - authenticated GitHub contents reads still return `404` for `tools/lib/symbol/kallsyms.zig`
  - authenticated GitHub contents reads now serve `zigux/tests/phase8_kallsyms_only_build.zig`
  - authenticated contents readback and GitHub blob-url readback both serve `zigux/tests/phase8_kallsyms.zig` on current `master`
  - direct raw GitHub URL readback currently returns `403` for `tools/lib/symbol/kallsyms.zig`
  - direct raw GitHub URL readback currently returns `403` for `zigux/tests/phase8_kallsyms_only_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

That keeps `kallsyms` in scope as a valid helper-first tooling lane. Current repo evidence is still mixed rather than fully stable across every read path, but it is narrower and more truthful than the older missing-file cue: the focused build shard and focused test packet are directly readable again through the authenticated GitHub routes available here, while the helper source itself still fails closed on both contents and raw fallback readback from this environment.

The honest same-lane follow-through is therefore to keep the note, validator, and directly coupled reminder surfaces aligned with that current split instead of repeating the older raw-readable helper claim or understating the restored focused build shard.

## Current repo-read surface

The current lane should be treated as a parked helper-first parser-and-wrapper packet with three directly readable same-packet files through authenticated contents and blob-url readback on current `master`, while the helper source still lacks a stable direct route from this environment.

What this run could verify directly:

- `Documentation/zigux/phase8-kallsyms-slice.md` still exists on current `master`
- `zigux/tests/phase8_kallsyms.zig` is directly readable again on current `master`
- `zigux/tests/phase8_kallsyms_only_build.zig` is directly readable again through authenticated GitHub contents readback on current `master`
- the focused build shard still points at `../../tools/lib/symbol/kallsyms.zig`, so the helper path remains part of the parked packet even though direct helper reads still fail closed from this environment on current `master`
- the readable focused test keeps one direct `kallsymsParse()` wrapper explicit
- the readable focused test keeps oversized symbol names now truncate to `KSYM_NAME_LEN` explicit
- the readable focused test keeps weak-object `V` and `v` classes still follow the current C header contract explicit
- the readable focused test keeps the parked callback contract, chunked truncation replay, and downstream callback-failure bubbling explicit
- shared reminder surfaces still keep `make -C zigux phase8-help-kallsyms-test` and `make -C zigux phase8-kallsyms-test` visible as the parked focused routes

Because of that read surface, this note should now describe the following as current parked evidence:

- the roadmap anchor at `tools/lib/symbol/kallsyms.c`
- this slice note, the readable `zigux/tests/phase8_kallsyms.zig` packet, and the readable `zigux/tests/phase8_kallsyms_only_build.zig` shard as the directly inspectable same-lane evidence from this environment
- the current contents-route instability for `tools/lib/symbol/kallsyms.zig` from this environment on current `master`
- the current raw-URL `403` fallback failure for `tools/lib/symbol/kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` from this environment on current `master`
- the need to keep shared Phase 8 reminder and validator wording honest until the helper's authenticated contents route becomes stable again or the checker packet is deliberately narrowed to a smaller read-path contract

## Non-goals

This slice does not currently claim:

- stable authenticated-contents coverage for `tools/lib/symbol/kallsyms.zig` on current `master`
- direct raw GitHub URL coverage for `tools/lib/symbol/kallsyms.zig` or `zigux/tests/phase8_kallsyms_only_build.zig` from this environment
- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the parked helper-first parser-and-wrapper packet

## Next bounded step

Leave the `kallsyms` lane parked unless one of the following happens:

- the authenticated contents route for `tools/lib/symbol/kallsyms.zig` becomes stable again on current `master`
- one directly coupled checker, validator, or reminder surface still treats the readable focused build shard or focused test packet as missing and needs one bounded truthfulness repair
- a same-lane helper restoration lands and can be verified through readable current-tree evidence

If the lane reopens, keep it to one helper-local, validator-local, or note-local truthfulness pass at a time, compare the readable `zigux/tests/phase8_kallsyms.zig` packet and `zigux/tests/phase8_kallsyms_only_build.zig` shard against the shared reminder routes first, and avoid widening into unrelated Phase 8 tooling work.
