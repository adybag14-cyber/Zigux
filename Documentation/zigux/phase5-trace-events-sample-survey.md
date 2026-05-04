# Phase 5 Trace-Events Sample Survey

This sample-backed survey note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_SLICE=trace-events-reference-sample-starter`
- `PHASE5_LANE_KEY=P5-L24`
- `PHASE5_SURVEYED_COMMIT=d46fb91493e6e9126d5111bf0e5b21184e0ec1d1`
- scope: roadmap-vs-repo sample delivery, approved payload and callback idiom guidance, contributor refresh cues, and exact bounded checks for the landed `samples/zigux/` trace-events replay
- product boundary:
  - `Documentation/zigux/phase5-trace-events-sample-survey.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/trace_events_sample.zig`
  - `zigux/tests/phase5_build.zig`
  - `zigux/tests/phase5_trace_events_sample.zig`
  - `zigux/tests/phase5_trace_events_sample_manifest.json`
  - `zigux/tests/phase5_trace_events_sample_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/trace_events/trace-events-sample.c` as one of the Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection now shows that current `master` carries all four roadmap-approved bounded Phase 5 reference samples under `samples/zigux/`, including the landed `trace_events_sample` slice. The trace-events-specific job is no longer missing sample delivery; it is to keep this approved payload-and-callback idiom reviewable and repeatable, with its exact checks and non-goals kept honest now that the broader Phase 5 anchor set is complete.

## Survey findings

- `samples/trace_events/trace-events-sample.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a runtime slice.
- the Linux sample mixes four concerns:
  - payload shaping for the `foo_bar`, template, conditional, and relative-location tracepoint families
  - string and array selection derived from `cnt % 5`
  - function-callback registration and unregister balance for the second thread path
  - real runtime substrate through `CREATE_TRACE_POINTS`, tracepoint macros, `kthread_run()`, `schedule_timeout()`, and module init or exit hooks
- the honest Phase 5 move is to make the payload shape, chosen string, formatted message, family counts, public selected-string slot and payload-length cues, and callback-registration balance reviewable in memory while leaving runtime thread creation and tracepoint macro wiring out of scope.
- the shared sample-root catalog in `samples/zigux/README.md` is part of that boundary now, because it is the shortest shared place to keep the four Phase 5 reference readings visibly separate from the later runtime starters that live in the same directory.
- the shared sample-root catalog now also carries a dedicated trace-events review-packet stanza, so contributors can refresh the exact replay contract, callback-balance cues, and out-of-scope runtime claims without having to infer them from the deeper survey note alone.
- the shared tests-root guide in `zigux/tests/README.md` is part of that same contributor packet now, because it names the direct `zig test samples/zigux/trace_events_sample.zig` replay, the paired `zig test zigux/tests/phase5_trace_events_sample_survey.zig` replay, and the wider Phase 5 boundary cues that keep this landed sample distinct from the separate Phase 7 helper-only evidence and the later Phase 9 runtime follow-ons.
- the same contributor packet also has to keep the sample-owned `zigux/tests/phase5_trace_events_sample.zig` replay explicit as a `phase5_build.zig`-wired check: that focused replay imports `trace_events_reference_sample`, so reviewers should treat it as a focused shared-build replay rather than a standalone `zig test` command.
- the same trace-events family boundary should stay explicit in reviewer-facing prose too: current `master` ships `samples/zigux/runtime_trace_events.zig` as a sample-only blocked Phase 9 pilot, and the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is shipped now as a separate follow-on surface whose runtime-substrate handoff still stays blocked, so the landed `trace_events_sample` packet remains the non-runtime reference idiom for this family.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/trace_events_sample.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `TraceEventsReferenceSample.descriptor()`
- it models only the bounded array payload, selected string, public selected-string slot and payload-length cues, public main-path and callback-path iteration cues, the `iter=%d` message, and the dedicated `runStringFormattingCycleReplay()` summary that keeps the full modulo-selected string cycle reviewable through one public five-case replay
- it now makes the replay summary itself carry explicit `vararg_payload_path_checked`, `relative_location_path_checked`, and `function_callback_path_checked` flags so reviewers do not have to infer those paths from private sample state
- it now exposes `lifecycleSummary()` so the public review surface can read stage plus init, replay, and exit counts, registration depth, and total event calls without private field access
- it uses a tiny `init()` -> `replayMainIteration()` -> `registerFunctionCallback()` -> `replayFunctionIteration()` -> `unregisterFunctionCallback()` -> `exit()` lifecycle so ownership and teardown stay explicit, including unregister-underflow rejection before a callback is armed and `OutstandingRegistration` rejection if `exit()` is attempted while one callback is still live
- it provides one bounded self-check through `runAnchorReplay()` instead of implying a runtime-ready trace-events module

