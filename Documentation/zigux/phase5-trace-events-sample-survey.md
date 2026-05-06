# Phase 5 Trace-Events Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_SLICE=trace-events-reference-sample-starter`
- `PHASE5_LANE_KEY=P5-L16`
- `PHASE5_SURVEYED_COMMIT=beb1065024e41b266c1492d7be5a446c04e42368`
- scope: roadmap-vs-repo sample delivery, approved payload and callback idiom guidance, and exact bounded checks for the first `samples/zigux/` trace-events replay
- product boundary:
  - `Documentation/zigux/phase5-trace-events-sample-survey.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/trace_events_sample.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_trace_events_sample.zig`
  - `zigux/tests/phase5_trace_events_sample_manifest.json`
  - `zigux/tests/phase5_trace_events_sample_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/trace_events/trace-events-sample.c` as one of the Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection already showed landed Phase 5 FIFO, kobject, and kretprobe reference samples plus a later Phase 9 runtime `trace-events` starter. The missing Phase 5 job was still the earlier non-runtime reading of the same Linux anchor so reviewers can see the payload and callback idioms without confusing them with runtime substrate work.

## Survey findings

- `samples/trace_events/trace-events-sample.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a runtime slice.
- the Linux sample mixes four concerns:
  - payload shaping for the `foo_bar`, template, conditional, and relative-location tracepoint families
  - string and array selection derived from `cnt % 5`
  - function-callback registration and unregister balance for the second thread path
  - real runtime substrate through `CREATE_TRACE_POINTS`, tracepoint macros, `kthread_run()`, `schedule_timeout()`, and module init or exit hooks
- the honest Phase 5 move is to make the payload shape, chosen string, formatted message, family counts, and callback-registration balance reviewable in memory while leaving runtime thread creation and tracepoint macro wiring out of scope.
- current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample, so the approved formatting idiom cue in this lane remains the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`; standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/trace_events_sample.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `TraceEventsReferenceSample.descriptor()`
- it models only the bounded array payload, selected string, `iter=%d` message, `0xdeadbeef` bitmask word, conditional-family coverage, and one balanced register-then-unregister callback idiom in memory
- it now exposes `runPayloadBoundaryReplay()` so the count-4 payload prefix, zero sentinel, `iter=4` message, and `One ring to rule them all` branch stay reviewable through a public helper instead of private field inspection
- it now makes the replay summary itself carry explicit `vararg_payload_path_checked`, `relative_location_path_checked`, and `function_callback_path_checked` flags so reviewers do not have to infer those paths from private sample state
- it uses a tiny `init()` -> `replayMainIteration()` -> `registerFunctionCallback()` -> `replayFunctionIteration()` -> `unregisterFunctionCallback()` -> `exit()` lifecycle so ownership and teardown stay explicit
- it keeps its sample-owned replay entrypoints bounded through `runAnchorReplay()` and `runPayloadBoundaryReplay()` instead of implying a runtime-ready trace-events module

