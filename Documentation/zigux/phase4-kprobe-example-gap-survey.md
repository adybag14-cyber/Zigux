# Phase 4 Kprobe Example Gap Survey

This note records a bounded Phase 4 survey packet for the roadmap's `samples/kprobes/kprobe_example.c` anchor without claiming that a Zig starter has landed.

## Status

- `PHASE4_KPROBE_STATUS=parked_gap_survey`
- `PHASE4_LANE_KEY=P4-L23`
- `PHASE4_ANCHOR_PATH=samples/kprobes/kprobe_example.c`
- `PHASE4_ANCHOR_BLOB_SHA=53ec6c8b8c40d0f41f2d4f9becacc9d6b98f1d0d`
- `PHASE4_SAMPLE_PATH=samples/zigux/kprobe_example.zig`
- `PHASE4_SAMPLE_PRESENT=false`
- `PHASE4_CURRENT_REPLAY=make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- `PHASE4_LOCAL_LAB_REPLAY=make -C zigux phase4-kprobe-example-survey`
- `PHASE4_SURVEY_OWNER=Validation and Perf Team`
- `PHASE4_ROLLBACK_OWNER=Validation and Perf Team`
- `PHASE4_SHARED_GATE_EVIDENCE_PACKET_PRESENT=true`
- `PHASE4_VALIDATION_ENTRYPOINT=zig test zigux/tests/phase4_kprobe_example_survey.zig`
- `PHASE4_REVERSIBLE_DELIVERY_EVIDENCE=the dedicated local survey wrapper `make -C zigux phase4-kprobe-example-survey` plus the adjacent shared gate-evidence packet keep the parked kprobe gap reviewable and reversible without claiming a shipped Zig starter`

## Scope

- keep the current C anchor path, anchor blob, replay command, dedicated local survey wrapper, owner, rollback owner, reversible-delivery evidence, and missing-Zig-starter posture reviewable
- keep this packet adjacent to the shared Phase 4 validator-first packet while the shared gate-evidence note now names that same survey note, manifest, replay command, local survey wrapper, and reversible-delivery evidence without claiming a shipped Zig starter
- prepare the smallest truthful handoff for a future manifest-backed promotion into the broader Phase 4 validation surfaces

## Current Readback

- `samples/kprobes/kprobe_example.c` is present on `master` and still plants a bounded `kprobe` around `kernel_clone`
- the live Linux replay path remains `make M=samples/kprobes CONFIG_SAMPLE_KPROBES=m`
- the dedicated local survey wrapper now reruns this parked packet through `make -C zigux phase4-kprobe-example-survey`, and together with the adjacent shared gate-evidence packet it serves as the reversible-delivery evidence for the parked gap while the direct validation entrypoint stays `zig test zigux/tests/phase4_kprobe_example_survey.zig`
- `samples/zigux/kprobe_example.zig` is still absent on current `master`
- the dedicated parked gap packet already spans this note, `zigux/tests/phase4_kprobe_example_manifest.json`, and `zigux/tests/phase4_kprobe_example_survey.zig`, and the shared gate-evidence note now names that same survey note, manifest, replay command, local survey wrapper, and reversible-delivery evidence as adjacent evidence without claiming that a shipped Zig starter exists
- `zigux/tests/README.md` now explicitly names this adjacent parked kprobe survey packet and `make -C zigux phase4-kprobe-example-survey` inside its compact Phase 4 reminder, so the shared tests-root summary, the dedicated local survey wrapper, and this owner note are aligned on current `master`

## Non-Goals

- claiming a shipped Zig starter for `samples/zigux/kprobe_example.zig`
- treating adjacent gate-evidence visibility as a shipped Zig starter
- claiming approved hard perf thresholds for the kprobe anchor

## Next Bounded Step

keep this parked packet adjacent to the shared gate-evidence note, `zigux/tests/phase4_kprobe_example_manifest.json`, `zigux/tests/phase4_kprobe_example_survey.zig`, the compact tests-root Phase 4 reminder, and the dedicated local survey wrapper until a future bounded lane intentionally opens either the Zig starter or a broader validation-surface promotion. If the next same-lane slot still stays below starter work, prefer the next one-file same-packet truthfulness repair that keeps the kprobe gap note, `zigux/tests/phase4_kprobe_example_manifest.json`, `zigux/tests/phase4_kprobe_example_survey.zig`, the shared gate-evidence note, `zigux/tests/README.md`, the reversible-delivery evidence, and `make -C zigux phase4-kprobe-example-survey` aligned.