The exact checks currently recorded in `zigux/tests/phase5_trace_events_sample_manifest.json`, exercised directly through `zigux/tests/phase5_trace_events_sample.zig`, and exercised through `zigux/tests/phase5_build.zig` are:

- the in-memory sample keeps `samples/trace_events/trace-events-sample.c` explicit and stays in the non-runtime sample lane
- `runAnchorReplay()` formats iter=7, selects Gandalf, and exposes selected-string slot `2` from the Linux `random_strings` table for `len = 2`
- the dedicated `runStringFormattingCycleReplay()` summary replays counts `0` through `4` through five public cases so the full modulo-selected string cycle stays explicit: `Mother Goose`, `Snoopy`, `Gandalf`, `Frodo`, and `One ring to rule them all`
- the replay summary now exposes main iteration `7` and function-callback iteration `9` so the Linux `cnt`-driven split between the two thread paths stays reviewable without reading private sample state
- the replay exposes payload length `2` and keeps the `1,2` payload prefix plus a zero sentinel so the Linux array idiom remains reviewable in memory
- the replay records the `0xdeadbeef` bitmask word and marks the relative-location payload path as checked in the replay summary
- the replay marks the vararg payload path as checked so the `fmt` plus `va_list` `trace_foo_bar` idiom stays explicit in the public replay summary
- the replay records six main-thread event calls and two function-callback event calls for a total of eight bounded tracepoint-family calls
- the public `lifecycleSummary()` reports `replay_complete` with init, replay, and exit counts `1,1,0`, zero registration depth, and eight total event calls after `runAnchorReplay()`, then reports `exited` with counts `1,1,1` after `exit()`
- the replay summary keeps the exact `checked_focus` order `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` so the approved review surface stays visible without reading private sample state
- the function-callback replay requires registration first, marks that callback path as checked, and restores the registration balance to zero before the sample completes
- before a callback is registered, the in-memory sample rejects `replayFunctionIteration()` with `FunctionCallbackNotRegistered` so the callback-entry boundary stays reviewable without implying tracepoint enablement parity
- the in-memory callback lane rejects a second `registerFunctionCallback()` call while already registered so the Phase 5 sample keeps one live callback registration before balance returns to zero
- before balance returns to zero, the same ownership lane also rejects `unregisterFunctionCallback()` underflow before registration and rejects `exit()` with `OutstandingRegistration` while a callback remains armed
- after `exit()` the sample rejects later `replayMainIteration()`, `registerFunctionCallback()`, `replayFunctionIteration()`, and `unregisterFunctionCallback()` calls

## Latest verification snapshot

- inspected `master` head: `d46fb91493e6e9126d5111bf0e5b21184e0ec1d1`
- attached Zig toolchain: `0.17.0-dev.87+9b177a7d2`
- exact commands and observed results:
  - `zig test samples/zigux/trace_events_sample.zig`
    - `1/5 trace_events_sample.test.trace-events sample replay keeps the anchor reviewable and non-runtime...OK`
    - `2/5 trace_events_sample.test.trace-events sample replays every modulo-selected string and formatted message through one bounded replay...OK`
    - `3/5 trace_events_sample.test.trace-events sample exposes callback boundary recovery as one bounded replay...OK`
    - `4/5 trace_events_sample.test.trace-events sample rejects every mutable entry point after exit...OK`
    - `5/5 trace_events_sample.test.trace-events sample keeps callback registration single-live...OK`
    - `All 5 tests passed.`
  - `zig test zigux/tests/phase5_trace_events_sample_survey.zig`
    - `1/2 phase5_trace_events_sample_survey.test.phase 5 trace-events manifest records the exact bounded checks...OK`
    - `2/2 phase5_trace_events_sample_survey.test.phase 5 trace-events contributor docs stay aligned with the shipped review surface...OK`
    - `All 2 tests passed.`
  - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
    - `Build Summary: 18/18 steps succeeded; 29/29 tests passed`
    - `phase5-bytestream-fifo-tests 5 pass (5 total)`
    - `phase5-bytestream-fifo-survey-tests 2 pass (2 total)`
    - `phase5-kobject-example-tests 5 pass (5 total)`
    - `phase5-kobject-example-survey-tests 2 pass (2 total)`
    - `phase5-kretprobe-example-sample-tests 1 pass (1 total)`
    - `phase5-kretprobe-example-tests 5 pass (5 total)`
    - `phase5-kretprobe-example-survey-tests 2 pass (2 total)`
    - `phase5-trace-events-sample-tests 5 pass (5 total)`
    - `phase5-trace-events-sample-survey-tests 2 pass (2 total)`
