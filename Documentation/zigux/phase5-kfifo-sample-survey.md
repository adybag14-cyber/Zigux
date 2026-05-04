# Phase 5 Kfifo Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/kfifo/bytestream-example.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_LANE_KEY=P5-L04`
- `PHASE5_SLICE=kfifo-reference-sample-starter`
- `PHASE5_SURVEYED_COMMIT=a15760c3e46103fd41ae0da852b61f612e9116c6`
- scope: roadmap-vs-repo sample delivery, approved reference-sample idiom guidance, and exact bounded checks for the first `samples/zigux/` kfifo-style replay
- product boundary:
  - `Documentation/zigux/phase5-kfifo-sample-survey.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/bytestream_fifo.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_bytestream_fifo.zig`
  - `zigux/tests/phase5_bytestream_fifo_manifest.json`
  - `zigux/tests/phase5_bytestream_fifo_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/kfifo/bytestream-example.c` as one of the four Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection now shows that `samples/zigux/` carries all four roadmap-approved bounded Phase 5 reference samples and several later Phase 9 runtime starters or loader-side follow-ons that stay outside this non-runtime survey lane:

- `bytestream_fifo.zig`
- `kobject_example.zig`
- `kretprobe_example.zig`
- `trace_events_sample.zig`
- `runtime_atomic64.zig`
- `runtime_atomic64_loader.zig`
- `runtime_bitmap.zig`
- `runtime_bitmap_loader.zig`
- `runtime_bitmap_top_bit_contract.zig`
- `runtime_bitmap_top_bit_build.zig`
- `runtime_kretprobe.zig`
- `runtime_kretprobe_loader.zig`
- `runtime_trace_events.zig`
- `runtime_trace_events_loader.zig`

