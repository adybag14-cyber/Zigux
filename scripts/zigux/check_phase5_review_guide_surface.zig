const std = @import("std");
const Io = std.Io;
const guard = @import("zigux_guard.zig");

pub const live_pass_marker = "PHASE5_REVIEW_GUIDE_SURFACE=pass";
pub const self_test_pass_marker = "PHASE5_REVIEW_GUIDE_SURFACE_SELF_TEST=pass";

const MARKERS__Documentation_zigux_phase5-sample-review-guide_md = [_][]const u8{
    "Treat those four anchors as the approved Phase 5 destination set unless the roadmap changes.",
    "The same authenticated route also directly returns the shared build-route companion `zigux/tests/phase5_build.zig` for this packet.",
    "Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample, and it still ships no standalone broad `*format*` Phase 5 reference sample outside the bounded trace-events cues carried by `samples/zigux/trace_events_string_formatting_sample.zig` and the shared reminder packet.",
    "Keep the direct validation routes explicit in that same guidance too: `zig test samples/zigux/bytestream_fifo.zig`, `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig`, and `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` stay visible as the sample-owned self-check route, the focused replay route, and the survey-packet guard, while the shared `zigux/tests/phase5_build.zig` line stays visible as current directly readable shared build-route companion evidence for this bytestream packet rather than as sample-local proof.",
    "keep the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit alongside the registered teardown, post-`exit()` rejection, and anchor-replay rejection packet",
    "Fresh 2026-05-20 follow-up reread also keeps the current direct packet shape explicit: `samples/zigux/bytestream_fifo.zig` now carries four in-file self-checks, `zigux/tests/phase5_bytestream_fifo.zig` keeps five focused replay tests, and `zigux/tests/phase5_bytestream_fifo_survey.zig` keeps five survey-packet checks aligned with the survey note and manifest.",
    "`zig test samples/zigux/kobject_example_attr_group_contract.zig` stays the companion-only validation route for the attr-group contract while `zigux/tests/phase5_build.zig` remains the directly readable shared build-route companion for this packet",
    "`samples/zigux/trace_events_callback_focus_contract.zig` keeps the shared `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` `checked_focus` order plus the callback-registration recovery cues explicit at the sample root without turning that companion into a fifth Phase 5 sample.",
    "`samples/zigux/trace_events_payload_preview_contract.zig` keeps the sibling payload-preview companion explicit through `referencePattern()`, the five-case modulo-selected preview ladder, the direct `conditional_event_families` cue, the `vararg_payload_path_checked` and `relative_location_path_checked` booleans, and the largest bounded preview case `\"One ring to rule them all\"` plus `\"iter=4\"` instead of turning that companion into a fifth Phase 5 sample.",
    "`samples/zigux/kretprobe_example_probe_spec.zig` plus `zigux/tests/phase5_kretprobe_example_probe_spec.zig` keep the direct Linux anchor path, default symbol, one-word private-data width, default `maxactive`, replay return and duration summary, missed-instance cue, and the pre-init-only symbol-selection and maxactive-tuning rules explicit beside the main replay packet instead of leaving that probe-spec reviewability trapped in the dedicated survey note alone",
};

const MARKERS__Documentation_zigux_README_md = [_][]const u8{
    "keep `scripts\\zigux/check_phase5_review_guide_surface.zig` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.",
    "keep the bounded `kobject` attr-group companion explicit here too: `samples/zigux/kobject_example_attr_group_contract.zig` is current direct sample-root evidence for the `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot rather than a fifth Phase 5 sample family.",
    "keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording.",
    "keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.",
    "keep the current `kobject` ownership-and-lifetime split explicit too: `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are current direct reminder or packet evidence again, while `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` stay public-tree-backed companion evidence until a fresh authenticated reread restores direct proof for those three routes.",
};

