# Phase 5 Kretprobe Sample Survey

This note tracks the bounded Phase 5 survey for the roadmap's `samples/kprobes/kretprobe_example.c` anchor.
## Status

  * `PHASE5_STATUS=restored-direct-sample-packet`
  * `PHASE5_LANE_KEY=P5-L22`
  * `PHASE5_SLICE=kretprobe-sample-reviewability-packet`
  * `PHASE5_SURVEYED_COMMIT=4387decfa0a96506f8207b81f74c8ac794a006a6`
  * scope: keep the restored direct sample packet and its focused review guard aligned without widening into Phase 9 runtime work
## Current repo reality on `master`

This restored Phase 5 packet now reads directly through:

  * `samples/zigux/kretprobe_example.zig`
  * `samples/zigux/kretprobe_example_instance_budget_contract.zig`
  * `samples/zigux/kretprobe_example_probe_spec.zig`
  * `zigux/tests/phase5_kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig`
  * `zigux/tests/phase5_kretprobe_example_probe_spec.zig`
  * `zigux/tests/phase5_kretprobe_example_manifest.json`
  * `zigux/tests/phase5_kretprobe_example_survey.zig`

Fresh authenticated contents reread in this lane also directly returned this shared build path:

  * `zigux/tests/phase5_build.zig`
Keep the restored kretprobe packet anchored to the directly readable sample, focused test, instance-budget companion, probe-spec companion, focused instance-budget replay, focused probe-spec replay, manifest, and survey gate above, while treating the returned shared `zigux/tests/phase5_build.zig` route as current directly readable shared build-route companion evidence rather than sample-local proof.
That shared build-route companion now reruns the sample-owned `samples/zigux/kretprobe_example.zig` self-checks alongside the focused replay, survey gate, sample-owned instance-budget companion checks, focused instance-budget replay, sample-owned probe-spec companion checks, and focused probe-spec replay, so the direct sample proof stays exercised from the shared Phase 5 rerun handle without widening this note into runtime or module-registration claims.

