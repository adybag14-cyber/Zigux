# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- scope: roadmap-backed symbol-lane reminder truthfulness, helper-first expansion wording, focused build-route verification, and one future helper-local reopen cue only
- current readable packet:
  - `Documentation/zigux/phase8-kallsyms-slice.md`
  - `tools/lib/symbol/kallsyms.zig`
  - `scripts/zigux/check-phase8-help-kallsyms-packet.py`
  - `scripts/zigux/validate-phase8.py`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_kallsyms_only_build.zig`
  - `zigux/tests/phase8_help_kallsyms_only_build.zig`
  - `zigux/Makefile` route names for the broader `phase8-validate`, `phase8-exec-cmd-test`, `phase8-test`, and `phase8` entrypoints only
- current blocker:
  - current `master` still presents a mixed readback surface in this scheduled environment: public raw GitHub fallback reads the focused helper, checker, validator, test, and build files cleanly, but authenticated contents reads for some of the same symbol-lane paths still return `404`, so this lane remains parked on reminder truthfulness and direct raw-backed survey evidence rather than a fresh in-workspace replay

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor, calls for helper-first expansion plus output-stable tooling behavior, and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination.

This lane therefore stays reserved for one direct `kallsymsParse()` wrapper and the smaller helper-first parser-and-wrapper packet around it. Current `master` still keeps that future helper-first expansion explicit through the live helper path and the directly readable focused checker-and-replay packet, even though exact authenticated contents reads remain inconsistent from this scheduled environment.

## Verified current behavior

Current `master` keeps the dedicated helper surface directly readable at `tools/lib/symbol/kallsyms.zig`.

That helper still exposes the bounded parser-and-wrapper behavior this lane is meant to protect, including:

- `pub const KSYM_NAME_LEN: usize = 512;`
- one direct `parseLine()` parser entrypoint inside the helper
- one direct `kallsymsParse()` callback wrapper surface
- oversized symbol names now truncate to `KSYM_NAME_LEN`
- weak-object `V` and `v` classes still follow the current C header contract
- chunked parsing coverage for oversized input lines before callback delivery
- reader, path, and callback wrapper coverage that preserves raw carriage returns before newline

Current `master` also keeps the directly coupled focused packet readable through raw GitHub fallback, including:

- `scripts/zigux/check-phase8-help-kallsyms-packet.py`
- `scripts/zigux/validate-phase8.py`
- `zigux/tests/phase8_kallsyms.zig`
- `zigux/tests/phase8_kallsyms_only_build.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`
- `zigux/Makefile` route names for the broader `phase8-validate`, `phase8-exec-cmd-test`, `phase8-test`, and `phase8` entrypoints only, while the focused symbol replays remain direct `zig build test --build-file ...` entrypoints rather than dedicated make wrappers

That means the current symbol lane is no longer a missing-checker or missing-test packet from a repo-read perspective. The honest current lane posture is narrower: the helper-first parser-and-wrapper packet is readable again through the fallback path, while authenticated contents reads still disagree on some of those same paths and keep exact-file verification degraded in this scheduled environment.

## Current parity surface

The current readable packet still covers:

- the roadmap-backed claim that `kallsyms` remains a valid Phase 8 tool lane
- the helper-first expansion wording and one direct `kallsymsParse()` wrapper target
- direct helper-backed reminder truthfulness for truncation, weak-object classification, chunked oversized-line handling, and callback-wrapper stability
- a directly readable focused checker, validator, test, and build packet for the bounded symbol lane
- the fact that current `master` keeps only the broader Phase 8 make routes, so focused symbol review depends on the dedicated build files rather than per-slice make wrappers
- a directly verifiable blocker: authenticated contents reads and in-workspace replay remain degraded even though raw GitHub fallback now surfaces the packet

The current packet does not yet provide:

- a fresh in-workspace parser replay captured from this scheduled environment against one consistent helper source
- a successful `phase8-kallsyms-only` or shared `help-kallsyms` focused build replay captured from this scheduled workspace
- a proof that the authenticated contents path has caught back up with the raw fallback surface for every focused symbol-lane file
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Non-goals

This slice does not yet claim:

- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the future helper-local parser lane
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Next bounded step

Keep the lane narrow.

If this lane reopens before a focused helper replay is practical, correct one directly coupled symbol-lane reminder, checker, or focused-test truthfulness gap only so the `kallsyms` packet stays aligned with the live helper, the direct build-file replays, and the broader shared Phase 8 make routes.

If helper replay becomes practical later, restart with one focused replay step around the already readable dedicated packet: rerun `zig build test --build-file zigux/tests/phase8_kallsyms_only_build.zig --summary all`, then confirm the same result against `zigux/tests/phase8_help_kallsyms_only_build.zig` before widening into any other Phase 8 tooling work.
