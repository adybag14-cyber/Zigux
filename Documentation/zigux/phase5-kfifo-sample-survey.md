# Phase 5 Kfifo Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

* `PHASE5_STATUS=parked`
* `PHASE5_LANE_KEY=P5-L01`
* `PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea`
* `PHASE5_SLICE=kfifo-reference-sample-starter`
* scope: roadmap-vs-repo sample delivery, approved reference-sample idiom guidance, and exact bounded checks for the shipped `samples/zigux/bytestream_fifo.zig` replay
* product boundary:
  * `Documentation/zigux/phase5-kfifo-sample-survey.md`
  * `Documentation/zigux/phase5-sample-review-guide.md`
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `samples/zigux/README.md`
  * `scripts/zigux/README.md`
  * `zigux/tests/README.md`
  * `.github/workflows/zigux-bootstrap.yml`
  * `samples/zigux/bytestream_fifo.zig`
  * `zigux/tests/phase5_build.zig`
  * `zigux/tests/phase5_bytestream_fifo.zig`
  * `zigux/tests/phase5_bytestream_fifo_manifest.json`
  * `zigux/tests/phase5_bytestream_fifo_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the four Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection now shows that `samples/zigux/` carries four bounded Phase 5 reference samples plus several later runtime-oriented starters, loader-side follow-ons, and one focused bitmap companion replay:

* `bytestream_fifo.zig`
* `kobject_example.zig`
* `kretprobe_example.zig`
* `trace_events_sample.zig`
* `runtime_atomic64.zig`
* `runtime_atomic64_loader.zig`
* `runtime_bitmap.zig`
* `runtime_bitmap_loader.zig`
* `runtime_bitmap_top_bit_contract.zig`
* `runtime_kretprobe.zig`
* `runtime_kretprobe_loader.zig`
* `runtime_trace_events.zig`
* `runtime_trace_events_loader.zig`

For the `kfifo` anchor, current `master` already ships the roadmap-backed side-by-side sample port. The remaining same-lane work is to keep its exact checks, approved in-memory idiom, and non-goals visible while the full four-anchor Phase 5 reference sample set stays visibly separate from the later runtime-oriented starters, loader-side follow-ons, and the focused runtime bitmap companion replay.

## Survey findings

* `samples/kfifo/bytestream-example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a subsystem slice.
* the Linux sample mixes three concerns:
  * bounded in-memory FIFO behavior such as `kfifo_in`, `kfifo_out`, `kfifo_put`, `kfifo_get`, `kfifo_skip`, and `kfifo_peek`
  * lifecycle setup and teardown around `example_init()` and `example_exit()`
  * procfs and user-copy plumbing through `proc_create`, `kfifo_from_user`, `kfifo_to_user`, and mutex-protected read or write paths
