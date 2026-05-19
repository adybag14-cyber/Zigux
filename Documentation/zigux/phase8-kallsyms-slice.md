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
  - `scripts/zigux/check-phase8-help-kallsyms-packet.py` through the public raw fallback
  - `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` through the public raw fallback
- current degraded readback for the dedicated symbol lane:
  - authenticated GitHub contents reads still return `404` for `tools/lib/symbol/kallsyms.zig`, `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig`
  - the container and devbox still could not fetch those raw file bodies directly over the network here, so this lane remains dependent on public raw readback plus contents-API spot checks rather than one single in-container source

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor, calls for helper-first expansion plus output-stable tooling behavior, and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination.

This lane therefore stays reserved for one direct `kallsymsParse()` wrapper and the smaller helper-first parser-and-wrapper packet around it. Current `master` still keeps that future helper-first expansion on the roadmap, and this scheduled environment can now recover the helper, checker, and focused kallsyms test surfaces through the public raw fallback even though the authenticated contents API still disagrees about those paths.

## Verified current behavior

The current repo state that is directly verifiable from this run is narrower than the broader helper packet described by earlier kallsyms notes, but it is no longer note-only.

This run could verify that:

- `Documentation/zigux/phase8-kallsyms-slice.md` is present on `master`
- `scripts/zigux/validate-phase8.py` is present on `master`
- the public raw fallback returns usable `tools/lib/symbol/kallsyms.zig` helper content, including the direct parser callback wrapper surface around `kallsymsParseFile()` and `forEachParsedPath()`, and the current `parseLine()` path trims one trailing `\r` before symbol-name slicing so CRLF-backed records normalize to the same symbol names as LF-backed input
- the public raw fallback also returns usable `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig` bodies, so the checker markers, focused replay names, and focused build route wording are all readable again from one public source type
- authenticated GitHub contents reads still fail for the dedicated kallsyms helper, checker, focused test, and focused build file paths
- the current container and devbox still could not replay those same raw file fetches directly, so this run still stops short of a local helper replay even though the public raw readback is now coherent

That means the remaining lane-local drift is no longer simple helper-packet unreadability. The stale claim now lives inside this dedicated note, which previously undercounted the readable checker and focused test packet.

## Current parity surface

The current readable packet still covers:

- the roadmap-backed claim that `kallsyms` remains a valid Phase 8 tool lane
- the helper-first expansion wording and one future `kallsymsParse()` wrapper target
- one directly readable lane note that now matches the mixed read surface available to this scheduled run
- one directly readable `tools/lib/symbol/kallsyms.zig` helper body through the public raw fallback
- one directly readable `scripts/zigux/check-phase8-help-kallsyms-packet.py` checker body through the public raw fallback
- directly readable focused replay and focused build surfaces in `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` through the public raw fallback
- the fact that broader shared Phase 8 validation infrastructure is still present even though the authenticated contents API still disagrees with the readable public raw packet

The current packet does not yet provide:

- authenticated contents reads that agree with the readable helper, checker, focused test, and focused build packet
- a fresh in-workspace parser replay captured from a trusted local checkout
- a proof that the authenticated contents API and the readable public raw fallback now point at the same exact current symbol-lane bodies
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Non-goals

This slice does not yet claim:

- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond the future helper-local parser lane
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Next bounded step

Keep the lane narrow.

Because the public raw source now exposes the helper, checker, focused test, and focused build packet together again, the next honest reopen should be one directly coupled checker- or focused-test truthfulness repair rather than another absence note. The strongest currently visible candidate remains the parked `zigux/tests/phase8_kallsyms.zig` CRLF expectation sync already suggested by the readable helper body, but that follow-through stays in the neighboring focused test lane instead of reopening broader Phase 8 wording here.

If authenticated contents reads become practical later, restart with one focused replay step around the dedicated packet: reread `tools/lib/symbol/kallsyms.zig`, `scripts/zigux/check-phase8-help-kallsyms-packet.py`, and `zigux/tests/phase8_kallsyms.zig` from the same exact-write-capable source, then land the smallest helper- or test-local follow-through that the reread actually proves.