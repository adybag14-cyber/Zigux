# Phase 5 Kfifo Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_LANE_KEY=P5-L01`
- `PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea`
- `PHASE5_SLICE=kfifo-reference-sample-starter`
- scope: roadmap-vs-repo sample delivery, approved reference-sample idiom guidance, and exact bounded checks for the first `samples/zigux/` kfifo-style replay
- product boundary:
  - `Documentation/zigux/phase5-kfifo-sample-survey.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/bytestream_fifo.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_bytestream_fifo.zig`
  - `zigux/tests/phase5_bytestream_fifo_manifest.json`
  - `zigux/tests/phase5_bytestream_fifo_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the four Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection now shows that `samples/zigux/` carries four bounded Phase 5 reference samples plus several later runtime-oriented starters and loader-side follow-ons:

- `bytestream_fifo.zig`
- `kobject_example.zig`
- `kretprobe_example.zig`
- `trace_events_sample.zig`
- `runtime_atomic64.zig`
- `runtime_atomic64_loader.zig`
- `runtime_bitmap.zig`
- `runtime_bitmap_loader.zig`
- `runtime_kretprobe.zig`
- `runtime_kretprobe_loader.zig`
- `runtime_trace_events.zig`
- `runtime_trace_events_loader.zig`

The Phase 5 gap is now narrowed to one landed sample-backed reference pattern for the `kfifo` anchor. The remaining work is to keep its exact checks and non-goals visible while the full four-anchor Phase 5 reference sample set stays visibly separate from the later runtime-oriented starters and their loader-side follow-ons.

## Survey findings

- `samples/kfifo/bytestream-example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a subsystem slice.
- the Linux sample mixes three concerns:
  - bounded in-memory FIFO behavior such as `kfifo_in`, `kfifo_out`, `kfifo_put`, `kfifo_get`, `kfifo_skip`, and `kfifo_peek`
  - lifecycle setup and teardown around `example_init()` and `example_exit()`
  - procfs and user-copy plumbing through `proc_create`, `kfifo_from_user`, `kfifo_to_user`, and mutex-protected read or write paths
- the live Zigux repo now ships bounded Phase 5 side-by-side samples under `samples/zigux/` for the `kfifo`, `kobject`, `kretprobe`, and `trace-events` anchors, while still keeping the later Phase 9 runtime starters and loader-side follow-ons separate from these non-runtime reference readings.
- the live shared contributor packet for this landed sample is broader than the sample file and its paired manifest alone: `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` already help keep this FIFO note aligned with the same four-sample Phase 5 packet described from the docs root, scripts root, sample root, and tests root.
- the generic review checklist already covers the Phase 5 boundary between a reviewable idiom and a runtime-ready module, but contributors still benefit from one sample-backed set of prompts tied directly to the shipped bytestream FIFO slice.

## Approved idiom for the landed kfifo-style sample

Until a bounded runtime substrate exists, the landed Phase 5 `samples/zigux/` reference sample for this anchor should:

- model FIFO state and ordered operations entirely in memory
- keep the Linux anchor path explicit in a descriptor or note
- include a tiny self-check or fixture-backed replay for the queue-order expectations that make the sample useful to reviewers
- show ownership and lifetime boundaries clearly, especially initialization, reset, and teardown
- keep procfs, user-copy, blocking lock behavior, and module-registration claims out of scope unless a later lane lands the required substrate first

In practice, the approved Phase 5 in-memory FIFO idiom is a side-by-side behavior sample, not a claim that Zigux already has `proc_create()`, `kfifo_from_user()`, or module-load parity.

## Landed sample and exact checks

The repo now carries that first bounded sample in `samples/zigux/bytestream_fifo.zig`.

The sample intentionally stays small:

- it models only bounded in-memory FIFO state with a fixed 32-byte ring buffer
- it replays the Linux anchor's queue-order behavior without any procfs or user-copy substrate
- it now makes ownership and lifetime explicit through a tiny `init()` -> `runAnchorReplay()` -> `exit()` flow instead of implying a runtime-ready module lifecycle
- it now records one non-destructive snapshot of the filled queue before the final drain so reviewers can confirm the exact anchor sequence without inferring hidden mutation
- it now exposes a tiny `runPreviewBoundaryReplay()` check so reviewers can see preview truncation stay non-destructive before the full drain
- it exposes a single bounded self-check that resets state, replays the bytestream example, and returns the exact observations that reviewers should care about

