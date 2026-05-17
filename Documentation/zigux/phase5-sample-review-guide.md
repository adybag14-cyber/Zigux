# Phase 5 Sample Review Guide

This guide keeps the roadmap-backed Phase 5 sample lane reviewable without letting a stale shared reminder surface override newer direct packet proof.

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

Fresh repo-first inspection on 2026-05-17 confirmed that the current trace-events packet on `master` is directly readable again through the public current-`master` sample-plus-tests packet even though the authenticated contents route stayed flaky for part of the same family:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
* `Documentation/zigux/phase5-trace-events-sample-survey.md`
* `samples/zigux/trace_events_sample.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `zigux/tests/README.md`
* `zigux/tests/phase5_trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample_manifest.json`
* `zigux/tests/phase5_trace_events_sample_survey.zig`
* `zigux/tests/phase5_build.zig`

Treat that restored direct trace-events packet together with the bounded formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig` as the current concrete trace-events evidence in this lane.
Keep the formatting companion explicit as a bounded sibling cue inside the returned direct packet rather than as a replacement for it.

For the shared tracing and probe lane, ground reviewer guidance in the current direct-readback packet above plus these shared reminder surfaces:

* `Documentation/zigux/phase5-kretprobe-sample-survey.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `scripts/zigux/README.md`
* `zigux/tests/README.md`

Keep those shared surfaces honest about the restored direct trace-events packet, the bounded formatting companion, and the current public-tree-backed `zigux/tests/phase5_build.zig` shared route instead of treating the trace-events anchor as a formatting-only gap.

## Tracing and probe posture

For `kretprobe`, follow the restored direct packet recorded in `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, and `zigux/tests/phase5_kretprobe_example_manifest.json`, while keeping `zigux/tests/phase5_build.zig` framed only as current public-tree-backed companion evidence.

For `trace_events`, follow the restored direct packet through `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and the current public-tree-backed `zigux/tests/phase5_build.zig` route, while keeping the bounded formatting companion explicit through `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` and `samples/zigux/trace_events_string_formatting_sample.zig`.

Use the shared docs to preserve these bounded cues:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` keeps the selected-string plus `iter=%d` formatting cue bounded to the trace-events packet instead of turning it into a fifth Phase 5 sample
* `samples/zigux/trace_events_sample.zig` keeps the restored direct anchor packet explicit through `formattedMessage()`, `runPayloadBoundaryReplay()`, `runCallbackBoundaryRecoveryReplay()`, `runStringFormattingCycleReplay()`, `runLifecycleBoundaryReplay()`, and `lifecycleSummary()`
* `samples/zigux/trace_events_string_formatting_sample.zig` keeps the sibling formatting companion explicit through `selectedStringForIteration(...)`, the exact `iter=%d` buffer print, and the non-allocating lifecycle boundary around the bounded replay instead of standing in for the whole trace-events packet
* `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, and `zigux/tests/phase5_kretprobe_example_manifest.json` keep the restored non-runtime kretprobe packet explicit without widening into the Phase 9 runtime family

## Approved idiom gap

Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample, and it still ships no standalone broad `*format*` Phase 5 reference sample outside the bounded trace-events cues carried by `samples/zigux/trace_events_sample.zig` and `samples/zigux/trace_events_string_formatting_sample.zig`.

Keep the approved formatting idiom bounded to the selected-string plus `iter=%d` reminder carried by the trace-events review packet:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`

Do not describe that formatting cue as a fifth Phase 5 sample, a standalone formatting-helper port, or the whole proof of the trace-events packet.

## Review posture

Because current `master` now directly exposes the restored trace-events sample packet plus the bounded formatting companion, same-lane follow-through should stay inside these bounded categories:

* one trace-events reminder-surface truthfulness repair at a time
* one trace-events approved-idiom-gap repair at a time
* one trace-events sample-root, tests-root, or shared-build reminder alignment repair at a time

Avoid:

* treating the restored direct trace-events packet as missing when current public rereads already recover the sample, focused test, manifest, survey, and shared-build companions
* broadening the lane into runtime-loader, module-registration, procfs, sysfs, workqueue, or ring-buffer claims
* treating Phase 9 runtime samples as extra Phase 5 evidence
* treating the trace-events packet as permission to reopen unrelated bytestream, kobject, or kretprobe reminder work here

## Boundary reminders

Phase 5 stays non-runtime.

Keep later runtime-facing sample work under the separate Phase 9 lane.

Keep these no-extra-sample reminders explicit too:

* `samples/zigux/trace_events_string_formatting_sample.zig` is a bounded trace-events formatting companion, not a fifth Phase 5 anchor and not a standalone helper packet
* there is no standalone `samples/zigux/*string*` Phase 5 reference sample on current `master` outside the returned trace-events packet and its bounded formatting companion
* there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`
* there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`

Respect the freeze map too.
Do not widen Phase 5 work toward `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.