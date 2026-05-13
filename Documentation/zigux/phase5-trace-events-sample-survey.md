# Phase 5 Trace-Events Sample Survey

This sample-backed survey note tracks the bounded Phase 5 reference-sample survey for the roadmap's `samples/trace_events/trace-events-sample.c` anchor.

## Status

- `PHASE5_STATUS=parked-readback-gap-aligned`
- `PHASE5_SLICE=trace-events-reference-sample-readback`
- `PHASE5_LANE_KEY=P5-L16`
- `PHASE5_SURVEYED_COMMIT=368dcb11d347e77c13bef6607bd99b313573e389`
- scope: roadmap-vs-repo sample delivery, approved payload and callback idiom guidance, contributor refresh cues, and exact bounded checks for the directly readable `samples/zigux/` trace-events replay packet
- product boundary:
  - `Documentation/zigux/phase5-trace-events-sample-survey.md`
  - `Documentation/zigux/phase5-sample-review-guide.md`
  - `Documentation/zigux/README.md`
  - `Documentation/zigux/review-checklist.md`
  - `samples/zigux/README.md`
  - `scripts/zigux/README.md`
  - `zigux/tests/README.md`
  - `samples/zigux/trace_events_sample.zig`
  - `zigux/tests/phase5_trace_events_sample.zig`
  - `zigux/tests/phase5_trace_events_sample_manifest.json`
  - `zigux/tests/phase5_trace_events_sample_survey.zig`

## Why this slice exists

The roadmap's Phase 5 target is "Samples and Reference Patterns" and explicitly names `samples/trace_events/trace-events-sample.c` as one of the Linux anchors that should make approved Zigux idioms reviewable and repeatable.

Fresh repo inspection now shows that current `master` carries the landed non-runtime `trace_events_sample` slice again inside the roadmap-backed Phase 5 reference-sample family, but it does not directly expose the older shared `zigux/tests/phase5_build.zig` route that some wider reminder surfaces still describe. The trace-events-specific job is to keep this approved payload-and-callback idiom reviewable and repeatable, with its exact checks and non-goals kept honest beside the broader shared Phase 5 packet.

## Current repo reality on `master`

Fresh repo-first inspection on 2026-05-13 directly recovered these trace-events packet paths from current `master`:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

That same direct readback did not recover the older shared build route:

- `zigux/tests/phase5_build.zig`

Treat the trace-events packet as directly readable through the sample root, focused replay, manifest, and survey replay above, while keeping the missing shared build entrypoint explicit until a fresh reread proves it returned.

## Survey findings

- `samples/trace_events/trace-events-sample.c` stays the Linux anchor for this sample family.
- the Linux sample mixes four concerns:
  - payload shaping for the `foo_bar`, template, conditional, and relative-location tracepoint families
  - string and array selection derived from `cnt % 5`
  - function-callback registration and unregister balance for the second thread path
  - real runtime substrate through `CREATE_TRACE_POINTS`, tracepoint macros, `kthread_run()`, `schedule_timeout()`, and module init or exit hooks
