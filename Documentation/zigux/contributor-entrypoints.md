# Contributor Entry Points

Use this note when a docs, checklist, or workflow change needs one current-master starting map instead of reconstructing the right reminder packet from scattered docs-root, scripts-root, and tests-root surfaces.

This note is a developer-enablement companion only. It does not close a tranche, create a new replay route, or promote repo-reality gaps into shipped evidence.

## Start Here

Reread these shared entry surfaces together before widening contributor-facing wording:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Keep those four files aligned as the baseline contributor packet:

- docs-root scope and packet truthfulness live in `Documentation/zigux/README.md`
- reviewer prompts and boundary rules live in `Documentation/zigux/review-checklist.md`
- shipped checker and validator entrypoints live in `scripts/zigux/README.md`
- tests-root replay and fixture reminders live in `zigux/tests/README.md`

## Pick The Right Guide

After the shared entry reread, choose one bounded guide instead of widening across multiple lanes.

### Top-Level Contributor Onboarding

Use this path when the change is about the main contributor starting map, the start-here file list, or the routine workflow wording that new contributors see first.

Stable onboarding packet:

- `CONTRIBUTING.md`
- `Documentation/zigux/contributor-entrypoints.md`
- `Documentation/zigux/contributor-workflow.md`

Matching guard:

- `python3 scripts/zigux/check-contributor-onboarding-packet.py`

Keep this packet scoped to contributor-facing onboarding only. Do not widen it into phase-local status claims or helper-local proof.

### Developer Enablement Reminder Work

Use `Documentation/zigux/developer-enablement-contributor-workflow.md` when the change stays inside docs-only reminder work, checklist maintenance, or contributor workflow guidance and does not reopen implementation lanes.

Supporting companions:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

Keep this path scoped to reminder-surface maintenance: reread the owning packet first, update only the smallest understated shared surface, and leave absent routes, files, or wrappers framed as repo-reality gaps instead of shipped evidence.

### Samples And Reference Patterns

Use `Documentation/zigux/phase5-sample-review-guide.md` when the change touches sample-facing contributor guidance, approved Phase 5 idioms, or review wording around the bytestream, kobject, kretprobe, or bounded trace-events packet.

Supporting companions:

- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `samples/zigux/README.md`
- `Documentation/zigux/phase5-kfifo-sample-survey.md`
- `Documentation/zigux/phase5-kretprobe-sample-survey.md`
- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `Documentation/zigux/phase5-trace-events-sample-survey.md`

Keep the current Phase 5 sample split explicit while you use that guide:

- `samples/zigux/bytestream_fifo.zig` and `samples/zigux/kretprobe_example.zig` are direct non-runtime sample proof in the current shared packet
- `samples/zigux/kobject_example.zig` stays the sample-root owner path through the shared reminder packet, while `zigux/tests/phase5_kobject_example_manifest.json` and `zigux/tests/phase5_kobject_example_survey.zig` can still depend on public-tree-backed companion readback in this runtime
- `samples/zigux/trace_events_string_formatting_sample.zig` and `samples/zigux/trace_events_callback_focus_contract.zig` are the direct bounded trace-events companions, while `samples/zigux/runtime_*.zig` remains Phase 9 evidence rather than extra Phase 5 proof

Matching guard:

- `python3 scripts/zigux/check-phase5-review-guide-surface.py --self-test`

### Shared Helper Contributor Packet

Use `Documentation/zigux/phase13-contributor-workflow-guide.md` when the change touches the active shared-helper contributor packet for `libfs`, `devres`, `landlock/ruleset`, or `landlock/syscalls`.

Supporting companions:

- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`

Matching guards:

- `python3 scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `python3 scripts/zigux/check-phase13-tests-readme-alignment.py`

### Active Shared Packet Sync

Use `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md` when a change needs one compact cross-phase owner map for the still-active Phase 10, Phase 11, and Phase 13 contributor surfaces.

Keep this note as a sync companion only. It is not closure proof for any of those phases.

### Release Closure And PMO Checklist Work

Use `Documentation/zigux/phase12-release-closure-checklist.md` when the change is really release-readiness, closure-state, or PMO reminder work rather than a broad contributor guide refresh.

Matching support bundle:

- `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
- `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
- `python3 scripts/zigux/validate-phase12.py`

## Minimal Edit Loop

When the change stays inside the developer-enablement lane, use this bounded loop:

1. reread the four shared entry surfaces together
2. reread one phase-local guide or `Documentation/zigux/developer-enablement-contributor-workflow.md` that matches the actual change
3. if the change touches top-level onboarding wording, keep `CONTRIBUTING.md`, `Documentation/zigux/contributor-entrypoints.md`, and `Documentation/zigux/contributor-workflow.md` aligned and rerun `python3 scripts/zigux/check-contributor-onboarding-packet.py`
4. update one shared reminder surface plus the smallest necessary companion note
5. rerun the smallest checker set that matches the packet you touched
6. keep absent routes, helpers, and replay files recorded as repo-reality gaps instead of promoting them into shipped evidence

## Current Route Truths

Keep these current-master route boundaries explicit while refreshing contributor guidance:

- `zigux/Makefile` is present, but Phase 13 still does not expose `make -C zigux phase13-validate` or `make -C zigux phase13`
- Phase 12 does expose `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`
- Phase 5 stays non-runtime; do not use sample guidance to imply runtime-loader, module-registration, procfs, sysfs, workqueue, or ring-buffer delivery claims
- cross-phase sync notes are contributor-surface companions, not substitutes for helper-local owner maps or validator results

## Non-Goals

This note does not:

- replace `Documentation/zigux/review-checklist.md`
- replace phase-local owner maps or closure checklists
- create a new build, smoke, or validation route
- treat public-tree fallback, historical wording, or missing files as direct current-master proof