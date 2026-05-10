# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 lane reviewable without overstating what current `master` actually ships.

## Purpose

Use this guide when a change touches Phase 5 contributor guidance, one of the approved Linux sample anchors, or a future `samples/zigux/` reference-sample port.

The roadmap-backed goal for Phase 5 is still narrow:

* make approved Zigux idioms reviewable and repeatable
* keep ownership and lifetime cues explicit
* keep exact replay routes visible once they actually land
* avoid widening non-runtime samples into runtime-substrate claims

## Roadmap anchors

Phase 5 is still scoped by the four Linux sample anchors named in the roadmap:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Treat those anchors as the approved Phase 5 destination set unless the roadmap changes.

## Current repo reality on master

Fresh repo-first inspection for this guide showed that current `master` keeps Phase 5 mostly in contributor-guidance and review-surface form rather than as a completed four-sample delivery packet.

Verified current Phase 5 review surfaces on `master` are:

* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/phase5-kfifo-sample-survey.md`
* `Documentation/zigux/phase5-argv-split-no-sample-boundary.md`
* `Documentation/zigux/README.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`
* `.github/workflows/zigux-bootstrap.yml`

The same inspection also confirmed one later runtime-facing sample surface is present on `master`:

* `samples/zigux/runtime_atomic64_loader.zig`

Do not count that later runtime-facing loader surface as Phase 5 evidence.

The same inspection did not verify shipped current-`master` files for the planned four-sample packet such as:

* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_sample.zig`
* `zigux/tests/phase5_build.zig`
* `make -C zigux phase5-test`
* `make -C zigux phase5`

Keep Phase 5 guidance honest about that gap. Do not describe those sample, test, or wrapper surfaces as already shipped until the files themselves land on `master`.

## Review posture

Until the missing Phase 5 reference-sample packet actually lands, same-lane work should stay inside one of these bounded categories:

* contributor-guidance truthfulness fixes
* exact-readback repairs in shared review surfaces
* one approved sample port at a time
* one paired survey note or manifest update at a time, but only when the coupled sample surface already exists on `master`

## Boundary reminders

Phase 5 stays non-runtime.

Do not treat later runtime-oriented loader or pilot work as extra Phase 5 samples. Keep runtime-facing sample delivery under the later runtime lane instead of using it to imply that the roadmap's non-runtime Phase 5 packet has already landed.

Keep these no-extra-sample reminders explicit too:

* there is no verified standalone `samples/zigux/*string*` Phase 5 reference sample on current `master`; keep string-helper reviewability under the Phase 7 helper packet
* there is no verified standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`; keep cmdline reviewability under the Phase 7 helper packet
* there is no verified standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`; keep `argv_split` reviewability under the Phase 7 helper packet and the dedicated no-sample boundary note
* there is no verified standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`; keep `rbtree` reviewability under the Phase 7 helper packet
* there is no verified standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`; keep direct bitmap helper reviewability under the earlier helper and rollback packets while runtime bitmap work stays in the later runtime lane
* there is no verified standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample on current `master`

Respect the freeze map too. Do not widen Phase 5 work toward freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`, and do not pull the study-only `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` families into this lane.

## Contributor checklist

Before landing a Phase 5 change, confirm:

* the roadmap anchor is one of the four approved Linux sample paths listed above
* the change says clearly whether it is guidance-only work or a real landed sample surface
* if a new Phase 5 sample file lands, the paired survey note and replay route land with it instead of being deferred into prose-only promises
* if a shared Phase 5 guide, README, checklist, or survey note mentions a sample, manifest, test entrypoint, or make wrapper, that surface is actually present on current `master`
* the change keeps runtime-substrate claims out of scope unless a later roadmap-backed runtime lane explicitly owns them

## Non-goals

This shared Phase 5 guide does not claim:

* procfs parity
* sysfs creation parity
* probe registration parity
* tracepoint macro parity
* user-copy parity
* module registration or loader wiring parity
* scheduler-facing, workqueue-facing, ring-buffer-facing, or other deep-core runtime substrate closure
