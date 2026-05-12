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
- it uses a tiny `init()` -> `replayMainIteration()` -> `registerFunctionCallback()` -> `replayFunctionIteration()` -> `unregisterFunctionCallback()` -> `exit()` lifecycle so ownership and teardown stay explicit as part of the same bounded trace-events idiom
- it now keeps the sample-owned ownership path public through `runOwnershipReplay()` so the `cold` -> `initialized` -> `replay_complete` -> `exited` lifecycle, the final `Gandalf` plus `iter=7` snapshot, and the restored registration balance stay reviewable without direct lifecycle choreography in every focused test
- it keeps its sample-owned replay entrypoints bounded through `runAnchorReplay()`, `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, and `runOwnershipReplay()` so the payload-shape, conditional-family, formatted-message, callback-boundary, and ownership-lifetime checks stay public instead of implying a runtime-ready trace-events module

The exact checks now exercised through `zigux/tests/phase5_build.zig` and the directly coupled focused sample packet are:

- the in-memory sample keeps `samples/trace_events/trace-events-sample.c` explicit and stays in the non-runtime reference-sample lane
- `runAnchorReplay()` formats `iter=7` and selects `Gandalf` from the Linux `random_strings` table for `len = 2`
- the replay keeps the `1,2` payload prefix plus a zero sentinel so the Linux array idiom remains reviewable in memory
- `runPayloadBoundaryReplay()` keeps the count-4 `1,2,3,4` payload prefix, zero sentinel, `iter=4` message, `One ring to rule them all` selection, and the initialized-stage boundary reviewable through a public helper instead of private sample state
- `runConditionalBoundaryReplay()` keeps the full public `0..5` selected-string and `iter=%d` cycle reviewable through one helper: `Mother Goose`, `Snoopy`, `Gandalf`, `Frodo`, `One ring to rule them all`, then the count-5 wraparound back to `Mother Goose`, alongside the `0xdeadbeef` bitmask cue and the six main-thread family counts instead of private sample-state reads
- the replay records the `0xdeadbeef` bitmask word and marks the relative-location payload path as checked in the replay summary
- the replay marks the vararg payload path as checked so the `fmt` plus `va_list` `trace_foo_bar` idiom stays explicit in the public replay summary
- the replay records six main-thread event calls and two function-callback event calls for a total of eight bounded tracepoint-family calls
- the public `runCallbackBoundaryReplay()` helper keeps the register-then-unregister callback replay self-contained, rejects outstanding registration, records the callback-path replay explicitly, and restores the registration balance to zero before the sample completes
- `runOwnershipReplay()` keeps the `cold` -> `initialized` -> `replay_complete` -> `exited` lifecycle public with one init, replay, and exit run, the final `Gandalf` plus `iter=7` snapshot, restored registration balance, and the post-exit rejection boundary explicit

## Latest verification snapshot

Fresh focused review-surface replay on 2026-05-11 kept the shipped trace-events packet repo-local and explicit after the callback-focus closure remained landed on current `master`.

- connector-backed current-`master` note readback on 2026-05-11 confirmed that the older blocked callback-focus handoff stayed superseded: `samples/zigux/trace_events_sample.zig` still includes `checked_focus` on `CallbackBoundarySummary` and threads `reviewContract().focus` through `runCallbackBoundaryReplay()`, while the paired manifest, survey gate, and this survey note remain aligned on that same public callback-boundary packet
- `zig fmt --check zigux/tests/phase5_trace_events_sample_survey.zig` passed for the survey-gate half of this note packet
- connector-backed current-`master` note readback confirmed the contributor-note wording now matches that focused survey gate instead of claiming a Markdown `zig fmt` route that the shipped toolchain does not support
- `zig test --test-no-exec zigux/tests/phase5_trace_events_sample_survey.zig` passed a compile-only recheck of the manifest-backed survey gate for this note packet
- connector-backed current-`master` inspection confirmed that `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, `zigux/tests/phase5_trace_events_sample_survey.zig`, the shared `zigux/tests/phase5_build.zig` route, `.github/workflows/zigux-bootstrap.yml`, `make -C zigux phase5-test`, `make -C zigux phase5`, and the separate Phase 9 `runtime_trace_events` family still describe the same bounded non-runtime packet, with the workflow rerunning only the shared build route while the make targets stay local Linux-style wrappers over it
- the manifest-backed review prompts and survey gate still keep the exact `checked_focus` order plus the `unregisterFunctionCallback()` underflow, `OutstandingRegistration`, and post-exit replay-rejection cues explicit after this packet-local refresh
- the public `runPayloadBoundaryReplay()`, `runConditionalBoundaryReplay()`, `runCallbackBoundaryReplay()`, and `runOwnershipReplay()` helpers, the `formattedMessage()` surface, the count-0 `Mother Goose` plus `0xdeadbeef` conditional-family boundary, replay-summary callback-path markers, and the registration-balance cue all remain explicit on current `master`
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