* the live Zigux repo now ships bounded Phase 5 side-by-side samples under `samples/zigux/` for the `kfifo`, `kobject`, `kretprobe`, and `trace-events` anchors, while still keeping the later Phase 9 runtime starters, loader-side follow-ons, and focused `runtime_bitmap_top_bit_contract.zig` companion replay separate from these non-runtime reference readings.
* the live shared contributor packet for this landed sample is broader than the sample file and its paired manifest alone: `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `.github/workflows/zigux-bootstrap.yml` already help keep this FIFO note aligned with the same four-sample Phase 5 packet described from the docs root, shared guide, checklist, sample root, scripts root, tests root, and workflow surface.
* the generic review checklist already covers the Phase 5 boundary between a reviewable idiom and a runtime-ready module, but contributors still benefit from one sample-backed set of prompts tied directly to the shipped bytestream FIFO slice and its sample-owned review packet.

## Approved idiom for the landed bytestream FIFO sample

Until a bounded runtime substrate exists, the landed Phase 5 `samples/zigux/` reference sample for this anchor should:

* model FIFO state and ordered operations entirely in memory
* keep the storage backing explicit as an embedded fixed-buffer ring, so the approved idiom stays reviewable as a bounded sample instead of drifting toward an implicit allocation or runtime-substrate claim
* keep the Linux anchor path explicit in a descriptor or note
* keep both the tiny sample-local self-check and the shared manifest-backed replay route explicit, so the same approved idiom stays reviewable in the sample file and repeatable through the shipped Phase 5 packet instead of leaving contributors to infer one route from the other
* show ownership and lifetime boundaries clearly, especially initialization, reset, and teardown
* keep preview and snapshot cues explicit too, so truncated reads and full-sequence inspection stay reviewable as part of the bounded ring idiom instead of being left implicit inside helper internals
* keep procfs, user-copy, blocking lock behavior, and module-registration claims out of scope unless a later lane lands the required substrate first

In practice, the approved Phase 5 in-memory FIFO idiom is a side-by-side behavior sample, not a claim that Zigux already has `proc_create()`, `kfifo_from_user()`, or module-load parity.

## Landed sample and exact checks

The repo now carries that first bounded sample in `samples/zigux/bytestream_fifo.zig`.

The sample intentionally stays bounded in scope:

* it models only bounded in-memory FIFO state with a fixed 32-byte ring buffer
* it keeps `StorageBacking.embedded_fixed_buffer` explicit, making the roadmap-backed idiom a fixed in-memory ring rather than an allocation-backed or substrate-dependent queue claim
* it replays the Linux anchor's queue-order behavior without any procfs or user-copy substrate
* it now makes ownership and lifetime explicit through a tiny `init()` -> `runAnchorReplay()` -> `exit()` flow instead of implying a runtime-ready module lifecycle
* it now keeps `previewInto()` explicit so reviewers can see preview truncation stay non-destructive before the final drain
* it now keeps `snapshotInto()` explicit so reviewers can inspect the full queued anchor sequence before draining it
* it now keeps helper boundaries explicit through empty-queue, overflow, short-drain, full-preview, and reset checks instead of leaving those edges implicit
* it exposes a single bounded self-check that resets state, replays the bytestream example, and returns the exact observations that reviewers should care about

The exact checks currently recorded in `zigux/tests/phase5_bytestream_fifo_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

* the queue length is `15` after enqueueing "hello" and bytes `0` through `9`
* the first drain returns "hello"
* the second drain returns bytes `0` and `1`, and those same bytes are re-enqueued at the tail
* the Linux-style transfer counts stay explicit too: initial string copy count is `5`, first drain count is `5`, second drain count is `2`, and requeue count is `2`
* skipping the next byte removes `2`
* peeking afterward observes `3` without draining it
* the fill loop succeeds for bytes `20` through `42` inclusive and then stops at the bounded capacity
* `previewInto()` copies the first eight queued bytes `[3,4,5,6,7,8,9,0]`, reports `32` visible bytes, marks the preview as truncated, and leaves the queued data intact
* `snapshotInto()` captures the exact 32-byte Linux anchor sequence `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]` before the final drain without mutating queue state
* the final drain yields the exact 32-byte Linux anchor sequence `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
* empty-queue peek and skip return `null`, empty enqueue copies `0` bytes, an empty preview reports `0` visible bytes without mutating the destination buffer, pushing past capacity returns `false`, and a full-capacity preview copies all `32` visible bytes without truncation
* draining a three-byte destination from the queued string `"hello"` yields `"hel"`, leaves the remaining prefix `"lo"` queued in order, and a follow-up drain on the now-empty queue returns `0`
* `reset()` clears queue state without rewinding lifecycle bookkeeping at the initialized, replay-complete, and exited boundaries
* the sample starts in a cold state, requires `init()` before replay, records `replay_complete` after the self-check, and `exit()` returns it to an empty bounded state

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/bytestream_fifo.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

Shared no-extra-sample reminders for `bitmap`, `string`, `cmdline`, `argv_split`, and `rbtree` live in `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `samples/zigux/README.md`. This sample-local prompt list stays focused on the bytestream FIFO packet itself.

