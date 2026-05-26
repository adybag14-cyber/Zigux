# Phase 5 Closure

This note closes the missing closure-note record for the active Phase 5 non-runtime sample tranche on current `master`.

## Status

- `PHASE5_STATUS=parked`
- `PHASE5_CLOSURE_RESTORE_STATE=docs_only_closure_note`
- roadmap anchors:
  - `samples/kfifo/bytestream-example.c`
  - `samples/kobject/kobject-example.c`
  - `samples/kprobes/kretprobe_example.c`
  - `samples/trace_events/trace-events-sample.c`
- current authority: this closure note, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-kfifo-sample-survey.md`, `Documentation/zigux/phase5-kretprobe-sample-survey.md`, `Documentation/zigux/phase5-kobject-sample-survey.md`, `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`, `Documentation/zigux/phase5-trace-events-sample-survey.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/check-phase5-review-guide-surface.py`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `zigux/tests/phase5_build.zig` remain the trustworthy current-master packet for the bounded Phase 5 tranche.

The active Phase 5 tranche is not a broad runtime or helper-family lane. It stays limited to the four approved non-runtime sample anchors plus the shared reminder surfaces that keep those anchors reviewable.

## Current Closure Packet

The currently reviewable Phase 5 closure packet is:

- `Documentation/zigux/phase5-closure.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/check-phase5-review-guide-surface.py`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/phase5_build.zig`

- `PHASE5_CURRENT_CLOSURE_PACKET=Documentation/zigux/phase5-closure.md,Documentation/zigux/phase5-sample-lane-sequencing.md,Documentation/zigux/phase5-sample-review-guide.md,Documentation/zigux/phase5-kfifo-sample-survey.md,Documentation/zigux/phase5-kretprobe-sample-survey.md,Documentation/zigux/phase5-kobject-sample-survey.md,Documentation/zigux/phase5-trace-events-approved-idiom-gap.md,Documentation/zigux/phase5-trace-events-sample-survey.md,Documentation/zigux/review-checklist.md,samples/zigux/README.md,scripts/zigux/check-phase5-review-guide-surface.py,scripts/zigux/README.md,zigux/tests/README.md,zigux/tests/phase5_build.zig`

## Current Repo-Reality Split

Current `master` keeps the direct bytestream sample packet explicit through:

- `samples/zigux/bytestream_fifo.zig`
- `samples/zigux/bytestream_fifo_window_contract.zig`
- `zigux/tests/phase5_bytestream_fifo.zig`
- `zigux/tests/phase5_bytestream_fifo_manifest.json`
- `zigux/tests/phase5_bytestream_fifo_survey.zig`

Current `master` keeps the direct kretprobe packet explicit through:

- `samples/zigux/kretprobe_example.zig`
- `samples/zigux/kretprobe_example_instance_budget_contract.zig`
- `samples/zigux/kretprobe_example_probe_spec.zig`
- `zigux/tests/phase5_kretprobe_example.zig`
- `zigux/tests/phase5_kretprobe_example_manifest.json`
- `zigux/tests/phase5_kretprobe_example_survey.zig`
- `zigux/tests/phase5_kretprobe_example_instance_budget_contract.zig`
- `zigux/tests/phase5_kretprobe_example_probe_spec.zig`

Current `master` keeps the trace-events side narrower than a full returned sample packet:

- direct reminder surfaces and companions:
  - `Documentation/zigux/phase5-trace-events-approved-idiom-gap.md`
  - `Documentation/zigux/phase5-trace-events-sample-survey.md`
  - `samples/zigux/trace_events_string_formatting_sample.zig`
  - `samples/zigux/trace_events_callback_focus_contract.zig`
  - `zigux/tests/phase5_build.zig`
- broader public-tree-backed or split companions:
  - `samples/zigux/trace_events_sample.zig`
  - `zigux/tests/phase5_trace_events_sample.zig`
  - `zigux/tests/phase5_trace_events_sample_manifest.json`
  - `zigux/tests/phase5_trace_events_sample_survey.zig`