const MARKERS__Documentation_zigux_phase5-trace-events-approved-idiom-gap_md = [_][]const u8{
    "Keep the approved formatting idiom bounded to the current landed reminder packet:",
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
    "Keep the sample-owned review contract explicit too: the bounded formatting companion now centralizes the exact `checked_focus` order `string_selection,formatted_message,bounded_destination_discipline,non_allocating_runtime_safe`, and the approved-idiom reminder should preserve that same reading order beside the selected-string slot and `iter=%d` cue instead of reducing the trace-events packet to message text alone.",
    "Keep the bounded destination discipline explicit in that same reminder packet too: `formatIterationMessageInto(12, [5]u8)` still returns `error.NoSpaceLeft` without advancing the sample stage or `replay_runs`, while `formatIterationMessageInto(12, [7]u8)` still returns `\"iter=12\"` and keeps the sample in `.initialized`.",
    "Keep the direct modulo-selected cycle explicit too: `runStringFormattingCycleReplay()` now walks all five selected strings through the bounded `iter=%d` formatter while keeping the companion in `.initialized` and leaving `replay_runs` unchanged.",
    "Keep the selected-string iteration companion explicit too: `formatSelectedIterationMessageInto(3, [12]u8)` still returns `\"Frodo iter=3\"` while keeping the sample in `.initialized`, so the approved-idiom note must preserve the selected-string-plus-iteration wording instead of reducing the packet to the bare `iter=%d` formatter.",
    "The same authenticated sample-root reread now directly exposes this bounded callback-focus companion too:",
    "The same authenticated sample-root reread now directly exposes this bounded payload-preview companion too:",
    "## Exact checks run on 2026-05-20",
    "This run verified the current formatting companion with the attached Zig toolchain `0.17.0-dev.877+a3ae499dc` using a focused `zig test` against the current `master` file body.",
    "The exact checks that passed were:",
    "- `phase 5 trace-events formatting companion keeps the selected-string cue reviewable`",
    "- `phase 5 trace-events formatting companion keeps the modulo-selected string cycle reviewable`",
    "- `phase 5 trace-events formatting companion keeps lifecycle boundaries explicit`",
    "- `phase 5 trace-events formatting companion keeps bounded destination failures explicit`",
    "This survey note is directly readable again on current `master` and should stay grouped with the shared reminder packet rather than with the still-split sample-local companion set:",
};

const MARKERS__Documentation_zigux_phase5-kobject-sample-survey_md = [_][]const u8{
    "`samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` together keep the bounded `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, NULL-terminated attribute-list slot, and shared build-route linkage explicit rather than turning that companion into a fifth Phase 5 sample",
    "`zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` stays the focused replay route for the same attr-group packet",
    "`zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` stays the survey-guard route that checks the companion, focused replay, and shared build-route markers together",
};

const MARKERS__Documentation_zigux_review-checklist_md = [_][]const u8{
    "if the change touches the shared Phase 5 sample packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts\\zigux/check_phase5_review_guide_surface.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still agree on the current four-anchor reminder packet,",
    "keep `samples/zigux/trace_events_string_formatting_sample.zig` framed only as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample,",
    "keep `scripts\\zigux/check_phase5_review_guide_surface.zig` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording,",
    "keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` explicit as the current direct reminder or replay surfaces in this runtime, keep `samples/zigux/kobject_example.zig` framed as the current shared-reminder-backed owner path, keep `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again,",
};

const MARKERS__scripts_zigux_README_md = [_][]const u8{
    "`zig run scripts\\zigux/check_phase5_review_guide_surface.zig -- --self-test` replays the shipped shared Phase 5 scripts-root reminder guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording",
    "keep the current kobject split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the direct reminder or replay surfaces in this runtime, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again",
    "keep the bytestream build split explicit too: `zigux/tests/phase5_build.zig` is current directly readable shared build-route companion evidence for this scripts-root packet rather than public-tree-backed support or sample-local proof",
    "keep the no-extra-sample boundary explicit from the scripts root too: do not treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence, and do not treat standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 scripts-root packet.",
};

const MARKERS__zigux_tests_README_md = [_][]const u8{
    "Keep `scripts\\zigux/check_phase5_review_guide_surface.zig` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording instead of treating the Phase 5 tests-root packet as docs-only guidance.",
    "Keep `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` explicit as the direct bytestream replay, manifest, and survey packet while `zigux/tests/phase5_build.zig` stays current directly readable shared build-route companion evidence in this runtime.",
    "Keep `Documentation/zigux/phase5-trace-events-sample-survey.md` explicit with the shared Phase 5 reminder packet as the directly readable survey note for that anchor, while `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` stay framed as public-tree-backed companion or repo-reality-gap references until a fresh authenticated reread returns that broader four-file trace-events packet directly again.",
    "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again, `samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract plus the shared `0664`, unnamed-group, and NULL-terminated attribute-list cues, keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet, while `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.",
    "Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.",
};

