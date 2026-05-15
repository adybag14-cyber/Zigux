# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- scope: roadmap-backed symbol-lane reminder truthfulness, focused build-route verification, and one future helper-local reopen cue only
- current readable packet:
  - `Documentation/zigux/phase8-kallsyms-slice.md`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_kallsyms_only_build.zig`
  - `zigux/tests/phase8_help_kallsyms_only_build.zig`
- current blocker:
  - `tools/lib/symbol/kallsyms.zig` still returns `404` on direct current-`master` GitHub contents reads, so the focused symbol packet is parked on reminder-and-build truthfulness rather than a directly runnable helper module

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination for this tranche.

This lane therefore stays reserved for one future `kallsyms` parser-and-wrapper follow-through, but current `master` does not yet expose a readable `tools/lib/symbol/kallsyms.zig` helper to validate directly. The honest current product surface is narrower: a dedicated slice note, the parked focused Phase 8 kallsyms test note, and the build shards that still point at the missing helper path.

## Verified current behavior

Current `master` still keeps the focused symbol replay routes visible:

- `zigux/tests/phase8_kallsyms_only_build.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`
- `zigux/tests/phase8_kallsyms.zig`

But the bounded build replay is presently blocked before parser behavior can run:

1. direct GitHub contents reads for `tools/lib/symbol/kallsyms.zig` return `404`
2. a focused replay of `zig build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all` fails immediately because Zig cannot open `tools/lib/symbol/kallsyms.zig`

That means the current symbol lane is parked on build-route truthfulness and reminder maintenance, not on a live helper-first parser packet.

## Current parity surface

The current readable packet still covers:

- the roadmap-backed claim that `kallsyms` remains a valid future Phase 8 tool lane
- a focused external Phase 8 kallsyms note at `zigux/tests/phase8_kallsyms.zig`
- focused build shards that still declare the intended `kallsyms` replay routes
- a directly verifiable current blocker: both focused build shards still depend on the missing `tools/lib/symbol/kallsyms.zig` helper path

The current packet does not yet provide:

- a readable `tools/lib/symbol/kallsyms.zig` helper on current `master`
- a runnable `zig test tools/lib/symbol/kallsyms.zig` replay
- a successful `phase8-kallsyms-only` or shared `help-kallsyms` focused build replay

## Non-goals

This slice does not yet claim:

- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the future helper-local parser lane
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Next bounded step

Keep the lane narrow. If `P8-L11` reopens again before the helper is restored, correct one directly coupled checker, validator, or note surface so it stops treating the missing `tools/lib/symbol/kallsyms.zig` path as a passing current-`master` build packet. If the helper path becomes readable later, restart with one focused replay of `zig build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all` before widening into any other Phase 8 tooling work.
