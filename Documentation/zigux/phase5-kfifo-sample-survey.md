# Phase 5 Kfifo Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

* `PHASE5_STATUS=parked`
* `PHASE5_LANE_KEY=P5-L01`
* `PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea`
* `PHASE5_SLICE=kfifo-reference-sample-starter`
* scope: roadmap-vs-repo sample delivery, approved reference-sample idiom guidance, exact bounded checks for the shipped `samples/zigux/bytestream_fifo.zig` replay, and current shared-packet truthfulness around the restored four-file sample-root packet plus the directly readable bytestream survey companion
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

Fresh repo inspection now shows that current `master` keeps the directly readable non-runtime Phase 5 packet aligned with the full approved four-anchor set:

* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_sample.zig`

The kobject anchor still belongs to that same approved four-anchor Phase 5 set, and current `master` now keeps it reviewable through the directly readable sample-root file plus its paired survey-and-tests packet:

* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `samples/zigux/kobject_example.zig`
* `zigux/tests/phase5_build.zig`
* `zigux/tests/phase5_kobject_example.zig`
* `zigux/tests/phase5_kobject_example_manifest.json`
* `zigux/tests/phase5_kobject_example_survey.zig`

Current `master` also keeps the later runtime-oriented family separate from these non-runtime reference samples and their loader-side follow-ons:

* `samples/zigux/runtime_atomic64.zig`
* `samples/zigux/runtime_atomic64_loader.zig`
* `samples/zigux/runtime_bitmap.zig`
* `samples/zigux/runtime_bitmap_loader.zig`
* `samples/zigux/runtime_kretprobe.zig`
* `samples/zigux/runtime_kretprobe_loader.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_loader.zig`

For the `kfifo` anchor, current `master` already ships the roadmap-backed side-by-side sample port. The remaining same-lane job in this note is to keep its exact checks, approved in-memory idiom, and non-goals visible while keeping the bytestream packet aligned with the live four-file sample-root packet, the directly readable bytestream survey companion, the restored public-tree kobject packet, and the separate Phase 9 runtime family.

## Survey findings

* `samples/kfifo/bytestream-example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a subsystem slice.
* the Linux sample mixes three concerns:
  * bounded in-memory FIFO behavior such as `kfifo_in`, `kfifo_out`, `kfifo_put`, `kfifo_get`, `kfifo_skip`, and `kfifo_peek`
  * lifecycle setup and teardown around `example_init()` and `example_exit()`
  * procfs and user-copy plumbing through `proc_create`, `kfifo_from_user`, `kfifo_to_user`, and mutex-protected read or write paths
