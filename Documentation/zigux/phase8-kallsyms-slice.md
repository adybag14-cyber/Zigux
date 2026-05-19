# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- scope: roadmap-backed symbol-lane reminder truthfulness, helper-first expansion wording, focused build-route verification, and one future helper-local reopen cue only
- current directly readable packet in this scheduled environment:
  - `Documentation/zigux/phase8-kallsyms-slice.md`
  - `scripts/zigux/validate-phase8.py`
  - `tools/lib/symbol/kallsyms.zig` through the public raw fallback
- current degraded readback for the dedicated symbol lane:
  - authenticated GitHub contents reads still return `404` for `tools/lib/symbol/kallsyms.zig`, `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig`
  - the public raw fallback now yields usable helper content for `tools/lib/symbol/kallsyms.zig`, but this run still could not recover the paired checker, focused test, or focused build file bodies from one consistent source type, so the lane remains parked below a fresh helper-local replay

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor, calls for helper-first expansion plus output-stable tooling behavior, and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination.

This lane therefore stays reserved for one direct `kallsymsParse()` wrapper and the smaller helper-first parser-and-wrapper packet around it. Current `master` still keeps that future helper-first expansion on the roadmap, and this scheduled environment can now recover the helper body itself through the public raw fallback even though the dedicated checker-and-test packet still lacks one consistent readable source.

## Verified current behavior

The current repo state that is directly verifiable from this run is narrower than the broader helper packet described by earlier kallsyms notes, but it is no longer note-only.

This run could verify that:

- `Documentation/zigux/phase8-kallsyms-slice.md` is present on `master`
- `scripts/zigux/validate-phase8.py` is present on `master`
- the public raw fallback now returns usable `tools/lib/symbol/kallsyms.zig` helper content, including the direct parser callback wrapper surface around `kallsymsParseFile()` and `forEachParsedPath()`
- authenticated GitHub contents reads still fail for the dedicated kallsyms helper, checker, focused test, and focused build file paths
- the current container and devbox still could not recover the dedicated kallsyms checker, focused test, and focused build files through one consistent source during this scheduled pass

This run could not freshly verify helper-local parser test expectations, focused kallsyms test behavior, or the combined help-and-kallsyms checker contents from one consistent source.

## Current parity surface

The current readable packet still covers:

- the roadmap-backed claim that `kallsyms` remains a valid Phase 8 tool lane
- the helper-first expansion wording and one future `kallsymsParse()` wrapper target
- one directly readable lane note that now matches the mixed read surface available to this scheduled run
- one directly readable `tools/lib/symbol/kallsyms.zig` helper body through the public raw fallback
- the fact that broader shared Phase 8 validation infrastructure is still present even though the focused kallsyms checker-and-test packet is not consistently readable here

The current packet does not yet provide:

- one consistent source type that yields the helper, checker, focused test, and focused build bodies together
- a directly readable focused checker or focused kallsyms replay file from this scheduled environment
- a fresh in-workspace parser replay captured from one consistent helper-plus-test source
- a proof that authenticated contents reads and public fallback reads agree on the focused symbol-lane files
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Non-goals

This slice does not yet claim:

- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the future helper-local parser lane
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Next bounded step

Keep the lane narrow.

If this lane reopens before a focused helper replay is practical, correct one directly coupled symbol-lane checker, focused-test, or review-surface truthfulness gap only after one consistent source exposes the relevant file body again.

If exact helper reads become practical later, restart with one focused replay step around the dedicated packet: reread `tools/lib/symbol/kallsyms.zig`, `scripts/zigux/check-phase8-help-kallsyms-packet.py`, and `zigux/tests/phase8_kallsyms.zig` from the same source type, then land the smallest helper- or test-local follow-through that the reread actually proves.