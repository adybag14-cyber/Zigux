# Phase 4 kprobe_example Gap Survey

## Status
- `PHASE4_KPROBE_STATUS=parked_gap_packet_landed`
- `PHASE4_KPROBE_LANE_KEY=P4-L19`
- `PHASE4_KPROBE_PHASE=Phase 4`
- `PHASE4_KPROBE_C_ANCHOR=samples/kprobes/kprobe_example.c`
- `PHASE4_KPROBE_CURRENT_LINUX_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- `PHASE4_KPROBE_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey`
- `PHASE4_KPROBE_LOCAL_SURVEY_WRAPPER=make -C zigux phase4-kprobe-example-survey`
- `PHASE4_KPROBE_BOOTSTRAP_CI_POSTURE=reviewability_only_local_survey_wrapper_not_on_shared_phase4_test_or_bootstrap_workflow`
- `PHASE4_KPROBE_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig`
- `PHASE4_KPROBE_OWNER=Validation and Perf Team`
- `PHASE4_KPROBE_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=keep the dedicated parked survey packet, the explicit local_lab_replay marker, the local survey wrapper, the explicit bootstrap-CI posture, the direct validation entrypoint, and the absent Zig starter boundary explicit until a later bounded validator or starter lane intentionally widens this surface`

## Purpose

This parked Phase 4 gap packet keeps the still-absent `samples/zigux/kprobe_example.zig`
boundary reviewable without pretending that a shipped Zig starter already exists on
`master`.

The packet is intentionally narrow:
- keep the current C anchor explicit
- keep the current Linux replay command explicit
- keep the explicit local lab replay marker explicit
- keep the dedicated local survey wrapper explicit
- keep the explicit bootstrap-CI posture explicit while the starter remains absent
- keep the direct validation entrypoint explicit
- keep ownership and rollback ownership explicit
- keep the next bounded evidence step explicit until a later Phase 4 lane intentionally
  widens the packet

## Current Measurable Status

Current `master` still does not ship `samples/zigux/kprobe_example.zig`.

The bounded evidence packet instead remains:
- `Documentation/zigux/phase4-kprobe-example-gap-survey.md`
- `zigux/tests/phase4_kprobe_example_manifest.json`
- `zigux/tests/phase4_kprobe_example_survey.zig`
- `make -C zigux phase4-kprobe-example-survey`
- `zig test zigux/tests/phase4_kprobe_example_survey.zig`

That packet keeps the current C anchor, replay path, owner, rollback owner, explicit
local lab replay marker, dedicated local survey route, explicit bootstrap-CI posture,
and direct validation entrypoint measurable while the shared Phase 4 rollback-readiness
lane remains below starter implementation.

The same packet also keeps its reversible-delivery evidence string pinned in the paired
manifest so the absent-starter boundary does not fall back to note prose alone.

## Next Bounded Evidence Step

Keep this parked packet adjacent to the shared gate-evidence note, the shared Phase 4
exact-readback packet, the validation matrix, the explicit bootstrap-CI posture, the
explicit local lab replay marker, the dedicated local `make -C zigux
phase4-kprobe-example-survey` wrapper, and the direct `zig test
zigux/tests/phase4_kprobe_example_survey.zig` validation entrypoint until a later
bounded Phase 4 lane intentionally chooses one of these follow-through steps:
- promote the same note, manifest, and replay commands into a stricter shared validator
  packet
- or land the actual Zig starter with an updated rollback-readiness contract

Until then, this note should stay truthful about the absent Zig starter boundary.