The exact checks currently recorded in `zigux/tests/phase5_trace_events_sample_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the in-memory sample keeps `samples/trace_events/trace-events-sample.c` explicit and stays in the non-runtime reference-sample lane
- `runAnchorReplay()` formats `iter=7` and selects `Gandalf` from the Linux `random_strings` table for `len = 2`
- the replay keeps the `1,2` payload prefix plus a zero sentinel so the Linux array idiom remains reviewable in memory
- `runPayloadBoundaryReplay()` keeps the count-4 `1,2,3,4` payload prefix, zero sentinel, `iter=4` message, and `One ring to rule them all` selection reviewable through a public helper instead of private sample state
- the replay records the `0xdeadbeef` bitmask word and marks the relative-location payload path as checked in the replay summary
- the replay marks the vararg payload path as checked so the `fmt` plus `va_list` `trace_foo_bar` idiom stays explicit in the public replay summary
- the replay records six main-thread event calls and two function-callback event calls for a total of eight bounded tracepoint-family calls
- the function-callback replay requires registration first, marks that callback path as checked, and restores the registration balance to zero before the sample completes
- after `exit()` the sample rejects later payload replay or callback-registration calls

## Latest verification posture

Fresh live current-`master` inspection on 2026-05-06 confirmed that the shipped trace-events packet still presents one repo-local, non-runtime review surface rather than a runtime handoff claim.

- `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, and `zigux/tests/phase5_build.zig` still describe the same bounded payload, formatting, callback, and teardown contract
- the public `runPayloadBoundaryReplay()` helper, `formattedMessage()` surface, replay-summary callback-path markers, and registration-balance cue all remain explicit on current `master`
- the survey gate still enforces repo-local review guidance by rejecting `/workspace/agent_files` leakage and by keeping the no-standalone-format-sample boundary tied to the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet
- the shared review route remains `zig build test --build-file zigux/tests/phase5_build.zig --summary all` plus `make -C zigux phase5`, while the sample stays visibly separate from the Phase 9 `runtime_trace_events` family

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/trace_events_sample.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `TraceEventsReferenceSample.descriptor()` still name `samples/trace_events/trace-events-sample.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_trace_events_sample_manifest.json` and `zigux/tests/phase5_trace_events_sample_survey.zig` still describe the exact vararg-payload, message, relative-location, callback-path, and teardown contract run through `zigux/tests/phase5_build.zig`?
- does the contributor packet still name `runPayloadBoundaryReplay()` as the approved public count-4 payload-boundary helper instead of implying private field inspection for the `1,2,3,4` prefix, zero sentinel, `iter=%d` replay, and selected-string branch?
- does the in-memory replay still keep the array payload, selected string, and `iter=%d` message reviewable instead of hiding them behind runtime thread state?
- does function-callback replay stay a balanced register-then-unregister idiom rather than implying `kthread_run()`, thread scheduling, or tracepoint enablement parity?
- do the sample-owned prompts keep the exact `checked_focus` order, the balanced register-then-unregister callback flow, `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, and post-exit replay rejection explicit instead of leaving those callback-boundary cues implied?
- if the sample behavior changes, is the manifest updated alongside the replay contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that `CREATE_TRACE_POINTS`, tracepoint macros from `trace-events-sample.h`, kernel scheduling, and module registration wiring remain out of scope for this Phase 5 sample?
- if this survey note moves again, does it still keep the latest verification posture repo-local and explicit about the shared `phase5_build.zig` route plus the separate Phase 9 `runtime_trace_events` family?
- if this survey note moves again, does it still say there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample, and does it keep the selected-string plus `iter=%d` replay tied to the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet instead of implying a new standalone formatting helper sample?

## Recorded gap vs roadmap

The current gap is no longer "Zigux has no trace-events sample guidance." The more precise state is:

- the repo now has a reviewable Phase 5 `trace_events_sample` reference sample plus manifest-backed checks for payload shape, string selection, formatted messages, bounded family counts, vararg-payload coverage, relative-location coverage, callback-path coverage, the public count-4 payload-boundary helper, and teardown
- the repo still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample, so reviewers should keep treating the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` as the approved formatting idiom cue while standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet
- this sample must remain visibly separate from the later Phase 9 runtime `trace-events` starter so contributors do not over-claim runtime substrate coverage
- the Phase 5 roadmap's four named sample anchors are now all represented by bounded `samples/zigux/` reference readings, but that does not close the separate Phase 9 runtime pilot tranche

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux trace-events sample
   - `rg -n "samples/trace_events/trace-events-sample.c|PHASE5_SLICE|phase5_trace_events_sample|Phase 5" Documentation/zigux samples/zigux zigux/tests`
2. confirm the current `samples/zigux/` surface keeps the Phase 5 and Phase 9 trace-events lanes distinct
   - `find samples/zigux -maxdepth 1 -type f | sort | rg "trace_events_sample|runtime_trace_events"`
3. run the exact bounded Phase 5 sample checks
   - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`

## Non-goals

This survey does not yet claim:

- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity

## Next bounded step

Keep this trace-events note packet parked unless fresh repo inspection shows another same-family helper or contributor-guidance drift on current `master`. 