const MARKERS__Documentation_zigux_phase5-sample-lane-sequencing_md = [_][]const u8{
    "Keep the dedicated scripts-side review-guide guard explicit too: `scripts\\zigux/check_phase5_review_guide_surface.zig` is the shipped checker for the guide's direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording, so same-lane follow-through should not describe the shared Phase 5 packet as guide-only reminder prose anymore.",
    "Treat `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` as the current direct reminder or replay surfaces inside the mixed kobject packet recorded by `Documentation/zigux/phase5-kobject-sample-survey.md`, while `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain the public-tree-backed owner-plus-companion set in this runtime.",
    "Keep `samples/zigux/kobject_example_attr_group_contract.zig` explicit as direct current sample-root evidence for the bounded kobject attr-group companion rather than leaving that shipped reviewability file outside the sample-root inventory.",
    "Treat `samples/zigux/trace_events_string_formatting_sample.zig` as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.",
    "the current trace-events packet split: the bounded formatting companion stays directly readable through `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, and the shared Phase 5 reminder surfaces; authenticated contents reread in this run also directly returned `zigux/tests/phase5_build.zig`; the broader sample-local companions `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` still depend on fresh public GitHub blob or tree fallback in this runtime, so keep those four broader trace-events companions explicit as public-tree-backed or shared-reminder evidence rather than direct authenticated proof, and keep the returned `zigux/tests/phase5_build.zig` route framed separately as the shared rerun handle rather than sample-local proof",
    "Keep the returned runtime bitmap reminder packet separate too: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` are current direct sample-root evidence for the separate Phase 9 runtime bitmap family, not extra Phase 5 sample proof.",
    "Keep `samples/zigux/kretprobe_example_instance_budget_contract.zig` and `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig` explicit too as the current direct sample-root companion and focused replay for the bounded kretprobe instance-budget packet, so the shared lane note reflects that shipped reviewability surface already on `master`.",
    "there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`",
    "Keep `phase5-kobject-example-sample-selfcheck` explicit too as the named shared `zigux/tests/phase5_build.zig` step that reruns the sample-owned `zig test samples/zigux/kobject_example.zig` self-check, so contributor guidance does not leave that owner-side rerun handle buried in the build wiring alone.",
};

const MARKERS__samples_zigux_README_md = [_][]const u8{
    "Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the current direct reminder or replay surfaces, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again.",
    "Current `master` also ships `samples/zigux/kobject_example_attr_group_contract.zig` as a bounded kobject companion. Keep that file framed as reviewability help for the current `foo`/`baz`/`bar` attribute-group contract, `0664` modes, unnamed-group cue, and NULL-terminated attribute-list slot rather than as a fifth Phase 5 sample family.",
    "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
    "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here. Keep that formatting boundary tied to `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` and the bounded `samples/zigux/trace_events_string_formatting_sample.zig` companion.",
    "* `samples/zigux/trace_events_callback_focus_contract.zig` keeps the shared `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` focus order explicit as trace-events reviewability help at the sample root rather than as a separate Phase 5 sample family",
    "* `samples/zigux/trace_events_payload_preview_contract.zig` stays direct sample-root proof for the bounded payload-shape and conditional-event-family companion, while `samples/zigux/trace_events_sample.zig` stays broader public-tree-backed companion evidence rather than a returned full trace-events port or a fifth sample",
    "* `*kasprintf*`\n* `*strarray*`",
    "* `*rbtree*`",
    "Keep `zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` explicit as the focused replay route for that bounded attr-group packet, and keep `zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` explicit as the survey-guard route that checks the companion, focused replay, and shared build-route markers together while `zigux/tests/phase5_build.zig` stays the current directly readable shared build-route companion for the broader kobject packet.",
    "Current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace_events` anchor instead of treating it as a standalone helper packet or a fifth Phase 5 sample.",
};

const FORBIDDEN_GUIDE_TEXT = [_][]const u8{
    "Treat `samples/zigux/trace_events_string_formatting_sample.zig` as a returned full trace-events port or a fifth sample.",
    "Treat the whole `kobject` packet as fully direct authenticated proof.",
    "Treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence.",
};

const FORBIDDEN_SAMPLE_ROOT_TEXT = [_][]const u8{
    "Keep the kobject anchor framed as a roadmap-backed Phase 5 target with the current mixed packet explicit in this runtime:",
};

