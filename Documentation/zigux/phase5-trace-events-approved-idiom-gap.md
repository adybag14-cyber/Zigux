# Phase 5 Trace-Events Approved Idiom Gap

This note keeps the roadmap-backed Phase 5 trace-events packet truthful when shared reviewer surfaces need to mention the bounded formatting idiom that current `master` still approves.

## Current approved cue on `master`

The roadmap-backed Phase 5 trace-events anchor is still:

- `samples/trace_events/trace-events-sample.c`

Authenticated sample-root readback still directly exposes this bounded non-runtime formatting companion:

- `samples/zigux/trace_events_string_formatting_sample.zig`

The same authenticated sample-root reread now directly exposes this bounded callback-focus companion too:

- `samples/zigux/trace_events_callback_focus_contract.zig`

The same current sample-root packet also directly exposes this bounded payload-preview companion:

- `samples/zigux/trace_events_payload_preview_contract.zig`

Fresh mixed reread on 2026-05-27 keeps the dedicated survey note and the broader non-runtime trace-events companions in a split state rather than a missing state.

This survey note is directly readable again on current `master` and should stay grouped with the shared reminder packet rather than with the still-split sample-local companion set:

- `Documentation/zigux/phase5-trace-events-sample-survey.md`

The broader non-runtime trace-events sample-local companions still remain on the split authenticated-versus-public path in this lane:

- `samples/zigux/trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample.zig`
- `zigux/tests/phase5_trace_events_sample_manifest.json`
- `zigux/tests/phase5_trace_events_sample_survey.zig`

Those four paths are again carried by the live trace-events reminder packet and current public-tree-backed reread surfaces, but the authenticated contents route used for this lane still did not return them directly on 2026-05-27.

The shared `zigux/tests/phase5_build.zig` route remains useful support material too, and the current lane reread now returns that path directly again. Keep it framed as returned shared build-route evidence rather than as part of the broader sample-local companion set.

Keep the approved formatting idiom bounded to the current landed reminder packet:

- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `samples/zigux/trace_events_string_formatting_sample.zig`
- `samples/zigux/trace_events_callback_focus_contract.zig`
- `samples/zigux/trace_events_payload_preview_contract.zig`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase5-review-guide-surface.py`
- `zigux/tests/README.md`

The selected-string plus `iter=%d` cue remains the approved bounded formatting reminder while staying honest about the current split: the bounded formatting companion remains directly readable through the authenticated sample-root route, the bounded callback-focus companion is directly readable there too as reviewability help for the same anchor, the bounded payload-preview companion is directly readable there too as the current direct payload-shape and conditional-event-family cue, `Documentation/zigux/phase5-trace-events-sample-survey.md` is directly readable again as a shared reminder surface, the broader non-runtime trace-events sample-local companions are visible again through the live public-tree-backed packet but are not yet returned authenticated proof in this lane, the shared `zigux/tests/phase5_build.zig` path is returned shared build-route evidence again rather than companion-only support, and `scripts/zigux/check-phase5-review-guide-surface.py` remains the shipped shared guard for that reminder family rather than an optional extra.

Keep the bounded destination discipline explicit in that same reminder packet too: `formatIterationMessageInto(12, [5]u8)` still returns `error.NoSpaceLeft` without advancing the sample stage or `replay_runs`, while `formatIterationMessageInto(12, [7]u8)` still returns `"iter=12"` and keeps the sample in `.initialized`.

Keep the direct modulo-selected cycle explicit too: `runStringFormattingCycleReplay()` now walks all five selected strings through the bounded `iter=%d` formatter while keeping the companion in `.initialized` and leaving `replay_runs` unchanged.

Keep the selected-string iteration companion explicit too: `formatSelectedIterationMessageInto(3, [12]u8)` still returns `"Frodo iter=3"` while keeping the sample in `.initialized`, so the approved-idiom note must preserve the selected-string-plus-iteration wording instead of reducing the packet to the bare `iter=%d` formatter.

Keep the sample-owned review contract explicit too: the bounded formatting companion now centralizes the exact `checked_focus` order `string_selection,formatted_message,bounded_destination_discipline,non_allocating_runtime_safe`, and the approved-idiom reminder should preserve that same reading order beside the selected-string slot and `iter=%d` cue instead of reducing the trace-events packet to message text alone.

Keep the bounded callback-focus companion explicit too: `anchorFocusOrder()` and `callbackBoundaryContract()` now keep the shared `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` focus order plus the callback-registration recovery cues reviewable at the sample root without turning that companion into a fifth Phase 5 sample family.

Keep the bounded payload-preview companion explicit too: `referencePattern()` now keeps the same shared focus order grounded in direct payload-shape evidence through the five-case modulo-selected ladder, the `payload_preview` prefix growth from `0` through `4`, the preserved initialized-stage posture, the direct `conditional_event_families` cue, the `vararg_payload_path_checked` and `relative_location_path_checked` booleans, and the largest bounded preview case `"One ring to rule them all"` plus `"iter=4"` without turning that companion into a fifth Phase 5 sample family.

## Exact checks run on 2026-05-27

This run verified the current direct trace-events companion packet through authenticated file reread against current `master`.
The same lane comparison stayed scoped to the shared approved-idiom packet rather than widening into a broader trace-events replay or Phase 9 runtime work.

The exact current direct companion cues reconfirmed in this lane were:

- `samples/zigux/trace_events_string_formatting_sample.zig` still keeps the selected-string plus `iter=%d` formatting cue bounded to the Phase 5 trace-events anchor
- `samples/zigux/trace_events_callback_focus_contract.zig` still keeps the shared callback-focus order and registration-recovery cues explicit beside that same anchor
- `samples/zigux/trace_events_payload_preview_contract.zig` now also sits in the same direct sample-root packet as the payload-shape and conditional-event-family companion for that same anchor
- `Documentation/zigux/phase5-trace-events-sample-survey.md` still stays directly readable as the owner survey note for the same narrow packet
- the broader sample-local trace-events replay set still stays on the public-tree-backed companion side of the split instead of direct authenticated proof in this lane

Those checks confirmed this current sample behavior:

- `runAnchorReplay(7)` still keeps the roadmap anchor explicit, transitions from `.initialized` to `.replay_complete`, selects `"Gandalf"`, renders `"iter=7"` with length `6`, and keeps the packet tied to the exact `checked_focus` order `string_selection,formatted_message,bounded_destination_discipline,non_allocating_runtime_safe`.
- `runStringFormattingCycleReplay()` still keeps the modulo-selected cycle directly reviewable too: it replays all five strings in order, renders `"iter=0"` through `"iter=4"`, stays in `.initialized`, and leaves `replay_runs` at `0`.
- bounded destination behavior stays directly covered too: `formatIterationMessageInto(12, [5]u8)` returns `error.NoSpaceLeft` without changing the sample stage or incrementing `replay_runs`, while `formatIterationMessageInto(12, [7]u8)` returns `"iter=12"` and keeps the sample in the `.initialized` stage.
- selected-string exact-fit behavior also stays directly covered too: `formatSelectedIterationMessageInto(3, [11]u8)` returns `error.NoSpaceLeft` without changing the sample stage or incrementing `replay_runs`, while `formatSelectedIterationMessageInto(3, [12]u8)` returns `"Frodo iter=3"` and keeps the sample in `.initialized`.
- the payload-preview companion now also stays directly visible in the same packet: `referencePattern()` preserves the initialized-stage posture, keeps `event_family_count = 6` and `callback_family_count = 2` explicit, walks the five selected strings through the bounded preview ladder, and keeps the largest direct preview case tied to `payload_preview = { 1, 2, 3, 4 }` and `formatted_message = "iter=4"`.

## Review boundary

Current `master` still ships no standalone `samples/zigux/*printf*`, `*vsprintf*`, or `*format*` Phase 5 reference sample outside the bounded trace-events companions.
Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.
Keep that no-extra-sample boundary separate from the bounded trace-events companion packet so this note does not blur helper-family reminders into trace-events proof.

Use this note only to restate the bounded formatting cue that Phase 5 reviewers should preserve inside the roadmap-backed `trace_events` anchor.

Do not treat this note as proof of:

- standalone formatting-helper delivery
- standalone broad `*format*` sample delivery
- standalone `printf` parity
- standalone `vsprintf` parity
- standalone string-helper delivery
- standalone `*cmdline*` sample delivery
- standalone `*argv*` sample delivery
- standalone `*rbtree*` sample delivery
- standalone `*bitmap*` sample delivery
- a fifth approved Phase 5 sample

Keep standalone formatting-helper evidence under the closed Phase 1 `tools/lib/vsprintf.zig` packet, keep standalone string-helper, `cmdline`, `argv_split`, and `rbtree` evidence under the bounded Phase 7 helper packet, keep direct bitmap helper reviewability under the closed Phase 1 plus bounded Phase 4 reminder packet, and keep runtime-facing trace-events loader work under the separate Phase 9 lane.

## Next bounded step

Leave this note parked unless a fresh reread shows that another shared trace-events reminder surface still collapses the current split by treating the broader sample-local packet as fully missing, or by promoting it to fully returned authenticated proof before the contents route actually does so, or by losing the selected-string plus `iter=%d` cue, the exact `checked_focus` review order, the callback-focus reviewability cue, the payload-preview companion cue, or the shipped guide-surface guard.