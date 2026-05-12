# Phase 5 Trace-Events Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_SLICE=trace-events-reference-sample-starter`
- `PHASE5_LANE_KEY=P5-L24`
- `PHASE5_SURVEYED_COMMIT=c9b956c155281407bf86bf56d122b08d6fc634ea`
- scope: roadmap-vs-repo sample delivery, exact public helper, callback, and ownership-lifetime idiom guidance, plus the bounded formatting cue already shipped in the current non-runtime trace-events packet
- product boundary:
  - `Documentation/zigux/phase5-trace-events-sample-survey.md`
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`
  - `samples/zigux/README.md`
  - `samples/zigux/trace_events_sample.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_trace_events_sample.zig`
  - `zigux/tests/phase5_trace_events_sample_manifest.json`
  - `zigux/tests/phase5_trace_events_sample_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/trace_events/trace-events-sample.c` as one of the Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Current `master` already carries that anchor as `samples/zigux/trace_events_sample.zig` inside the shipped four-sample Phase 5 packet, while the separate Phase 9 `runtime_trace_events` family stays distinct. The remaining job in this note is to keep the sample-backed review contract honest without implying runtime substrate closure or inventing a standalone formatting sample that the roadmap never approved.

## Current packet

- the landed sample keeps the Linux anchor explicit through `TraceEventsReferenceSample.descriptor()` and stays in the non-runtime reference-sample lane
- the in-memory replay keeps the bounded array payload, selected string, formatted message, public payload and conditional helpers, callback-balance cues, ownership-and-lifetime summary, event-family counts, and post-exit rejection cues reviewable together in one small packet
- the formatting cue for this lane is still the selected-string plus `iter=%d` replay inside `samples/zigux/trace_events_sample.zig`
- the ownership half of the packet stays explicit through `ownershipSummary()` plus sample-owned `runOwnershipReplay()`, which keep the `cold` -> `initialized` -> `replay_complete` -> `exited` lifecycle and the final `Gandalf` plus `iter=7` snapshot readable beside the tracing cues
- current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample, so standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet
- the shared contributor surface for this sample remains broader than the sample file alone: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `.github/workflows/zigux-bootstrap.yml`, and the shared `zigux/tests/phase5_build.zig` route all need to keep the same four-sample non-runtime packet and the same Phase 5 versus Phase 9 boundary visible

## Exact checks

The manifest-backed contract for the current trace-events sample packet is:

- the in-memory sample names `samples/trace_events/trace-events-sample.c` and stays in the non-runtime reference-sample lane
- `runAnchorReplay()` formats `iter=7` and selects `Gandalf` from the Linux `random_strings` table for `len = 2`
- the replay keeps a `1,2` payload prefix with a zero sentinel in the next slot so the Linux array idiom remains reviewable in memory
- the replay records the `0xdeadbeef` bitmask word and marks the relative-location payload path as checked in the replay summary
- the replay marks the vararg payload path as checked so the `fmt` plus `va_list` `trace_foo_bar` idiom stays explicit in the public replay summary
- `ownershipSummary()` plus sample-owned `runOwnershipReplay()` keep the `cold`, `initialized`, `replay_complete`, and `exited` lifecycle plus the final `Gandalf` plus `iter=7` snapshot explicit in the same bounded packet
- the replay records six main-thread event calls and two function-callback event calls for a total of eight bounded tracepoint-family calls
- the function-callback replay requires registration first, marks that callback path as checked, restores the registration balance to zero before the sample completes, and keeps `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection explicit
- after `exit()` the sample rejects later payload replay or callback-registration calls

## Latest verification snapshot

Fresh current-`master` reread on 2026-05-12 compared the live Phase 5 trace-events note packet against the roadmap, the bootstrap ledger, the current shared review surfaces, and the still-readable survey note packet.

- connector-backed readback confirmed the current survey note had drifted behind the shared `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase5-sample-review-guide.md`, and `samples/zigux/README.md` wording, so this note now names the exact public helper surfaces, ownership replay, and callback-boundary cues those reminder surfaces already keep explicit
- connector-backed readback also confirmed that the shared `zigux/tests/phase5_build.zig` route, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase5-test`, and `make -C zigux phase5` still describe the same bounded non-runtime Phase 5 packet and still keep the later `runtime_trace_events` family separate
- the note keeps the no-standalone-format-sample boundary explicit so the selected-string plus `iter=%d` replay remains the approved Phase 5 formatting cue and does not drift into a fifth sample claim
- no local `zig` replay was run in this lane because this scheduled environment did not provide a normal writable Zigux checkout or direct raw-file fetch path for truthful end-to-end reruns; validation for this note update stayed on connector-backed repo inspection and roadmap-to-note alignment

## Contributor refresh prompts

When `samples/zigux/trace_events_sample.zig` or its directly coupled Phase 5 test packet moves, keep these prompts explicit:

- does `TraceEventsReferenceSample.descriptor()` still name `samples/trace_events/trace-events-sample.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `formattedMessage()`, `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, `ownershipSummary()`, and sample-owned `runOwnershipReplay()` still expose the exact public packet reviewers should point to first?
- does the exact `checked_focus` order stay `descriptor_anchor`, `selected_string_cycle`, `formatted_message_surface`, `conditional_family_markers`, `callback_balance`, and `ownership_and_lifetime`?
- do `zigux/tests/phase5_trace_events_sample_manifest.json` and `zigux/tests/phase5_trace_events_sample_survey.zig` still describe the same vararg-payload, message, relative-location, callback-path, ownership-lifetime, and teardown contract run through `zigux/tests/phase5_build.zig`?
- does the sample still keep the selected string and `iter=%d` message reviewable in memory instead of hiding them behind runtime thread state?
- does function-callback replay still require registration first, restore balance to zero, keep `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection explicit, and avoid implying `kthread_run()`, scheduling, or tracepoint enablement parity?
- if the sample behavior changes, is the manifest updated alongside the replay contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that `CREATE_TRACE_POINTS`, tracepoint macros from `trace-events-sample.h`, kernel scheduling, and module registration wiring remain out of scope for this Phase 5 sample?
- if the broader shared review packet moves, does it still keep the exact same four-sample Phase 5 packet, the shared `zig build test --build-file zigux/tests/phase5_build.zig --summary all` replay, the local `make -C zigux phase5-test` and `make -C zigux phase5` wrappers, the no-standalone-format-sample boundary, and the separate Phase 9 `runtime_trace_events` family explicit?

## Non-goals

This survey still does not claim:

- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity

## Next bounded step

Keep this trace-events survey packet parked unless fresh repo inspection shows this note drifting again from the shared trace-events reminder surfaces or the directly coupled manifest-backed prompts on current `master`. If that happens, reopen only for the next smallest same-family note or survey sync and keep the formatting boundary tied to the landed selected-string plus `iter=%d` replay rather than widening into a standalone formatting sample claim.