const MARKERS = [_][]const u8{
    "Treat those four anchors as the approved Phase 5 destination set unless the roadmap changes.",
    "The same authenticated route also directly returns the shared build-route companion `zigux/tests/phase5_build.zig` for this packet.",
    "Current `master` still ships no standalone `samples/zigux/*printf*` or `*vsprintf*` Phase 5 reference sample, and it still ships no standalone broad `*format*` Phase 5 reference sample outside the bounded trace-events cues carried by `samples/zigux/trace_events_string_formatting_sample.zig` and the shared reminder packet.",
    "Keep the direct validation routes explicit in that same guidance too: `zig test samples/zigux/bytestream_fifo.zig`, `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig`, and `zig test zigux/tests/phase5_bytestream_fifo_survey.zig` stay visible as the sample-owned self-check route, the focused replay route, and the survey-packet guard, while the shared `zigux/tests/phase5_build.zig` line stays visible as current directly readable shared build-route companion evidence for this bytestream packet rather than as sample-local proof.",
    "keep the `abandoned_before_registration` versus `tore_down_registered_attributes` exit split explicit alongside the registered teardown, post-`exit()` rejection, and anchor-replay rejection packet",
    "Fresh 2026-05-20 follow-up reread also keeps the current direct packet shape explicit: `samples/zigux/bytestream_fifo.zig` now carries four in-file self-checks, `zigux/tests/phase5_bytestream_fifo.zig` keeps five focused replay tests, and `zigux/tests/phase5_bytestream_fifo_survey.zig` keeps five survey-packet checks aligned with the survey note and manifest.",
    "`zig test samples/zigux/kobject_example_attr_group_contract.zig` stays the companion-only validation route for the attr-group contract while `zigux/tests/phase5_build.zig` remains the directly readable shared build-route companion for this packet",
    "`samples/zigux/trace_events_callback_focus_contract.zig` keeps the shared `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` `checked_focus` order plus the callback-registration recovery cues explicit at the sample root without turning that companion into a fifth Phase 5 sample.",
    "`samples/zigux/trace_events_payload_preview_contract.zig` keeps the sibling payload-preview companion explicit through `referencePattern()`, the five-case modulo-selected preview ladder, the direct `conditional_event_families` cue, the `vararg_payload_path_checked` and `relative_location_path_checked` booleans, and the largest bounded preview case `\"One ring to rule them all\"` plus `\"iter=4\"` instead of turning that companion into a fifth Phase 5 sample.",
    "`samples/zigux/kretprobe_example_probe_spec.zig` plus `zigux/tests/phase5_kretprobe_example_probe_spec.zig` keep the direct Linux anchor path, default symbol, one-word private-data width, default `maxactive`, replay return and duration summary, missed-instance cue, and the pre-init-only symbol-selection and maxactive-tuning rules explicit beside the main replay packet instead of leaving that probe-spec reviewability trapped in the dedicated survey note alone",
    "keep `scripts\\zigux/check_phase5_review_guide_surface.zig` explicit here as the shipped shared guard for the direct bytestream and kretprobe proof markers, the bounded trace-events companion wording, and the no-extra-sample boundary instead of treating the docs-root Phase 5 packet as guide-only prose.",
    "keep the bounded `kobject` attr-group companion explicit here too: `samples/zigux/kobject_example_attr_group_contract.zig` is current direct sample-root evidence for the `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, and NULL-terminated attribute-list slot rather than a fifth Phase 5 sample family.",
    "keep `samples/zigux/runtime_*.zig` framed as separate Phase 9 runtime-pilot evidence rather than extra Phase 5 proof, and keep the current `kobject` anchor split explicit instead of falling back to older repo-reality-gap wording.",
    "keep the no-extra-sample boundary explicit here too: there is no standalone `samples/zigux/*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep those helper families tied to their existing helper or later-phase packets instead of treating the sample root as proof they landed here.",
    "keep the current `kobject` ownership-and-lifetime split explicit too: `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are current direct reminder or packet evidence again, while `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` stay public-tree-backed companion evidence until a fresh authenticated reread restores direct proof for those three routes.",
    "Keep the approved formatting idiom bounded to the current landed reminder packet:",
    "Current `master` also still ships no standalone Phase 5 `samples/zigux/*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, or `*bitmap*` reference sample.",
    "Keep the sample-owned review contract explicit too: the bounded formatting companion now centralizes the exact `checked_focus` order `string_selection,formatted_message,bounded_destination_discipline,non_allocating_runtime_safe`, and the approved-idiom reminder should preserve that same reading order beside the selected-string slot and `iter=%d` cue instead of reducing the trace-events packet to message text alone.",
    "Keep the bounded destination discipline explicit in that same reminder packet too: `formatIterationMessageInto(12, [5]u8)` still returns `error.NoSpaceLeft` without advancing the sample stage or `replay_runs`, while `formatIterationMessageInto(12, [7]u8)` still returns `\"iter=12\"` and keeps the sample in `.initialized`.",
    "Keep the direct modulo-selected cycle explicit too: `runStringFormattingCycleReplay()` now walks all five selected strings through the bounded `iter=%d` formatter while keeping the companion in `.initialized` and leaving `replay_runs` unchanged.",
    "Keep the selected-string iteration companion explicit too: `formatSelectedIterationMessageInto(3, [12]u8)` still returns `\"Frodo iter=3\"` while keeping the sample in `.initialized`, so the approved-idiom note must preserve the selected-string-plus-iteration wording instead of reducing the packet to the bare `iter=%d` formatter.",
    "The same authenticated sample-root reread now directly exposes this bounded callback-focus companion too:",
    "The same authenticated sample-root reread now directly exposes this bounded payload-preview companion too:",
    "## Exact checks run on 2026-05-20",
    "This run verified the current formatting companion with the attached Zig toolchain `0.17.0-dev.877+a3ae499dc` using a focused `zig test` against the current `master` file body.",
    "The exact checks that passed were:",
    "- `phase 5 trace-events formatting companion keeps the selected-string cue reviewable`",
    "- `phase 5 trace-events formatting companion keeps the modulo-selected string cycle reviewable`",
    "- `phase 5 trace-events formatting companion keeps lifecycle boundaries explicit`",
    "- `phase 5 trace-events formatting companion keeps bounded destination failures explicit`",
    "This survey note is directly readable again on current `master` and should stay grouped with the shared reminder packet rather than with the still-split sample-local companion set:",
    "`samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` together keep the bounded `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, unnamed-group marker, NULL-terminated attribute-list slot, and shared build-route linkage explicit rather than turning that companion into a fifth Phase 5 sample",
    "`zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` stays the focused replay route for the same attr-group packet",
    "`zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` stays the survey-guard route that checks the companion, focused replay, and shared build-route markers together",
    "if the change touches the shared Phase 5 sample packet, do `Documentation/zigux/README.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts\\zigux/check_phase5_review_guide_surface.zig`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still agree on the current four-anchor reminder packet,",
    "keep `samples/zigux/trace_events_string_formatting_sample.zig` framed only as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample,",
    "keep `scripts\\zigux/check_phase5_review_guide_surface.zig` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording,",
    "keep `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` explicit as the current direct reminder or replay surfaces in this runtime, keep `samples/zigux/kobject_example.zig` framed as the current shared-reminder-backed owner path, keep `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` framed as current public-tree-backed companion evidence until a fresh reread proves broader direct authenticated proof again,",
    "`zig run scripts\\zigux/check_phase5_review_guide_surface.zig -- --self-test` replays the shipped shared Phase 5 scripts-root reminder guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording",
    "keep the current kobject split explicit too: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the direct reminder or replay surfaces in this runtime, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again",
    "keep the bytestream build split explicit too: `zigux/tests/phase5_build.zig` is current directly readable shared build-route companion evidence for this scripts-root packet rather than public-tree-backed support or sample-local proof",
    "keep the no-extra-sample boundary explicit from the scripts root too: do not treat `samples/zigux/runtime_*.zig` as extra Phase 5 evidence, and do not treat standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 scripts-root packet.",
    "Keep `scripts\\zigux/check_phase5_review_guide_surface.zig` explicit as the shipped guide-surface guard for the direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording instead of treating the Phase 5 tests-root packet as docs-only guidance.",
    "Keep `zigux/tests/phase5_bytestream_fifo.zig`, `zigux/tests/phase5_bytestream_fifo_manifest.json`, and `zigux/tests/phase5_bytestream_fifo_survey.zig` explicit as the direct bytestream replay, manifest, and survey packet while `zigux/tests/phase5_build.zig` stays current directly readable shared build-route companion evidence in this runtime.",
    "Keep `Documentation/zigux/phase5-trace-events-sample-survey.md` explicit with the shared Phase 5 reminder packet as the directly readable survey note for that anchor, while `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` stay framed as public-tree-backed companion or repo-reality-gap references until a fresh authenticated reread returns that broader four-file trace-events packet directly again.",
    "Keep the current kobject split explicit too: `zigux/tests/phase5_kobject_example.zig` is direct tests-root packet evidence again, `samples/zigux/kobject_example_attr_group_contract.zig` stays explicit as the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract plus the shared `0664`, unnamed-group, and NULL-terminated attribute-list cues, keep `zigux/tests/phase5_build.zig` explicit as the current directly readable shared build-route companion for that packet, while `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread returns those routes directly again.",
    "Keep `samples/zigux/runtime_*.zig` plus standalone `*string*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, and broad `*format*` sample claims out of this non-runtime Phase 5 tests-root packet.",
    "Keep the dedicated scripts-side review-guide guard explicit too: `scripts\\zigux/check_phase5_review_guide_surface.zig` is the shipped checker for the guide's direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording, so same-lane follow-through should not describe the shared Phase 5 packet as guide-only reminder prose anymore.",
    "Treat `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` as the current direct reminder or replay surfaces inside the mixed kobject packet recorded by `Documentation/zigux/phase5-kobject-sample-survey.md`, while `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain the public-tree-backed owner-plus-companion set in this runtime.",
    "Keep `samples/zigux/kobject_example_attr_group_contract.zig` explicit as direct current sample-root evidence for the bounded kobject attr-group companion rather than leaving that shipped reviewability file outside the sample-root inventory.",
    "Treat `samples/zigux/trace_events_string_formatting_sample.zig` as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.",
    "the current trace-events packet split: the bounded formatting companion stays directly readable through `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, and the shared Phase 5 reminder surfaces; authenticated contents reread in this run also directly returned `zigux/tests/phase5_build.zig`; the broader sample-local companions `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` still depend on fresh public GitHub blob or tree fallback in this runtime, so keep those four broader trace-events companions explicit as public-tree-backed or shared-reminder evidence rather than direct authenticated proof, and keep the returned `zigux/tests/phase5_build.zig` route framed separately as the shared rerun handle rather than sample-local proof",
    "Keep the returned runtime bitmap reminder packet separate too: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` are current direct sample-root evidence for the separate Phase 9 runtime bitmap family, not extra Phase 5 sample proof.",
    "Keep `samples/zigux/kretprobe_example_instance_budget_contract.zig` and `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig` explicit too as the current direct sample-root companion and focused replay for the bounded kretprobe instance-budget packet, so the shared lane note reflects that shipped reviewability surface already on `master`.",
    "there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`",
    "Keep `phase5-kobject-example-sample-selfcheck` explicit too as the named shared `zigux/tests/phase5_build.zig` step that reruns the sample-owned `zig test samples/zigux/kobject_example.zig` self-check, so contributor guidance does not leave that owner-side rerun handle buried in the build wiring alone.",
    "Current `master` keeps the roadmap-backed `kobject` packet split explicit in this runtime: `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` are the current direct reminder or replay surfaces, while `samples/zigux/kobject_example.zig` remains the current shared-reminder-backed owner path and `zigux/tests/phase5_kobject_example_manifest.json` plus `zigux/tests/phase5_kobject_example_survey.zig` remain current public-tree-backed companion evidence until a fresh authenticated reread proves broader direct authenticated proof again.",
    "Current `master` also ships `samples/zigux/kobject_example_attr_group_contract.zig` as a bounded kobject companion. Keep that file framed as reviewability help for the current `foo`/`baz`/`bar` attribute-group contract, `0664` modes, unnamed-group cue, and NULL-terminated attribute-list slot rather than as a fifth Phase 5 sample family.",
    "Current `master` still ships no `samples/zigux/*bitmap*` Phase 5 reference sample. Keep the returned runtime bitmap files framed only as separate Phase 9 runtime-pilot evidence.",
    "Current `master` also still ships no standalone broad `*format*` Phase 5 reference sample here. Keep that formatting boundary tied to `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` and the bounded `samples/zigux/trace_events_string_formatting_sample.zig` companion.",
    "* `samples/zigux/trace_events_callback_focus_contract.zig` keeps the shared `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` focus order explicit as trace-events reviewability help at the sample root rather than as a separate Phase 5 sample family",
    "* `samples/zigux/trace_events_payload_preview_contract.zig` stays direct sample-root proof for the bounded payload-shape and conditional-event-family companion, while `samples/zigux/trace_events_sample.zig` stays broader public-tree-backed companion evidence rather than a returned full trace-events port or a fifth sample",
    "* `*kasprintf*`n* `*strarray*`",
    "* `*rbtree*`",
    "Keep `zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig` explicit as the focused replay route for that bounded attr-group packet, and keep `zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig` explicit as the survey-guard route that checks the companion, focused replay, and shared build-route markers together while `zigux/tests/phase5_build.zig` stays the current directly readable shared build-route companion for the broader kobject packet.",
    "Current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace_events` anchor instead of treating it as a standalone helper packet or a fifth Phase 5 sample.",
};

