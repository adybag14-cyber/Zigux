# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh public-tree readback on 2026-05-17 shows that current `master` directly exposes these files in `samples/zigux/` through the authenticated contents route used for this lane:

* `samples/zigux/README.md`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`

The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Current `master` now restores one directly readable non-runtime Phase 5 sample-root port through `samples/zigux/kretprobe_example.zig`.
The other three roadmap-backed Phase 5 sample-root ports remain absent from `samples/zigux/` on current `master` through this authenticated route.
Keep shared contributor guidance honest about that split instead of repeating older sample-root packets as if all four files were directly here.

## Phase 5 reminder

When a shared Phase 5 guide, checklist, or README mentions the bytestream, kobject, kretprobe, or trace-events anchors, treat `samples/zigux/kretprobe_example.zig` as current direct sample-root proof for the restored kretprobe packet.
Treat the remaining bytestream, kobject, and trace-events anchors as roadmap-backed reference targets and reminder surfaces unless a fresh reread confirms those exact files have returned.

Keep the shared `zigux/tests/phase5_build.zig` route out of direct-proof wording unless a fresh reread confirms that exact path too.

Do not widen this lane into runtime-loader, module-registration, procfs, sysfs, user-copy, workqueue, ring-buffer, or other runtime-substrate claims.

## Kretprobe review packet

Current `master` now ships one directly readable non-runtime probe-side packet here:

* `samples/zigux/kretprobe_example.zig`

Keep that restored packet tied to the same bounded review cues already described in the directly coupled Phase 5 survey and manifest surfaces:

* pre-init symbol retargeting only
* fixed `maxactive = 20`
* explicit skipped-kernel-thread handling
* explicit timestamp-order rejection and recovered-duration replay
* explicit post-exit rejection without claiming runtime module wiring or `register_kretprobe()` parity

## Phase 5 string and formatting companion

Current `master` now also carries one bounded non-runtime companion for the existing trace-events anchor:

* `samples/zigux/trace_events_string_formatting_sample.zig`

Treat it as a reviewable restatement of the selected-string plus `iter=%d` cue already approved under the non-runtime trace-events packet.
Do not count it as a fifth approved Phase 5 anchor, standalone `printf` or `vsprintf` parity, or standalone string-helper delivery.

## Phase 9 runtime pilot family

The directly readable sample-root evidence that does exist here today also includes later runtime-lane files:

* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`

Keep those runtime-facing files in the separate Phase 9 packet instead of counting them as extra Phase 5 samples.

## No-extra-sample reminders

Current `master` still ships no standalone Phase 5 sample-root files here for:

* `*cmdline*`
* `*argv*`
* `*rbtree*`
* `*bitmap*`

Current `master` does now ship one bounded `*string*` and `*format*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace-events` anchor and its selected-string plus `iter=%d` formatting cue instead of treating it as a standalone helper packet.

Keep broader helper and formatting review surfaces in their existing helper, closure, or later-phase packets instead of treating this directory as proof that dedicated cmdline, argv, rbtree, bitmap, `printf`, or `vsprintf` sample families landed here.