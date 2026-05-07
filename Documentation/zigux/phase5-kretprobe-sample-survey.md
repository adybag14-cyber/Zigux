# Phase 5 Kretprobe Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kprobes/kretprobe_example.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_LANE_KEY=P5-L18`
- `PHASE5_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
- `PHASE5_SLICE=kretprobe-reference-sample-starter`
- scope: roadmap-vs-repo sample delivery, approved probe-lifecycle guidance, and exact bounded checks for the first `samples/zigux/` kretprobe-style replay
- product boundary:
  - `Documentation/zigux/phase5-kretprobe-sample-survey.md`
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/kretprobe_example.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_kretprobe_example.zig`
  - `zigux/tests/phase5_kretprobe_example_manifest.json`
  - `zigux/tests/phase5_kretprobe_example_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kprobes/kretprobe_example.c` as one of the Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection already showed landed Phase 5 FIFO and kobject reference samples plus a later Phase 9 runtime `kretprobe` starter. The missing Phase 5 job was still the earlier non-runtime reading of the same Linux anchor so reviewers can see the anchor behavior without confusing it with runtime substrate work.

## Survey findings

- `samples/kprobes/kretprobe_example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a substrate slice.
- the Linux sample mixes five concerns:
  - symbol selection through a module parameter
  - entry skipping for kernel threads with no `current->mm`
  - per-instance private data that stores one entry timestamp for the later return-side duration report
  - return-value and duration reporting from the stored entry timestamp
  - real registration and teardown substrate through `register_kretprobe()`, `unregister_kretprobe()`, `pt_regs`, and module init or exit hooks
- the honest Phase 5 move is to make symbol choice, skip behavior, the one-word private timestamp record, return-duration bookkeeping, the fixed `maxactiveBudget()` review cue at `20`, the `nmissed` summary, and ownership snapshots reviewable in memory while leaving probe registration and module plumbing out of scope.
- the live shared contributor packet for this landed sample is broader than the sample file and its paired manifest alone: `Documentation/zigux/phase5-sample-review-guide.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now keep this kretprobe note aligned with the same four-sample Phase 5 packet described from the docs root, guide, sample root, scripts root, and tests root.
- the narrower same-lane guidance risk on current `master` is no longer missing broad shared-packet coverage; it is sample-local drift between this survey note, the shared Phase 5 guide, and the manifest-backed replay prompts whenever retargeting, lifecycle-guard, or teardown wording changes.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/kretprobe_example.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `KretprobeExampleSample.descriptor()`
- it models only the default symbol name, a pre-init retarget hook, kernel-thread skip behavior, a single per-instance timestamp record, return-duration replay, and a bounded `nmissed` summary in memory
- it uses a tiny `init()` -> `entryHandler()` -> `retHandler()` -> `recordMissedInstance()` -> `exit()` lifecycle so ownership and teardown stay explicit
- it provides `runAnchorReplay()` for the bounded skip, private-data, return-duration, and missed-summary contract
- it provides `runLifecycleGuardReplay()` so pre-init rejection, double-init rejection, and post-init retarget rejection stay reviewable without implying a runtime-ready kretprobe implementation
- it provides `ownershipSummary()` so the sample-owned lifecycle packet stays explicit across `cold`, `initialized`, `armed`, `replay_complete`, and `exited` without borrowing the separate Phase 9 runtime summary surface