* the live Zigux repo ships the bytestream sample itself in `samples/zigux/bytestream_fifo.zig`, the focused replay in `zigux/tests/phase5_bytestream_fifo.zig`, the manifest in `zigux/tests/phase5_bytestream_fifo_manifest.json`, the dedicated survey companion in `zigux/tests/phase5_bytestream_fifo_survey.zig`, and the shared build route in `zigux/tests/phase5_build.zig`
* the live shared contributor packet for this landed sample is broader than the sample file and its paired manifest alone: `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `.github/workflows/zigux-bootstrap.yml` already help keep this FIFO note aligned with the same bounded Phase 5 packet described from the docs root, shared guide, checklist, sample root, scripts root, tests root, and workflow surface
* the generic review checklist already covers the Phase 5 boundary between a reviewable idiom and a runtime-ready module, but contributors still benefit from one sample-backed set of prompts tied directly to the shipped bytestream FIFO slice and its current sample-owned review packet

## Approved idiom for the landed bytestream FIFO sample

Until a bounded runtime substrate exists, the landed Phase 5 `samples/zigux/` reference sample for this anchor should:

* model FIFO state and ordered operations entirely in memory
* keep the storage backing explicit as an embedded fixed-buffer ring, so the approved Phase 5 in-memory FIFO idiom stays reviewable as a bounded sample instead of drifting toward an implicit allocation or runtime-substrate claim
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
* empty-queue peek and skip returned `null`, empty enqueue copied `0` bytes, overflow push was rejected at the 32-byte capacity, skip-at-capacity returned `0`, pop-after-reset returned `null`, and a full-capacity preview copies all `32` visible bytes without truncation
* draining a three-byte destination from the queued string `"hello"` yields `"hel"`, leaves the remaining prefix `"lo"` queued in order, and a follow-up drain on the now-empty queue returns `0`
* `reset()` clears queue state without rewinding lifecycle bookkeeping at the initialized, replay-complete, and exited boundaries
* the sample starts in a cold state, requires init before replay, records `replay_complete` after the self-check, and `exit()` returns it to an empty bounded state

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/bytestream_fifo.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

* does `BytestreamFifoSample.descriptor()` still name the Linux anchor `samples/kfifo/bytestream-example.c` and keep `requires_runtime_substrate false` plus `provides_selfcheck = true`?
* does the same sample packet still keep `StorageBacking.embedded_fixed_buffer` explicit so reviewers can read the approved Phase 5 in-memory FIFO idiom as a bounded fixed-buffer ring instead of an implied allocation-backed runtime queue?
* do `previewInto()`, `snapshotInto()`, the short-drain `"hel"` plus queued `"lo"` helper boundary, and the dedicated `zigux/tests/phase5_bytestream_fifo_survey.zig` companion still stay aligned across this note, `zigux/tests/phase5_bytestream_fifo.zig`, and `zigux/tests/phase5_bytestream_fifo_manifest.json` through `zigux/tests/phase5_build.zig` instead of leaving reviewers to infer the bounded packet from only one surface?
* does that same lifecycle packet still keep the bounded `init()` -> `runAnchorReplay()` -> `exit()` path and the `cold -> initialized -> replay_complete -> exited` ownership boundary visible instead of leaving lifetime review to the shared tests alone?
* if the sample behavior changes, is the manifest updated alongside the replay expectations and the dedicated survey companion instead of leaving reviewers to infer the new contract from code alone?
* do the docs and tests still say clearly that procfs, user-copy, locking, and runtime registration remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The current gap is not "Zigux lacks every sample." The more precise gap is:

* the repo already ships the roadmap-backed bytestream sample itself plus its focused replay, manifest, dedicated survey companion, and shared `phase5_build.zig` route
* the directly readable sample-root half of the broader non-runtime Phase 5 packet is now four files, and the approved kobject anchor stays reviewable through `samples/zigux/kobject_example.zig` plus its paired note, focused replay, manifest, dedicated survey companion, and shared build route
* the completed Phase 5 sample set still has to stay visibly separate from the later Phase 9 runtime starters, loader-side follow-ons, and focused runtime-boundary companions for `trace-events`, `kretprobe`, `bitmap`, and `atomic64`
* the approved kfifo idiom should keep the embedded fixed-buffer storage cue and both repeatability routes explicit in the survey note too, so reviewers can see the sample-local self-check, dedicated survey companion, and shared manifest-backed replay as one roadmap-backed contract instead of inferring one route from the other
* the kfifo sample now covers queue-order replay, preview truncation, full snapshot inspection, helper-boundary edge checks, and one ownership-lifetime path, but it still intentionally does not claim procfs, user-copy, locking, or module registration support

This slice therefore documents the already-landed `kfifo` side-by-side sample port against the roadmap's approved-idiom goal while keeping the bytestream note aligned with current repo reality instead of reviving the older three-file packet wording or the older missing kobject sample-root caveat.

## Latest verification snapshot

The underlying bytestream sample contract remains anchored to the last focused replay recorded for `PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea`.

That replay used Zig `0.17.0-dev.87+9b177a7d2` and recorded the same bounded behavior packet this note still describes today.

* `zig test samples/zigux/bytestream_fifo.zig` passed `5/5` sample self-checks
* `zig build test --build-file zigux/tests/phase5_build.zig --summary all` passed `5/5` build steps and `8/8` tests
* `len_after_initial_fill = 15`
* `first_out = "hello"`
* `second_out = {0, 1}`
* `skipped_byte = 2`
* `peek_value = 3`
* `fill_start = 20`
* `fill_end = 42`
* `snapshot_len = 32`
* `snapshot_sequence stayed [3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
* `final_len = 32`
* empty-queue helper proof stayed explicit too: peek and skip returned `null`, empty enqueue copied `0` bytes, overflow push was rejected at the 32-byte capacity, skip-at-capacity returned `0`, and pop-after-reset returned `null`
* lifecycle proof stayed explicit too: `cold -> initialized -> replay_complete -> exited`

This note was refreshed again on 2026-05-13 through repo-first current-`master` inspection so the review surface stays truthful about the live packet.

* current shared Phase 5 guidance already describes a restored four-file sample-root packet, and this note now matches that same repo reality instead of keeping the older three-file wording
* the same repo-first comparison confirmed that the broader shared Phase 5 contributor packet already keeps the direct sample-root packet at four files and keeps the kobject anchor on its restored public-tree packet rather than the older note-plus-tests-only caveat
* the same repo-first comparison confirmed that the later `runtime_*` family remains present and separate from the non-runtime Phase 5 reference packet
* no new local `zig` replay was run for this note-only truthfulness refresh; validation for this update stayed on current-`master` repo inspection and roadmap-to-note alignment rather than claiming a fresh end-to-end sample rerun

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

Stay in the Phase 5 samples-and-reference-patterns lane and tighten contributor guidance or one exact replay check only if fresh repo inspection shows another real same-lane drift on current `master`. If the bytestream packet itself changes later, keep the survey note, sample, focused replay, manifest, dedicated survey companion, and shared build route aligned together.