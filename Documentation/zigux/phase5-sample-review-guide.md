# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 sample lane reviewable without treating older sample-root packets as current proof when the repo no longer exposes those files directly.

## Purpose

Use this guide when a change touches Phase 5 contributor guidance, one of the approved Linux sample anchors, or the shared tracing and probe reviewer surfaces.

The Phase 5 goal stays narrow:

* keep the approved Zigux idioms reviewable
* keep ownership and lifetime cues explicit
* keep exact review surfaces visible
* avoid widening non-runtime samples into runtime-substrate claims

## Roadmap anchors

Phase 5 is still scoped by the same four Linux sample anchors named in the roadmap:

* `samples/kfifo/bytestream-example.c`
* `samples/kobject/kobject-example.c`
* `samples/kprobes/kretprobe_example.c`
* `samples/trace_events/trace-events-sample.c`

Treat those four anchors as the approved Phase 5 destination set unless the roadmap changes.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-17 found that `samples/zigux/README.md` now says the current sample root directly exposes these files:

* `samples/zigux/README.md`
* `samples/zigux/runtime_trace_events.zig`
* `samples/zigux/runtime_trace_events_unregistered_gate.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`

That means the four non-runtime Phase 5 sample-root ports are not current direct sample-root proof on `master`, even though the roadmap-backed anchors remain approved.

For the shared tracing and probe lane, keep reviewer guidance grounded in the reminder surfaces that are still present:

* `Documentation/zigux/phase5-sample-lane-sequencing.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `zigux/tests/README.md`

The same reread also confirmed that authenticated contents reads now return missing for these older dedicated survey notes:

* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/phase5-trace-events-sample-survey.md`

Keep those shared surfaces honest about the gap between the roadmap-approved anchors and the files that current `master` directly exposes.

## Tracing and probe posture

For `kretprobe` and `trace_events`, treat the Phase 5 anchors as approved reference targets and reviewer reminders unless a fresh reread proves the sample-root ports have returned.

Use the shared docs to preserve these bounded cues:

* `zigux/tests/README.md` keeps the direct-readback gap visible by recording that current authenticated readback still returns missing for `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, `zigux/tests/phase5_kretprobe_example_survey.zig`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and `zigux/tests/phase5_build.zig`
* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` keeps the tracing-side formatting cue visible without claiming direct sample-root proof from `samples/zigux/trace_events_sample.zig`
* `samples/zigux/README.md` remains the source of truth for whether those non-runtime sample-root files are directly present on current `master`

## Approved idiom gap

Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample, and it still ships no standalone `*format*` reference sample beyond the bounded trace-events formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig`.

Keep the approved formatting idiom bounded to the selected-string plus `iter=%d` reminder carried by the trace-events review packet:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`

Do not describe that formatting cue as a fifth Phase 5 sample, a standalone formatting-helper port, or proof that the trace-events sample-root file is currently present.

## Review posture

Because current `master` does not directly expose the non-runtime Phase 5 sample-root files, same-lane follow-through should stay inside these bounded categories:

* one shared reminder-surface truthfulness repair at a time
* one survey-note or approved-idiom-gap repair at a time
* one tests-root reminder alignment repair at a time

Avoid:

* inventing direct sample-root proof that `samples/zigux/README.md` does not confirm
* broadening the lane into runtime-loader, module-registration, procfs, sysfs, workqueue, or ring-buffer claims
* treating Phase 9 runtime samples as extra Phase 5 evidence

## Boundary reminders

Phase 5 stays non-runtime.

Keep later runtime-facing sample work under the separate Phase 9 lane.

Keep these no-extra-sample reminders explicit too:

* `samples/zigux/trace_events_string_formatting_sample.zig` is a bounded trace-events formatting companion, not a fifth Phase 5 anchor and not a standalone helper packet
* there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master` outside that trace-events-bound companion
* there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`

Respect the freeze map too.
Do not widen Phase 5 work toward `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.