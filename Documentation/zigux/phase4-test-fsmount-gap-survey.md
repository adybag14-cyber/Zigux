# Phase 4 Test Fsmount Gap Survey

This note records a bounded Phase 4 survey packet for the roadmap's `samples/vfs/test-fsmount.c` anchor without claiming that a Zig starter has landed.

## Status

- `PHASE4_TEST_FSMOUNT_STATUS=parked_gap_survey`
- `PHASE4_LANE_KEY=validation-perf`
- `PHASE4_ANCHOR_PATH=samples/vfs/test-fsmount.c`
- `PHASE4_ANCHOR_BLOB_SHA=50f47b72e85fbc8dd52dedad96ee96e6379da5b8`
- `PHASE4_SAMPLE_PATH=samples/zigux/test_fsmount.zig`
- `PHASE4_SAMPLE_PRESENT=false`
- `PHASE4_CURRENT_REPLAY=make M=samples/vfs`
- `PHASE4_SURVEY_OWNER=Validation and Perf Team`
- `PHASE4_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=false`
- `PHASE4_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`

## Scope

- keep the current C anchor path, anchor blob, replay command, owner, rollback owner, and missing-Zig-starter posture reviewable
- keep this packet adjacent to the shared Phase 4 validator-first packet instead of pretending the exact-readback gate already owns it
- prepare the smallest truthful handoff for a future manifest-backed promotion into the broader Phase 4 validation surfaces

## Current Readback

- `samples/vfs/test-fsmount.c` is present on `master` and still keeps the fd-based mount flow around `fsopen`, `fsconfig`, `fsmount`, and `move_mount` explicit
- the live replay path remains `make M=samples/vfs`
- `samples/zigux/test_fsmount.zig` is still absent on current `master`
- the dedicated parked gap packet now spans this note, `zigux/tests/phase4_test_fsmount_manifest.json`, and `zigux/tests/phase4_test_fsmount_survey.zig`, and the dedicated local survey wrapper now lives at `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`, so the `test_fsmount` follow-through is no longer matrix prose alone even while it stays outside the shared gate-evidence packet
- the shared validator route already rereads this parked packet through `scripts/zigux/check-phase4-gate-evidence.py`, but `PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=false` remains truthful because the packet is still adjacent evidence rather than part of the exact-readback target set itself

## Non-Goals

- claiming a shipped Zig starter for `samples/zigux/test_fsmount.zig`
- claiming that the shared Phase 4 exact-readback gate already carries this packet
- claiming approved hard perf thresholds for the test_fsmount anchor

## Next Bounded Step

Keep this parked packet adjacent to the shared gate-evidence note, the dedicated exact-readback checker, the compact tests-root Phase 4 reminder, and the dedicated local survey wrapper until a future bounded lane intentionally opens either the Zig starter or a broader validation-surface promotion. If the next same-lane slot still stays below starter work, prefer the next one-file same-packet truthfulness repair that keeps this note, `zigux/tests/phase4_test_fsmount_manifest.json`, `Documentation/zigux/phase4-gate-evidence.md`, `Documentation/zigux/phase4-validation-matrix.md`, and `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig` aligned.
