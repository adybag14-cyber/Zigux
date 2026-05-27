# Phase 8 Kallsyms Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/symbol/kallsyms.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=kallsyms-parse-wrapper-parked`
- scope: roadmap-backed symbol-lane reminder truthfulness, helper-first expansion wording, focused build-route verification, and one remaining helper-local reopen cue only
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

This lane therefore stays reserved for one direct `kallsymsParse()` wrapper and the smaller helper-first parser-and-wrapper packet around it. On current `master`, that wrapper surface is already landed in `tools/lib/symbol/kallsyms.zig` beside `kallsymsParseFile()` and `forEachParsedPath()`, so the remaining survey work is truthfulness and narrow follow-through around the shipped parser packet rather than future-facing wrapper planning.

## Verified current behavior

The current repo state that is directly verifiable from this run is narrower than a full single-source checkout replay, but it now proves more than note-only roadmap intent.

This run could verify that:

- `Documentation/zigux/phase8-kallsyms-slice.md` is present on `master`
- `scripts/zigux/validate-phase8.py` is present on `master`
- `scripts/zigux/check-phase8-help-kallsyms-packet.py` is present on `master` through authenticated GitHub contents readback, keeping the dedicated lane markers for shared validation overlap only, `make -C zigux phase8-kallsyms-test`, and the current CRLF-normalizing parser contract reviewable without relying on the raw fallback for that checker body
- the public raw fallback returns usable `tools/lib/symbol/kallsyms.zig` helper content, including the landed direct parser callback wrapper surface around `kallsymsParseFile()`, `forEachParsedPath()`, and `kallsymsParse()`
- that same helper body still shows that oversized symbol names now truncate to `KSYM_NAME_LEN`
- that same helper body still shows that weak-object `V` and `v` classes still follow the current C header contract
- the helper-local source tests still keep the CRLF normalization contract reviewable: the chunked helper test and the reader, path, and callback wrapper tests all normalize the split-name fixture to `startup_64` by trimming the trailing `\r` before newline
- the public raw fallback also returns usable `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` bodies; the dedicated replay keeps the chunked-reader `startup_64` witness visible after CRLF normalization, and the focused build shard still maps directly to `../../tools/lib/symbol/kallsyms.zig`
- the authenticated GitHub contents readback for `zigux/Makefile` still keeps both `make -C zigux phase8-kallsyms-test` and `make -C zigux phase8-help-kallsyms-test` aligned with that focused replay packet
- authenticated GitHub contents reads still fail for the dedicated kallsyms helper, focused test, and focused build file paths
- the current container and devbox still could not replay those same raw file fetches directly, so this run still stops short of a local helper replay even though the public raw readback is coherent enough to survey the shipped wrapper surface

## Current parity surface

The current readable packet still covers:

- the roadmap-backed claim that `kallsyms` remains a valid Phase 8 tool lane
- the helper-first expansion wording and the landed direct `kallsymsParse()` wrapper surface
- one directly readable lane note that matches the mixed read surface available to this scheduled run
- one directly readable `scripts/zigux/check-phase8-help-kallsyms-packet.py` checker body through authenticated GitHub contents readback
- one directly readable `zigux/Makefile` route packet through authenticated GitHub contents readback
- one directly readable `tools/lib/symbol/kallsyms.zig` helper body through the public raw fallback
- oversized symbol names now truncate to `KSYM_NAME_LEN`
- weak-object `V` and `v` classes still follow the current C header contract
- directly readable focused replay and focused build surfaces in `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` through the public raw fallback
- the dedicated `make -C zigux phase8-kallsyms-test` route still matches that focused replay and focused build packet
- the normalized raw-backed CRLF contract: the dedicated replay keeps the chunked-reader `startup_64` witness visible after CRLF normalization, and the helper-local wrapper tests normalize the trailing carriage return before newline
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
- procfs, module-loading, or loader-facing ownership beyond this landed helper-local parser lane
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Next bounded step

Keep the lane narrow.

Because the current mixed-source readback now exposes the checker and Makefile through authenticated contents reads and the helper plus focused test/build packet through the public raw fallback, the next honest reopen should be one directly coupled checker, helper, or focused-test follow-through only if the roadmap-backed output-stable contract needs to change from the currently readable CRLF-normalizing behavior.

Until then, keep the note aligned with the landed wrapper surface, keep the dedicated `make -C zigux phase8-kallsyms-test` route tied to the helper-local source tests, keep the broader dedicated replay packet visible through its parked `startup_64` witness after CRLF normalization, and treat the mixed `phase8-help-kallsyms` smoke route as shared validation only instead of reopening broader Phase 8 wording or help-lane ownership.

If authenticated contents reads become practical later, restart with one focused replay step around the dedicated packet: reread `tools/lib/symbol/kallsyms.zig`, `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, and `make -C zigux phase8-kallsyms-test` from the same exact-write-capable source, then land the smallest checker-, helper-, or test-local follow-through that the reread actually proves.