Fresh Phase 5 readback in this run also confirmed that the shared reminder packet is aligned around the restored direct sample packet and shared build-route companion:
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/phase5-sample-lane-sequencing.md`
  * `Documentation/zigux/phase5-sample-review-guide.md`
  * `Documentation/zigux/review-checklist.md`
  * `scripts/zigux/check-phase5-review-guide-surface.py`
  * `samples/zigux/README.md`
  * `scripts/zigux/README.md`
  * `zigux/tests/README.md`

Those aligned shared surfaces keep the restored direct `samples/zigux/kretprobe_example.zig` packet explicit, keep the dedicated review-guide surface checker visible as the shipped shared guard for that reminder family, and keep the returned shared `zigux/tests/phase5_build.zig` route visible as current directly readable shared build-route companion evidence instead of flattening it into sample-local proof. Fresh reread in this run also confirms that the bounded companion detail is no longer limited to one shared reminder pair: `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, and `samples/zigux/README.md` now name both `samples/zigux/kretprobe_example_instance_budget_contract.zig` with `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig` and `samples/zigux/kretprobe_example_probe_spec.zig` with `zigux/tests/phase5_kretprobe_example_probe_spec.zig`, while `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still keep the narrower direct-sample proof wording without that extra bounded companion detail.
## Landed sample and exact checks
  * `KretprobeExampleSample.descriptor()` names `samples/kprobes/kretprobe_example.c` and keeps `requires_runtime_substrate = false`
  * `KretprobeExampleSample.reviewContract()` keeps the six review focuses and four explicit non-goals visible, including `register_kretprobe` parity, `unregister_kretprobe` parity, `pt_regs or regs_return_value` parity, and loadable module wiring as out of scope for this Phase 5 sample
  * the sample defaults `symbol_name` to `kernel_clone` and keeps pre-init `retargetMaxactive(3)` reviewable through the focused maxactive test, with zero-value rejection, replay `maxactive = 3`, and post-init retarget rejection all explicit
  * `runAnchorReplay()` keeps skipped kernel-thread handling, `private_data_size_bytes = 8`, `return_value = 42`, `duration_ns = 75`, and `maxactive = 20` explicit
  * the focused `phase 5 kretprobe sample keeps symbol retargeting and handler boundaries explicit` test keeps empty-symbol rejection, pre-init retargeting to `do_sys_openat2`, post-init retarget rejection, the skipped kernel-thread count, the armed-state guard, the outstanding-instance guard, `retval = 37`, and `duration_ns = 45` explicit
  * the focused `phase 5 kretprobe sample makes ownership and teardown boundaries explicit` test keeps pre-init replay and exit rejection, double-init rejection, outstanding-instance exit rejection, invalid timestamp-order rejection, recovered duration `60`, `entry_stamp_ns = -1` reset, and post-exit `recordMissedInstance()` rejection explicit
  * the sample-owned `samples/zigux/kretprobe_example_instance_budget_contract.zig` companion plus the focused `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig` replay keep the Linux `func` parameter, shared `0o644` mode, default `kernel_clone`, one-word private-data shape, return-value and duration reporting, skipped-kernel-thread handling, and the `nmissed`-suggests-increasing-`maxactive` cue explicit beside the main replay packet without turning that companion into a fifth Phase 5 sample
  * the sample-owned `samples/zigux/kretprobe_example_probe_spec.zig` companion plus the focused `zigux/tests/phase5_kretprobe_example_probe_spec.zig` replay keep the direct Linux anchor path, default symbol, one-word private-data size, default `maxactive`, bounded replay return and duration summary, missed-instance count, and the pre-init-only symbol-selection and maxactive-tuning rules explicit beside the main replay packet without turning that companion into a fifth Phase 5 sample
  * the sample packet keeps the `cold`, `initialized`, `armed`, `replay_complete`, and `exited` stage progression explicit across the sample and paired tests, with `active_instances = 1` only while armed and `exit_runs = 1` after teardown
## Contributor checklist

When a contributor updates `samples/zigux/kretprobe_example.zig` or one of its directly coupled reminder surfaces, keep these packet-local prompts explicit here instead of relying on the broader shared guides alone:
  * does `KretprobeExampleSample.descriptor()` still name `samples/kprobes/kretprobe_example.c` and keep `requires_runtime_substrate = false` so the packet stays in the non-runtime Phase 5 lane?
  * do `reviewContract()` and the focused lane tests still keep the six review focuses and four explicit non-goals visible, so the packet continues to say plainly that `register_kretprobe`, `unregister_kretprobe`, `pt_regs or regs_return_value`, and loadable module wiring are out of scope here?
  * do the sample and focused test still keep the default `kernel_clone` path explicit together with pre-init `retargetSymbol("do_sys_openat2")`, empty-symbol rejection, skipped kernel-thread handling, and post-init retarget rejection?
  * do the focused maxactive and replay checks still keep pre-init-only `retargetMaxactive(3)`, zero-value rejection, replay `maxactive = 3`, the `my_data`-style private entry timestamp shape, and the returned anchor replay `maxactive = 20` path explicit without implying module parameters or runtime registration parity?
  * do `runAnchorReplay()` plus the focused handler-boundary and teardown tests still describe the same bounded packet across the sample, focused test, manifest-backed contract, and survey gate, including `private_data_size_bytes = 8`, `return_value = 42`, `duration_ns = 75`, `nmissed = 1`, and recovered duration `60` with post-exit rejection still explicit?
  * do the sample-owned instance-budget companion and focused replay still keep the same bounded `func`-parameter, `0o644`, default-`kernel_clone`, one-word private-data, and `nmissed` / `maxactive` cues explicit without widening this packet into runtime registration or module wiring claims?
  * do the sample-owned probe-spec companion and focused replay still keep the same direct anchor, default symbol, `@sizeOf(i64)` private-data width, default `maxactive`, replay return and duration summary, missed-instance cue, and pre-init-only selection or tuning rules explicit without widening this packet into runtime registration or module wiring claims?
  * do the direct validation routes stay explicit too: `zig test samples/zigux/kretprobe_example.zig`, `zig test --dep kretprobe_example_sample -Mroot=zigux/tests/phase5_kretprobe_example.zig -Mkretprobe_example_sample=samples/zigux/kretprobe_example.zig`, and `zig test zigux/tests/phase5_kretprobe_example_survey.zig` should stay visible as the sample-owned self-check route, the focused replay route, and the survey-packet guard, while the shared `zigux/tests/phase5_build.zig` line stays current directly readable shared build-route companion evidence and keeps rerunning the sample-owned self-checks together with the focused replay, survey gate, instance-budget companion checks, and probe-spec companion checks rather than slipping back to partial sample coverage or sample-local proof?
  * do the direct instance-budget validation routes stay explicit too: `zig test samples/zigux/kretprobe_example_instance_budget_contract.zig` should stay visible as the sample-owned companion route, and `zig test --dep kretprobe_example_instance_budget_contract -Mroot=zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig -Mkretprobe_example_instance_budget_contract=samples/zigux/kretprobe_example_instance_budget_contract.zig` should stay visible as the focused replay route for that bounded packet while `zigux/tests/phase5_build.zig` keeps rerunning both checks from the shared Phase 5 handle?
  * do the direct probe-spec validation routes stay explicit too: `zig test samples/zigux/kretprobe_example_probe_spec.zig` should stay visible as the sample-owned companion route, and `zig test --dep kretprobe_example_probe_spec -Mroot=zigux/tests/phase5_kretprobe_example_probe_spec.zig -Mkretprobe_example_probe_spec=samples/zigux/kretprobe_example_probe_spec.zig` should stay visible as the focused replay route for that bounded packet while `zigux/tests/phase5_build.zig` keeps rerunning both checks from the shared Phase 5 handle?
  * if a shared reminder surface mentions the restored kretprobe packet, does it keep `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, `zigux/tests/phase5_kretprobe_example_survey.zig`, the shipped `scripts/zigux/check-phase5-review-guide-surface.py` guard, and the returned shared `zigux/tests/phase5_build.zig` route visible as current directly readable shared build-route companion evidence rather than sample-local proof, and if that surface also names the bounded instance-budget companion or probe-spec companion does it keep `samples/zigux/kretprobe_example_instance_budget_contract.zig`, `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig`, `samples/zigux/kretprobe_example_probe_spec.zig`, and `zigux/tests/phase5_kretprobe_example_probe_spec.zig` explicit too?
  * do the docs still keep the separate Phase 9 `runtime_kretprobe` family visible without widening this note into `register_kretprobe()` parity, `unregister_kretprobe()` parity, `pt_regs` parity, or runtime module wiring claims?
## Boundary reminders

Keep this packet separate from the later Phase 9 runtime family:

  * `samples/zigux/runtime_kretprobe.zig`
  * `samples/zigux/runtime_kretprobe_loader.zig`

This note does not claim `register_kretprobe()` parity, `unregister_kretprobe()` parity, `pt_regs` parity, or runtime module wiring.
## Next bounded step

Leave the restored direct kretprobe packet parked unless a future reread finds a new one-file same-lane note drift inside this sample packet:

  * if `Documentation/zigux/phase5-kretprobe-sample-survey.md` later misstates `samples/zigux/kretprobe_example.zig`, `samples/zigux/kretprobe_example_instance_budget_contract.zig`, `samples/zigux/kretprobe_example_probe_spec.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig`, `zigux/tests/phase5_kretprobe_example_probe_spec.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, `zigux/tests/phase5_kretprobe_example_survey.zig`, or the returned directly readable shared build-route companion status of `zigux/tests/phase5_build.zig`, repair only this note
  * otherwise leave the restored direct kretprobe packet parked while the sample-owned packet stays aligned
