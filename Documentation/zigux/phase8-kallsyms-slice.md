# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- scope: roadmap-backed symbol-lane reminder truthfulness, helper-first expansion wording, focused build-route verification, and one future helper-local reopen cue only
- current directly readable packet in this scheduled environment:
  - `Documentation/zigux/phase8-kallsyms-slice.md`
  - `scripts/zigux/validate-phase8.py`
  - `scripts/zigux/check-phase8-help-kallsyms-packet.py` through authenticated GitHub contents readback
  - `zigux/Makefile` through authenticated GitHub contents readback
  - `tools/lib/symbol/kallsyms.zig` through the public raw fallback
  - `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` through the public raw fallback
  - `make -C zigux phase8-kallsyms-test` through that returned `zigux/Makefile` wrapper
- current degraded readback for the dedicated symbol lane:
  - authenticated GitHub contents reads still return `404` for `tools/lib/symbol/kallsyms.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig`
  - the container and devbox still could not fetch those raw file bodies directly over the network here, so this lane remains dependent on public raw readback plus contents-API spot checks rather than one single in-container source

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor, calls for helper-first expansion plus output-stable tooling behavior, and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination.

This lane therefore stays reserved for one direct `kallsymsParse()` wrapper and the smaller helper-first parser-and-wrapper packet around it. Current `master` still keeps that future helper-first expansion on the roadmap, and this scheduled environment can now recover the checker and Makefile through authenticated GitHub contents reads while the helper and focused kallsyms tests remain recoverable only through the public raw fallback.

## Verified current behavior

The current repo state that is directly verifiable from this run is narrower than the broader helper packet described by earlier kallsyms notes, but it is no longer note-only.

This run could verify that:

- `Documentation/zigux/phase8-kallsyms-slice.md` is present on `master`
- `scripts/zigux/validate-phase8.py` is present on `master`
- `scripts/zigux/check-phase8-help-kallsyms-packet.py` is present on `master` through authenticated GitHub contents readback, keeping the dedicated lane markers for `shared validation overlap only`, `make -C zigux phase8-kallsyms-test`, and the current CRLF-preserving parser contract reviewable without relying on the raw fallback for that checker body
- the public raw fallback returns usable `tools/lib/symbol/kallsyms.zig` helper content, including the direct parser callback wrapper surface around `kallsymsParseFile()` and `forEachParsedPath()`, oversized symbol names now truncate to `KSYM_NAME_LEN`, weak-object `V` and `v` classes still follow the current C header contract, and the current `parseLine()` plus reader and wrapper tests still preserve one trailing `\r` on CRLF-backed symbol names instead of normalizing those names before slicing
- the public raw fallback also returns usable `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` bodies, and the focused replay still expects `startup_64\r` on the chunked-reader path while the wrapper contract keeps that same raw carriage-return behavior below broader parser redesign work
- the authenticated GitHub contents readback for `zigux/Makefile` still keeps the dedicated `make -C zigux phase8-kallsyms-test` route aligned with that focused replay and focused build shard
- authenticated GitHub contents reads still fail for the dedicated kallsyms helper, focused test, and focused build file paths
- the current container and devbox still could not replay those same raw file fetches directly, so this run still stops short of a local helper replay even though the public raw readback is now coherent

That means the remaining lane-local drift is no longer simple helper-packet unreadability. The stale claim this run closed was the older checker-readback warning inside this dedicated note, not the focused replay.

## Current parity surface

The current readable packet still covers:

- the roadmap-backed claim that `kallsyms` remains a valid Phase 8 tool lane
- the helper-first expansion wording and one future `kallsymsParse()` wrapper target
- one directly readable lane note that now matches the mixed read surface available to this scheduled run
- one directly readable `scripts/zigux/check-phase8-help-kallsyms-packet.py` checker body through authenticated GitHub contents readback
- one directly readable `zigux/Makefile` route packet through authenticated GitHub contents readback
- one directly readable `tools/lib/symbol/kallsyms.zig` helper body through the public raw fallback
- oversized symbol names now truncate to `KSYM_NAME_LEN`
- weak-object `V` and `v` classes still follow the current C header contract
- directly readable focused replay and focused build surfaces in `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` through the public raw fallback
- the dedicated `make -C zigux phase8-kallsyms-test` route still matches that focused replay and focused build packet
- the current raw-backed CRLF contract, where chunked reader and wrapper paths still preserve the trailing carriage return in symbol names
- the mixed `zigux/tests/phase8_help_kallsyms_only_build.zig` plus `make -C zigux phase8-help-kallsyms-test` route remains shared validation overlap only; it is not a lane-ownership handoff away from the dedicated `kallsyms` parser packet
- the fact that broader shared Phase 8 validation infrastructure is still present even though the authenticated contents API still disagrees with the readable public raw packet

The current packet does not yet provide:

- authenticated contents reads that agree with the readable helper, focused test, and focused build packet
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

Because the current mixed-source readback now exposes the checker and Makefile through authenticated contents reads and the helper plus focused test/build packet through the public raw fallback, the next honest reopen should be one directly coupled helper- or focused-test follow-through only if the roadmap-backed output-stable contract needs to change from the currently readable CRLF-preserving behavior. Until then, keep the note and focused replay aligned with that mixed-source packet, keep the dedicated `make -C zigux phase8-kallsyms-test` route tied to that same focused build shard, and treat the mixed `phase8-help-kallsyms` smoke route as shared validation only instead of reopening broader Phase 8 wording or help-lane ownership.

If authenticated contents reads become practical later, restart with one focused replay step around the dedicated packet: reread `tools/lib/symbol/kallsyms.zig`, `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, and `make -C zigux phase8-kallsyms-test` from the same exact-write-capable source, then land the smallest helper- or test-local follow-through that the reread actually proves.
