# Phase 5 Kretprobe Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kprobes/kretprobe_example.c` anchor.

## Status

- `PHASE5_STATUS=active`
- `PHASE5_SLICE=kretprobe-reference-sample-starter`
- scope: roadmap-vs-repo sample delivery, approved probe-lifecycle guidance, and exact bounded checks for the first `samples/zigux/` kretprobe-style replay
- product boundary:
  - `Documentation/zigux/phase5-kretprobe-sample-survey.md`
  - `Documentation/zigux/README.md`
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
  - a fixed `maxactive = 20` concurrency budget plus the exit-side `nmissed` summary that explains when that budget was too low
  - real registration and teardown substrate through `register_kretprobe()`, `unregister_kretprobe()`, `pt_regs`, and module init or exit hooks
- the honest Phase 5 move is to make symbol choice, skip behavior, the one-word private timestamp record, duration bookkeeping, the fixed `maxactive` budget, and the `nmissed` summary reviewable in memory while leaving probe registration and module plumbing out of scope.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/kretprobe_example.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `KretprobeExampleSample.descriptor()`
- it models only the default symbol name, a pre-init retarget hook, kernel-thread skip behavior, a single per-instance timestamp record, return-duration replay, the Linux `maxactive = 20` budget, and a bounded `nmissed` summary in memory
- it uses a tiny `init()` -> `entryHandler()` -> `retHandler()` -> `recordMissedInstance()` -> `exit()` lifecycle so ownership and teardown stay explicit
- it provides one bounded self-check through `runAnchorReplay()` instead of implying a runtime-ready kretprobe implementation

The exact checks currently recorded in `zigux/tests/phase5_kretprobe_example_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the in-memory sample keeps `kernel_clone` as the default symbol name while allowing pre-init retargeting
- `runAnchorReplay()` checks that an entry with no `current->mm` is skipped instead of arming a tracked instance
- the in-memory sample keeps a single private entry-timestamp record so the Linux `struct my_data` anchor shape stays explicit as one `i64`-sized word
- the replay records return value `42` and duration `75 ns` after an entry timestamp of `100` and a return timestamp of `175`
- the in-memory sample keeps the Linux `maxactive` budget explicit at `20` concurrent instances even though this Phase 5 slice does not model registration-pressure handling
- the replay records one missed instance so the exit-side `nmissed` summary stays reviewable without claiming registration-pressure parity
- `exit()` rejects an armed sample until `retHandler()` clears the outstanding tracked instance
- after `exit()` the sample rejects later `recordMissedInstance()`, `entryHandler()`, or `retHandler()` calls

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/kretprobe_example.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `KretprobeExampleSample.descriptor()` still name `samples/kprobes/kretprobe_example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_kretprobe_example_manifest.json` and `zigux/tests/phase5_kretprobe_example_survey.zig` still describe the exact skip, private-data, return-value, duration, fixed `maxactive`, and missed-summary contract run through `zigux/tests/phase5_build.zig`?
- does `zigux/tests/phase5_kretprobe_example_manifest.json` still pin the exact surveyed commit for the inspected `master` head instead of a floating branch label?
- does the sample-backed survey note, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md` still keep this landed Phase 5 kretprobe slice distinct from the separate Phase 9 runtime starter while pointing reviewers at the shared `phase5_build.zig` entrypoint?
- does the sample keep the Linux `maxactive = 20` budget explicit as a reviewable in-memory ceiling instead of silently drifting away from the anchor or implying runtime tuning support?
- does symbol retargeting stay a pre-init in-memory choice instead of implying `module_param` or runtime registration parity?
- if the sample behavior changes, is the manifest updated alongside the replay and teardown contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that `register_kretprobe()`, `unregister_kretprobe()`, `pt_regs` return extraction, and loadable module wiring remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The current gap is no longer "Zigux has no kretprobe sample guidance." The more precise state is:

- the repo now has a reviewable Phase 5 `kretprobe_example` sample plus manifest-backed checks for symbol choice, skip behavior, private-data shape, return timing, fixed `maxactive`, summary recording, and teardown
- this sample must remain visibly separate from the later Phase 9 runtime `kretprobe` starter so contributors do not over-claim runtime substrate coverage
- the Phase 5 roadmap's four named sample anchors are now all represented by bounded `samples/zigux/` reference readings, but that does not close the separate Phase 9 runtime pilot tranche

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux kretprobe example
   - `rg -n "samples/kprobes/kretprobe_example.c|Phase 5" Documentation/zigux samples /workspace/agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP\ \(1\).md`
2. confirm the current `samples/zigux/` surface keeps the Phase 5 and Phase 9 kretprobe lanes distinct
   - `find samples/zigux -maxdepth 1 -type f | sort | rg "kretprobe|runtime_kretprobe"`
3. run the exact bounded Phase 5 sample checks
   - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`

## Non-goals

This survey does not yet claim:

- `register_kretprobe()` parity
- `unregister_kretprobe()` parity
- `pt_regs` or `regs_return_value()` parity
- loadable module wiring

## Next bounded step

Stay in the Phase 5 samples-and-reference-patterns lane and tighten contributor guidance or one exact replay check only if fresh repo inspection shows a real sample drift on current `master`, while keeping this landed Phase 5 sample distinct from the separate Phase 9 runtime starter.
