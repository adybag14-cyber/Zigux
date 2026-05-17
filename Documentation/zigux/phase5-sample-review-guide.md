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

Fresh repo-first inspection on 2026-05-17 confirmed that the current trace-events packet is directly readable on `master` through these packet-local surfaces:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
* `Documentation/zigux/phase5-trace-events-sample-survey.md`
* `samples/zigux/trace_events_sample.zig`
* `samples/zigux/trace_events_string_formatting_sample.zig`
* `zigux/tests/phase5_trace_events_sample.zig`
* `zigux/tests/phase5_trace_events_sample_manifest.json`
* `zigux/tests/phase5_trace_events_sample_survey.zig`

That direct packet proof is stronger than the current shared sample-root reminder wording in `samples/zigux/README.md`, which still lags the landed non-runtime trace-events packet.

For the shared tracing and probe lane, ground reviewer guidance in the packet-local proof above plus these shared reminder surfaces:

* `Documentation/zigux/phase5-sample-lane-sequencing.md`
* `Documentation/zigux/phase5-sample-review-guide.md`
* `Documentation/zigux/review-checklist.md`
* `samples/zigux/README.md`
* `zigux/tests/README.md`

Keep those shared surfaces honest about direct packet proof that is already readable today, and treat stale README or authenticated-readback gaps as reminder drift rather than as evidence that the trace-events packet disappeared.

## Tracing and probe posture

For `kretprobe`, keep the Phase 5 anchor in the reminder-only posture unless a fresh reread proves the direct sample packet is back.

For `trace_events`, follow the landed direct packet instead of the stale README posture.

Use the shared docs to preserve these bounded cues:

* `Documentation/zigux/phase5-trace-events-sample-survey.md` keeps the direct packet inventory explicit and records when `zigux/tests/phase5_build.zig` is only public-tree-backed companion evidence instead of authenticated direct proof
* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` keeps the selected-string plus `iter=%d` formatting cue bounded to the trace-events packet instead of turning it into a fifth Phase 5 sample
* `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, and `zigux/tests/phase5_trace_events_sample_survey.zig` keep the current helper names and lifecycle cues explicit: `runAnchorReplay()`, `runPayloadBoundaryReplay()`, `runCallbackBoundaryRecoveryReplay()`, `runStringFormattingCycleReplay()`, `runLifecycleBoundaryReplay()`, `lifecycleSummary()`, the exact `checked_focus` order, and the callback-boundary rejection path through `OutstandingRegistration`
* `zigux/tests/phase5_trace_events_sample_manifest.json` keeps the same callback-boundary and armed-exit expectations reviewable in machine-readable form

## Approved idiom gap

Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample, and it still ships no standalone broad `*format*` Phase 5 reference sample outside the bounded trace-events formatting companion at `samples/zigux/trace_events_string_formatting_sample.zig`.

Keep the approved formatting idiom bounded to the selected-string plus `iter=%d` reminder carried by the trace-events review packet:

* `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`

Do not describe that formatting cue as a fifth Phase 5 sample, a standalone formatting-helper port, or the whole proof of the trace-events packet.

## Review posture

Because current `master` now directly exposes the trace-events packet, same-lane follow-through should stay inside these bounded categories:

* one trace-events reminder-surface truthfulness repair at a time
* one trace-events survey-note or approved-idiom-gap repair at a time
* one trace-events tests-root reminder alignment repair at a time

Avoid:

* letting stale `samples/zigux/README.md` wording overrule the direct trace-events packet
* broadening the lane into runtime-loader, module-registration, procfs, sysfs, workqueue, or ring-buffer claims
* treating Phase 9 runtime samples as extra Phase 5 evidence
* treating the trace-events packet as permission to reopen unrelated bytestream, kobject, or kretprobe reminder work here

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