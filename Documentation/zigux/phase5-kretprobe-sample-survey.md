# Phase 5 Kretprobe Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kprobes/kretprobe_example.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_LANE_KEY=P5-L22`
- `PHASE5_SLICE=kretprobe-reference-sample-starter`
- `PHASE5_SURVEYED_COMMIT=7c1e6840cf73a321e775e8e77448157b1304ee1d`
- scope: roadmap-vs-repo sample reviewability, approved probe-lifecycle guidance, and exact bounded checks for the landed `samples/zigux/` kretprobe-style replay
- product boundary:
  - `Documentation/zigux/phase5-kretprobe-sample-survey.md`
  - `scripts/zigux/README.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/kretprobe_example.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_kretprobe_example.zig`
  - `zigux/tests/phase5_kretprobe_example_manifest.json`
  - `zigux/tests/phase5_kretprobe_example_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kprobes/kretprobe_example.c` as one of the Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection now shows that current `master` carries all four roadmap-approved bounded Phase 5 reference samples under `samples/zigux/`, including the landed `kretprobe_example` slice. The kretprobe-specific job is no longer missing sample delivery; it is to keep this probe-lifecycle idiom, its exact checks, and its non-goals honest now that the broader Phase 5 anchor set is complete.

## Survey findings

- `samples/kprobes/kretprobe_example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a substrate slice.
- the Linux sample mixes five concerns:
  - symbol selection through a module parameter
  - entry skipping for kernel threads with no `current->mm`
  - per-instance private data that stores one entry timestamp for the later return-side duration report
  - return-value and duration reporting from the stored entry timestamp
  - a fixed `maxactive = 20` concurrency budget plus the exit-side `nmissed` summary that explains when that budget was too low
  - real registration and teardown substrate through `register_kretprobe()`, `unregister_kretprobe()`, `pt_regs`, and module init or exit hooks
- the ongoing Phase 5 review job is to keep symbol choice, skip behavior, the one-word private timestamp record, duration bookkeeping, the fixed helper-backed `maxactive` budget, and the `nmissed` summary reviewable in memory while leaving probe registration and module plumbing out of scope.
- the scripts-root Phase 5 flow in `scripts/zigux/README.md`, the shared sample-root catalog in `samples/zigux/README.md`, the top-level docs-root guide in `Documentation/zigux/README.md`, the shared tests-root guide in `zigux/tests/README.md`, and the shared `Documentation/zigux/review-checklist.md` prompts are part of that same contributor packet now, because together they keep this landed non-runtime `kretprobe` idiom visibly separate from the later `samples/zigux/runtime_kretprobe.zig` and `samples/zigux/runtime_kretprobe_loader.zig` Phase 9 follow-ons while naming the direct `zig test samples/zigux/kretprobe_example.zig` replay, the paired `zig test zigux/tests/phase5_kretprobe_example_survey.zig` replay, and the shared `zigux/tests/phase5_build.zig` entrypoint in one place.
- the same contributor packet also has to keep the sample-owned `zigux/tests/phase5_kretprobe_example.zig` replay explicit as a `phase5_build.zig`-wired check: that focused replay imports `kretprobe_example_sample`, so reviewers should treat it as a focused shared-build replay rather than a standalone `zig test` command.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/kretprobe_example.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `KretprobeExampleSample.descriptor()`
- it models only the default symbol name, a pre-init retarget hook, kernel-thread skip behavior, a single per-instance timestamp record, return-duration replay, a `maxactiveBudget()` helper that keeps the Linux `maxactive = 20` cue fixed, and a bounded `nmissed` summary in memory
- it uses a tiny `init()` -> `entryHandler()` -> `retHandler()` -> `recordMissedInstance()` -> `exit()` lifecycle so ownership and teardown stay explicit
- it keeps bounded replay helpers through `runAnchorReplay()`, `runRetargetRecoveryReplay()`, `runMaxactiveBudgetReplay()`, and `runOwnershipBoundaryReplay()` instead of implying a runtime-ready kretprobe implementation

The exact checks currently recorded in `zigux/tests/phase5_kretprobe_example_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the in-memory sample keeps `kernel_clone` as the default symbol name while allowing pre-init retargeting
- before `init()` the in-memory sample allows retargeting the symbol to `do_sys_openat2` and preserves that choice through initialization without implying `module_param` or runtime registration parity
- `runAnchorReplay()` checks that an entry with no `current->mm` is skipped instead of arming a tracked instance
- the in-memory sample keeps a single private entry-timestamp record so the Linux `struct my_data` anchor shape stays explicit as one `i64`-sized word
- the replay records return value `42` and duration `75 ns` after an entry timestamp of `100` and a return timestamp of `175`
- `retHandler()` rejects a return timestamp of `199` after an entry timestamp of `200`, then accepts `260` and reports duration `60 ns` while clearing the private entry timestamp
- `runMaxactiveBudgetReplay()` keeps the Linux `maxactive` budget explicit through `maxactiveBudget()` at `20` concurrent instances even though this Phase 5 slice does not model registration-pressure handling
- the replay records one missed instance so the exit-side `nmissed` summary stays reviewable without claiming registration-pressure parity
- `runOwnershipBoundaryReplay()` rejects `exit()` on an armed sample until `retHandler()` clears the outstanding tracked instance
- after `runOwnershipBoundaryReplay()` exits the sample rejects later `recordMissedInstance()`, `entryHandler()`, or `retHandler()` calls

