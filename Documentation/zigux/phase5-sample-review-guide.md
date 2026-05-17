# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 sample lane reviewable without pretending that every older sample-root, focused-test, survey-replay, or shared-build path is directly readable on current `master`.

## Purpose

Use this guide when a change touches Phase 5 contributor guidance, one of the approved Linux sample anchors, or one of the current `samples/zigux/` reference-sample ports.

The roadmap-backed goal for Phase 5 is still narrow:
* make approved Zigux idioms reviewable and repeatable
* keep ownership and lifetime cues explicit
* keep exact review surfaces visible
* avoid widening non-runtime samples into runtime-substrate claims

## Roadmap anchors

Phase 5 is still scoped by the four Linux sample anchors named in the roadmap:
* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Treat those anchors as the approved Phase 5 destination set unless the roadmap changes.

## Current repo reality on `master`

Fresh GitHub-app readback on 2026-05-16 in this run confirmed that current `master` still carries the bounded four-anchor Phase 5 packet together with its shared contributor surfaces, but the directly readable sample-local evidence is mixed rather than evenly restored across every anchor.

The shared reminder surfaces presently present on `master` are:
* `Documentation/zigux/phase5-sample-lane-sequencing.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/phase5-kfifo-sample-survey.md`
* `Documentation/zigux/phase5-kobject-sample-survey.md`
* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/phase5-trace-events-sample-survey.md`
* `Documentation/zigux/README.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

Current-run GitHub-app readback now also recovers `scripts/zigux/README.md`, and that scripts-root reminder now carries a bounded Phase 5 note that keeps the four-anchor non-runtime packet reviewable without inventing a validator or make-route family.
Keep it in the shared-surface inventory, but continue treating it as a reminder surface rather than direct proof of sample-local replay or build paths.

The directly readable sample-local evidence recovered in this run is:
* the bytestream sample-root packet through `Documentation/zigux/phase5-kfifo-sample-survey.md`, `samples/zigux/bytestream_fifo.zig`, and the directly readable companion manifest `zigux/tests/phase5_bytestream_fifo_manifest.json`, with that survey note also carrying the current public-tree-backed companion packet through `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `zigux/tests/phase5_build.zig` while authenticated contents readback for those remaining broader bytestream paths still fails in this environment
* `zigux/tests/README.md` now keeps the bytestream anchor aligned with the sibling docs-root reminders by naming `Documentation/zigux/phase5-kfifo-sample-survey.md`, `samples/zigux/bytestream_fifo.zig`, and the directly readable companion manifest `zigux/tests/phase5_bytestream_fifo_manifest.json`, while still framing `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_survey.zig`, and `zigux/tests/phase5_build.zig` as current public-tree-backed companion evidence rather than direct authenticated-contents proof
* the kobject packet through `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`
* the restored kretprobe packet through `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`
* the trace-events packet through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`

The kretprobe-specific survey note and the current shared reminder surfaces now keep that restored kretprobe packet explicit while the older shared `zigux/tests/phase5_build.zig` route remains missing from authenticated GitHub-app readback in this environment.
Broader shared reminder surfaces should be re-read one file at a time before they are reused as proof text for the restored kretprobe packet.

Authenticated GitHub-app readback in this run still did not recover these older Phase 5 packet paths directly:
* `zigux/tests/phase5_build.zig`
* `zigux/tests/phase5_bytestream_fifo.zig`
* `zigux/tests/phase5_bytestream_fifo_survey.zig`
* `zigux/tests/phase5_kobject_example_survey.zig`

For the bytestream anchor, keep the split explicit: `Documentation/zigux/phase5-kfifo-sample-survey.md` now preserves the directly readable bytestream manifest companion together with current public-tree blob readback for those remaining bytestream companion files even though authenticated contents readback still fails for those remaining paths.
Keep shared contributor wording aligned with that mixed packet instead of flattening every anchor into the same restored or gap-only posture.

That same inspection also confirmed that current `master` now keeps only a narrow surviving runtime-facing sample packet through `samples/zigux/runtime_trace_events.zig`, while direct rereads in this run did not recover the older runtime bitmap sample, runtime bitmap loader, runtime bitmap top-bit contract, or the broader `runtime_*_loader` family that earlier reminder surfaces referenced.
Keep runtime-facing sample work in the separate Phase 9 lane instead of counting it as extra Phase 5 evidence, and treat the removed runtime bitmap packet as absent until a fresh reread proves it has returned.

## Review posture