Current `master` also keeps the roadmap-backed `kobject` anchor in a mixed packet:

- direct reminder or replay surfaces:
  - `Documentation/zigux/phase5-kobject-sample-survey.md`
  - `samples/zigux/kobject_example_attr_group_contract.zig`
  - `zigux/tests/phase5_kobject_attr_group_contract.zig`
  - `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`
  - `zigux/tests/phase5_kobject_example.zig`
  - `zigux/tests/phase5_build.zig`
- public-tree-backed owner or companion surfaces:
  - `samples/zigux/kobject_example.zig`
  - `zigux/tests/phase5_kobject_example_manifest.json`
  - `zigux/tests/phase5_kobject_example_survey.zig`

Keep the no-extra-sample boundary explicit across this closure packet too:

- `samples/zigux/runtime_*.zig` remain separate Phase 9 runtime evidence
- current `master` still ships no standalone Phase 5 `*string*`, `*kasprintf*`, `*strarray*`, `*cmdline*`, `*argv*`, `*rbtree*`, `*bitmap*`, `*printf*`, `*vsprintf*`, or broad `*format*` sample family

- `PHASE5_PUBLIC_TREE_COMPANION_PACKET=samples/zigux/trace_events_sample.zig,zigux/tests/phase5_trace_events_sample.zig,zigux/tests/phase5_trace_events_sample_manifest.json,zigux/tests/phase5_trace_events_sample_survey.zig,samples/zigux/kobject_example.zig,zigux/tests/phase5_kobject_example_manifest.json,zigux/tests/phase5_kobject_example_survey.zig`

## Closure Validation

The current closure packet stays intentionally narrow. The shared Phase 5 guard and the landed sample-owned routes remain the honest replay surfaces that current `master` already names directly:

- `python3 scripts/zigux/check-phase5-review-guide-surface.py --self-test`
- `zig test samples/zigux/bytestream_fifo.zig`
- `zig test samples/zigux/bytestream_fifo_window_contract.zig`
- `zig test --dep bytestream_fifo_sample -Mroot=zigux/tests/phase5_bytestream_fifo.zig -Mbytestream_fifo_sample=samples/zigux/bytestream_fifo.zig`
- `zig test zigux/tests/phase5_bytestream_fifo_survey.zig`
- `zig test samples/zigux/kobject_example.zig`
- `zig test samples/zigux/kobject_example_attr_group_contract.zig`
- `zig test --dep kobject_attr_group_contract -Mroot=zigux/tests/phase5_kobject_attr_group_contract.zig -Mkobject_attr_group_contract=samples/zigux/kobject_example_attr_group_contract.zig`
- `zig test zigux/tests/phase5_kobject_attr_group_contract_survey.zig`
- `zig test samples/zigux/kretprobe_example.zig`
- `zig test samples/zigux/kretprobe_example_instance_budget_contract.zig`
- `zig test samples/zigux/kretprobe_example_probe_spec.zig`
- `zig test --dep kretprobe_example_sample -Mroot=zigux/tests/phase5_kretprobe_example.zig -Mkretprobe_example_sample=samples/zigux/kretprobe_example.zig`
- `zig test zigux/tests/phase5_kretprobe_example_survey.zig`

Treat `zigux/tests/phase5_build.zig` as the returned shared rerun handle for the bytestream, kobject, and kretprobe packet members rather than as sample-local proof or as direct authenticated proof for the broader trace-events sample-local companion set.

## Next Step

The next bounded same-lane follow-through is to keep the new closure note parked unless one shared reminder surface drifts again. If the lane reopens soon, the smallest honest follow-through is to wire this closure note into one shared docs-root reminder surface or one checker-backed packet note without widening into runtime families, extra-sample claims, or unrelated helper-lane work.

- `PHASE5_NEXT_SAFE_STEP=keep the closure note parked unless a shared reminder surface drifts; if same-lane follow-through reopens, wire the closure note into one shared docs-root reminder surface or one checker-backed packet note without widening into runtime families or extra-sample claims`
