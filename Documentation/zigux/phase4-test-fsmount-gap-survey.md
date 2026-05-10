# Phase 4 Test Fsmount Gap Survey

This note records a bounded Phase 4 survey packet for the roadmap's `samples/vfs/test-fsmount.c` anchor without claiming that a Zig starter has landed.

## Status

- `PHASE4_TEST_FSMOUNT_STATUS=parked_gap_survey`
- `PHASE4_LANE_KEY=P4-L24`
- `PHASE4_ANCHOR_PATH=samples/vfs/test-fsmount.c`
- `PHASE4_ANCHOR_BLOB_SHA=50f47b72e85fbc8dd52dedad96ee96e6379da5b8`
- `PHASE4_SAMPLE_PATH=samples/zigux/test_fsmount.zig`
- `PHASE4_SAMPLE_PRESENT=false`
- `PHASE4_CURRENT_REPLAY=make M=samples/vfs`
- `PHASE4_LOCAL_LAB_REPLAY=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
- `PHASE4_MAKEFILE_WRAPPER=make -C zigux phase4-test-fsmount-survey`
- `PHASE4_SURVEY_OWNER=Validation and Perf Team`
- `PHASE4_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=false`
- `PHASE4_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=the dedicated local survey wrapper `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`, the matching Linux-style wrapper `make -C zigux phase4-test-fsmount-survey`, and the adjacent shared gate-evidence packet keep the parked test_fsmount gap reviewable and reversible without claiming a shipped Zig starter`

## Scope

- keep the current C anchor path, anchor blob, replay command, dedicated local survey wrapper, dedicated Linux-style Makefile wrapper, owner, rollback owner, reversible-delivery evidence, and missing-Zig-starter posture reviewable
- keep this packet adjacent to the shared Phase 4 validator-first packet instead of pretending the exact-readback gate already owns it
- prepare the smallest truthful handoff for a future manifest-backed promotion into the broader Phase 4 validation surfaces

## Current Readback

- `samples/vfs/test-fsmount.c` is present on `master` and still keeps the fd-based mount flow around `fsopen`, `fsconfig`, `fsmount`, and `move_mount` explicit
- the live replay path remains `make M=samples/vfs`
- `samples/zigux/test_fsmount.zig` is still absent on current `master`
- the dedicated parked gap packet now spans this note, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`, and the dedicated local survey wrapper now lives at `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` while the matching Linux-style wrapper now lives at `make -C zigux phase4-test-fsmount-survey`, so the `test_fsmount` follow-through is no longer matrix prose alone even while it stays outside the shared gate-evidence packet
- the dedicated local survey wrapper, the matching Linux-style wrapper, and the adjacent shared gate-evidence packet now serve as the reversible-delivery evidence for this parked gap while the direct validation entrypoint stays `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
- `zigux/tests/README.md` now keeps that same dedicated local survey wrapper and matching Linux-style wrapper explicit beside the parked note and survey files, so the compact tests-root reminder stays aligned with the shared validator reread path without claiming a shipped Zig starter
- the shared validator route already rereads this parked packet through `scripts/zigux/check-phase4-gate-evidence.py`, but `PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=false` remains truthful because the packet is still adjacent evidence rather than part of the exact-readback target set itself

## Non-Goals

- claiming a shipped Zig starter for `samples/zigux/test_fsmount.zig`
- claiming that the shared Phase 4 exact-readback gate already carries this packet
- claiming approved hard perf thresholds for the test_fsmount anchor

## Next Bounded Step

Keep this parked packet adjacent to the shared gate-evidence note, the dedicated exact-readback checker, the compact tests-root reminder at `zigux/tests/README.md`, and both dedicated local survey wrappers at `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` and `make -C zigux phase4-test-fsmount-survey` until a future bounded lane intentionally opens either the Zig starter or a broader validation-surface promotion. If the next same-lane slot still stays below starter work, prefer the next one-file same-packet truthfulness repair that keeps this note, `zigux/tests/phase4_test_fsmount_manifest.json`, `zigux/tests/README.md`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, and both dedicated local survey wrappers aligned.
