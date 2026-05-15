# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- scope: roadmap-backed symbol-lane reminder truthfulness, helper-first expansion wording, focused build-route verification, and one future helper-local reopen cue only
- current readable packet:
  - `Documentation/zigux/phase8-kallsyms-slice.md`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_kallsyms_only_build.zig`
  - `zigux/tests/phase8_help_kallsyms_only_build.zig`
- current blocker:
  - exact direct helper readback for `tools/lib/symbol/kallsyms.zig` is still intermittent from this environment, so the focused symbol packet stays parked on reminder-and-build truthfulness plus slice-note alignment rather than a fresh in-repo parser replay

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor, calls for helper-first expansion plus output-stable tooling behavior, and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination.

This lane therefore stays reserved for one direct `kallsymsParse()` wrapper and the smaller parser-and-wrapper follow-through around it. Current `master` already keeps that future helper-first expansion explicit through this slice note, the focused `zigux/tests/phase8_kallsyms.zig` packet, and the build shards that still point at the dedicated symbol helper path.

## Verified current behavior

Current `master` still keeps the focused symbol replay routes visible:

- `zigux/tests/phase8_kallsyms_only_build.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`
- `zigux/tests/phase8_kallsyms.zig`

The dedicated slice review route also stays explicit through `zigux/tests/phase8_kallsyms.zig`, which currently rechecks that this note still names:

- helper-first expansion
- output-stable tooling behavior
- one direct `kallsymsParse()` wrapper
- oversized symbol names now truncate to `KSYM_NAME_LEN`
- weak-object `V` and `v` classes still follow the current C header contract
- `make -C zigux phase8-help-kallsyms-test`

That means the current symbol lane is still parked, but it is no longer parked on a roadmap-vs-survey wording gap inside the dedicated slice note.

## Current parity surface

The current readable packet still covers:

- the roadmap-backed claim that `kallsyms` remains a valid future Phase 8 tool lane
- the roadmap-backed helper-first expansion wording and one direct `kallsymsParse()` wrapper target
- a focused external Phase 8 kallsyms note at `zigux/tests/phase8_kallsyms.zig`
- focused build shards that still declare the intended `kallsyms` replay routes
- a directly verifiable current blocker: exact direct helper readback remains intermittent from this environment even while the focused test and build routes stay visible

The current packet does not yet provide:

- a fresh in-repo parser replay from this environment against directly readable helper contents
- a successful `phase8-kallsyms-only` or shared `help-kallsyms` focused build replay captured from this scheduled workspace
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Non-goals

This slice does not yet claim:

- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the future helper-local parser lane
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Next bounded step

Keep the lane narrow. If `P8-L09` reopens again before a direct helper replay is practical, correct one directly coupled slice-note or focused-test reminder only so the dedicated `kallsyms` survey stays aligned with the roadmap-backed helper-first expansion wording and one direct `kallsymsParse()` wrapper target. If helper readback becomes stable enough for exact replay later, restart with one focused `zig build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all` run before widening into any other Phase 8 tooling work.