- the honest Phase 5 move is to make the payload shape, chosen string, formatted message, family counts, public selected-string slot and payload-length cues, and callback-registration balance reviewable in memory while leaving runtime thread creation and tracepoint macro wiring out of scope.
- the shared sample-root catalog in `samples/zigux/README.md` is part of that boundary now, because it is the shortest shared place to keep the four Phase 5 reference readings visibly separate from the later runtime starters that live in the same directory.
- the shared sample-root catalog also carries a dedicated trace-events review-packet stanza, so contributors can refresh the exact replay contract, callback-balance cues, and out-of-scope runtime claims without having to infer them from the deeper survey note alone.
- the shared tests-root guide in `zigux/tests/README.md` is part of that same contributor packet now, because it names the direct `zig test samples/zigux/trace_events_sample.zig` replay, the paired `zig test zigux/tests/phase5_trace_events_sample_survey.zig` replay, and the wider Phase 5 boundary cues that keep this landed sample distinct from the separate Phase 7 helper-only evidence and the later Phase 9 runtime follow-ons.
- the shared scripts-root guide in `scripts/zigux/README.md` is part of that same contributor packet now, because it names the direct `zig test samples/zigux/trace_events_sample.zig` replay, the paired `zig test zigux/tests/phase5_trace_events_sample_survey.zig` replay, and the blocked runtime-trace-events handoff cues beside the same later follow-on files, without restating the missing shared `phase5_build.zig` route as current direct evidence.
- the same contributor packet also has to keep the sample-owned `zigux/tests/phase5_trace_events_sample.zig` replay explicit as a focused tests-root check, without claiming that current `master` directly exposes the older shared `phase5_build.zig` entrypoint for this packet.
- the same trace-events family boundary should stay explicit in reviewer-facing prose too: current `master` ships `samples/zigux/runtime_trace_events.zig` as a sample-only blocked Phase 9 pilot, and the bounded `samples/zigux/runtime_trace_events_loader.zig` scaffold is shipped now as a separate follow-on surface whose runtime-substrate handoff still stays blocked, so the landed `trace_events_sample` packet remains the non-runtime reference idiom for this family.
- the same contributor packet also has to keep the current no `samples/zigux/*string*`, no `samples/zigux/*cmdline*`, and no `samples/zigux/*rbtree*` Phase 5 boundaries explicit, so helper evidence stays under the separate Phase 7 bundles rooted in `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, `zigux/tests/phase7_string_helpers.zig`, `Documentation/zigux/phase7-cmdline-slice.md`, `lib/cmdline.zig`, `zigux/tests/phase7_cmdline.zig`, `Documentation/zigux/phase7-rbtree-slice.md`, `lib/rbtree.zig`, and `zigux/tests/phase7_build.zig` instead of reading like missing Phase 5 sample ports beside this landed trace-events idiom.
- current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample; the approved formatting cue in this lane remains the selected-string and `iter=%d` replay surface inside `samples/zigux/trace_events_sample.zig`, while standalone formatting-helper evidence stays under the closed Phase 1 `tools/lib/vsprintf.zig` packet plus the bounded Phase 7 `string_get_size()` helper packet.

## Landed sample and exact checks

The repo now carries that bounded sample in `samples/zigux/trace_events_sample.zig`.

The sample intentionally stays small:

- it keeps the Linux anchor path explicit in `TraceEventsReferenceSample.descriptor()`
- it models only the bounded array payload, selected string, public selected-string slot and payload-length cues, public main-path and callback-path iteration cues, the `iter=%d` message, and the dedicated `runStringFormattingCycleReplay()` summary that keeps the full modulo-selected string cycle reviewable through one public five-case replay
- it makes the replay summary itself carry explicit `vararg_payload_path_checked`, `relative_location_path_checked`, and `function_callback_path_checked` flags so reviewers do not have to infer those paths from private sample state
- it exposes `lifecycleSummary()` so the public review surface can read stage plus init, replay, and exit counts, registration depth, and total event calls without private field access
- it uses a tiny `init()` -> `replayMainIteration()` -> `registerFunctionCallback()` -> `replayFunctionIteration()` -> `unregisterFunctionCallback()` -> `exit()` lifecycle so ownership and teardown stay explicit, including unregister-underflow rejection before a callback is armed and `OutstandingRegistration` rejection if `exit()` is attempted while one callback is still live
- it provides one bounded self-check through `runAnchorReplay()` instead of implying a runtime-ready trace-events module

The exact checks currently recorded in `zigux/tests/phase5_trace_events_sample_manifest.json`, exercised directly through `zigux/tests/phase5_trace_events_sample.zig`, and cross-checked by `zigux/tests/phase5_trace_events_sample_survey.zig` are:

- the in-memory sample keeps `samples/trace_events/trace-events-sample.c` explicit and stays in the non-runtime sample lane
- `runAnchorReplay()` formats iter=7, selects Gandalf, and exposes selected-string slot `2` from the Linux `random_strings` table for `len = 2`
- the dedicated `runStringFormattingCycleReplay()` summary replays counts `0` through `4` through five public cases so the full modulo-selected string cycle stays explicit: `Mother Goose`, `Snoopy`, `Gandalf`, `Frodo`, and `One ring to rule them all`
- the replay summary exposes main iteration `7` and function-callback iteration `9` so the Linux `cnt`-driven split between the two thread paths stays reviewable without reading private sample state
- the replay exposes payload length `2` and keeps the `1,2` payload prefix plus a zero sentinel so the Linux array idiom remains reviewable in memory
- the replay records the `0xdeadbeef` bitmask word and marks the relative-location payload path as checked in the replay summary
- the replay marks the vararg payload path as checked so the `fmt` plus `va_list` `trace_foo_bar` idiom stays explicit in the public replay summary
- the replay records six main-thread event calls and two function-callback event calls for a total of eight bounded tracepoint-family calls
- the public `lifecycleSummary()` reports `replay_complete` with init, replay, and exit counts `1,1,0`, zero registration depth, and eight total event calls after `runAnchorReplay()`, then reports `exited` with counts `1,1,1` after `exit()`
- the replay summary keeps the exact `checked_focus` order `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` so the approved review surface stays visible without reading private sample state
- the function-callback replay requires registration first, marks that callback path as checked, and restores the registration balance to zero before the sample completes
- before a callback is registered, the in-memory sample rejects `replayFunctionIteration()` with `FunctionCallbackNotRegistered` so the callback-entry boundary stays reviewable without implying tracepoint enablement parity
- the in-memory callback lane rejects a second `registerFunctionCallback()` call while already registered so the Phase 5 sample keeps one live callback registration before balance returns to zero
- before balance returns to zero, the same ownership lane rejects `unregisterFunctionCallback()` underflow before registration and rejects `exit()` with `OutstandingRegistration` while one callback remains armed
- after `exit()` the sample rejects later `replayMainIteration()`, `registerFunctionCallback()`, `replayFunctionIteration()`, and `unregisterFunctionCallback()` calls

## Latest verification snapshot

- sampled from the current direct-readback trace-events packet on `master` as of 2026-05-13
- the directly readable packet in this run is the sample root, focused replay, manifest, and survey replay listed above
- the older shared `zigux/tests/phase5_build.zig` route was not directly readable in this run, so this note now keeps that missing-path caveat explicit instead of treating it as live verification evidence

## Contributor refresh prompts for the landed sample

When a contributor updates `samples/zigux/trace_events_sample.zig` or its directly coupled Phase 5 test files, keep these prompts explicit:

- does `TraceEventsReferenceSample.descriptor()` still name `samples/trace_events/trace-events-sample.c` and keep `requires_runtime_substrate = false` plus `provides_selfcheck = true`?
- does `zigux/tests/phase5_trace_events_sample_manifest.json` still pin `surveyed_commit` to the exact inspected `master` head instead of a floating branch label?
- do the sample-backed survey note, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md` still describe the same bounded replay contract and keep this Phase 5 sample visibly separate from the later Phase 9 runtime pilot?
- do those same shared contributor surfaces keep the current readback split explicit by naming the directly readable sample-root-plus-focused-tests packet above while not restating the missing `zigux/tests/phase5_build.zig` route as current direct evidence until a fresh reread proves it returned?
- do those same shared contributor surfaces still say plainly that current `master` ships no `samples/zigux/*string*`, `samples/zigux/*cmdline*`, or `samples/zigux/*rbtree*` Phase 5 reference sample, and still point string, cmdline, and rbtree evidence back to `Documentation/zigux/phase7-string-helpers-slice.md`, `Documentation/zigux/phase7-cmdline-slice.md`, `Documentation/zigux/phase7-rbtree-slice.md`, `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/rbtree.zig`, `zigux/tests/phase7_string_helpers.zig`, `zigux/tests/phase7_cmdline.zig`, `zigux/tests/phase7_rbtree.zig`, and `zigux/tests/phase7_build.zig` instead of treating helper-only evidence like missing Phase 5 sample ports?
- do `zigux/tests/phase5_trace_events_sample.zig` and `zigux/tests/phase5_trace_events_sample_survey.zig` still describe the exact selected-string-slot, payload-length, main-iteration, callback-iteration, vararg-payload, lifecycle-summary, message, relative-location, callback-path, and teardown contract without requiring a missing shared build route to understand the packet?
- does `lifecycleSummary()` still keep stage plus init, replay, and exit counts, registration depth, and total event calls visible without private field access?
- does `runStringFormattingCycleReplay()` still keep the full modulo-selected string cycle explicit across counts `0` through `4` through five public cases instead of reducing the review surface to only one reviewed string case?
- do the sample self-check and `zigux/tests/phase5_trace_events_sample.zig` still assert the exact `checked_focus` list and order instead of only its length?
- do the in-memory replay and `runStringFormattingCycleReplay()` still keep the array payload, selected string, selected-string slot, payload length, and `iter=%d` message reviewable instead of hiding them behind runtime thread state?
- does function-callback replay stay a single-live register-then-unregister idiom, including rejection of a second `registerFunctionCallback()` call while one callback is already registered, rather than implying `kthread_run()`, thread scheduling, or tracepoint enablement parity?
- before a callback is registered, does the sample still reject `replayFunctionIteration()` with `FunctionCallbackNotRegistered` so the callback-entry boundary stays explicit without relying on private state?
- before callback balance returns to zero, does the sample still reject `unregisterFunctionCallback()` underflow and reject `exit()` with `OutstandingRegistration` while a callback remains armed, so the ownership boundary is explicit before teardown?
- after `exit()`, do `replayMainIteration()`, `registerFunctionCallback()`, `replayFunctionIteration()`, and `unregisterFunctionCallback()` all stay rejected so the teardown boundary is fully reviewable instead of only partially implied?
- do the sample-backed survey note, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/review-checklist.md` still point reviewers back to the descriptor, manifest-backed survey, sample-backed survey note, shared sample-root catalog, shared tests-root guide, shared scripts-root guide, and focused trace-events replay packet for this exact contract, while treating `zigux/tests/phase5_build.zig` as absent until it is directly readable again?
- if the sample behavior changes, is the manifest updated alongside the replay contract instead of leaving reviewers to infer the new boundary from code alone?
- do the docs and tests still say clearly that `CREATE_TRACE_POINTS`, tracepoint macros from `trace-events-sample.h`, kernel scheduling, and module registration wiring remain out of scope for this Phase 5 sample?
- do the sample-backed survey note, `scripts/zigux/README.md`, `samples/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/README.md`, and `Documentation/zigux/review-checklist.md` still say plainly that current `master` ships no standalone Phase 5 formatting-helper sample and that the selected-string plus `iter=%d` replay is the approved formatting cue while standalone formatting evidence stays under the Phase 1 `vsprintf` packet and the bounded Phase 7 `string_get_size()` helper packet?

## Recorded gap vs roadmap

The current gap is no longer "Zigux has no trace-events sample guidance." The more precise state is:

- the repo has a directly readable Phase 5 `trace_events_sample` reference sample plus manifest-backed checks for payload shape, string selection, selected-string slot cues, payload-length cues, main-path and callback-path iteration cues, formatted messages, bounded family counts, lifecycle-summary counts, the exact `checked_focus` review surface, vararg-payload coverage, relative-location coverage, callback-path coverage, and teardown
- current `master` still has no separate formatting-helper sample under `samples/zigux/`, so roadmap-aligned review should treat the trace-events sample's selected-string and `iter=%d` surface as the approved formatting idiom cue and keep standalone formatting-helper evidence under `Documentation/zigux/phase1-closure.md`, `tools/lib/vsprintf.zig`, `zigux/tests/phase1_helpers.zig`, `Documentation/zigux/phase7-string-helpers-slice.md`, `lib/string_helpers.zig`, and `zigux/tests/phase7_build.zig`
- the same shared contributor packet also needs to keep the no `samples/zigux/*string*`, no `samples/zigux/*cmdline*`, and no `samples/zigux/*rbtree*` boundaries visible so helper-only Phase 7 evidence does not read like three more missing Phase 5 sample ports beside the landed trace-events idiom
- the same shared contributor packet also needs to keep the missing shared `zigux/tests/phase5_build.zig` route explicit until direct readback proves it returned, so reviewers do not over-claim a broader shared replay packet than current `master` exposes
- this sample must remain visibly separate from the later Phase 9 runtime `trace-events` starter so contributors do not over-claim runtime substrate coverage
- the Phase 5 roadmap's four named sample anchors remain represented by bounded `samples/zigux/` reference readings or survey-note-backed gap records, but that does not close the separate Phase 9 runtime pilot tranche

## Review gates for this survey

1. confirm the Phase 5 anchor is still the Linux trace-events sample
   - `rg -n "samples/trace_events/trace-events-sample.c|Phase 5" Documentation/zigux samples`
2. confirm the current `samples/zigux/` surface keeps the Phase 5 and Phase 9 trace-events lanes distinct
   - `find samples/zigux -maxdepth 1 -type f | sort | rg "trace_events_sample|runtime_trace_events"`
3. run the focused self-check that keeps the in-memory replay behavior explicit
   - `zig test samples/zigux/trace_events_sample.zig`
4. run the manifest-backed survey gate from the repo root so the exact-check record stays readable
   - `zig test zigux/tests/phase5_trace_events_sample_survey.zig`

## Non-goals

This survey does not yet claim:

- `CREATE_TRACE_POINTS` parity
- tracepoint macro parity from `trace-events-sample.h`
- kernel thread scheduling or timeout parity
- module registration or unregister wiring parity

## Next bounded step

Leave this trace-events survey lane parked unless fresh repo inspection finds one more directly coupled replay-summary or contributor-guidance wording drift inside the landed `trace_events_sample` packet, while keeping the sample visibly separate from the later Phase 9 runtime pilot, preserving the exact verification packet recorded under `P5-L16`, and keeping the missing shared `zigux/tests/phase5_build.zig` route explicit until it returns.
