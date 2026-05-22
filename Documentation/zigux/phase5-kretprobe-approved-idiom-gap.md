# Phase 5 Kretprobe Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 kretprobe packet truthful when reviewers need one dedicated reminder of the bounded non-runtime idiom that current `master` still approves.

## Status

  * `PHASE5_STATUS=direct-sample-approved-idiom-packet`
  * `PHASE5_LANE_KEY=P5-L13`
  * `PHASE5_SLICE=kretprobe-approved-idiom-gap`
  * scope: keep the non-runtime kretprobe sample packet reviewable and repeatable without widening into Phase 9 runtime work

## Current approved cue on `master`

The roadmap-backed Phase 5 anchor is still:

  * `samples/kprobes/kretprobe_example.c`

The current non-runtime packet now reads directly through:

  * `Documentation/zigux/phase5-kretprobe-sample-survey.md`
  * `samples/zigux/kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example.zig`
  * `zigux/tests/phase5_kretprobe_example_manifest.json`
  * `zigux/tests/phase5_kretprobe_example_survey.zig`

The returned shared `zigux/tests/phase5_build.zig` route remains useful companion evidence too. Keep it framed as shared build-route support rather than as the primary approved-idiom proof.

## Approved idiom to preserve

Keep the approved Phase 5 kretprobe cue bounded to the current landed packet:

  * `KretprobeExampleSample.descriptor()` still names `samples/kprobes/kretprobe_example.c` and keeps `requires_runtime_substrate = false`
  * `reviewContract()` still keeps the six focus areas explicit: symbol selection, entry timestamp, private-data shape, return duration, missed summary, and ownership-and-lifetime
  * the same contract still keeps the four non-goals explicit: `register_kretprobe` parity, `unregister_kretprobe` parity, `pt_regs or regs_return_value` parity, and loadable module wiring
  * the sample still keeps `kernel_clone` as the default symbol name while making pre-init `retargetSymbol("do_sys_openat2")` a direct in-memory choice instead of implying module-parameter or runtime-registration parity
  * the sample still keeps `retargetMaxactive(3)` as a pre-init-only in-memory choice, while `runAnchorReplay()` keeps the shipped `default_maxactive = 20` path explicit
  * the private-data cue remains one `i64`-sized entry timestamp word through `InstanceData.entry_stamp_ns`
  * `runAnchorReplay()` still keeps the bounded handler packet explicit: skipped kernel-thread entry, armed tracked instance, `retval = 42`, `duration_ns = 75`, `nmissed = 1`, and replay stage closure at `.replay_complete`
  * the focused `phase 5 kretprobe sample keeps symbol retargeting and handler boundaries explicit` test still keeps empty-symbol rejection, pre-init retargeting, post-init retarget rejection, skipped-kernel-thread handling, outstanding-instance rejection, `retval = 37`, and `duration_ns = 45` reviewable
  * the focused `phase 5 kretprobe sample makes ownership and teardown boundaries explicit` test still keeps pre-init replay rejection, double-init rejection, outstanding-instance exit rejection, invalid timestamp-order rejection, recovered duration `60`, `entry_stamp_ns = -1` reset, and post-exit `recordMissedInstance()` rejection explicit

## Validation routes that keep the idiom repeatable

Keep the direct packet-local checks visible too:

  * `zig test samples/zigux/kretprobe_example.zig`
  * `zig test --dep kretprobe_example_sample -Mroot=zigux/tests/phase5_kretprobe_example.zig -Mkretprobe_example_sample=samples/zigux/kretprobe_example.zig`
  * `zig test zigux/tests/phase5_kretprobe_example_survey.zig`

Those three routes should stay the sample-owned self-check, the focused replay proof, and the survey-packet guard for this approved idiom. The manifest-backed contract in `zigux/tests/phase5_kretprobe_example_manifest.json` should keep the same packet-local review prompts and exact checks visible beside them.

## Review boundary

Use this note only to restate the bounded non-runtime idiom that Phase 5 reviewers should preserve inside the roadmap-backed `kretprobe_example` anchor.

Do not treat this note as proof of:

  * `register_kretprobe()` parity
  * `unregister_kretprobe()` parity
  * `pt_regs` or `regs_return_value` parity
  * loadable module wiring
  * module-parameter parity
  * the later Phase 9 `runtime_kretprobe` family

Keep the separate runtime lane separate from this note:

  * `samples/zigux/runtime_kretprobe.zig`
  * `samples/zigux/runtime_kretprobe_loader.zig`

## Next bounded step

Leave this note parked unless a fresh reread finds one new one-file drift between this approved-idiom note and the live kretprobe packet in `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, or `zigux/tests/phase5_kretprobe_example_survey.zig`.
