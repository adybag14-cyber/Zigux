# Phase 5 Kfifo Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

- `PHASE5_STATUS=active`
- `PHASE5_SLICE=kfifo-reference-sample-starter`
- scope: roadmap-vs-repo sample delivery, approved reference-sample idiom guidance, and exact bounded checks for the first `samples/zigux/` kfifo-style replay
- product boundary:
  - `Documentation/zigux/phase5-kfifo-sample-survey.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/bytestream_fifo.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_bytestream_fifo.zig`
  - `zigux/tests/phase5_bytestream_fifo_manifest.json`
  - `zigux/tests/phase5_bytestream_fifo_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the four Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection now shows that `samples/zigux/` carries all four roadmap-approved bounded Phase 5 reference samples plus several later runtime-oriented starters:

- `bytestream_fifo.zig`
- `kobject_example.zig`
- `kretprobe_example.zig`
- `trace_events_sample.zig`
- `runtime_atomic64.zig`
- `runtime_bitmap.zig`
- `runtime_kretprobe.zig`
- `runtime_trace_events.zig`

The `kfifo`-specific gap is no longer missing sample delivery. The remaining work in this lane is to keep the approved idiom, exact checks, and non-goals honest now that the full Phase 5 anchor set is landed, especially where later Phase 9 runtime pilots exist under neighboring Linux sample families.

## Survey findings

- `samples/kfifo/bytestream-example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a subsystem slice.
- the Linux sample mixes three concerns:
  - bounded in-memory FIFO behavior such as `kfifo_in`, `kfifo_out`, `kfifo_put`, `kfifo_get`, `kfifo_skip`, and `kfifo_peek`
  - lifecycle setup and teardown around `example_init()` and `example_exit()`
  - procfs and user-copy plumbing through `proc_create`, `kfifo_from_user`, `kfifo_to_user`, and mutex-protected read or write paths
- the live Zigux repo now ships bounded Phase 5 side-by-side samples under `samples/zigux/` for the `kfifo`, `kobject`, `kretprobe`, and `trace-events` anchors, while still keeping the later Phase 9 runtime starters separate from these non-runtime reference readings.
- the generic review checklist already covers the Phase 5 boundary between a reviewable idiom and a runtime-ready module, but contributors still benefit from one sample-backed set of prompts tied directly to the shipped bytestream FIFO slice.

## Approved idiom for the landed kfifo-style sample

For the already-landed Phase 5 `samples/zigux/bytestream_fifo.zig` slice, the approved idiom remains:

- model FIFO state and ordered operations entirely in memory
- keep the Linux anchor path explicit in a descriptor or note
- include a tiny self-check or fixture-backed replay for the queue-order expectations that make the sample useful to reviewers
- show ownership and lifetime boundaries clearly, especially initialization, reset, and teardown
- keep procfs, user-copy, blocking lock behavior, and module-registration claims out of scope unless a later lane lands the required substrate first

In practice, that means the approved first idiom is a side-by-side behavior sample, not a claim that Zigux already has `proc_create()`, `kfifo_from_user()`, or module-load parity.

## Landed sample and exact checks

The repo now carries that first bounded sample in `samples/zigux/bytestream_fifo.zig`.

The sample intentionally stays small:

- it models only bounded in-memory FIFO state with a fixed 32-byte ring buffer
- it replays the Linux anchor's queue-order behavior without any procfs or user-copy substrate
- it now makes ownership and lifetime explicit through a tiny `init()` -> `runAnchorReplay()` -> `exit()` flow instead of implying a runtime-ready module lifecycle
- it now exposes a non-destructive `snapshotInto()` helper so reviewers can inspect queue order without consuming the sample state
- it exposes a single bounded self-check that resets state, replays the bytestream example, and returns the exact observations that reviewers should care about

The exact checks currently recorded in `zigux/tests/phase5_bytestream_fifo_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the queue length is `15` after enqueueing "hello" and bytes `0` through `9`
- the first drain returns "hello"
- the second drain returns bytes `0` and `1`, and those same bytes are re-enqueued at the tail
- skipping the next byte removes `2`
- peeking afterward observes `3` without draining it
- a non-destructive snapshot before the final drain preserves the exact 32-byte Linux anchor sequence `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
- the fill loop succeeds for bytes `20` through `42` inclusive and then stops at the bounded capacity
- the final drain yields the exact 32-byte Linux anchor sequence `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
- empty-queue peek and skip return `null`, `snapshotInto()` leaves queue order intact, pushing past capacity returns `false`, and `reset()` restores an empty queue
- the replay advertises exactly six review-focus areas: `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `reset_and_replay`, and `ownership_and_lifetime`
- the sample starts in a cold state, requires `init()` before replay, records `replay_complete` after the self-check, and `exit()` returns it to an empty bounded state
- `runAnchorReplay()` fails before `init()` and after `exit()`, `init()` fails if repeated outside the cold state, `exit()` fails if repeated after teardown, and one successful pass leaves `init_runs = 1` plus `exit_runs = 1`

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/bytestream_fifo.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `BytestreamFifoSample.descriptor()` still name the Linux anchor `samples/kfifo/bytestream-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_bytestream_fifo_manifest.json` and `zigux/tests/phase5_bytestream_fifo_survey.zig` still record the exact queue-order replay, non-destructive snapshot, and bounded helper checks that `zigux/tests/phase5_build.zig` runs?
- if the sample behavior changes, is the manifest updated alongside the replay expectations instead of leaving reviewers to infer the new contract from code alone?
- do the docs and tests still say clearly that procfs, user-copy, locking, and runtime registration remain out of scope for this Phase 5 sample?

These prompts are intentionally sample-backed rather than generic. They tie review back to the concrete descriptor, manifest, and build entrypoint that current `master` already ships.

## Recorded gap vs roadmap

The current gap is not missing Phase 5 sample delivery for `kfifo`. The more precise gap is:

- all four roadmap anchors now have bounded non-runtime `samples/zigux/` reference samples on current `master`
- the canonical `kfifo` survey still has to say that plainly so reviewers do not mistake this slice for an unfinished anchor or confuse it with the separate later Phase 9 runtime pilots
- the landed bytestream FIFO sample still intentionally does not claim procfs, user-copy, locking, or module registration support

This slice now keeps the `kfifo` survey aligned with the live Phase 5 sample set and the roadmap-approved boundary for the shipped bytestream FIFO replay, so future work can leave this lane parked unless a real same-family drift appears.

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux bytestream example
- `rg -n "samples/kfifo/bytestream-example.c|Phase 5" Documentation/zigux samples /workspace/agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP\ \(1\).md`

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

Leave this narrow `kfifo` survey lane parked unless fresh repo inspection shows one more same-family drift in the approved idiom, contributor prompts, or roadmap-gap wording for the already-landed bytestream FIFO sample.