const SURFACE_PATHS = [_][]const u8{
    "Documentation/zigux/phase5-kfifo-sample-survey.md",
    "Documentation/zigux/phase5-kretprobe-sample-survey.md",
    "Documentation/zigux/phase5-sample-lane-sequencing.md",
    "Documentation/zigux/phase5-sample-review-guide.md",
    "Documentation/zigux/phase5-trace-events-approved-idiom-gap.md",
    "Documentation/zigux/phase5-trace-events-sample-survey.md",
    "Documentation/zigux/review-checklist.md",
    "samples/zigux/README.md",
    "samples/zigux/bytestream_fifo.zig",
    "samples/zigux/bytestream_fifo_window_contract.zig",
    "samples/zigux/kobject_example.zig",
    "samples/zigux/kobject_example_attr_group_contract.zig",
    "samples/zigux/kretprobe_example.zig",
    "samples/zigux/kretprobe_example_instance_budget_contract.zig",
    "samples/zigux/kretprobe_example_probe_spec.zig",
    "samples/zigux/trace_events_callback_focus_contract.zig",
    "samples/zigux/trace_events_payload_preview_contract.zig",
    "samples/zigux/trace_events_string_formatting_sample.zig",
    "scripts/zigux/README.md",
    "scripts\\zigux/check_phase5_review_guide_surface.zig",
    "zigux/tests/README.md",
    "zigux/tests/phase5_bytestream_fifo.zig",
    "zigux/tests/phase5_bytestream_fifo_manifest.json",
    "zigux/tests/phase5_bytestream_fifo_survey.zig",
    "zigux/tests/phase5_kobject_example.zig",
    "zigux/tests/phase5_kretprobe_example.zig",
    "zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig",
    "zigux/tests/phase5_kretprobe_example_manifest.json",
    "zigux/tests/phase5_kretprobe_example_probe_spec.zig",
    "zigux/tests/phase5_kretprobe_example_survey.zig",
    "zigux/tests/phase5_build.zig",
};