## Latest verification snapshot

- inspected `master` head: `7c1e6840cf73a321e775e8e77448157b1304ee1d`
- attached Zig toolchain: `0.17.0-dev.87+9b177a7d2`
- exact commands and observed results:
  - `zig test samples/zigux/kretprobe_example.zig`
    - `1/1 kretprobe_example.test.kretprobe sample replay keeps the anchor reviewable and non-runtime...OK`
    - `All 1 tests passed.`
  - `zig test zigux/tests/phase5_kretprobe_example_survey.zig`
    - `1/2 phase5_kretprobe_example_survey.test.phase 5 kretprobe manifest records the exact bounded checks...OK`
    - `2/2 phase5_kretprobe_example_survey.test.phase 5 kretprobe contributor docs stay aligned with the shipped review surface...OK`
    - `All 2 tests passed.`
  - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
    - `Build Summary: 18/18 steps succeeded; 29/29 tests passed`
    - `phase5-kretprobe-example-sample-tests 1 pass (1 total)`
    - `phase5-kretprobe-example-tests 5 pass (5 total)`
    - `phase5-kretprobe-example-survey-tests 2 pass (2 total)`
- the focused `zigux/tests/phase5_kretprobe_example.zig` replay remains part of the shipped `phase5_build.zig` packet rather than a standalone direct `zig test` command, so this note keeps that surface explicit without overstating a separate direct replay.

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/kretprobe_example.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `KretprobeExampleSample.descriptor()` still name `samples/kprobes/kretprobe_example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_kretprobe_example_manifest.json` and `zigux/tests/phase5_kretprobe_example_survey.zig` still describe the exact skip, pre-init retargeting, timestamp-order boundary, private-data, return-value, duration, fixed `maxactive`, missed-summary, and sample-owned `runRetargetRecoveryReplay()`, `runMaxactiveBudgetReplay()`, and `runOwnershipBoundaryReplay()` contract run through `zigux/tests/phase5_build.zig`?
- does `zigux/tests/phase5_kretprobe_example_manifest.json` still pin the exact surveyed commit for the inspected `master` head instead of a floating branch label?
- do the sample-backed survey note, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md` still keep this landed Phase 5 kretprobe slice distinct from the separate `samples/zigux/runtime_kretprobe.zig` and `samples/zigux/runtime_kretprobe_loader.zig` Phase 9 follow-ons while pointing reviewers at the shared `phase5_build.zig` entrypoint?
- does `zigux/tests/phase5_kretprobe_example.zig` still stay wired through `zigux/tests/phase5_build.zig` via the `kretprobe_example_sample` import so the focused replay remains explicit even though it is not a standalone `zig test` entrypoint?
- does the sample keep the Linux `struct my_data`-style private entry timestamp explicit as one `i64`-sized in-memory word instead of hiding the anchor's private-data cue in unstructured state?
- does the sample keep the Linux `maxactive = 20` budget explicit through `maxactiveBudget()` as a fixed reviewable in-memory ceiling instead of silently drifting away from the anchor or implying runtime tuning support?
- does symbol retargeting stay a pre-init in-memory choice instead of implying `module_param` or runtime registration parity?
- does `runRetargetRecoveryReplay()`, `runMaxactiveBudgetReplay()`, and `runOwnershipBoundaryReplay()` still keep the retargeting, fixed-budget, armed-exit rejection, and post-exit handler rejection boundaries explicit as sample-owned replay instead of leaving them to ad hoc test-body assembly?
- if the sample behavior changes, is the manifest updated alongside the replay and teardown contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that `register_kretprobe()`, `unregister_kretprobe()`, `pt_regs` return extraction, and loadable module wiring remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The current gap is no longer "Zigux has no kretprobe sample guidance." The more precise state is:

- the repo now has a reviewable Phase 5 `kretprobe_example` sample plus manifest-backed checks for symbol choice, pre-init retargeting, skip behavior, private-data shape, timestamp-order rejection and recovery, return timing, helper-backed fixed `maxactive`, summary recording, and teardown
- this sample must remain visibly separate from the later `samples/zigux/runtime_kretprobe.zig` and `samples/zigux/runtime_kretprobe_loader.zig` Phase 9 follow-ons so contributors do not over-claim runtime substrate coverage
- this approved probe-lifecycle idiom is now pinned to `PHASE5_SURVEYED_COMMIT=7c1e6840cf73a321e775e8e77448157b1304ee1d` so the survey note, manifest-backed checks, shared sample-root catalog, shared tests-root guide, and shared review checklist all point at the same inspected `master` head
- the Phase 5 roadmap's four named sample anchors are now all represented by bounded `samples/zigux/` reference readings, but that does not close the separate Phase 9 runtime pilot tranche

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux kretprobe example
   - `rg -n "samples/kprobes/kretprobe_example.c|Phase 5" Documentation/zigux samples`
2. confirm the current `samples/zigux/` surface keeps the Phase 5 and Phase 9 kretprobe lanes distinct
   - `find samples/zigux -maxdepth 1 -type f | sort | rg "kretprobe|runtime_kretprobe"`
3. run the focused self-check that keeps the in-memory replay explicit
   - `zig test samples/zigux/kretprobe_example.zig`
4. confirm the focused shared-build replay still stays wired through `zigux/tests/phase5_build.zig`
   - `rg -n "phase5-kretprobe-example-sample-tests|phase5-kretprobe-example-tests|kretprobe_example_sample" zigux/tests/phase5_build.zig zigux/tests/phase5_kretprobe_example.zig`
5. run the manifest-backed survey gate from the repo root so the exact-check record stays readable
   - `zig test zigux/tests/phase5_kretprobe_example_survey.zig`
6. run the exact bounded Phase 5 sample checks
   - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`

## Non-goals

This survey does not yet claim:

- `register_kretprobe()` parity
- `unregister_kretprobe()` parity
- `pt_regs` or `regs_return_value()` parity
- loadable module wiring

## Next bounded step

Stay in the Phase 5 samples-and-reference-patterns lane and tighten contributor guidance or one exact replay check only if fresh repo inspection shows a real sample drift on current `master`, while keeping this landed Phase 5 sample distinct from the separate `samples/zigux/runtime_kretprobe.zig` and `samples/zigux/runtime_kretprobe_loader.zig` Phase 9 follow-ons.
