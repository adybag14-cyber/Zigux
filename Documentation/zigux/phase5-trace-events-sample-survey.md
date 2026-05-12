# Phase 5 Trace-Events Sample Survey

This document tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_SLICE=trace-events-reference-sample-starter`
- `PHASE5_LANE_KEY=P5-L24`
- `PHASE5_SURVEYED_COMMIT=beb1065024e41b266c1492d7be5a446c04e42368`
- scope: roadmap-vs-repo sample delivery, approved payload, callback, and ownership-lifetime idiom guidance, and exact bounded checks for the first `samples/zigux/` trace-events replay
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

Fresh repo inspection now shows the bounded roadmap anchor already landed as `samples/zigux/trace_events_sample.zig` inside the four-sample Phase 5 packet, with the separate Phase 9 `runtime_trace_events` family still kept distinct. The remaining same-lane job is no longer to add a missing trace-events anchor; it is to keep the payload, callback, and ownership-lifetime idiom and its coupled contributor surfaces truthful without implying runtime substrate closure.

## Survey findings

- `samples/trace_events/trace-events-sample.c` is present on `master` and stays small enough to function as a reference-pattern anchor rather than a runtime slice.
- the Linux sample mixes four concerns:
  - payload shaping for the `foo_bar`, template, conditional, and relative-location tracepoint families
  - string and array selection derived from `cnt % 5`
  - function-callback registration and unregister balance for the second thread path
  - real runtime substrate through `CREATE_TRACE_POINTS`, tracepoint macros, `kthread_run()`, `schedule_timeout()`, and module init or exit hooks
- the honest Phase 5 move is to make the payload shape, chosen string, formatted message, family counts, callback-registration balance, lifecycle ownership, and post-exit rejection reviewable in memory while leaving runtime thread creation and tracepoint macro wiring out of scope.
- the live shared contributor packet for this landed sample is broader than the sample file and its paired manifest alone: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `.github/workflows/zigux-bootstrap.yml` already keep this note aligned with the same four-sample Phase 5 packet described from the docs root, checklist, sample root, scripts root, tests root, and workflow surface.
- the shared Phase 5 guide already keeps the workflow surface honest for this landed sample: `.github/workflows/zigux-bootstrap.yml` reruns only `zig build test --build-file zigux/tests/phase5_build.zig --summary all`, while `make -C zigux phase5-test` and `make -C zigux phase5` stay local Linux-style wrappers over that same shared build entrypoint.
- current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample, so the approved formatting idiom cue in this lane remains the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig`; standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/trace_events_sample.zig`.

Within the roadmap's Phase 5 `tracing examples` scope, this landed sample is the approved tracing-plus-ownership idiom reviewers should preserve on current `master`: payload shaping, selected-string formatting, callback balance, and teardown ownership cues stay reviewable together in one bounded non-runtime packet.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `TraceEventsReferenceSample.descriptor()`
- it models only the bounded array payload, selected string, `iter=%d` message, `0xdeadbeef` bitmask word, conditional-family coverage, one balanced register-then-unregister callback idiom, and the post-exit ownership boundary in memory
- it keeps `formattedMessage()` explicit as the approved public formatting surface for the selected-string plus `iter=%d` replay instead of implying direct reads of private message storage
- it now exposes `runPayloadBoundaryReplay()` so the count-4 payload prefix, zero sentinel, `iter=4` message, and `One ring to rule them all` branch stay reviewable through a public helper instead of private field inspection
- it now makes the replay summary itself carry explicit `vararg_payload_path_checked`, `relative_location_path_checked`, and `function_callback_path_checked` flags so reviewers do not have to infer those paths from private sample state
- it still keeps the lifecycle explicit as a tiny `init()` -> replay helpers -> `exit()` packet, and `runAnchorReplay()` now routes its callback portion through the public callback-boundary helper before closing the bounded replay
- it now keeps the sample-owned ownership path public through `runOwnershipReplay()` so the `cold` -> `initialized` -> `replay_complete` -> `exited` lifecycle, the final `Gandalf` plus `iter=7` snapshot, and the restored registration balance stay available through one public helper when later packet-local follow-through needs the condensed lifecycle replay
- it keeps its sample-owned replay entrypoints bounded through `runAnchorReplay()`, `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, and `runOwnershipReplay()` so the payload-shape, conditional-family, formatted-message, callback-boundary, and ownership-lifetime checks stay public instead of implying a runtime-ready trace-events module

The exact checks now exercised through `zigux/tests/phase5_build.zig` and the directly coupled focused sample packet are:

- the in-memory sample keeps `samples/trace_events/trace-events-sample.c` explicit and stays in the non-runtime reference-sample lane through `TraceEventsReferenceSample.descriptor()`
- `runAnchorReplay()` formats `iter=7`, selects `Gandalf` from the Linux `random_strings` table for `len = 2`, keeps the `1,2` payload prefix plus a zero sentinel, records the `0xdeadbeef` bitmask word, records six main-thread and two callback-path event calls for a total of eight bounded family calls, restores the callback-registration balance to zero, and keeps all six review-focus markers present in the replay summary
- `runPayloadBoundaryReplay()` is called only after `init()` and keeps the count-4 `1,2,3,4` payload prefix, zero sentinel, `iter=4` message, `One ring to rule them all` selection, initialized-stage boundary, six main-thread event calls, and the vararg, relative-location, and conditional-path markers reviewable through the public helper
- the focused callback-guard checks still directly prove that `replayFunctionIteration()` rejects missing registration, `unregisterFunctionCallback()` rejects underflow, the explicit register -> replayFunctionIteration(3) -> unregister flow records `last_function_count = 3`, sets the callback-path marker, reaches eight total event calls, and restores `registration_depth` to zero
- the focused lifecycle-guard checks still directly prove that `runAnchorReplay()` and `exit()` reject the pre-init cold state, `init()` rejects a second initialization attempt, `exit()` rejects outstanding registration, `exit()` succeeds after unregister, the sample reaches `.exited` with one init and one exit run recorded, and both `replayMainIteration()` and `registerFunctionCallback()` reject post-exit mutation
- the sample also still exposes `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, and `runOwnershipReplay()` as public packet-local helpers for follow-through packet checks, but the current focused executable checks are the narrower anchor, payload-boundary, callback-guard, and lifecycle-guard routes listed above

## Latest verification snapshot

Fresh exact-check reread on 2026-05-12 kept the shipped trace-events packet repo-local and explicit after the current focused sample packet was compared against the broader survey note on current `master`.

- connector-backed current-`master` note readback confirmed that this survey note, the shared `zigux/tests/phase5_build.zig` route, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase5-test`, `make -C zigux phase5`, and the separate Phase 9 `runtime_trace_events` family still describe the same bounded non-runtime packet
- GitHub web fallback readback of the current `samples/zigux/trace_events_sample.zig` and `zigux/tests/phase5_trace_events_sample.zig` file views confirmed that the directly exercised behavior checks today are the bounded `runAnchorReplay()` packet, the public `runPayloadBoundaryReplay()` packet, the manual callback underflow/register/replay/unregister guard packet, and the init-or-exit lifecycle guard packet rather than a focused executable packet that directly calls `runConditionalBoundaryReplay()` or `runOwnershipReplay()`
- connector-backed current-`master` manifest readback still keeps the broader review prompts explicit for `formattedMessage()`, `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, `runOwnershipReplay()`, the exact `checked_focus` order, `unregisterFunctionCallback()` underflow, `OutstandingRegistration`, and the post-exit replay and callback-registration rejection cues
- the previously recorded note-packet compile-only checks remain the latest executed survey-gate route on current `master`: `zig fmt --check zigux/tests/phase5_trace_events_sample_survey.zig` and `zig test --test-no-exec zigux/tests/phase5_trace_events_sample_survey.zig` still stand as the most recent executed survey-note checks, while this lane's reread stayed on connector-backed and web-fallback inspection because no writable checkout or direct raw-file fetch path was available here
- the public helper surface itself still remains explicit on current `master`: `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, `runOwnershipReplay()`, the `formattedMessage()` surface, the `0xdeadbeef` conditional-family cue, replay-summary callback-path markers, and the registration-balance cue are all still visible in the landed sample packet
- the survey gate still enforces repo-local review guidance by keeping the no-standalone-format-sample boundary tied to the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/trace_events_sample.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `TraceEventsReferenceSample.descriptor()` still name `samples/trace_events/trace-events-sample.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- do `zigux/tests/phase5_trace_events_sample_manifest.json` and `zigux/tests/phase5_trace_events_sample_survey.zig` still describe the exact vararg-payload, message, relative-location, callback-path, and teardown contract run through `zigux/tests/phase5_build.zig`?
- does the contributor packet still keep `formattedMessage()` explicit as the approved public formatting surface for the selected-string plus `iter=%d` replay instead of implying direct reads of private message storage?
- does the contributor packet still name `runPayloadBoundaryReplay()` as the approved public count-4 payload-boundary helper instead of implying private field inspection for the `1,2,3,4` prefix, zero sentinel, initialized-stage boundary, `iter=%d` replay, and selected-string branch?
- does the contributor packet still name `runConditionalBoundaryReplay()` as the approved public conditional-family helper instead of implying private sample-state reads for the full `0..5` selected-string and `iter=%d` cycle, namely `Mother Goose`, `Snoopy`, `Gandalf`, `Frodo`, `One ring to rule them all`, and the count-5 wraparound back to `Mother Goose`, plus the `0xdeadbeef` bitmask cue and the six main-thread family counts?
- does the contributor packet still name `runCallbackBoundaryReplay()` as the approved public callback-boundary helper instead of leaving the balanced register-then-unregister replay, callback-path proof, and restored registration balance implicit?
- does the contributor packet still keep `runOwnershipReplay()` explicit as the approved public ownership-and-lifetime helper for the `cold` -> `initialized` -> `replay_complete` -> `exited` lifecycle, the final `Gandalf` plus `iter=7` snapshot, and the post-exit rejection boundary?
- does the in-memory replay still keep the array payload, selected string, and `iter=%d` message reviewable instead of hiding them behind runtime thread state?
- does the sample still keep the `init()` -> replay helpers -> `exit()` lifecycle explicit so the same landed trace-events packet remains a bounded ownership-and-lifetime example instead of only a tracing example?
- does function-callback replay stay a balanced register-then-unregister idiom rather than implying `kthread_run()`, thread scheduling, or tracepoint enablement parity?
- do the sample-owned prompts keep the exact `checked_focus` order, the balanced register-then-unregister callback flow, `unregisterFunctionCallback()` underflow plus `OutstandingRegistration` rejection, and post-exit replay rejection explicit instead of leaving those callback-boundary cues implied?
- if the sample behavior changes, is the manifest updated alongside the replay contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that `CREATE_TRACE_POINTS`, tracepoint macros from `trace-events-sample.h`, kernel scheduling, and module registration wiring remain out of scope for this Phase 5 sample?
- if the broader shared review packet is refreshed, does it keep `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` pointing at this exact landed `samples/zigux/trace_events_sample.zig` packet, keep `zig build test --build-file zigux/tests/phase5_build.zig --summary all` as the shared CI replay, keep `make -C zigux phase5-test` and `make -C zigux phase5` explicit as local Linux-style wrappers over that same build entrypoint, and still separate this sample from the later Phase 9 `runtime_trace_events` family instead of leaving that distinction trace-events-only?
- if this survey note moves again, does it still keep the latest verification snapshot explicit with `zig fmt --check zigux/tests/phase5_trace_events_sample_survey.zig`, a connector-backed note readback for `Documentation/zigux/phase5-trace-events-sample-survey.md`, `zig test --test-no-exec zigux/tests/phase5_trace_events_sample_survey.zig`, the shared `phase5_build.zig` route, `.github/workflows/zigux-bootstrap.yml`, the workflow-only `zig build test --build-file zigux/tests/phase5_build.zig --summary all` replay, `make -C zigux phase5-test`, `make -C zigux phase5`, and the separate Phase 9 `runtime_trace_events` family instead of falling back to a softer posture-only summary?
- if this survey note moves again, does it still say there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample, and does it keep the selected-string plus `iter=%d` replay tied to the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet instead of implying a new standalone formatting helper sample?

## Recorded gap vs roadmap

The current gap is no longer "Zigux has no trace-events sample guidance." The more precise state is:

- the repo now has a reviewable Phase 5 `trace_events_sample` reference sample plus manifest-backed checks for payload shape, string selection, formatted messages, bounded family counts, vararg-payload coverage, relative-location coverage, callback-path coverage, the public payload and conditional boundary helpers, the public callback boundary helper, the sample-owned `runOwnershipReplay()` helper, and teardown-owned ownership-lifetime boundaries
- the repo still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample, so reviewers should keep treating the selected-string plus `iter=%d` replay in `samples/zigux/trace_events_sample.zig` as the approved formatting idiom cue while standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet
- the shared docs-root, checklist, sample-root, scripts-root, tests-root, and workflow surface should stay explicit here too, so this survey note does not understate the already-shipped review surface for the landed sample
- this sample must remain visibly separate from the later Phase 9 runtime `trace-events` starter so contributors do not over-claim runtime substrate coverage
- the Phase 5 roadmap's four named sample anchors are now all represented by bounded `samples/zigux/` reference readings, but that does not close the separate Phase 9 runtime pilot tranche

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux trace-events sample
   - `rg -n "samples/trace_events/trace-events-sample.c|PHASE5_LANE_KEY=P5-L24|PHASE5_SURVEYED_COMMIT=beb1065024e41b266c1492d7be5a446c04e42368|Phase 5" Documentation/zigux samples/zigux zigux/tests`
2. confirm the current `samples/zigux/` surface keeps the Phase 5 and Phase 9 trace-events lanes distinct
   - `find samples/zigux -maxdepth 1 -type f | sort | rg "trace_events_sample|runtime_trace_events"`
3. run the exact bounded Phase 5 sample checks
   - `zig build test --build-file zigux/tests/phase5_build.zig --summary all`
   - `make -C zigux phase5-test`
   - `make -C zigux phase5`

## Non-goals

This survey does not yet claim:

- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity

## Next bounded step

Keep this trace-events note packet parked unless fresh repo inspection shows the survey note, manifest review prompts, survey gate, or shared trace-events sample guidance drifting apart on current `master`.
