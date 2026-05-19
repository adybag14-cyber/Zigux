# samples/zigux

This directory is the sample-root boundary for Zigux.

## Current repo reality on `master`

Fresh mixed readback on 2026-05-19 confirmed these current sample-root files on `master`:

* `samples/zigux/README.md`
* `samples/zigux/bytestream_fifo.zig`
* `samples/zigux/kobject_example.zig`
* `samples/zigux/kretprobe_example.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`
* `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`

The Phase 5 roadmap still scopes the non-runtime sample lane to these four Linux anchors:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Current `master` keeps the bytestream sample-root port directly readable in `samples/zigux/` through `samples/zigux/bytestream_fifo.zig`.
Current `master` keeps the kobject sample-root port directly readable in `samples/zigux/` through `samples/zigux/kobject_example.zig`.
Current `master` keeps the kretprobe sample-root port directly readable in `samples/zigux/` through `samples/zigux/kretprobe_example.zig`.
For the trace-events anchor, current `master` keeps the direct non-runtime sample packet reviewable through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig`, while `samples/zigux/trace_events_string_formatting_sample.zig` remains a bounded formatting companion inside the same approved anchor rather than a fifth sample.
Keep the shared `zigux/tests/phase5_build.zig` route framed as companion evidence rather than direct authenticated proof.

## Phase 5 reminder

When a shared Phase 5 guide, checklist, or README mentions the bytestream, kobject, kretprobe, or trace-events anchors, keep the roadmap-backed non-runtime lane explicit and keep the shared `zigux/tests/phase5_build.zig` route out of direct-proof wording unless a fresh reread confirms that exact path too.

Do not widen this lane into runtime-loader, module-registration, procfs, sysfs, user-copy, workqueue, ring-buffer, or other runtime-substrate claims.

## Separate helper-backed sample packet

This draft branch also carries one bounded helper-backed review surface:

* `samples/zigux/string_helpers_sample.zig`

Treat it as a bounded Phase 7 string-helper replay, not a fifth Phase 5 reference anchor.
The roadmap-backed Phase 7 product destination still remains `lib/string_helpers.zig`; the draft sample stays supporting review evidence for that helper lane rather than an approved sample-root idiom on its own.
Review that packet through `Documentation/zigux/phase7-string-helpers-slice.md`, `zigux/tests/phase7_string_helpers_sample_manifest.json`, `zigux/tests/phase7_string_helpers_sample_survey.zig`, and `zigux/tests/phase7_build.zig`.
Keep the sample tied to the shared Phase 7 helper lane instead of treating it as a new standalone sample family.

Current `master` still ships no standalone `samples/zigux/*cmdline*`, `samples/zigux/*argv*`, or `samples/zigux/*rbtree*` Phase 5 reference sample.
Current `master` does carry one bounded `*string*` and `*format*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace-events` anchor and its selected-string plus `iter=%d` formatting cue instead of treating it as standalone string-helper delivery.

## Phase 9 runtime pilot family

The directly readable runtime-facing sample-root evidence on current `master` belongs to the separate later runtime lane:

* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`
* `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`

Keep those files in the separate Phase 9 runtime packet instead of counting them as extra Phase 5 samples.