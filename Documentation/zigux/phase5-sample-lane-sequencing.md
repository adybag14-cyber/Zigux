# Phase 5 Sample Lane Sequencing

This note keeps the roadmap-backed Phase 5 lane narrow on current `master`.

## Purpose

Use this shared note when a Phase 5 change touches approved sample anchors, shared contributor guidance, or the tracing and probe reminder surfaces.

Keep the lane sequencing honest:

- stay inside the four approved non-runtime Linux sample anchors
- prefer one reminder-surface repair at a time
- keep roadmap anchors distinct from current repo-readback proof
- keep later runtime-facing sample families in the separate Phase 9 lane

## Approved anchors

Phase 5 remains limited to these roadmap-backed sample anchors:

- `samples/kfifo/bytestream-example.c`
- `samples/kobject/kobject-example.c`
- `samples/kprobes/kretprobe_example.c`
- `samples/trace_events/trace-events-sample.c`

Treat those four anchors as the full Phase 5 destination set unless the roadmap changes.

## Current shared packet on `master`

Fresh repo-first inspection in this run confirmed that current `master` still keeps the shared Phase 5 reminder packet reviewable through these directly readable surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/check-phase5-review-guide-surface.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_build.zig`

The same reread also confirmed that current `master` still keeps the restored direct bytestream packet, the restored direct kretprobe packet, the bounded trace-events formatting companion, the bounded callback-focus companion, and the bounded payload-preview companion visible from the sample root, and the roadmap-backed `kobject` anchor in a mixed current-readback packet: authenticated contents readback in this runtime directly returned `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig`, while the same-lane survey note and fresh public current-`master` GitHub file readback still keep `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` explicit beside that direct packet.

Keep this shared note truthful about that current packet instead of repeating older missing-sample wording for bytestream, older broader direct-sample wording for trace-events, or collapsing the still-visible kobject packet into repo absence.
Keep the directly readable `zigux/tests/phase5_build.zig` route explicit too: it is current shared rerun evidence for the restored bytestream and kretprobe reminder packet, but it still should not be described as sample-local proof.
Keep the dedicated scripts-side review-guide guard explicit too: `scripts/zigux/check-phase5-review-guide-surface.py` is the shipped checker for the guide's direct-proof, public-tree-backed-companion, and no-extra-sample boundary wording, so same-lane follow-through should not describe the shared Phase 5 packet as guide-only reminder prose anymore.

## Current sample-root reality

Fresh authenticated reread in this run still directly proves these current sample-root files on `master`:

- `samples/zigux/README.md`
- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/bytestream_fifo_window_contract.zig`
- `samples/zigux/kobject_example_attr_group_contract.zig`
- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/kretprobe_example_instance_budget_contract.zig`
- `samples/zigux/kretprobe_example_probe_spec.zig`
- `samples/zigux/trace_events_string_formatting_sample.zig`
- `samples/zigux/trace_events_callback_focus_contract.zig`
- `samples/zigux/trace_events_payload_preview_contract.zig`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_direct_init_contract.zig`
- `samples/zigux/runtime_bitmap_cold_stage_guard.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
- `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`

So the current direct sample-root evidence for the roadmap-backed non-runtime Phase 5 lane is the restored bytestream port, the bounded bytestream window companion, the bounded kobject attr-group companion, the restored kretprobe port, the bounded kretprobe instance-budget companion, the bounded kretprobe probe-spec companion, the bounded trace-events formatting companion, the bounded trace-events callback-focus companion, and the bounded trace-events payload-preview companion.
Treat `samples/zigux/bytestream_fifo.zig` as the current direct sample-root proof for its approved anchor.
Keep the bytestream queue-shape posture explicit too: the current direct replay packet now exact-checks `occupancySummary().queue_len`, `available`, and `wrapped` together with the visible-span and writable-span boundaries, so shared reminders should not collapse that packet back to queue length alone.
Keep the direct rerun split explicit too: `samples/zigux/bytestream_fifo.zig` now carries four in-file self-checks, `zigux/tests/phase5_bytestream_fifo.zig` carries five focused replay tests, `zigux/tests/phase5_bytestream_fifo_survey.zig` carries five survey-packet checks, and `zigux/tests/phase5_build.zig` is the shared rerun handle that replays those three bytestream surfaces together without turning the shared build route into sample-local proof.
Treat `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` as the current direct reminder or replay surfaces inside the mixed kobject packet recorded by `Documentation/zigux/phase5-kobject-sample-survey.md`, while `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain the public-tree-backed owner-plus-companion set in this runtime.
Keep `samples/zigux/kobject_example_attr_group_contract.zig` explicit as direct current sample-root evidence for the bounded kobject attr-group companion rather than leaving that shipped reviewability file outside the sample-root inventory.
Keep `zigux/tests/phase5_kobject_attr_group_contract.zig` and `zigux/tests/phase5_kobject_attr_group_contract_survey.zig` explicit too as the current direct focused replay and survey-guard companions for that same bounded attr-group packet, so the shared lane note reflects the full concrete sample-backed kobject review surface already on `master`.
Keep `phase5-kobject-example-sample-selfcheck` explicit too as the named shared `zigux/tests/phase5_build.zig` step that reruns the sample-owned `zig test samples/zigux/kobject_example.zig` self-check, so contributor guidance does not leave that owner-side rerun handle buried in the build wiring alone.
Treat `samples/zigux/kretprobe_example.zig` as the current direct sample-root proof for its approved anchor.
Keep `samples/zigux/kretprobe_example_instance_budget_contract.zig` and `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig` explicit too as the current direct sample-root companion and focused replay for the bounded kretprobe instance-budget packet, and keep `zigux/tests/phase5_build.zig` explicit as the shared rerun handle that replays those companion checks beside the main kretprobe packet without turning that build route into sample-local proof, so the shared lane note reflects that shipped reviewability surface already on `master`.
Keep `samples/zigux/kretprobe_example_probe_spec.zig` and `zigux/tests/phase5_kretprobe_example_probe_spec.zig` explicit too as the current direct sample-root companion and focused replay for the bounded kretprobe probe-spec packet, and keep `zigux/tests/phase5_build.zig` explicit as the shared rerun handle that replays those companion checks beside the main kretprobe packet without turning that build route into sample-local proof, so the shared lane note reflects that shipped reviewability surface already on `master`.
Keep `zig test samples/zigux/kretprobe_example_instance_budget_contract.zig` and `zig test samples/zigux/kretprobe_example_probe_spec.zig` explicit too as the companion-only validation routes for those bounded kretprobe packets, so contributor guidance keeps the sample-owned review hooks visible beside the focused replay routes and shared rerun handle.
Treat `samples/zigux/trace_events_string_formatting_sample.zig` as the bounded trace-events formatting companion rather than a returned full trace-events port or a fifth sample.
Treat `samples/zigux/trace_events_callback_focus_contract.zig` as the bounded trace-events callback-focus companion that keeps the shared `payload_shape`, `string_selection`, `formatted_message`, `conditional_event_families`, `function_callback_registration`, and `ownership_and_lifetime` focus order reviewable without turning that companion into a fifth sample.
Treat `samples/zigux/trace_events_payload_preview_contract.zig` as the bounded trace-events payload-preview companion that keeps the five-case preview ladder, the `conditional_event_families` cue, the `vararg_payload_path_checked` and `relative_location_path_checked` booleans, and the largest bounded preview case reviewable without turning that companion into a fifth sample.
Keep the roadmap-backed `kobject` anchor explicit because `Documentation/zigux/phase5-kobject-sample-survey.md`, `samples/zigux/kobject_example_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract.zig`, `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`, `zigux/tests/phase5_kobject_example.zig`, and `zigux/tests/phase5_build.zig` remain the direct authenticated reminder or replay packet in this runtime, while fresh public current-`master` GitHub file readback still keeps `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` visible as the owner-plus-companion evidence. Keep shared contributor guidance honest about that mixed direct-versus-public-tree-backed split instead of repeating older kobject-reread-needed wording, collapsing the packet into repo absence, or overstating fully direct authenticated proof. When the lane reopens, reread the dedicated kobject survey note before tightening deeper lifecycle wording here.
Keep `samples/zigux/kobject_example_attr_group_contract.zig` framed as a bounded kobject companion for the current `foo`/`baz`/`bar` attribute-group contract, shared `0664` mode cues, the unnamed-group marker, and the NULL-terminated attribute-list slot rather than as a fifth Phase 5 sample family.
Keep the returned runtime bitmap reminder packet separate too: `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` are current direct sample-root evidence for the separate Phase 9 runtime bitmap family, not extra Phase 5 sample proof.