* does `BytestreamFifoSample.descriptor()` still name the Linux anchor `samples/kfifo/bytestream-example.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
* does the same sample packet still keep `StorageBacking.embedded_fixed_buffer` explicit so reviewers can read the approved idiom as a bounded fixed-buffer ring instead of an implied allocation-backed runtime queue?
* does `BytestreamFifoSample.reviewContract().focus` still keep the sample-owned cue order explicit for `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `remaining_capacity`, `queue_shape_boundaries`, `helper_boundaries`, `reset_and_replay`, and `ownership_and_lifetime`, with `zigux/tests/phase5_bytestream_fifo.zig` still exact-checking that same order?
* do `previewInto()`, `snapshotInto()`, the short-drain `"hel"` plus queued `"lo"` helper boundary, and the reset-bookkeeping checks still stay aligned across `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` through `zigux/tests/phase5_build.zig` instead of leaving reviewers to infer the bounded packet from only one surface?
* does that same lifecycle packet still keep the bounded `init()` -> `runAnchorReplay()` -> `exit()` path and the `cold -> initialized -> replay_complete -> exited` ownership boundary visible instead of leaving lifetime review to the shared tests alone?
* do the shared Phase 5 contributor surfaces still keep this exact bytestream FIFO packet aligned with `zig build test --build-file zigux/tests/phase5_build.zig --summary all`, `make -C zigux phase5-test`, and `make -C zigux phase5`, while the direct `zig test samples/zigux/bytestream_fifo.zig` replay remains a sample-local focused check and `.github/workflows/zigux-bootstrap.yml` stays honest about rerunning only the direct `zig build test --build-file zigux/tests/phase5_build.zig --summary all` command instead of the local `make` wrappers?
* does that same approved in-memory FIFO idiom still keep its preview and snapshot evidence explicit so `previewInto()` stays non-destructive, `snapshotInto()` preserves the full anchor order for review, and the bounded overflow or reset edges remain visible from the same sample-backed packet?
* do `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still point at this exact sample packet and keep it separate from the later Phase 9 runtime starters, loader-side follow-ons, and focused bitmap companion replay instead of leaving this note to carry the boundary alone?
* does that same helper-facing packet still keep the bounded helper contract explicit so empty-queue peek and skip return `null`, empty enqueue copies `0` bytes, an empty preview reports `0` visible bytes without mutating its destination buffer, overflow push is rejected at the 32-byte capacity, a full-capacity preview copies all `32` visible bytes without truncation, draining a three-byte destination from `"hello"` yields `"hel"`, preserves the `"lo"` remainder in queue order, and `reset()` clears queue state without rewinding lifecycle bookkeeping?
* if the sample behavior changes, is the manifest updated alongside the replay expectations instead of leaving reviewers to infer the new contract from code alone?
* do the docs and tests still say clearly that procfs, user-copy, locking, and runtime registration remain out of scope for this Phase 5 sample?

These prompts are intentionally sample-backed rather than generic. They tie review back to the concrete sample behavior test, descriptor, manifest, and build entrypoint that current `master` already ships.

## Recorded gap vs roadmap

The current gap is not "Zigux lacks every sample." The more precise gap is:

* the repo now has four reviewable Phase 5 samples plus later runtime-oriented starters, loader-side follow-ons, and the focused `runtime_bitmap_top_bit_contract.zig` companion replay in `samples/zigux/`
* the completed Phase 5 sample set still has to stay visibly separate from the later Phase 9 runtime starters, loader-side follow-ons, and the focused runtime bitmap companion replay for `trace-events`, `kretprobe`, `bitmap`, and `atomic64`
* the shared docs-root, checklist, Phase 5 guide, sample-root, scripts-root, tests-root, and workflow contributor packet should stay explicit here too, so this survey note does not understate the already-shipped review surface for the landed sample
* the approved kfifo idiom should keep the embedded fixed-buffer storage cue and both repeatability routes explicit in the survey note too, so reviewers can see the sample-local self-check and the shared manifest-backed replay as one roadmap-backed contract instead of inferring one route from the other
* the kfifo sample now covers queue-order replay, preview truncation, full snapshot inspection, helper-boundary edge checks, and one ownership-lifetime path, but it still intentionally does not claim procfs, user-copy, locking, or module registration support

This slice now documents the already-landed `kfifo` side-by-side sample port against the roadmap's approved-idiom goal and keeps its exact checks visible so future Phase 5 work advances from a concrete baseline instead of drifting back into ambiguous sample naming or runtime-substrate claims.

## Latest verification snapshot

A focused replay for the recorded `PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea` packet was re-run on 2026-05-05 with the attached Zig toolchain `0.17.0-dev.87+9b177a7d2`.

This snapshot is commit-pinned to `PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea`; newer unrelated `master` commits should not be read as automatically re-verified unless this note, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` move together.

