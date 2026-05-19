# Phase 5 Kretprobe Sample Survey

This note tracks the bounded Phase 5 survey for the roadmap's `samples/kprobes/kretprobe_example.c` anchor.
## Status

  * `PHASE5_STATUS=restored-direct-sample-packet`
  * `PHASE5_LANE_KEY=P5-L18`
  * `PHASE5_SLICE=kretprobe-sample-reviewability-packet`
  * `PHASE5_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
  * scope: keep the restored direct sample packet and its focused review guard aligned without widening into Phase 9 runtime work
## Current repo reality on `master`

This restored Phase 5 packet now reads directly through:

  * `samples/zigux/kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example_manifest.json`
  * `zigux/tests/phase5_kretprobe_example_survey.zig`

A later public-tree reread in this lane also confirmed this older shared build path:

  * `zigux/tests/phase5_build.zig`
Keep the restored kretprobe packet anchored to the directly readable sample, focused test, manifest, and survey gate above, while treating the returned shared `zigux/tests/phase5_build.zig` route as current public-tree-backed companion evidence rather than direct authenticated-contents proof.

Fresh Phase 5 readback in this run also confirmed that the shared reminder packet is aligned around that restored direct sample packet:
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/phase5-sample-lane-sequencing.md`
  * `Documentation/zigux/phase5-sample-review-guide.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/check-phase5-review-guide-surface.py`
  * `samples/zigux/README.md`
  * `scripts/zigux/README.md`
  * `zigux/tests/README.md`

Those aligned shared surfaces keep the restored direct packet explicit, keep the dedicated review-guide surface checker visible as the shipped shared guard for that reminder family, and keep the returned shared `zigux/tests/phase5_build.zig` route visible as current public-tree-backed companion evidence instead of treating it as direct authenticated proof.
## Landed sample and exact checks
  * `KretprobeExampleSample.descriptor()` names `samples/kprobes/kretprobe_example.c` and keeps `requires_runtime_substrate = false`
  * the sample defaults `symbol_name` to `kernel_clone`
  * `runAnchorReplay()` keeps skipped kernel-thread handling, `private_data_size_bytes = 8`, `return_value = 42`, `duration_ns = 75`, `nmissed = 1`, and `maxactive = 20` explicit
  * the focused `phase 5 kretprobe sample keeps symbol retargeting and handler boundaries explicit` test keeps empty-symbol rejection, pre-init retargeting to `do_sys_openat2`, post-init retarget rejection, the skipped kernel-thread count, the armed-state guard, the outstanding-instance guard, `retval = 37`, and `duration_ns = 45` explicit
  * the focused `phase 5 kretprobe sample makes ownership and teardown boundaries explicit` test keeps pre-init replay and exit rejection, double-init rejection, outstanding-instance exit rejection, invalid timestamp-order rejection, recovered duration `60`, `entry_stamp_ns = -1` reset, and post-exit `recordMissedInstance()` rejection explicit
  * the sample packet keeps the `cold`, `initialized`, `armed`, `replay_complete`, and `exited` stage progression explicit across the sample and paired tests, with `active_instances = 1` only while armed and `exit_runs = 1` after teardown
## Contributor checklist

When a contributor updates `samples/zigux/kretprobe_example.zig` or one of its directly coupled reminder surfaces, keep these packet-local prompts explicit here instead of relying on the broader shared guides alone:
  * does `KretprobeExampleSample.descriptor()` still name `samples/kprobes/kretprobe_example.c` and keep `requires_runtime_substrate = false` so the packet stays in the non-runtime Phase 5 lane?
  * do the sample and focused test still keep the default `kernel_clone` path explicit together with pre-init `retargetSymbol("do_sys_openat2")`, empty-symbol rejection, skipped kernel-thread handling, and post-init retarget rejection?
  * do `runAnchorReplay()` plus the focused handler-boundary and teardown tests still describe the same bounded packet across the sample, focused test, manifest-backed contract, and survey gate, including `private_data_size_bytes = 8`, `return_value = 42`, `duration_ns = 75`, `nmissed = 1`, `maxactive = 20`, and recovered duration `60` with post-exit rejection still explicit?
  * if a shared reminder surface mentions the restored kretprobe packet, does it keep `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig` explicit while also keeping the shipped `scripts/zigux/check-phase5-review-guide-surface.py` guard and the returned shared `zigux/tests/phase5_build.zig` route visible as current public-tree-backed companion evidence rather than direct authenticated proof?
  * do the docs still keep the separate Phase 9 `runtime_kretprobe` family visible without widening this note into `register_kretprobe()` parity, `unregister_kretprobe()` parity, `pt_regs` parity, or runtime module wiring claims?
## Boundary reminders

Keep this packet separate from the later Phase 9 runtime family:

  * `samples/zigux/runtime_kretprobe.zig`
  * `samples/zigux/runtime_kretprobe_loader.zig`

This note does not claim `register_kretprobe()` parity, `unregister_kretprobe()` parity, `pt_regs` parity, or runtime module wiring.
## Next bounded step

Leave the restored direct kretprobe packet parked unless a future reread finds a new one-file same-lane shared reminder drift:

  * if a shared README, guide, checklist, or dedicated guide-surface checker later stops naming the restored direct packet or misstates the returned shared `phase5_build.zig` route as either missing or direct authenticated proof, repair only that one file
  * otherwise leave the restored direct kretprobe packet parked while the shared reminder surfaces stay aligned