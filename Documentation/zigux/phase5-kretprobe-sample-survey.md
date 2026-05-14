# Phase 5 Kretprobe Sample Survey

This note tracks the bounded Phase 5 survey for the roadmap's `samples/kprobes/kretprobe_example.c` anchor.

## Status

- `PHASE5_STATUS=restored-direct-sample-packet`
- `PHASE5_LANE_KEY=P5-L18`
- `PHASE5_SLICE=kretprobe-reference-sample-readback`
- `PHASE5_SURVEYED_COMMIT=fcf670977ef02f9fa7e5d1950d67ba0589baa230`
- scope: restore one directly readable non-runtime kretprobe packet without widening into Phase 9 runtime work

## Current repo reality on `master`

This restored Phase 5 packet now reads directly through:

- `samples/zigux/kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`

The older shared `zigux/tests/phase5_build.zig` route remains missing and should stay explicit as a gap instead of being treated as current proof.

Fresh Phase 5 readback in this run also confirmed that most of the shared reminder packet is already aligned around that restored direct sample packet:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`

Those aligned shared surfaces keep the restored direct packet explicit while still keeping the missing shared `zigux/tests/phase5_build.zig` route framed as a gap instead of returned evidence.

The remaining shared-surface drift in this reread is `zigux/tests/README.md`: it still describes the kretprobe anchor as survey-note-only and still treats `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` as missing current direct evidence even though current `master` now exposes that restored direct packet.

## Landed sample and exact checks

- `KretprobeExampleSample.descriptor()` names `samples/kprobes/kretprobe_example.c` and keeps `requires_runtime_substrate = false`
- the sample defaults `symbol_name` to `kernel_clone`
- `runRetargetReplay("do_sys_openat2")` keeps empty-symbol rejection, pre-init retargeting, initialized post-retarget state, and post-init retarget rejection explicit
- `runAnchorReplay()` keeps skipped kernel-thread handling, `private_data_size_bytes = 8`, `return_value = 42`, `duration_ns = 75`, `nmissed = 1`, and `maxactive = 20` explicit
- `runLifecycleGuardReplay()` keeps pre-init anchor rejection, pre-init exit rejection, double-init rejection, and post-init retarget rejection explicit
- `runOwnershipReplay()` keeps `cold`, `initialized`, `armed`, `replay_complete`, and `exited` snapshots explicit, with `active_instances = 1` and `entry_timestamp_armed = true` only in the armed state
- `runRecoveryReplay()` keeps outstanding-instance exit rejection, invalid timestamp-order rejection, recovered duration `60`, and post-exit handler rejection explicit

## Boundary reminders

Keep this packet separate from the later Phase 9 runtime family:

- `samples/zigux/runtime_kretprobe.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`

This note does not claim `register_kretprobe()` parity, `unregister_kretprobe()` parity, `pt_regs` parity, or runtime module wiring.

## Next bounded step

Keep the next move inside one shared review-surface repair only if a fresh reread still shows the remaining tests-root drift:

- if `zigux/tests/README.md` still presents the kretprobe anchor as survey-note-only, repair only that one file while still keeping the missing shared `phase5_build.zig` route explicit and the later Phase 9 runtime family out of scope
- otherwise leave the restored direct kretprobe packet parked while those shared reminder surfaces stay aligned