## Tracing and probe packet

For the tracing and probe lane, keep follow-through aligned with these bounded reminder surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_build.zig`

Those files should describe:

- the roadmap-backed `kretprobe` and `trace_events` anchors
- the current split between the restored direct kretprobe packet and the narrower trace-events formatting, callback-focus, and payload-preview companion packet
- the approved selected-string plus `iter=%d` formatting idiom cue
- the rule that Phase 9 runtime trace-events files are not extra Phase 5 sample proof
- the returned direct kretprobe packet through `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `samples/zigux/kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example.zig`, `zigux/tests/phase5_kretprobe_example_manifest.json`, and `zigux/tests/phase5_kretprobe_example_survey.zig`
- the bounded instance-budget companion through `samples/zigux/kretprobe_example_instance_budget_contract.zig` and `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig` as current direct sample-root and focused replay evidence for the packet-local `func` parameter, `0o644` mode, default `kernel_clone`, one-word private-data, and `nmissed` / `maxactive` cues, while `zigux/tests/phase5_build.zig` remains the shared rerun handle for those companion checks and the main kretprobe packet rather than sample-local proof
- the bounded probe-spec companion through `samples/zigux/kretprobe_example_probe_spec.zig` and `zigux/tests/phase5_kretprobe_example_probe_spec.zig` as current direct sample-root and focused replay evidence for the packet-local Linux anchor path, default symbol, one-word private-data width, default `maxactive`, replay return and duration summary, missed-instance cue, and the pre-init-only symbol-selection and maxactive-tuning rules, while `zigux/tests/phase5_build.zig` remains the shared rerun handle for those companion checks and the main kretprobe packet rather than sample-local proof
- the sample-owned companion-only validation routes `zig test samples/zigux/kretprobe_example_instance_budget_contract.zig` and `zig test samples/zigux/kretprobe_example_probe_spec.zig`, so the shared lane note keeps those companion review hooks visible beside the focused replay routes and the shared rerun handle
- the current trace-events packet split: the bounded formatting companion, the bounded callback-focus companion, and the bounded payload-preview companion stay directly readable through `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `samples/zigux/trace_events_string_formatting_sample.zig`, `samples/zigux/trace_events_callback_focus_contract.zig`, `samples/zigux/trace_events_payload_preview_contract.zig`, and the shared Phase 5 reminder surfaces; authenticated contents reread in this run also directly returned `zigux/tests/phase5_build.zig`; the broader sample-local companions `samples/zigux/trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample.zig`, `zigux/tests/phase5_trace_events_sample_manifest.json`, and `zigux/tests/phase5_trace_events_sample_survey.zig` still depend on fresh public GitHub blob or tree fallback in this runtime, so keep those four broader trace-events companions explicit as public-tree-backed or shared-reminder evidence rather than direct authenticated proof, and keep the returned `zigux/tests/phase5_build.zig` route framed separately as the shared rerun handle rather than sample-local proof

## Sequencing rules

When the lane reopens, sequence same-lane work in this order:

1. Fix one shared reminder-surface drift first when current packet surfaces disagree.
2. Prefer a shared tracing or probe reminder repair before any sample-local behavior change when the shared surfaces fall behind the already landed packet.
3. Keep wording truthful about what current `master` directly exposes, what currently depends on public raw or tree fallback, and what remains only roadmap-backed guidance.
4. Do not invent validator routes, make wrappers, or workflow coverage that the repo does not ship.
5. Leave the lane parked after one bounded repair unless fresh inspection shows another equally small same-lane drift.

## Phase boundaries

Keep the non-runtime Phase 5 boundary explicit:

- do not widen Phase 5 work into runtime-loader or runtime-pilot behavior
- keep the surviving `samples/zigux/runtime_trace_events*.zig` family in the separate Phase 9 lane, and keep the returned runtime bitmap reminder packet `Documentation/zigux/phase9-runtime-bitmap-survey.md`, `samples/zigux/runtime_bitmap.zig`, `samples/zigux/runtime_bitmap_direct_init_contract.zig`, `samples/zigux/runtime_bitmap_cold_stage_guard.zig`, `samples/zigux/runtime_bitmap_loader.zig`, and `samples/zigux/runtime_bitmap_top_bit_contract.zig` framed as separate Phase 9 runtime evidence rather than extra Phase 5 sample proof
- do not widen toward freeze-in-C anchors such as `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`
- do not pull study-only `kernel/workqueue.c` or `kernel/trace/ring_buffer.c` into this lane

Keep the no-extra-sample helper-family boundaries explicit too:

- current `master` does ship one bounded `*string*` companion through `samples/zigux/trace_events_string_formatting_sample.zig`, but keep it tied to the non-runtime `trace_events` anchor instead of treating it as a standalone helper packet
- there is no standalone `samples/zigux/*kasprintf*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*strarray*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*cmdline*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*argv*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*rbtree*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*bitmap*` Phase 5 reference sample on current `master`
- there is no standalone `samples/zigux/*printf*`, `*vsprintf*`, or broad `*format*` Phase 5 reference sample on current `master`; keep that formatting boundary tied to `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md` and the bounded `samples/zigux/trace_events_string_formatting_sample.zig` companion

## Next-step posture

The next honest Phase 5 step is another one-file reminder-surface repair that keeps the approved anchors explicit without flattening the narrower trace-events formatting packet, callback-focus companion, or payload-preview companion, collapsing the still-visible kobject packet into repo absence, or collapsing the returned shared `zigux/tests/phase5_build.zig` route back into either repo absence or sample-local proof. If the lane reopens soon, compare `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, `scripts/zigux/README.md`, and `zigux/tests/README.md` together before widening any sample behavior.
