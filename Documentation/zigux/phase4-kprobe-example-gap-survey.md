# Phase 4 Kprobe Example Gap Survey

This note records a bounded Phase 4 survey packet for the roadmap's `samples/kprobes/kprobe_example.c` anchor without claiming that a Zig starter has landed.

## Status

- `PHASE4_KPROBE_STATUS=parked_gap_survey`
- `PHASE4_LANE_KEY=validation-perf`
- `PHASE4_ANCHOR_PATH=samples/kprobes/kprobe_example.c`
- `PHASE4_ANCHOR_BLOB_SHA=53ec6c8b8c40d0f41f2d4f9becacc9d6b98f1d0d`
- `PHASE4_SAMPLE_PATH=samples/zigux/kprobe_example.zig`
- `PHASE4_SAMPLE_PRESENT=false`
- `PHASE4_CURRENT_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- `PHASE4_SURVEY_OWNER=Validation and Perf Team`
- `PHASE4_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=true`
- `PHASE4_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig`

## Scope

- keep the current C anchor path, anchor blob, replay command, owner, rollback owner, and missing-Zig-starter posture reviewable
- keep this packet adjacent to the shared Phase 4 validator-first packet while the shared gate-evidence note now names that same survey note, manifest, and replay command without claiming a shipped Zig starter
- prepare the smallest truthful handoff for a future manifest-backed promotion into the broader Phase 4 validation surfaces

## Current Readback

- `samples/kprobes/kprobe_example.c` is present on `master` and still plants a bounded `kprobe` around `kernel_clone`
- the live replay path remains `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- `samples/zigux/kprobe_example.zig` is still absent on current `master`
- the dedicated parked gap packet already spans this note, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`, and the shared gate-evidence note now names that same survey note, manifest, and replay command as adjacent evidence without claiming that a shipped Zig starter exists

## Non-Goals

- claiming a shipped Zig starter for `samples/zigux/kprobe_example.zig`
- treating adjacent gate-evidence visibility as a shipped Zig starter
- claiming approved hard perf thresholds for the kprobe anchor

## Next Bounded Step

Land one manifest-backed Phase 4 test_fsmount gap survey packet that keeps the current C anchor, replay command, owner, and rollback owner reviewable without claiming a shipped Zig starter.