* `zig fmt --check` passed for the surveyed `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and the shared repo-local `zigux/tests/phase5_build.zig` entrypoint for the shipped Phase 5 sample packet
* `zig test samples/zigux/bytestream_fifo.zig` passed `4/4` sample self-checks
* a focused scratch replay assembled from the surveyed `samples/zigux/bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `zigux/tests/phase5_bytestream_fifo_manifest.json` packet still passed the shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` route for the bytestream packet from a runnable scratch checkout, without relying on a brittle aggregate build-step or test count that can drift as the wider Phase 5 suite grows
* the observed sample markers matched the manifest-backed contract exactly: `initial_string_copy_count = 5`, `first_drain_count = 5`, `second_drain_count = 2`, `requeue_count = 2`, `len_after_initial_fill = 15`, `first_out = "hello"`, `second_out = {0, 1}`, `skipped_byte = 2`, `peek_value = 3`, `fill_start = 20`, `fill_end = 42`, `preview_len = 8`, `preview_total_visible = 32`, `preview_truncated = true`, `snapshot_len = 32`, `snapshot_sequence stayed [3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`, `final_len = 32`, and the final drain sequence stayed `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
* the preview replay also held: `previewInto()` kept `preview_prefix = {3, 4, 5, 6, 7, 8, 9, 0}`, reported `preview_total_visible = 32`, marked the view truncated, and left the queued data intact for `snapshotInto()` and the final drain
* the helper-boundary replay also held: empty peek and skip returned `null`, empty enqueue copied `0` bytes, empty preview reported `0` visible bytes without mutating its destination bytes, overflow push was rejected at the 32-byte capacity, a full-capacity preview copied all `32` visible bytes without truncation, the short-drain replay still produced `"hel"`, preserved the `"lo"` remainder, and `reset()` continued to clear queue state without rewinding lifecycle bookkeeping
* the ownership-and-lifetime replay also held: the sample still moved `cold -> initialized -> replay_complete -> exited`, rejected replay before `init()`, rejected duplicate `init()`, and rejected `exit()` after teardown

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux bytestream example

* `rg -n "samples/kfifo/bytestream-example.c|PHASE5_LANE_KEY=P5-L01|PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea|Phase 5" Documentation/zigux samples zigux/tests`

2. confirm the current `samples/zigux/` surface stays distinct from this reference-sample lane

* `find samples/zigux -maxdepth 1 -type f | sort`

3. run the exact bounded Phase 5 sample checks

* `zig test samples/zigux/bytestream_fifo.zig`
* `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
* `make -C zigux phase5-test`
* `make -C zigux phase5`

## Non-goals

This survey does not yet claim:

* procfs parity
* `kfifo_from_user()` or `kfifo_to_user()` parity
* loadable-module wiring or runtime registration support
* lock-contention or blocking semantics

## Next bounded step

Stay in the Phase 5 samples-and-reference-patterns lane and tighten contributor guidance or one exact replay check only if fresh repo inspection shows a real sample drift on current `master`, while keeping the landed Phase 5 sample set distinct from the later Phase 9 runtime starters, their loader-side follow-ons, and the focused runtime bitmap companion replay, and keeping the shared guide, note, manifest, checklist, and shared replay route aligned.