The `kfifo`-specific gap is no longer missing sample delivery. The remaining work in this lane is to keep the approved idiom, exact checks, and non-goals honest now that the full Phase 5 anchor set is landed, especially where later Phase 9 runtime pilots exist under neighboring Linux sample families.
The shared sample-root catalog in `samples/zigux/README.md`, the shared tests-root guide in `zigux/tests/README.md`, the top-level docs root in `Documentation/zigux/README.md`, and the shared prompts in `Documentation/zigux/review-checklist.md` are part of that contributor-facing boundary now, because together they keep the landed bytestream FIFO idiom visibly separate from the later runtime starters. The docs root and shared tests-root guide point reviewers back to the direct `zig test samples/zigux/bytestream_fifo.zig` replay, the direct helper-review replay `zig test zigux/tests/phase5_bytestream_fifo.zig`, the paired `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` replay, and the exact shipped review packet, while the review checklist keeps the same family tied to the descriptor, manifest-backed survey, sample-backed survey note, the direct sample replay, the paired survey replay, and the shared `phase5_build.zig` entrypoint without over-claiming the helper-review route.
The same sample-root catalog now also keeps the current no `samples/zigux/*cmdline*` Phase 5 boundary explicit, so the approved bytestream idiom does not drift into the separate Phase 7 cmdline helper bundle rooted in `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, and `zigux/tests/phase7_build.zig`.
The same shared packet also keeps the current no `samples/zigux/*string*` Phase 5 boundary explicit, so the landed bytestream idiom does not drift into the separate Phase 7 string-helper bundle rooted in `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, and `zigux/tests/phase7_build.zig`.
The same shared packet still keeps the blocked `samples/zigux/runtime_trace_events.zig` pilot separate from the later runtime follow-ons even though the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is shipped now, so this bytestream note cannot let the Phase 9 handoff read like another approved Phase 5 idiom.

## Survey findings

- `samples/kfifo/bytestream-example.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a subsystem slice.
- the Linux sample mixes three concerns:
  - bounded in-memory FIFO behavior such as `kfifo_in`, `kfifo_out`, `kfifo_put`, `kfifo_get`, `kfifo_skip`, and `kfifo_peek`
  - lifecycle setup and teardown around `example_init()` and `example_exit()`
  - procfs and user-copy plumbing through `proc_create`, `kfifo_from_user`, `kfifo_to_user`, and mutex-protected read or write paths
- the live Zigux repo now ships bounded Phase 5 side-by-side samples under `samples/zigux/` for the `kfifo`, `kobject`, `kretprobe`, and `trace-events` anchors, while still keeping the later Phase 9 runtime starters separate from these non-runtime reference readings.
- `samples/zigux/README.md` is the shared sample-root catalog for that directory boundary, so drift there is a Phase 5 reviewability problem even when the bytestream sample code itself has not changed.
- the shared tests-root guide in `zigux/tests/README.md` is part of that same contributor packet now, because it names the direct `zig test samples/zigux/bytestream_fifo.zig` replay, the direct helper-review replay `zig test zigux/tests/phase5_bytestream_fifo.zig`, the paired `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` replay, and the wider Phase 5 boundary cues that keep this landed sample distinct from the later runtime starters.
- the shared sample-root catalog and docs root both now say plainly that current `master` ships no `samples/zigux/*cmdline*` Phase 5 reference sample, so cmdline review stays in the separate Phase 7 helper bundle instead of reading like another missing sample port.
- the shared sample-root catalog and docs root also say plainly that current `master` ships no `samples/zigux/*string*` Phase 5 reference sample, so string-helper review stays in the separate Phase 7 helper bundle instead of reading like another missing sample port.
- the shared sample-root catalog now also carries a dedicated bytestream FIFO review-packet stanza, so contributors can refresh the exact replay contract, the exact `checked_focus` order, the helper-only review surface, and out-of-scope runtime claims without having to infer them from the sample code alone.
- the generic review checklist already covers the Phase 5 boundary between a reviewable idiom and a runtime-ready module, but contributors still benefit from one sample-backed set of prompts tied directly to the shipped bytestream FIFO slice.

## Approved idiom for the landed kfifo-style sample

For the already-landed Phase 5 `samples/zigux/bytestream_fifo.zig` slice, the approved idiom remains:

- model FIFO state and ordered operations entirely in memory
- keep the Linux anchor path explicit in a descriptor or note
- make the storage choice explicit as a fixed embedded ring buffer so reviewers do not read dynamic or runtime-owned backing into this bounded sample
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
- it now exposes the fixed embedded backing choice directly in the sample contract so the Phase 5 reading stays visibly separate from any later dynamic or runtime-owned storage lane
- it exposes a single bounded self-check that resets state, replays the bytestream example, and returns the exact observations that reviewers should care about

The manifest-backed reference-pattern list for this landed sample is now:

- fixed embedded 32-byte ring buffer keeps the Phase 5 sample in memory and reviewable
- exact queue-order replay mirrors the Linux bytestream anchor without claiming procfs or module parity
- wraparound requeue, skip, and peek stay explicit as bounded FIFO operations rather than hidden helper behavior
- non-destructive snapshot keeps reviewer inspection separate from the final drain sequence
- `init()`, replay, and `exit()` keep ownership and lifetime boundaries explicit for the bytestream sample

The exact checks currently recorded in `zigux/tests/phase5_bytestream_fifo_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the queue length is `15` after enqueueing "hello" and bytes `0` through `9`
- the first drain returns "hello"
- the second drain returns bytes `0` and `1`, and those same bytes are re-enqueued at the tail
- the initial string copy count is `5`, the first drain count is `5`, the second drain count is `2`, and the requeue count is `2`, so the Linux-style `kfifo_in()` and `kfifo_out()` transfer sizes stay reviewable instead of hiding inside helper state
- skipping the next byte removes `2`
- peeking afterward observes `3` without draining it
- before the full snapshot, a truncated 8-byte preview prefix preserves `[3,4,5,6,7,8,9,0]` from the wrapped 32-byte queue without consuming state
- a non-destructive snapshot before the final drain preserves the exact 32-byte Linux anchor sequence `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
- the fill loop succeeds for bytes `20` through `42` inclusive and then stops at the bounded capacity
- the final drain yields the exact 32-byte Linux anchor sequence `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`
- the descriptor and replay keep the sample on a fixed embedded 32-byte ring buffer rather than dynamic or runtime-backed storage
- empty-queue peek and skip return `null`, `snapshotInto()` leaves queue order intact, pushing past capacity returns `false`, and `reset()` restores an empty queue
- draining a three-byte destination from the queued string `"hello"` yields `"hel"`, leaves the remaining prefix `"lo"` queued in order, and a follow-up drain on the now-empty queue returns `0`
- after the wraparound replay setup, `snapshotInto()` truncates to the destination length and `previewInto()` surfaces that same bounded preview while reporting `total_visible = 10`; the same helper reports `0` for an empty queue and `32` for a full queue, so an 8-byte preview yields `[2,3,4,5,6,7,8,9]` while leaving the queue length at `10`
- queue-only reset clears buffered bytes back to an empty queue but does not rewind lifecycle state or the `init_runs` and `exit_runs` bookkeeping counters
- the replay advertises exactly seven review-focus areas: `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `reset_and_replay`, and `ownership_and_lifetime`
- the sample starts in a cold state, requires `init()` before replay, records `replay_complete` after the self-check, and `exit()` returns it to an empty bounded state
- `runAnchorReplay()` fails before `init()` and after `exit()`, `init()` fails if repeated outside the cold state, `exit()` fails if repeated after teardown, and one successful pass leaves `init_runs = 1` plus `exit_runs = 1`

## Latest verification snapshot

The latest direct Zig replay recorded for this packet remains the 2026-05-01 run against `master` commit `f5f4aa86602580b500f4d0ab8640ec6029e82e46` with the attached Zig toolchain.

The exact focused verification commands and observed results for the bytestream-local packet were:

- `zig test samples/zigux/bytestream_fifo.zig`
  - observed result: `1/4 bytestream_fifo.test.bytestream fifo sample replays the Linux anchor result sequence...OK`
  - observed result: `2/4 bytestream_fifo.test.bytestream fifo sample keeps helper boundaries explicit...OK`
  - observed result: `3/4 bytestream_fifo.test.bytestream fifo sample keeps ownership and lifetime guards explicit...OK`
  - observed result: `4/4 bytestream_fifo.test.bytestream fifo sample reset clears queue state without rewinding lifecycle bookkeeping...OK`
  - observed result: `All 4 tests passed.`
- `zig test zigux/tests/phase5_bytestream_fifo.zig`
  - observed result: `1/5 phase5_bytestream_fifo.test.phase 5 bytestream fifo sample stays in the reference-sample lane...OK`
  - observed result: `2/5 phase5_bytestream_fifo.test.phase 5 bytestream fifo sample replays exact queue behavior from the Linux anchor...OK`
  - observed result: `3/5 phase5_bytestream_fifo.test.phase 5 bytestream fifo sample keeps bounded helper behavior explicit...OK`
  - observed result: `4/5 phase5_bytestream_fifo.test.phase 5 bytestream fifo sample makes ownership and lifetime boundaries explicit...OK`
  - observed result: `5/5 phase5_bytestream_fifo.test.phase 5 bytestream fifo reset clears queue state without restarting lifecycle bookkeeping...OK`
  - observed result: `All 5 tests passed.`
- `zig test zigux/tests/phase5_bytestream_fifo_survey.zig`
  - observed result: `1/2 phase5_bytestream_fifo_survey.test.phase 5 bytestream fifo manifest records the exact bounded checks...OK`
  - observed result: `2/2 phase5_bytestream_fifo_survey.test.phase 5 bytestream fifo contributor docs stay aligned with the shipped review surface...OK`
  - observed result: `All 2 tests passed.`

The shared `zigux/tests/phase5_build.zig` entrypoint remains the umbrella review gate recorded in the manifest and contributor prompts, but this bounded verification pass did not rerun the whole Phase 5 sample bundle, so this note no longer republishes the older pre-expansion shared test count.

This note's 2026-05-02 refresh was provenance-only: it repins the inspected-head marker to `PHASE5_SURVEYED_COMMIT=a15760c3e46103fd41ae0da852b61f612e9116c6` after readback confirmed that the bytestream sample, the paired survey gate, and the shared `phase5_build.zig` entrypoint still keep the same bounded bytestream review surface on current `master` without claiming a newer direct Zig replay or republishing that older whole-bundle total.

Those recorded runs confirmed that the shipped bytestream FIFO sample still matches the exact bounded checks above: the embedded 32-byte queue reaches length `15` after the initial replay setup, drains `"hello"` first, drains and requeues `0` and `1`, skips `2`, peeks `3`, preserves the truncated replay preview prefix `[3,4,5,6,7,8,9,0]`, preserves the exact 32-byte snapshot and final drain sequence `[3,4,5,6,7,8,9,0,1,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42]`, and keeps the helper-only preview visibility counts explicit (`0` empty, `10` wrapped, `32` full-capacity) plus the preview truncation, reset, and lifecycle guards green under the shared Phase 5 build entrypoint.

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/bytestream_fifo.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `BytestreamFifoSample.descriptor()` still name the Linux anchor `samples/kfifo/bytestream-example.c`, keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`, and state that the sample uses fixed embedded storage?
- does `zigux/tests/phase5_bytestream_fifo_manifest.json` still pin `surveyed_commit` to the exact inspected `master` head while this note carries the same `PHASE5_SURVEYED_COMMIT` marker instead of a floating branch label?
- do `zigux/tests/phase5_bytestream_fifo_manifest.json`, its reference-pattern list, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and the sample-backed survey note still record the exact queue-order replay, transfer-count contract, the truncated 8-byte preview prefix, the later helper-side preview truncation plus preview-visible-length counts, the non-destructive snapshot, fixed embedded backing, and bounded helper checks that `zigux/tests/phase5_build.zig` runs?
- does `zigux/tests/phase5_bytestream_fifo.zig` still keep the separate bounded helper test surface explicit so empty-queue null handling, preview truncation, preview-visible-length counts, the capacity ceiling, and queue-only reset behavior remain reviewable outside the main replay path?
- if the sample behavior changes, is the manifest updated alongside the replay expectations instead of leaving reviewers to infer the new contract from code alone?
- do `Documentation/zigux/README.md` and `zigux/tests/README.md` still point reviewers back to the descriptor, manifest-backed survey, sample-backed survey note, the direct `zig test samples/zigux/bytestream_fifo.zig` replay, the direct helper-review replay `zig test zigux/tests/phase5_bytestream_fifo.zig`, the paired `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` replay, and the shared `phase5_build.zig` entrypoint for this exact Phase 5 replay contract?
- does `Documentation/zigux/review-checklist.md` still keep the same sample family tied to the descriptor, manifest-backed survey, sample-backed survey note, the direct `zig test samples/zigux/bytestream_fifo.zig` replay, the paired `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` replay, and the shared `phase5_build.zig` entrypoint without over-claiming the helper-review replay?
- does `samples/zigux/README.md` still separate the four Phase 5 reference samples from the later `runtime_*` starters that share the same directory, keep the dedicated bytestream FIFO review-packet stanza focused on the exact replay contract, the exact `checked_focus` order `bounded_fifo_order`, `wraparound_requeue`, `peek_and_skip`, `non_destructive_snapshot`, `preview_truncation`, `reset_and_replay`, and `ownership_and_lifetime`, the helper-only review surface, and out-of-scope runtime claims, and still say plainly that current `master` ships no `samples/zigux/*string*` or `samples/zigux/*cmdline*` Phase 5 reference sample because those helper families stay under the separate Phase 7 bundles?
- do the docs and tests still say clearly that procfs, user-copy, locking, and runtime registration remain out of scope for this Phase 5 sample?

These prompts are intentionally sample-backed rather than generic. They tie review back to the concrete descriptor, manifest, and build entrypoint that current `master` already ships.

## Recorded gap vs roadmap

The roadmap delivery gap is already closed. The more precise ongoing review job is:

- all four roadmap anchors now have bounded non-runtime `samples/zigux/` reference samples on current `master`
- `samples/zigux/README.md` now records that shipped anchor set plainly so reviewers can keep the bytestream FIFO slice distinct from the separate later Phase 9 runtime pilots
- this approved in-memory FIFO idiom is now pinned to `PHASE5_SURVEYED_COMMIT=a15760c3e46103fd41ae0da852b61f612e9116c6` so the survey note, manifest-backed checks, shared sample-root catalog, shared tests-root guide, shared review checklist, and contributor refresh path all point at the same inspected `master` head
- the full four-anchor Phase 5 reference-sample set is already landed on current `master`, so this note should describe the bytestream FIFO slice as one approved in-memory FIFO idiom inside that completed anchor set rather than as a placeholder for a still-missing tranche item
- the same sample-root packet also needs to keep the no-`samples/zigux/*cmdline*` boundary visible so the bytestream survey lane does not accidentally count the separate Phase 7 cmdline helper bundle as a missing Phase 5 sample gap
- contributor guidance still needs to keep the explicit fixed-storage boundary, transfer-count contract, preview and snapshot checks, and non-goals visibly separate from procfs, user-copy, locking, and module-registration claims

This slice keeps the landed bytestream FIFO sample reviewable by recording the exact lifecycle, queue-order replay, transfer-count contract, preview and snapshot checks, fixed embedded storage boundary, and non-goal cues reviewers should check before approving future edits, without reopening the closed Phase 5 sample-delivery gap.

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux bytestream example
- `rg -n "samples/kfifo/bytestream-example.c|Phase 5" Documentation/zigux samples /workspace/agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP\ \(1\).md`

2. confirm the current `samples/zigux/` surface stays distinct from this reference-sample lane
- `find samples/zigux -maxdepth 1 -type f | sort`

3. run the focused self-check that keeps the in-memory FIFO replay explicit
- `zig test samples/zigux/bytestream_fifo.zig`

4. run the direct helper-review replay from the repo root so the extra bounded queue-only checks stay explicit outside the main sample path
- `zig test zigux/tests/phase5_bytestream_fifo.zig`

5. run the manifest-backed survey gate from the repo root so the exact-check record stays readable
- `zig test zigux/tests/phase5_bytestream_fifo_survey.zig`

6. run the exact bounded Phase 5 sample checks
- `zig build test --build-file zigux/tests/phase5_build.zig --summary all`

## Non-goals

This survey does not yet claim:

- procfs parity
- `kfifo_from_user()` or `kfifo_to_user()` parity
- loadable-module wiring or runtime registration support
- lock-contention or blocking semantics

## Next bounded step

Leave this narrow `kfifo` survey lane parked unless fresh repo inspection shows one more same-family drift in the approved idiom, contributor prompts, or roadmap-gap wording for the already-landed bytestream FIFO sample.