fn checkRepo(io: Io, allocator: std.mem.Allocator, root: []const u8) !void {
    const text_markers__documentation_zigux_phase5-sample-review-guide_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-sample-review-guide/md");
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-review-guide_md_path);
    const text_markers__documentation_zigux_phase5-sample-review-guide_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_phase5-sample-review-guide_md_path);
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-review-guide_md);
    for (MARKERS__Documentation_zigux_phase5-sample-review-guide_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_phase5-sample-review-guide_md, marker);
    const text_markers__documentation_zigux_readme_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/README/md");
    defer allocator.free(text_markers__documentation_zigux_readme_md_path);
    const text_markers__documentation_zigux_readme_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_readme_md_path);
    defer allocator.free(text_markers__documentation_zigux_readme_md);
    for (MARKERS__Documentation_zigux_README_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_readme_md, marker);
    const text_markers__documentation_zigux_phase5-trace-events-approved-idiom-gap_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-trace-events-approved-idiom-gap/md");
    defer allocator.free(text_markers__documentation_zigux_phase5-trace-events-approved-idiom-gap_md_path);
    const text_markers__documentation_zigux_phase5-trace-events-approved-idiom-gap_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_phase5-trace-events-approved-idiom-gap_md_path);
    defer allocator.free(text_markers__documentation_zigux_phase5-trace-events-approved-idiom-gap_md);
    for (MARKERS__Documentation_zigux_phase5-trace-events-approved-idiom-gap_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_phase5-trace-events-approved-idiom-gap_md, marker);
    const text_markers__documentation_zigux_phase5-kobject-sample-survey_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-kobject-sample-survey/md");
    defer allocator.free(text_markers__documentation_zigux_phase5-kobject-sample-survey_md_path);
    const text_markers__documentation_zigux_phase5-kobject-sample-survey_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_phase5-kobject-sample-survey_md_path);
    defer allocator.free(text_markers__documentation_zigux_phase5-kobject-sample-survey_md);
    for (MARKERS__Documentation_zigux_phase5-kobject-sample-survey_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_phase5-kobject-sample-survey_md, marker);
    const text_markers__documentation_zigux_review-checklist_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/review-checklist/md");
    defer allocator.free(text_markers__documentation_zigux_review-checklist_md_path);
    const text_markers__documentation_zigux_review-checklist_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_review-checklist_md_path);
    defer allocator.free(text_markers__documentation_zigux_review-checklist_md);
    for (MARKERS__Documentation_zigux_review-checklist_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_review-checklist_md, marker);
    const text_markers__scripts_zigux_readme_md_path = try guard.joinPath(allocator, root, "scripts/zigux/README/md");
    defer allocator.free(text_markers__scripts_zigux_readme_md_path);
    const text_markers__scripts_zigux_readme_md = try guard.readUtf8File(io, allocator, text_markers__scripts_zigux_readme_md_path);
    defer allocator.free(text_markers__scripts_zigux_readme_md);
    for (MARKERS__scripts_zigux_README_md) |marker| try guard.requireMarker(text_markers__scripts_zigux_readme_md, marker);
    const text_markers__zigux_tests_readme_md_path = try guard.joinPath(allocator, root, "zigux/tests/README/md");
    defer allocator.free(text_markers__zigux_tests_readme_md_path);
    const text_markers__zigux_tests_readme_md = try guard.readUtf8File(io, allocator, text_markers__zigux_tests_readme_md_path);
    defer allocator.free(text_markers__zigux_tests_readme_md);
    for (MARKERS__zigux_tests_README_md) |marker| try guard.requireMarker(text_markers__zigux_tests_readme_md, marker);
    const text_markers__documentation_zigux_phase5-sample-lane-sequencing_md_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-sample-lane-sequencing/md");
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-lane-sequencing_md_path);
    const text_markers__documentation_zigux_phase5-sample-lane-sequencing_md = try guard.readUtf8File(io, allocator, text_markers__documentation_zigux_phase5-sample-lane-sequencing_md_path);
    defer allocator.free(text_markers__documentation_zigux_phase5-sample-lane-sequencing_md);
    for (MARKERS__Documentation_zigux_phase5-sample-lane-sequencing_md) |marker| try guard.requireMarker(text_markers__documentation_zigux_phase5-sample-lane-sequencing_md, marker);
    const text_markers__samples_zigux_readme_md_path = try guard.joinPath(allocator, root, "samples/zigux/README/md");
    defer allocator.free(text_markers__samples_zigux_readme_md_path);
    const text_markers__samples_zigux_readme_md = try guard.readUtf8File(io, allocator, text_markers__samples_zigux_readme_md_path);
    defer allocator.free(text_markers__samples_zigux_readme_md);
    for (MARKERS__samples_zigux_README_md) |marker| try guard.requireMarker(text_markers__samples_zigux_readme_md, marker);
    const text_forbidden_guide_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-sample-review-guide.md");
    defer allocator.free(text_forbidden_guide_text_path);
    const text_forbidden_guide_text = try guard.readUtf8File(io, allocator, text_forbidden_guide_text_path);
    defer allocator.free(text_forbidden_guide_text);
    for (FORBIDDEN_GUIDE_TEXT) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_guide_text, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_forbidden_sample_root_text_path = try guard.joinPath(allocator, root, "Documentation/zigux/phase5-sample-review-guide.md");
    defer allocator.free(text_forbidden_sample_root_text_path);
    const text_forbidden_sample_root_text = try guard.readUtf8File(io, allocator, text_forbidden_sample_root_text_path);
    defer allocator.free(text_forbidden_sample_root_text);
    for (FORBIDDEN_SAMPLE_ROOT_TEXT) |marker| {
        if (std.mem.indexOf(u8, text_forbidden_sample_root_text, marker) != null) return guard.GuardError.MissingMarker;
    }
    const text_markers_path = try guard.joinPath(allocator, root, ".github/workflows/zigux-bootstrap.yml");
    defer allocator.free(text_markers_path);
    const text_markers = try guard.readUtf8File(io, allocator, text_markers_path);
    defer allocator.free(text_markers);
    for (MARKERS) |marker| try guard.requireMarker(text_markers, marker);
    for (SURFACE_PATHS) |rel| {
        const path = try guard.joinPath(allocator, root, rel);
        defer allocator.free(path);
        if (!guard.pathExists(io, path)) return guard.GuardError.IOError;
    }
}

fn runSelfTest(io: Io, allocator: std.mem.Allocator) !u8 {
    try checkRepo(io, allocator, try guard.defaultRepoRoot(allocator));
    try guard.printLine(io, "{s}", .{self_test_pass_marker});
    return 0;
}

pub fn main(init: std.process.Init) !void {
    const allocator = init.gpa;
    const io = init.io;
    const args = try init.minimal.args.toSlice(allocator);

    var self_test = false;
    var explicit_root: ?[]const u8 = null;
    var index: usize = 1;
    while (index < args.len) : (index += 1) {
        const arg = args[index];
        if (std.mem.eql(u8, arg, "--self-test")) {
            self_test = true;
            continue;
        }
        if (std.mem.eql(u8, arg, "--root")) {
            if (index + 1 >= args.len) std.process.exit(2);
            index += 1;
            explicit_root = args[index];
            continue;
        }
    }

    const root = explicit_root orelse try guard.repoRootFromScript(allocator);
    defer if (explicit_root == null) allocator.free(root);

    if (self_test) {
        std.process.exit(try runSelfTest(io, allocator));
    }

    checkRepo(io, allocator, root) catch {
        std.process.exit(1);
    };
    try guard.printLine(io, "{s}", .{live_pass_marker});
}
