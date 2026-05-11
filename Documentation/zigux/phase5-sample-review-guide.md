# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 lane reviewable without overstating what current `master` actually ships.

## Purpose

Use this guide when a change touches Phase 5 contributor guidance, one of the approved Linux sample anchors, or one of the intended `samples/zigux/` reference-sample ports.

The roadmap-backed goal for Phase 5 is still narrow:

* make approved Zigux idioms reviewable and repeatable
* keep ownership and lifetime cues explicit
* keep exact replay routes visible
* avoid widening non-runtime samples into runtime-substrate claims

## Roadmap anchors

Phase 5 is still scoped by the four Linux sample anchors named in the roadmap:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Treat those anchors as the approved Phase 5 destination set unless the roadmap changes.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-11 confirmed that current `master` does carry the shared Phase 5 contributor surfaces below:

* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/README.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`
* `zigux/Makefile`
* `.github/workflows/zigux-bootstrap.yml`

That same repo-first inspection did **not** confirm the concrete sample-and-test artifact packet that those shared docs currently describe as already landed. Direct contents reads for these claimed Phase 5 sample and test paths returned not found on current `master`:

* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_sample.zig`
* `zigux/tests/phase5_build.zig`
* `zigux/tests/phase5_bytestream_fifo.zig`
* `zigux/tests/phase5_bytestream_fifo_manifest.json`
* `zigux/tests/phase5_bytestream_fifo_survey.zig`
* `zigux/tests/phase5_kobject_example.zig`
* `zigux/tests/phase5_kobject_example_manifest.json`
* `zigux/tests/phase5_kretprobe_example.zig`
* `zigux/tests/phase5_kretprobe_example_manifest.json`
* `zigux/tests/phase5_trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample_manifest.json`

Because those concrete artifact paths are not presently readable from current `master`, do not describe the full four-sample packet as shipped evidence until the sample files, tests, manifests, and shared build entrypoint are restorable and directly visible again.

The same inspection also confirmed that later runtime-facing guidance is still present in shared docs. Keep those later runtime-oriented sample families under the separate Phase 9 lane instead of counting them as extra Phase 5 evidence.

## Review posture

Until the concrete Phase 5 sample artifacts are directly visible again, same-lane follow-through should stay inside one of these bounded categories:

* contributor-guidance truthfulness fixes
* exact-readback repairs in shared review surfaces
* one missing-path or shared-route inventory repair at a time
* one concrete sample-restoration step at a time once the missing artifact packet can be re-established safely

Do not reopen sample behavior broadly, and do not claim the four-sample packet is landed, unless a fresh repo-first inspection can directly read the sample files, their paired test or manifest artifacts, and the shared `phase5_build.zig` entrypoint on current `master`.

## Boundary reminders

Phase 5 stays non-runtime.

Do not treat later runtime-oriented loader or pilot work as extra Phase 5 samples. Keep runtime-facing delivery under the later runtime lane instead of using it to imply that the roadmap's non-runtime Phase 5 packet is larger than the four approved anchors.

Keep these no-extra-sample reminders explicit too:

* there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master`; keep string-helper reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`; keep cmdline reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`; keep `argv_split` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`; keep `rbtree` reviewability under the Phase 7 helper packet
* there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`; keep direct bitmap helper reviewability under the earlier helper and rollback packets while runtime bitmap work stays in the later runtime lane
* there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample on current `master`; keep any formatting idiom guidance bounded to whatever directly readable Phase 5 evidence exists instead of implying a fifth formatting sample

Respect the freeze map too. Do not widen Phase 5 work toward freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`, and do not pull the study-only `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` families into this lane.

## Contributor checklist

Before landing a Phase 5 change, confirm:

* the roadmap anchor is one of the four approved Linux sample paths listed above
* the change says clearly whether it touches shared contributor guidance or one specific sample-restoration packet
* if a shared Phase 5 guide, README, checklist, survey note, manifest, test entrypoint, or make wrapper mentions a sample or replay route, that surface is directly readable on current `master`
* if a shared doc claims a sample-local replay route, the corresponding sample file, paired tests, paired manifest, and build entrypoint can all be read directly from the repo instead of being inferred from stale wording alone
* the lane keeps runtime-substrate claims out of scope unless a later roadmap-backed runtime lane explicitly owns them
* later `runtime_*` sample and loader families remain clearly separated from the non-runtime Phase 5 packet

## Non-goals

This shared Phase 5 guide does not claim:

* procfs parity
* sysfs creation parity
* probe registration parity
* tracepoint macro parity
* user-copy parity
* module registration or loader wiring parity
* scheduler-facing, workqueue-facing, ring-buffer-facing, or other deep-core runtime substrate closure
