# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh mixed readback on 2026-05-17 confirmed these current sample-root files on `master`:

* `samples/zigux/README.md`
* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_sample.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`

The authenticated contents route used for this lane stayed flaky for part of the older Phase 5 packet during this reread, so the bytestream, kobject, trace-events, and formatting-companion entries above were rechecked through the public-tree and raw-file fallback paths before this README was refreshed.

The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Current `master` keeps all four roadmap-backed non-runtime Phase 5 sample-root ports directly readable in `samples/zigux/` through `samples/zigux/bytestream_fifo.zig`, `samples/zigux/kobject_example.zig`, `samples/zigux/kretprobe_example.zig`, and `samples/zigux/trace_events_sample.zig`.
Keep shared contributor guidance honest about that restored packet instead of repeating the older one-file kretprobe-only split.

## Phase 5 reminder

When a shared Phase 5 guide, checklist, or README mentions the bytestream, kobject, kretprobe, or trace-events anchors, treat those four `.zig` files as the current direct sample-root proof for the roadmap-backed non-runtime lane.

Keep `samples/zigux/trace_events_string_formatting_sample.zig` tied to the same non-runtime trace-events anchor as a bounded formatting companion.
Do not count it as a fifth approved Phase 5 anchor, standalone string-helper delivery, standalone `printf` parity, or standalone `vsprintf` parity.

Keep the shared `zigux/tests/phase5_build.zig` route in companion-evidence wording only when a fresh reread confirms that path too.

Do not widen this lane into runtime-loader, module-registration, procfs, sysfs, user-copy, workqueue, ring-buffer, or other runtime-substrate claims.

## Phase 9 runtime pilot family

The directly readable sample-root evidence that also exists here today for the later runtime lane is:

* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`

Keep those runtime-facing files in the separate Phase 9 packet instead of counting them as extra Phase 5 samples.

## No-extra-sample reminders

Current `master` still ships no standalone Phase 5 sample-root files here for:

* `*cmdline*`
* `*argv*`
* `*rbtree*`
* `*bitmap*`

Keep broader helper and formatting review surfaces in their existing helper, closure, or later-phase packets instead of treating this directory as proof that dedicated cmdline, argv, rbtree, bitmap, `printf`, or `vsprintf` sample families landed here as standalone samples.
