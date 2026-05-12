# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Current `master` does not expose the approved non-runtime Phase 5 reference samples under this directory.

The files directly readable here today are the runtime-oriented sample family:

* `samples/zigux/runtime_atomic64_loader.zig`
* `samples/zigux/runtime_bitmap.zig`
* `samples/zigux/runtime_bitmap_loader.zig`
* `samples/zigux/runtime_bitmap_top_bit_contract.zig`
* `samples/zigux/runtime_kretprobe_loader.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_loader.zig`

Treat those files as the separate runtime sample family. Do not count them as shipped Phase 5 evidence.

## Approved Phase 5 sample scope

The roadmap-backed Phase 5 sample anchors are still limited to these four Linux sample paths:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Those anchors remain the approved Phase 5 target set, but they are not currently materialized as non-runtime `samples/zigux/*.zig` files in this directory on `master`.

## Contributor guidance

When touching Phase 5 contributor guidance:

* keep roadmap scope narrow to the four approved anchors above
* do not describe a Phase 5 sample as shipped from this directory unless the corresponding `samples/zigux/*.zig` file is directly readable on current `master`
* do not treat review notes by themselves as proof that a sample file is present in this directory
* keep runtime-facing `runtime_*` files in the separate later runtime lane instead of folding them into Phase 5
* keep helper-only reviewability for `string`, `cmdline`, `argv_split`, `rbtree`, and direct `bitmap` work in their existing helper or runtime lanes instead of implying extra Phase 5 samples

## Boundary notes

Respect the freeze map here too.

* do not add Phase 5 follow-ons derived from freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
* keep the study-only `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` families out of this directory until a later roadmap-backed lane explicitly reopens that boundary
* if a proposed sample needs runtime-loader wiring, scheduler-visible execution, workqueue handoff, ring-buffer substrate, or other live kernel execution context to make its contract honest, route it to the separate runtime lane instead of widening Phase 5

## Review pointers

For shared Phase 5 guidance, use:

* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `Documentation/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

Use those shared surfaces to keep roadmap scope, contributor wording, and the Phase 5-versus-runtime boundary honest until actual non-runtime sample files land in this directory.