Because the four approved Phase 5 anchors are still the intended packet, same-lane follow-through should stay inside one of these bounded categories:
* contributor-guidance truthfulness fixes
* exact-readback repairs in shared review surfaces
* one shared-route or packet-alignment repair at a time
* one sample-local survey-note, manifest, or replay-contract update at a time when the coupled landed sample changes

Treat the current Phase 5 packet as landed but intentionally non-runtime:
* keep the roadmap-backed four-anchor scope explicit even when one or more sample-local files are not directly readable in this run
* shared docs that describe those anchors should distinguish direct-readback evidence from survey-note-plus-sample evidence and from missing shared-build evidence instead of flattening every sample into the same packet shape
* when one reminder surface is already aligned, do not smooth over the remaining stale ones; keep the aligned-versus-drifted split explicit so same-lane follow-through can stay one shared surface at a time
* do not describe `zigux/tests/phase5_build.zig` as current directly readable proof surface unless a fresh reread confirms that exact path again, and do not imply shared `make -C zigux phase5-test`, `make -C zigux phase5`, or workflow replay routes because current `zigux/Makefile` exposes neither target and `.github/workflows/zigux-bootstrap.yml` carries no dedicated Phase 5 step
* do not reopen sample behavior broadly, and do not count runtime-loader or runtime-pilot work as part of the non-runtime Phase 5 packet

## Shared ownership map

When Phase 5 follow-through is doc-only, keep the shared-versus-sample-local split explicit so reminder-surface work does not reopen neighboring sample packets by accident.

* shared Phase 5 packet work belongs in `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/README.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` only when the change preserves the same four-sample non-runtime packet and the same direct-readback caveats recorded above
* within that shared set, future follow-through should start from whichever one-file reminder surface actually drifts next instead of reusing the older survey-note-only kretprobe posture or treating the returned shared `zigux/tests/phase5_build.zig` route as direct authenticated proof instead of current public-tree-backed companion evidence
* bytestream packet work currently belongs in `Documentation/zigux/phase5-kfifo-sample-survey.md`, `samples/zigux/bytestream_fifo.zig`, the aligned tests-root reminder in `zigux/tests/README.md`, and the directly readable companion manifest `zigux/tests/phase5_bytestream_fifo_manifest.json`; do not restate the focused replay, survey replay, or shared-build companions as directly readable evidence until a fresh reread proves those remaining paths returned
* kobject packet work currently belongs in `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_kobject_example_manifest.json`; keep the current public-tree-backed companion packet `zigux/tests/phase5_kobject_example_survey.zig` plus `zigux/tests/phase5_build.zig` explicit when shared guidance needs the broader packet, but do not restate those two paths as direct authenticated-contents evidence unless a fresh reread proves the connector path returned
* trace-events packet work currently belongs in `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`; do not restate the missing shared `phase5_build.zig` route as directly readable evidence until a fresh reread proves it returned
* kretprobe packet work currently belongs in `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`; keep the shared `zigux/tests/phase5_build.zig` route explicit as current public-tree-backed companion evidence for that restored packet, but do not restate that path as direct authenticated-contents evidence unless a fresh reread proves the connector path returned
* if a shared doc needs to remind reviewers about one sample-specific ownership cue, point to the exact currently readable packet for that sample instead of re-describing behavior from memory or borrowing cues from a different sample family
* keep the later `samples/zigux/runtime_*.zig` and `*_loader.zig` families out of shared Phase 5 reminder work unless the only purpose is to restate the already-landed Phase 5-versus-Phase 9 boundary

## Boundary reminders

Phase 5 stays non-runtime.
Do not treat later runtime-oriented loader or pilot work as extra Phase 5 samples. Keep runtime-facing delivery under the later runtime lane instead of using it to imply that the roadmap's non-runtime Phase 5 packet is larger than the four approved anchors.

Keep these no-extra-sample reminders explicit too:
* there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master`; keep string-helper reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`; keep cmdline reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`; keep `argv_split` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`; keep `rbtree` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`; keep direct bitmap helper reviewability under the earlier helper and rollback packets, and do not substitute removed runtime bitmap sample or loader paths as current evidence unless a fresh reread proves they have returned in the separate Phase 9 lane
* there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample on current `master`; keep the approved formatting idiom cue bounded to the selected-string plus `iter=%d` reminder carried by the directly readable `trace_events_sample` packet while standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet

Respect the freeze map too.
Do not widen Phase 5 work toward freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`, and do not pull the study-only `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` families into this lane.