The exact checks currently recorded in `zigux/tests/phase5_bytestream_fifo_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the queue length is `15` after enqueueing "hello" and bytes `0` through `9`
- the first drain returns "hello"
- the second drain returns bytes `0` and `1`, and those same bytes are re-enqueued at the tail
- skipping the next byte removes `2`
- peeking afterward observes `3` without draining it
- the fill loop succeeds for bytes `20` through `42` inclusive and then stops at the bounded capacity
- `runPreviewBoundaryReplay()` proves a truncated preview stays non-destructive: `snapshotInto()` still begins with `[2,3,4,5]`, `previewInto()` copies `[2,3,4,5,6,7,8,9]`, reports `10` visible bytes, and leaves the queued data intact
- `snapshotInto()` captures the exact 32-byte Linux anchor sequence `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]` before the final drain without mutating queue state
- the final drain yields the exact 32-byte Linux anchor sequence `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
- empty-queue peek and skip return `null`, pushing past capacity returns `false`, and `reset()` restores an empty queue
- draining a three-byte destination from the queued string `"hello"` yields `"hel"`, leaves the remaining prefix `"lo"` queued in order, and a follow-up drain on the now-empty queue returns `0`
- the sample starts in a cold state, requires `init()` before replay, records `replay_complete` after the self-check, and `exit()` returns it to an empty bounded state

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/bytestream_fifo.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `BytestreamFifoSample.descriptor()` still name the Linux anchor `samples/kfifo/bytestream-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` still describe the exact queue-order replay, preview truncation boundary, the non-destructive snapshot contract, lifecycle boundary, and bounded helper contract run through `zigux/tests/phase5_build.zig`?
- do the shared Phase 5 contributor surfaces in `Documentation/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still point at this exact sample packet and keep it separate from the later Phase 9 runtime starters instead of leaving this note to carry the boundary alone?
- do the shared Phase 5 packet and this sample note still say clearly that there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample, so direct bitmap helper reviewability stays under `tools/lib/bitmap.zig`, `Documentation/zigux/phase1-closure.md`, and `Documentation/zigux/phase4-validation-matrix.md` while the separate Phase 9 runtime bitmap family stays under `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/kernel/runtime_loader_contract.zig`, and `zigux/tests/phase9_build.zig` instead of being misread as a fifth Phase 5 sample?
- does that same helper-facing packet still keep the short-drain bytestream contract explicit so draining a three-byte destination from `"hello"` yields `"hel"`, preserves the `"lo"` remainder in queue order, and returns `0` once the queue is empty again?
- if the sample behavior changes, is the manifest updated alongside the replay expectations instead of leaving reviewers to infer the new contract from code alone?
- do the docs and tests still say clearly that procfs, user-copy, locking, and runtime registration remain out of scope for this Phase 5 sample?

These prompts are intentionally sample-backed rather than generic. They tie review back to the concrete sample behavior test, descriptor, manifest, and build entrypoint that current `master` already ships.

## Recorded gap vs roadmap

The current gap is not "Zigux lacks every sample." The more precise gap is:

- the repo now has four reviewable Phase 5 samples plus later runtime-oriented starters and loader-side follow-ons in `samples/zigux/`
- the completed Phase 5 sample set still has to stay visibly separate from the later Phase 9 runtime starters and loader-side follow-ons for `trace-events`, `kretprobe`, `bitmap`, and `atomic64`
- the shared docs-root, sample-root, scripts-root, and tests-root contributor packet should stay explicit here too, so this survey note does not understate the already-shipped review surface for the landed sample
- the kfifo sample now covers both queue-order replay and one explicit ownership-lifetime path, but it still intentionally does not claim procfs, user-copy, locking, or module registration support

This slice closes the `kfifo` survey-only gap by landing the first sample-backed replay and documenting its exact checks so future Phase 5 work can advance from a concrete baseline instead of another round of ambiguous sample naming.

## Latest verification snapshot

A focused current-`master` replay was re-run on 2026-05-05 with the attached Zig toolchain `0.17.0-dev.87+9b177a7d2`.

- `zig fmt --check` passed for the current `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and the shared repo-local `zigux/tests/phase5_build.zig` entrypoint for the shipped Phase 5 sample packet
- `zig test samples/zigux/bytestream_fifo.zig` passed `5/5` sample self-checks
- a focused scratch replay assembled from the current `master` versions of `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `zigux/tests/phase5_bytestream_fifo_manifest.json` passed `5/5` build steps and `8/8` tests via `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
- the observed sample markers matched the manifest-backed contract exactly: `len_after_initial_fill = 15`, `first_out = "hello"`, `second_out = {0, 1}`, `skipped_byte = 2`, `peek_value = 3`, `fill_start = 20`, `fill_end = 42`, `snapshot_len = 32`, `snapshot_sequence stayed [3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`, `final_len = 32`, and the final drain sequence stayed `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
- the preview-boundary replay also held: `runPreviewBoundaryReplay()` kept `snapshot_prefix = {2, 3, 4, 5}`, `preview_prefix = {2, 3, 4, 5, 6, 7, 8, 9}`, reported `preview_total_visible = 10`, and left `queue_len_after_preview = 10`
- the helper-boundary replay also held: empty peek and skip returned `null`, empty enqueue copied `0` bytes, overflow push was rejected at the 32-byte capacity, skip-at-capacity returned `0`, reset restored an empty queue, pop-after-reset returned `null`, and the helper-facing short-drain replay still produced `"hel"`, preserved the `"lo"` remainder, and returned `0` on the empty follow-up drain
- the ownership-and-lifetime replay also held: the sample still moved `cold -> initialized -> replay_complete -> exited`, rejected replay before `init()`, rejected duplicate `init()`, and rejected `exit()` after teardown

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux bytestream example
- `rg -n "samples/kfifo/bytestream-example.c|PHASE5_LANE_KEY=P5-L01|PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea|Phase 5" Documentation/zigux samples zigux/tests`

2. confirm the current `samples/zigux/` surface stays distinct from this reference-sample lane
- `find samples/zigux -maxdepth 1 -type f | sort`

3. run the exact bounded Phase 5 sample checks
- `zig build test --build-file zigux/tests/phase5_build.zig --summary all`

## Non-goals

This survey does not yet claim:

- procfs parity
- `kfifo_from_user()` or `kfifo_to_user()` parity
- loadable-module wiring or runtime registration support
- lock-contention or blocking semantics

## Next bounded step

Stay in the Phase 5 samples-and-reference-patterns lane and tighten contributor guidance or one exact replay check only if fresh repo inspection shows a real sample drift on current `master`, while keeping the landed Phase 5 sample set distinct from the later Phase 9 runtime starters and their loader-side follow-ons.