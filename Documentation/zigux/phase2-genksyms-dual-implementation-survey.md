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
- Current `master` also directly serves `scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py`, so the lane has a dedicated survey guard on head even though that guard is still narrower than the shared Phase 2 replay surfaces.

## Current repo-reality gap

- Authenticated current-`master` reads for `scripts/zigux/genksyms_crc.zig` and `scripts/zigux/check-genksyms-crc-diff.py` return missing.
- The current directly readable Phase 2 closure packet and validator packet also no longer name the CRC-side tool, checker, or fixture family as active current-master proof, while they do continue to name the wrapper bridge, its checker, and its fixtures.
- The survey guard itself is present on current `master`, but the directly readable shared replay surfaces still center the wrapper bridge packet rather than replaying the dedicated dual-implementation survey checker as part of the active `phase2-genksyms` evidence stack.
- That means the repo currently materializes the wrapper-first genksyms bridge, but not the earlier deeper same-family CRC-side dual-implementation evidence recorded in the ledger.

## Survey result

- Relative to the roadmap, `scripts/zigux/genksyms.zig` is still real product infrastructure, not churn: the bridge helper, checker, fixtures, standalone proofs, workflow hooks, and make route remain landed and reviewable.
- Relative to the stronger `selected dual implementations` roadmap wording and the ledger's two-step genksyms history, the current repo is only partially closed. The wrapper-first bridge is present, but the CRC-side dual-implementation slice is not directly materialized on current `master`.
- The truthful current state for lane `P2-L07` is therefore: wrapper bridge landed, deeper same-family dual-implementation evidence missing.
- The current lane-local follow-through gap is narrower than a fresh helper rewrite: keep the survey honest about the missing CRC-side packet and the still-lane-local survey guard instead of overstating the wrapper bridge as full dual-implementation closure.

## Verification note

- On May 28, 2026, this scheduled lane reread the current `master` payload for `scripts/zigux/genksyms.zig`, `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/check-phase2-genksyms-selftest-alignment.py`, `scripts/zigux/check-phase2-genksyms-dual-implementation-survey.py`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`, `zigux/tests/README.md`, `zigux/Makefile`, `scripts/zigux/validate-phase2.py`, and the genksyms bridge fixture packet.
- The same run also checked the roadmap and ledger anchors locally and confirmed that authenticated current-master reads for `scripts/zigux/genksyms_crc.zig` and `scripts/zigux/check-genksyms-crc-diff.py` returned missing.
- Direct checked-out `zig test` replay was not available in this runtime because repo checkout through raw GitHub transport was blocked, so validation stayed truthfulness-focused and artifact-backed.

## Next bounded same-family step

1. Keep the wrapper-first bridge packet parked unless its helper, checker, fixtures, manifest, tests-root reminder, or Phase 2 wrapper hooks drift.
2. If this lane resumes substantive implementation rather than survey upkeep, start with one smallest same-family closure step around the missing CRC-side packet: either rematerialize a bounded `genksyms_crc` survey or restore the missing CRC-side tool-plus-checker evidence before widening beyond `genksyms`.
3. If the lane next does reminder-surface upkeep instead of CRC restoration, wire the dedicated survey checker into the shared `phase2-genksyms` replay surfaces so the current wrapper-first packet and the dual-implementation gap statement cannot silently drift apart.
