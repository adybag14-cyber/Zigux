# Phase 5 Trace-Events Sample Survey

This sample-backed survey note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status

- `PHASE5_STATUS=active`
- `PHASE5_SLICE=trace-events-reference-sample-starter`
- scope: roadmap-vs-repo sample delivery, approved payload and callback idiom guidance, contributor refresh cues, and exact bounded checks for the landed `samples/zigux/` trace-events replay
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

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/trace_events_sample.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `TraceEventsReferenceSample.descriptor()`
- it models only the bounded array payload, selected string, public main-path and callback-path iteration cues, `iter=%d` message, `0xdeadbeef` bitmask word, conditional-family coverage, and one single-live register-then-unregister callback idiom in memory
- it now makes the replay summary itself carry explicit `vararg_payload_path_checked`, `relative_location_path_checked`, and `function_callback_path_checked` flags so reviewers do not have to infer those paths from private sample state
- it uses a tiny `init()` -> `replayMainIteration()` -> `registerFunctionCallback()` -> `replayFunctionIteration()` -> `unregisterFunctionCallback()` -> `exit()` lifecycle so ownership and teardown stay explicit
- it provides one bounded self-check through `runAnchorReplay()` instead of implying a runtime-ready trace-events module

The exact checks currently recorded in `zigux/tests/phase5_trace_events_sample_manifest.json` and exercised through `zigux/tests/phase5_build.zig` are:

- the in-memory sample keeps `samples/trace_events/trace-events-sample.c` explicit and stays in the non-runtime reference-sample lane
- `runAnchorReplay()` formats `iter=7` and selects `Gandalf` from the Linux `random_strings` table for `len = 2`
- the replay summary now exposes main iteration `7` and function-callback iteration `9` so the Linux `cnt`-driven split between the two thread paths stays reviewable without reading private sample state
- the replay keeps the `1,2` payload prefix plus a zero sentinel so the Linux array idiom remains reviewable in memory
- the replay records the `0xdeadbeef` bitmask word and marks the relative-location payload path as checked in the replay summary
- the replay marks the vararg payload path as checked so the `fmt` plus `va_list` `trace_foo_bar` idiom stays explicit in the public replay summary
- the replay records six main-thread event calls and two function-callback event calls for a total of eight bounded tracepoint-family calls
- the replay summary keeps the exact `checked_focus` order `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` so the approved review surface stays visible without reading private sample state
- the function-callback replay requires registration first, marks that callback path as checked, and restores the registration balance to zero before the sample completes
- the in-memory callback lane rejects a second `registerFunctionCallback()` call while already registered so the Phase 5 sample keeps one live callback registration before balance returns to zero
- after `exit()` the sample rejects later `replayMainIteration()`, `registerFunctionCallback()`, `replayFunctionIteration()`, and `unregisterFunctionCallback()` calls

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/trace_events_sample.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `TraceEventsReferenceSample.descriptor()` still name `samples/trace_events/trace-events-sample.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do the sample-backed survey note, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md` still describe the same bounded replay contract and keep this Phase 5 sample visibly separate from the later Phase 9 runtime pilot?
- do `zigux/tests/phase5_trace_events_sample_manifest.json` and `zigux/tests/phase5_trace_events_sample_survey.zig` still describe the exact main-iteration, callback-iteration, vararg-payload, message, relative-location, callback-path, and teardown contract run through `zigux/tests/phase5_build.zig`?
- do the sample self-check and `zigux/tests/phase5_trace_events_sample.zig` still assert the exact `checked_focus` list and order instead of only its length?
- does the in-memory replay still keep the array payload, selected string, and `iter=%d` message reviewable instead of hiding them behind runtime thread state?
- does function-callback replay stay a single-live register-then-unregister idiom, including rejection of a second `registerFunctionCallback()` call while one callback is already registered, rather than implying `kthread_run()`, thread scheduling, or tracepoint enablement parity?
- after `exit()`, do `replayMainIteration()`, `registerFunctionCallback()`, `replayFunctionIteration()`, and `unregisterFunctionCallback()` all stay rejected so the teardown boundary is fully reviewable instead of only partially implied?
- do the sample-backed survey note and `Documentation/zigux/review-checklist.md` still point reviewers back to the descriptor, manifest-backed survey, sample-backed survey note, and shared `phase5_build.zig` entrypoint for this exact replay contract?
- if the sample behavior changes, is the manifest updated alongside the replay contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that `CREATE_TRACE_POINTS`, tracepoint macros from `trace-events-sample.h`, kernel scheduling, and module registration wiring remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The current gap is no longer "Zigux has no trace-events sample guidance." The more precise state is:

- the repo now has a reviewable Phase 5 `trace_events_sample` reference sample plus manifest-backed checks for payload shape, string selection, main-path and callback-path iteration cues, formatted messages, bounded family counts, the exact `checked_focus` review surface, vararg-payload coverage, relative-location coverage, callback-path coverage, and teardown
- this sample must remain visibly separate from the later Phase 9 runtime `trace-events` starter so contributors do not over-claim runtime substrate coverage
- the Phase 5 roadmap's four named sample anchors are now all represented by bounded `samples/zigux/` reference readings, but that does not close the separate Phase 9 runtime pilot tranche

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux trace-events sample
   - `rg -n "samples/trace_events/trace-events-sample.c|Phase 5" Documentation/zigux samples /workspace/agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP\ \(1\).md`
2. confirm the current `samples/zigux/` surface keeps the Phase 5 and Phase 9 trace-events lanes distinct
   - `find samples/zigux -maxdepth 1 -type f | sort | rg "trace_events_sample|runtime_trace_events"`
3. run the focused self-check that keeps the in-memory replay behavior explicit
   - `zig test samples/zigux/trace_events_sample.zig`
4. run the manifest-backed survey gate from the repo root so the exact-check record stays readable
   - `zig test zigux/tests/phase5_trace_events_sample_survey.zig`
5. run the shared Phase 5 entrypoint for the full reference-sample lane
   - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`

## Non-goals

This survey does not yet claim:

- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity

## Next bounded step

Stay in the same Phase 5 samples-and-reference-patterns family and tighten one more directly coupled replay-summary or contributor-guidance edge only if fresh repo inspection shows real drift in the landed `trace_events_sample` contract on current `master`.
