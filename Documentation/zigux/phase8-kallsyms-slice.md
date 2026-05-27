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
  - `tools/lib/symbol/kallsyms.zig` through authenticated GitHub contents readback on current `master`
  - `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` through authenticated GitHub contents readback on current `master`
  - `zigux/tests/phase8_help_kallsyms_only_build.zig` through authenticated GitHub contents readback on current `master` as shared validation overlap only
  - `make -C zigux phase8-kallsyms-test` through that returned `zigux/Makefile` wrapper
  - `make -C zigux phase8-help-kallsyms-test` as shared validation overlap only
- current dedicated-lane readback:
  - authenticated GitHub contents reads now return the dedicated helper, replay, and focused build shard directly in this runtime
  - the mixed `zigux/tests/phase8_help_kallsyms_only_build.zig` route remains shared validation overlap only; it is not a lane-ownership handoff away from the dedicated `kallsyms` parser packet

## Why this slice exists

The Phase 8 roadmap explicitly names `tools/lib/symbol/kallsyms.c` as a userspace-adjacent tooling anchor, calls for helper-first expansion plus output-stable tooling behavior, and recommends `tools/lib/symbol/*.zig` as a bounded Zigux destination.

This lane therefore stays reserved for one direct `kallsymsParse()` wrapper and the smaller helper-first parser-and-wrapper packet around it. On current `master`, that wrapper surface is already landed in `tools/lib/symbol/kallsyms.zig` beside `kallsymsParseFile()` and `forEachParsedPath()`, so the remaining survey work is truthfulness and narrow follow-through around the shipped parser packet rather than future-facing wrapper planning.

## Verified current behavior

The current repo state that is directly verifiable from this run is still narrower than a full single-source writable checkout replay, but it now proves more than note-only roadmap intent.

This run could verify that:

- `Documentation/zigux/phase8-kallsyms-slice.md` is present on `master`
- `scripts/zigux/validate-phase8.py` is present on `master`
- `scripts/zigux/check-phase8-help-kallsyms-packet.py` is present on `master` through authenticated GitHub contents readback, keeping the dedicated lane markers for shared validation overlap only, `make -C zigux phase8-kallsyms-test`, and the current CRLF-normalization parser contract reviewable
- authenticated GitHub contents readback returns usable `tools/lib/symbol/kallsyms.zig` helper content, including the landed direct parser callback wrapper surface around `kallsymsParseFile()`, `forEachParsedPath()`, and `kallsymsParse()`
- that same helper body still shows that oversized symbol names now truncate to `KSYM_NAME_LEN`
- that same helper body still shows that weak-object `V` and `v` classes still follow the current C header contract
- the helper-local source tests keep the CRLF normalization contract reviewable: the chunked helper test normalizes the split-name fixture to `startup_64`, and the reader, path, and callback wrapper tests normalize carriage returns before newline
- authenticated GitHub contents readback also returns usable `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig` bodies; the dedicated replay now keeps the chunked-reader `startup_64` witness aligned with that helper-local CRLF normalization path, and the focused build shard still maps directly to `../../tools/lib/symbol/kallsyms.zig`
- the authenticated GitHub contents readback for `zigux/Makefile` still keeps both `make -C zigux phase8-kallsyms-test` and `make -C zigux phase8-help-kallsyms-test` aligned with that focused replay packet

## Current parity surface

The current readable packet still covers:

- the roadmap-backed claim that `kallsyms` remains a valid Phase 8 tool lane
- the helper-first expansion wording and the landed direct `kallsymsParse()` wrapper surface
- one directly readable lane note that matches the current dedicated symbol packet
- one directly readable `scripts/zigux/check-phase8-help-kallsyms-packet.py` checker body through authenticated GitHub contents readback
- one directly readable `zigux/Makefile` route packet through authenticated GitHub contents readback
- one directly readable `tools/lib/symbol/kallsyms.zig` helper body through authenticated GitHub contents readback
- oversized symbol names now truncate to `KSYM_NAME_LEN`
- weak-object `V` and `v` classes still follow the current C header contract
- directly readable focused replay and focused build surfaces in `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_kallsyms_only_build.zig`
- the dedicated `make -C zigux phase8-kallsyms-test` route still matches that focused replay and focused build packet
- the current CRLF-normalization contract: the dedicated replay now keeps the chunked-reader `startup_64` witness aligned with the helper-local parser behavior, and the helper-local wrapper tests normalize carriage returns before newline
- the mixed `zigux/tests/phase8_help_kallsyms_only_build.zig` plus `make -C zigux phase8-help-kallsyms-test` route remains shared validation overlap only; it is not a lane-ownership handoff away from the dedicated `kallsyms` parser packet
- the fact that broader shared Phase 8 validation infrastructure is still present even while this run remains limited to readback-plus-focused validation rather than a writable full-tree replay

The current packet does not yet provide:

- a fresh in-workspace parser replay captured from a trusted writable checkout
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Non-goals

This slice does not yet claim:

- broader ELF emission or downstream symbol-tooling integration
- procfs, module-loading, or loader-facing ownership beyond this landed helper-local parser lane
- a wider userspace symbol pipeline beyond the bounded parser-and-wrapper destination reserved by the roadmap

## Next bounded step

Keep the lane narrow.

Because the current readback now exposes the helper, dedicated replay, dedicated build shard, checker, and Makefile through authenticated contents reads, the next honest reopen should be one directly coupled checker, helper, or focused-test follow-through only if the roadmap-backed output-stable contract needs to change from the currently readable CRLF-normalization behavior.

Until then, keep the note aligned with the landed wrapper surface, keep the dedicated `make -C zigux phase8-kallsyms-test` route tied to the helper-local source tests, keep the broader dedicated replay packet visible through its parked `startup_64` witness, and treat the mixed `phase8-help-kallsyms` smoke route as shared validation only instead of reopening broader Phase 8 wording or help-lane ownership.
