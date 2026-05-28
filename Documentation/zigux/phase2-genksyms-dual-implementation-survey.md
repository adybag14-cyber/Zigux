# Phase 2 genksyms dual-implementation survey

Lane: `P2-L07`

## Roadmap and ledger anchor

- The Phase 2 roadmap still treats `scripts/genksyms/genksyms.c` as part of the bounded toolchain and Kbuild tranche, with `scripts/zigux/genksyms.zig` as the Zigux destination.
- The same roadmap also says Phase 2 should ship `selected dual implementations` and keep `wrapper-first` only as the default posture for parser-heavy tooling, not as proof that the deeper same-family implementation is already closed.
- The bootstrap ledger records two same-family genksyms steps rather than one: an earlier bounded CRC lane around `scripts/zigux/genksyms_crc.zig` and `scripts/zigux/check-genksyms-crc-diff.py`, then the later wrapper lane around `scripts/zigux/genksyms.zig` and `scripts/zigux/check-genksyms-bridge.py`.

## Current repo evidence

- Current `master` directly serves `scripts/zigux/genksyms.zig`, so the wrapper-first helper is still present on head.
- The live helper still exposes the bounded bridge shape rather than a deeper parser rollout: request and command structs, explicit parse-failure variants for option handling, a sixteen-file reference cap, long-option resolution for `help`, `version`, `debug`, `warnings`, `quiet`, `dump`, `reference`, `dump-types`, and `preserve`, and JSON bridge rendering through `renderGenksymsBridge()`.
- The live helper still carries embedded Zig unit tests for short and long option parsing, version or help side effects, getopt-style error rendering, empty inline `--reference=` and abbreviated `--dump-t=` argument preservation, passthrough handling, dash-prefixed short- and long-option arguments consumed as data, and the sixteen-reference-file cap.
- Current `master` also directly serves the bounded checker, invocation-fixture packet, dedicated manifest, help fixture, standalone version-side-effect proofs, process-output fixtures, tests-root reminder, closure note, Phase 2 validator surfaces, workflow hooks, and `phase2-genksyms` make wrapper tied to that bridge packet.
- Current `master` now also directly serves `scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py`, which keeps this survey anchored to the live wrapper-first helper and the still-missing CRC-side evidence instead of treating the ledger history as already fully closed.

## Current repo-reality gap

- Authenticated current-`master` reads for `scripts/zigux/genksyms_crc.zig` and `scripts/zigux/check-genksyms-crc-diff.py` return missing.
- The current directly readable Phase 2 closure packet and validator packet also no longer name the CRC-side tool, checker, or fixture family as active current-master proof, while they do continue to name the wrapper bridge, its checker, and its fixtures.
- That means the repo currently materializes the wrapper-first genksyms bridge, but not the earlier deeper same-family CRC-side dual-implementation evidence recorded in the ledger.

## Survey result

- Relative to the roadmap, `scripts/zigux/genksyms.zig` is still real product infrastructure, not churn: the bridge helper, checker, fixtures, standalone proofs, workflow hooks, and make route remain landed and reviewable.
- Relative to the stronger `selected dual implementations` roadmap wording and the ledger's two-step genksyms history, the current repo is only partially closed. The wrapper-first bridge is present, but the CRC-side dual-implementation slice is not directly materialized on current `master`.
- The truthful current state for lane `P2-L07` is therefore: wrapper bridge landed, deeper same-family dual-implementation evidence missing.

## Verification note

- On May 27, 2026, this scheduled lane reread the current `master` payload for `scripts/zigux/genksyms.zig`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `zigux/tests/README.md`, and the genksyms bridge fixture packet.
- The same run also checked the roadmap and ledger anchors locally and confirmed that authenticated current-master reads for `scripts/zigux/genksyms_crc.zig` and `scripts/zigux/check-genksyms-crc-diff.py` returned missing.
- Direct checked-out `zig test` replay was not available in this runtime because repo checkout through raw GitHub transport was blocked, so validation stayed truthfulness-focused and artifact-backed.

## Next bounded same-family step

1. Keep the wrapper-first bridge packet parked unless its helper, checker, fixtures, manifest, tests-root reminder, or Phase 2 wrapper hooks drift.
2. If this lane resumes substantive implementation rather than survey upkeep, start with one smallest same-family closure step around the missing CRC-side packet: either rematerialize a bounded `genksyms_crc` survey or restore the missing CRC-side tool-plus-checker evidence before widening beyond `genksyms`.
