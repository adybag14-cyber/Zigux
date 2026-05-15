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

A later public-tree reread in this lane also confirmed this older shared build path:

- `zigux/tests/phase5_build.zig`

Keep the restored kretprobe packet anchored to the directly readable sample, focused test, manifest, and survey gate above, while treating the returned shared `zigux/tests/phase5_build.zig` route as current public-tree-backed companion evidence rather than direct authenticated-contents proof.

Fresh Phase 5 readback in this run also confirmed that the shared reminder packet is aligned around that restored direct sample packet:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Those aligned shared surfaces keep the restored direct packet explicit and keep the returned shared `zigux/tests/phase5_build.zig` route visible as current public-tree-backed companion evidence instead of treating it as direct authenticated proof.

## Landed sample and exact checks

- `KretprobeExampleSample.descriptor()` names `samples/kprobes/kretprobe_example.c` and keeps `requires_runtime_substrate = false`
- the sample defaults `symbol_name` to `kernel_clone`
- `runRetargetReplay("do_sys_openat2")` keeps empty-symbol rejection, pre-init retargeting, initialized post-retarget state, and post-init retarget rejection explicit
- `runAnchorReplay()` keeps skipped kernel-thread handling, `private_data_size_bytes = 8`, `return_value = 42`, `duration_ns = 75`, `nmissed = 1`, and `maxactive = 20` explicit
- `runLifecycleGuardReplay()` keeps pre-init anchor rejection, pre-init exit rejection, double-init rejection, and post-init retarget rejection explicit
- `runOwnershipReplay()` keeps `cold`, `initialized`, `armed`, `replay_complete`, and `exited` snapshots explicit, with `active_instances = 1` and `entry_timestamp_armed = true` only in the armed state
- `runRecoveryReplay()` keeps outstanding-instance exit rejection, invalid timestamp-order rejection, recovered duration `60`, and post-exit handler rejection explicit

## Contributor checklist

When a contributor updates `samples/zigux/kretprobe_example.zig` or one of its directly coupled reminder surfaces, keep these packet-local prompts explicit here instead of relying on the broader shared guides alone:

- does `KretprobeExampleSample.descriptor()` still name `samples/kprobes/kretprobe_example.c` and keep `requires_runtime_substrate = false` so the packet stays in the non-runtime Phase 5 lane?
- does the sample still keep the default `kernel_clone` path explicit together with `runRetargetReplay("do_sys_openat2")`, including empty-symbol rejection before init and post-init retarget rejection afterward?
- do `runAnchorReplay()`, `runLifecycleGuardReplay()`, `runOwnershipReplay()`, and `runRecoveryReplay()` still describe the same bounded packet across the sample, focused test, manifest-backed contract, and survey gate, including `private_data_size_bytes = 8`, `return_value = 42`, `duration_ns = 75`, `nmissed = 1`, `maxactive = 20`, and recovered duration `60`?
- if a shared reminder surface mentions the restored kretprobe packet, does it keep `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` explicit while also keeping the returned shared `zigux/tests/phase5_build.zig` route visible as current public-tree-backed companion evidence rather than direct authenticated proof?
- do the docs still keep the separate Phase 9 `runtime_kretprobe` family visible without widening this note into `register_kretprobe()` parity, `unregister_kretprobe()` parity, `pt_regs` parity, or runtime module wiring claims?

## Boundary reminders

Keep this packet separate from the later Phase 9 runtime family:

- `samples/zigux/runtime_kretprobe.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`

This note does not claim `register_kretprobe()` parity, `unregister_kretprobe()` parity, `pt_regs` parity, or runtime module wiring.

## Next bounded step

Leave the restored direct kretprobe packet parked unless a future reread finds a new one-file same-lane shared reminder drift:

- if a shared README, guide, or checklist later stops naming the restored direct packet or misstates the returned shared `phase5_build.zig` route as either missing or direct authenticated proof, repair only that one file
- otherwise leave the restored direct kretprobe packet parked while the shared reminder surfaces stay aligned