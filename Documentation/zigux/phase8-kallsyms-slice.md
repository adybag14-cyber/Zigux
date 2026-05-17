# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- scope: roadmap-backed symbol-lane reminder truthfulness, helper-first expansion wording, focused build-route verification, and one future helper-local reopen cue only
- current readable packet:
  - `Documentation/zigux/phase8-kallsyms-slice.md`
  - `tools/lib/symbol/kallsyms.zig`
  - `zigux/Makefile` route names for `phase8-help-kallsyms-test` and `phase8-kallsyms-test`
- current blocker:
  - current `master` still does not directly read back `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `scripts/zigux/validate-phase8.py`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, or `zigux/tests/phase8_help_kallsyms_only_build.zig`, so the named Phase 8 kallsyms replay routes remain reminder-only until that focused checker-and-test packet is republished

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor, calls for helper-first expansion plus output-stable tooling behavior, and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination.

This lane therefore stays reserved for one direct `kallsymsParse()` wrapper and the smaller parser-and-wrapper follow-through around it. Current `master` still keeps that future helper-first expansion explicit through the live helper path, even though the old focused Phase 8 checker and test companions are not all directly readable today.

## Verified current behavior

Current `master` now keeps the dedicated helper surface directly readable again at `tools/lib/symbol/kallsyms.zig`.

That helper still exposes the bounded parser-and-wrapper behavior this lane is meant to protect, including:

- `pub const KSYM_NAME_LEN: usize = 512;`
- one direct `parseLine()` parser entrypoint inside the helper
- output-stable truncation of oversized symbol names to `KSYM_NAME_LEN`
- weak-object `V` and `v` classification coverage
- chunked parsing coverage for oversized input lines before callback delivery
- reader, path, and callback wrapper coverage that preserves raw carriage returns before newline

Current `master` also still names the intended replay routes in `zigux/Makefile`, including:

- `phase8-validate`
- `phase8-help-kallsyms-test`
- `phase8-kallsyms-test`

But the directly coupled checker and dedicated replay shards are not currently readable on `master` from this scheduled environment:

- `scripts/zigux/check-phase8-help-kallsyms-packet.py`
- `scripts/zigux/validate-phase8.py`
- `zigux/tests/phase8_kallsyms.zig`
- `zigux/tests/phase8_kallsyms_only_build.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`

That means the current symbol lane is parked on a mixed state: the helper is back, but the focused Phase 8 checker-and-test packet needed for an honest build replay is not yet directly present beside it.

## Current parity surface

The current readable packet still covers:

- the roadmap-backed claim that `kallsyms` remains a valid Phase 8 tool lane
- the helper-first expansion wording and one direct `kallsymsParse()` wrapper target
- direct helper-backed reminder truthfulness for truncation, weak-object classification, chunked oversized-line handling, and callback-wrapper stability
- the fact that `zigux/Makefile` still advertises focused Phase 8 kallsyms replay routes
- a directly verifiable blocker: the dedicated checker and replay shard files named by those routes are not currently directly readable on `master`

The current packet does not yet provide:

- a fresh in-workspace parser replay captured from this scheduled environment against one consistent helper source
- a successful `phase8-kallsyms-only` or shared `help-kallsyms` focused build replay captured from this scheduled workspace
- a directly readable dedicated Phase 8 kallsyms test note or build shard beside the helper
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Non-goals

This slice does not yet claim:

- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the future helper-local parser lane
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Next bounded step

Keep the lane narrow.

If this lane reopens before a focused helper replay is practical, correct one directly coupled checker, build-route, or dedicated slice-note reminder only so the `kallsyms` packet stays aligned with the live helper and the missing checker-and-test shard reality.

If helper replay becomes practical later, restart with one focused republish-or-replay step around the missing dedicated packet first: restore one of `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `scripts/zigux/validate-phase8.py`, `zigux/tests/phase8_kallsyms_only_build.zig`, or `zigux/tests/phase8_help_kallsyms_only_build.zig`, then run the narrowest honest `zig build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all` check before widening into any other Phase 8 tooling work.
