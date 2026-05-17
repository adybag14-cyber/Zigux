# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh public-tree readback on 2026-05-17 shows that current `master` directly exposes only these files in `samples/zigux/`:

* `samples/zigux/README.md`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`

The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

But those four Phase 5 sample-root ports are not currently present as directly readable files under `samples/zigux/` on current `master`.
Keep shared contributor guidance honest about that gap instead of repeating older sample-root packets as if those files were still directly here.

## Phase 5 reminder

When a shared Phase 5 guide, checklist, or README mentions the bytestream, kobject, kretprobe, or trace-events anchors, treat them as roadmap-backed reference targets and reminder surfaces rather than current sample-root proof from this directory unless a fresh reread confirms those exact files have returned.

Keep the shared `zigux/tests/phase5_build.zig` route out of direct-proof wording unless a fresh reread confirms that exact path too.

Do not widen this lane into runtime-loader, module-registration, procfs, sysfs, user-copy, workqueue, ring-buffer, or other runtime-substrate claims.

## Phase 9 runtime pilot family

The directly readable sample-root evidence that does exist here today belongs to the later runtime lane:

* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`

Keep those runtime-facing files in the separate Phase 9 packet instead of counting them as extra Phase 5 samples.

## No-extra-sample reminders

Current `master` still ships no standalone Phase 5 sample-root files here for:

* `*string*`
* `*cmdline*`
* `*argv*`
* `*rbtree*`
* `*bitmap*`
* `*printf*`
* `*vsprintf*`
* `*format*`

Keep those helper and formatting review surfaces in their existing helper, closure, or later-phase packets instead of treating this directory as proof that those sample families landed here.
