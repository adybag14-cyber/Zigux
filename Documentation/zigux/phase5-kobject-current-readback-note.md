# Phase 5 Kobject Current Readback Note

This note records the bounded 2026-05-25 readback state for the roadmap-backed `samples/kobject/kobject-example.c` anchor.

## Purpose

Use this note when a same-lane Phase 5 change needs one current evidence anchor for the `kobject` packet before touching broader shared reminder surfaces.

Keep the lane narrow:

- stay inside the approved non-runtime `kobject` sample family
- record what this run could prove directly versus through public current-`master` fallback
- avoid widening into sysfs, `kernel_kobj`, uevents, or module-registration claims

## Current bounded packet on 2026-05-25

Fresh repo-first inspection in this run kept the roadmap-backed kobject packet visible, but the strongest honest split narrowed further than this note recorded on 2026-05-23.

Authenticated contents readback in this run directly returned:

- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `samples/zigux/kobject_example_attr_group_contract.zig`
- `zigux/tests/phase5_kobject_attr_group_contract.zig`
- `zigux/tests/phase5_kobject_attr_group_contract_survey.zig`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_build.zig`

Fresh public current-`master` GitHub file readback still kept these owner-plus-companion packet members visible:

- `samples/zigux/kobject_example.zig`
- `zigux/tests/phase5_kobject_example_manifest.json`
- `zigux/tests/phase5_kobject_example_survey.zig`

That means the strongest honest current packet for this run is:

- the dedicated survey note, bounded attr-group companion trio, focused tests-root replay, and shared build route are readable through the authenticated contents route used here
- the sample-root owner, manifest-backed contract, and survey replay remain visible on public current `master` even though this run's authenticated contents route still returned `404` for that owner-plus-companion set
- same-lane reminder work should treat those authenticated-contents `404` results as connector-local readback flakiness, not as proof that the broader kobject packet vanished from the repo

## Sample-backed cues this run kept explicit

This run still confirmed the current kobject packet is the bounded Phase 5 in-memory ownership-and-lifetime sample, not a runtime substrate claim.

Keep these sample-backed cues explicit when the lane reopens:

- `samples/zigux/kobject_example.zig` remains tied to the roadmap anchor `samples/kobject/kobject-example.c` even when the current authenticated contents route flakes on that owner path
- `samples/zigux/kobject_example_attr_group_contract.zig` remains the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract, the shared `0664` mode cue, the unnamed-group marker, and the NULL-terminated attribute-list slot without turning that companion into a fifth Phase 5 sample
- `zigux/tests/phase5_kobject_example.zig` keeps the focused replay packet explicit around descriptor, registration, shared `baz` and `bar` dispatch, lifecycle boundaries, and teardown posture
- `Documentation/zigux/phase5-kobject-sample-survey.md` remains the direct survey-note companion for the same packet, while `samples/zigux/kobject_example.zig`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain the current owner-plus-companion set even when this run had to prove them through public current-`master` fallback instead of authenticated contents readback
- `zigux/tests/phase5_build.zig` remains part of the same packet on the direct authenticated contents route
- non-goals stay unchanged: no sysfs file creation parity, no `kernel_kobj` integration, no uevents, and no loadable module registration claim

## Shared-surface follow-through

Fresh same-lane rereads showed that this narrower split is not yet described consistently across every wider shared reminder surface.

`Documentation/zigux/phase5-kobject-sample-survey.md` and `Documentation/zigux/phase5-sample-lane-sequencing.md` already keep the dedicated survey note, bounded attr-group companion trio, focused replay, shared build route, and public-tree-backed owner-plus-companion split explicit. `samples/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` should be reread against this note before any broader same-lane wording is tightened again.

That means the next honest follow-through stays parked until a fresh repo-first reread proves one specific shared reminder surface still drifting against this split on current `master`.

## Review posture

When a future same-lane repair touches the dedicated survey note or another shared Phase 5 reminder surface, use this note to keep the kobject packet truthful in one bounded step at a time.

Prefer follow-through in this order:

1. reread this note beside the exact Phase 5 surface that looks stale and confirm whether the dedicated survey note, bounded attr-group companion trio, focused tests-root replay, shared build-route companion, and public-tree-backed owner-plus-companion set are still described with the same split
2. land one dedicated reminder-surface repair only if a fresh reread actually reintroduces a mismatch against that split on current `master`

Avoid widening from this note into sample behavior changes unless the sample, focused test, manifest, or survey replay actually changes.

## Next bounded step

Leave the lane parked unless a fresh reread finds another same-lane reminder surface drifting from the mixed direct-versus-public-tree-backed split recorded here.

If the lane reopens now, start with `samples/zigux/README.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, and repair only one bounded surface if it stops matching the direct survey-note plus public-tree-backed owner-and-companion split above.
