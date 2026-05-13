# Phase 4 test_fsmount Gap Survey

## Status
- `PHASE4_TEST_FSMOUNT_STATUS=parked_gap_packet_landed`
- `PHASE4_TEST_FSMOUNT_LANE_KEY=P4-L19`
- `PHASE4_TEST_FSMOUNT_PHASE=Phase 4`
- `PHASE4_TEST_FSMOUNT_C_ANCHOR=samples/vfs/test-fsmount.c`
- `PHASE4_TEST_FSMOUNT_CURRENT_LINUX_REPLAY=make M=samples/vfs`
- `PHASE4_TEST_FSMOUNT_LOCAL_SURVEY_WRAPPER=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
- `PHASE4_TEST_FSMOUNT_LINUX_STYLE_SURVEY_WRAPPER=make -C zigux phase4-test-fsmount-survey`
- `PHASE4_TEST_FSMOUNT_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrappers_not_on_shared_phase4_test_or_bootstrap_workflow`
- `PHASE4_TEST_FSMOUNT_VALIDATION_ENTRYPOINT=zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
- `PHASE4_TEST_FSMOUNT_OWNER=Validation and Perf Team`
- `PHASE4_TEST_FSMOUNT_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_TEST_FSMOUNT_THRESHOLD_POSTURE=reviewability_only_no_perf_threshold`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, both local survey wrappers, the explicit bootstrap-CI posture, the explicit no-perf-threshold posture, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface`

## Purpose

This parked Phase 4 gap packet keeps the still-absent `samples/zigux/test_fsmount.zig`
boundary reviewable without pretending that a shipped Zig starter already exists on
`master`.

The packet is intentionally narrow:
- keep the current C anchor explicit
- keep the current Linux replay command explicit
- keep the dedicated local survey wrappers explicit
- keep the explicit bootstrap-CI posture explicit while the starter remains absent
- keep ownership and rollback ownership explicit
- keep the current no-perf-threshold posture explicit while the starter remains absent
- keep the next bounded evidence step explicit until a later Phase 4 lane intentionally
  widens the packet

## Current Measurable Status

Current `master` still does not ship `samples/zigux/test_fsmount.zig`.

The bounded evidence packet instead remains:
- `Documentation/zigux/phase4-test-fsmount-gap-survey.md`
- `zigux/tests/phase4_test_fsmount_manifest.json`
- `zigux/tests/phase4_test_fsmount_survey.zig`
- `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
- `make -C zigux phase4-test-fsmount-survey`

That packet keeps the current C anchor, replay path, owner, rollback owner, dedicated
local survey routes, explicit bootstrap-CI posture, and the current
reviewability-only no-perf-threshold posture measurable while the shared Phase 4
rollback-readiness lane remains below starter implementation.

The same packet now also keeps its reversible-delivery evidence string pinned in the
paired manifest so the absent-starter boundary does not fall back to note prose
alone.

## Next Bounded Evidence Step

Keep this parked packet adjacent to the shared gate-evidence note, the shared Phase 4
exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the
dedicated local `zig build phase4-test-fsmount-survey --build-file zigux/tests/phase4_build.zig`
survey wrapper, and the matching Linux-style `make -C zigux phase4-test-fsmount-survey`
wrapper until a later bounded Phase 4 lane intentionally chooses one of these
follow-through steps:
- promote the same note, manifest, and both replay commands into a stricter shared
  validator packet
- or land the actual Zig starter with an updated rollback-readiness contract

Until then, this note should stay truthful about the absent Zig starter boundary and
its current reviewability-only threshold posture.