- the focused `zigux/tests/phase5_trace_events_sample.zig` replay remains part of the shipped `phase5_build.zig` packet rather than a standalone direct `zig test` command, so this note keeps that surface explicit without overstating a separate direct replay.

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/trace_events_sample.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `TraceEventsReferenceSample.descriptor()` still name `samples/trace_events/trace-events-sample.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- does `zigux/tests/phase5_trace_events_sample_manifest.json` still pin `surveyed_commit` to the exact inspected `master` head instead of a floating branch label?
- do the sample-backed survey note, `samples/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md` still describe the same bounded replay contract and keep this Phase 5 sample visibly separate from the later Phase 9 runtime pilot?
- does `zigux/tests/phase5_trace_events_sample.zig` still stay wired through `zigux/tests/phase5_build.zig` via the `trace_events_reference_sample` import so the focused replay remains explicit even though it is not a standalone `zig test` entrypoint?
- do `zigux/tests/phase5_trace_events_sample_manifest.json` and `zigux/tests/phase5_trace_events_sample_survey.zig` still describe the exact selected-string-slot, payload-length, main-iteration, callback-iteration, vararg-payload, lifecycle-summary, message, relative-location, callback-path, and teardown contract run through `zigux/tests/phase5_build.zig`?
- does `lifecycleSummary()` still keep stage plus init, replay, and exit counts, registration depth, and total event calls visible without private field access?
- does `runStringFormattingCycleReplay()` still keep the full modulo-selected string cycle explicit across counts `0` through `4` through five public cases instead of reducing the review surface to only one reviewed string case?
- do the sample self-check and `zigux/tests/phase5_trace_events_sample.zig` still assert the exact `checked_focus` list and order instead of only its length?
- do the in-memory replay and `runStringFormattingCycleReplay()` still keep the array payload, selected string, selected-string slot, payload length, and `iter=%d` message reviewable instead of hiding them behind runtime thread state?
- does function-callback replay stay a single-live register-then-unregister idiom, including rejection of a second `registerFunctionCallback()` call while one callback is already registered, rather than implying `kthread_run()`, thread scheduling, or tracepoint enablement parity?
- before a callback is registered, does the sample still reject `replayFunctionIteration()` with `FunctionCallbackNotRegistered` so the callback-entry boundary stays explicit without relying on private state?
- before callback balance returns to zero, does the sample still reject `unregisterFunctionCallback()` underflow and reject `exit()` with `OutstandingRegistration` while a callback remains armed, so the ownership boundary is explicit before teardown?
- after `exit()`, do `replayMainIteration()`, `registerFunctionCallback()`, `replayFunctionIteration()`, and `unregisterFunctionCallback()` all stay rejected so the teardown boundary is fully reviewable instead of only partially implied?
- do the sample-backed survey note, `samples/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` still point reviewers back to the descriptor, manifest-backed survey, sample-backed survey note, shared sample-root catalog, shared tests-root guide, and shared `phase5_build.zig` entrypoint for this exact replay contract?
- if the sample behavior changes, is the manifest updated alongside the replay contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that `CREATE_TRACE_POINTS`, tracepoint macros from `trace-events-sample.h`, kernel scheduling, and module registration wiring remain out of scope for this Phase 5 sample?

## Recorded gap vs roadmap

The current gap is no longer "Zigux has no trace-events sample guidance." The more precise state is:

- the repo now has a reviewable Phase 5 `trace_events_sample` reference sample plus manifest-backed checks for payload shape, string selection, selected-string slot cues, payload-length cues, main-path and callback-path iteration cues, formatted messages, bounded family counts, lifecycle-summary counts, the exact `checked_focus` review surface, vararg-payload coverage, relative-location coverage, callback-path coverage, and teardown
- this sample must remain visibly separate from the later Phase 9 runtime `trace-events` starter so contributors do not over-claim runtime substrate coverage
- the Phase 5 roadmap's four named sample anchors are now all represented by bounded `samples/zigux/` reference readings, but that does not close the separate Phase 9 runtime pilot tranche
- this approved payload-and-callback idiom is now pinned to `PHASE5_SURVEYED_COMMIT=d46fb91493e6e9126d5111bf0e5b21184e0ec1d1` so the sample-backed survey note, latest verification snapshot, sample-root catalog boundary, manifest-backed survey, and shared `phase5_build.zig` replay all point at the same inspected `master` head

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux trace-events sample
   - `rg -n "samples/trace_events/trace-events-sample.c|Phase 5" Documentation/zigux samples`
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

Leave this trace-events survey lane parked unless fresh repo inspection finds one more directly coupled replay-summary or contributor-guidance wording drift inside the landed `trace_events_sample` packet, while keeping the sample visibly separate from the later Phase 9 runtime pilot and preserving the exact verification packet recorded under `P5-L24`.