The exact checks currently recorded in `zigux/tests/phase5_kretprobe_example_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the in-memory sample keeps `kernel_clone` as the default symbol name while allowing pre-init retargeting
- `runAnchorReplay()` checks that an entry with no `current->mm` is skipped instead of arming a tracked instance
- the in-memory sample keeps a single private entry-timestamp record so the Linux `struct my_data` anchor shape stays explicit as one `i64`-sized word
- the replay records return value `42` and duration `75 ns` after an entry timestamp of `100` and a return timestamp of `175`
- `maxactiveBudget()` keeps the fixed review-only budget at `20` without implying runtime registration-pressure handling
- the replay records one missed instance so the exit-side `nmissed` summary stays reviewable without claiming registration-pressure parity
- `ownershipSummary()` keeps `cold`, `initialized`, `armed`, `replay_complete`, and `exited` snapshots explicit with active-instance and entry-timestamp state
- `exit()` rejects an armed sample until `retHandler()` clears the outstanding tracked instance
- after `exit()` the sample rejects later summary or handler calls

## Latest verification snapshot

A focused current-`master` scratch replay was re-run on 2026-05-06 with the attached Zig toolchain `0.17.0-dev.87+9b177a7d2`.

- `zig fmt --check` passed for `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_survey.zig`, and the focused scratch `zigux/tests/build.zig`
- `zig test samples/zigux/kretprobe_example.zig` passed `3/3` sample self-checks
- a focused scratch replay assembled from the current `master` versions of `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_survey.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and this survey note passed `5/5` build steps and `7/7` tests via `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
- the observed sample markers matched the manifest-backed replay contract exactly: `symbol_name = kernel_clone`, `private_data_size_bytes = 8`, `return_value = 42`, `duration_ns = 75`, `maxactive_budget = 20`, `nmissed = 1`, `maxactive = 20`, and `replay_runs = 1`
- the lifecycle-guard replay also held: `pre_init_anchor_rejected = true`, `pre_init_exit_rejected = true`, `double_init_rejected = true`, `post_init_retarget_rejected = true`, and `stage_after_init = initialized`
- `ownershipSummary()` also stayed explicit across the sample-owned lifecycle packet: `cold`, `initialized`, `armed`, `replay_complete`, and `exited` all remained reviewable through one helper, with `active_instances = 1` plus `entry_timestamp_armed = true` only in the armed state
- the focused `zigux/tests/phase5_kretprobe_example.zig` boundary replay also still held: `entryHandler(false, 11) still skips the kernel-thread path`, `entryHandler(true, 120) still rejects an outstanding tracked instance`, `retHandler(37, 145) still yields duration 45`, `retHandler(9, 199) still rejects invalid timestamp order`, and `retHandler(9, 260) still recovers with duration 60`
- the ownership and teardown path stayed explicit across the sample-owned anchor replay and the focused retarget-and-recovery replay: `cold -> initialized -> replay_complete` for the bounded anchor replay, and `cold -> initialized -> exited` after the teardown-focused recovery path completes

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/kretprobe_example.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `KretprobeExampleSample.descriptor()` still name `samples/kprobes/kretprobe_example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_kretprobe_example_manifest.json` and `zigux/tests/phase5_kretprobe_example_survey.zig` still describe the exact skip, private-data, return-value, duration, and missed-summary contract run through `zigux/tests/phase5_build.zig`?
- do the survey note and focused survey gate still name both `runAnchorReplay()` and `runLifecycleGuardReplay()` so the sample-owned replay and lifecycle-guard surfaces stay explicit?
- does the focused `zigux/tests/phase5_kretprobe_example.zig` replay still keep direct retargeting, outstanding-instance rejection, timestamp-order rejection and recovery, and post-exit teardown rejection explicit while the sample-owned helpers stay bounded?
- do the sample-owned prompts still keep the fixed `maxactiveBudget()` cue at `20`, timestamp-order rejection and recovery, and post-exit handler rejection explicit instead of leaving those probe-lifecycle boundaries implied?
- does `ownershipSummary()` still keep the `cold`, `initialized`, `armed`, `replay_complete`, and `exited` lifecycle packet explicit without implying the separate Phase 9 runtime summary surface?
- does symbol retargeting stay a pre-init in-memory choice instead of implying `module_param` or runtime registration parity?
- if the sample behavior changes, is the manifest updated alongside the replay and teardown contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that `register_kretprobe()`, `unregister_kretprobe()`, `pt_regs` return extraction, and runtime module wiring remain out of scope for this Phase 5 sample?
- if the broader shared review packet is refreshed, does it keep the landed `samples/zigux/kretprobe_example.zig` packet, the shared `Documentation/zigux/phase5-sample-review-guide.md` map, and the shipped `phase5_build.zig` plus make replay route explicit while still separating this sample from the later `runtime_kretprobe` family instead of leaving that distinction trace-events-only?

## Recorded gap vs roadmap

The current gap is no longer "Zigux has no kretprobe sample guidance." The more precise remaining job is:

- the repo now has a reviewable Phase 5 `kretprobe_example` sample plus manifest-backed checks for symbol choice, skip behavior, private-data shape, return timing, summary recording, ownership snapshots, and teardown
- this sample must remain visibly separate from the later Phase 9 runtime `kretprobe` starter so contributors do not over-claim runtime substrate coverage
- the live same-lane reviewability risk is no longer missing shared-packet coverage; it is drift between the kretprobe-owned survey note, the shared Phase 5 guide, and the existing manifest-backed replay prompts when the sample contract changes
- current `master` now carries all four roadmap-backed Phase 5 reference samples, so this slice should stay explicit about its own boundary rather than implying another anchor is still missing

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux kretprobe example
   - `rg -n "samples/kprobes/kretprobe_example.c|PHASE5_LANE_KEY=P5-L18|PHASE5_SURVEYED_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231|Phase 5" Documentation/zigux samples zigux/tests`
2. confirm the current `samples/zigux/` surface keeps the Phase 5 and Phase 9 kretprobe lanes distinct
   - `find samples/zigux -maxdepth 1 -type f | sort | rg "kretprobe|runtime_kretprobe"`
3. run the exact bounded Phase 5 sample checks
   - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
   - `make -C zigux phase5-test`
   - `make -C zigux phase5`

## Non-goals

This survey does not yet claim:

- `register_kretprobe()` parity
- `unregister_kretprobe()` parity
- `pt_regs` or `regs_return_value()` parity
- runtime module wiring

## Next bounded step

Leave this lane parked unless fresh repo inspection shows the kretprobe-owned survey note, the shared Phase 5 guide, or the manifest-backed replay prompts drifting apart. If that happens, keep the follow-through limited to the smallest truthfulness repair across those existing sample-owned surfaces and the shipped `phase5_build.zig` plus make replay route instead of widening into new sample semantics or runtime substrate claims.
