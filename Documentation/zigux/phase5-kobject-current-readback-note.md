# Phase 5 Kobject Current Readback Note

This note records the bounded 2026-05-21 readback state for the roadmap-backed `samples/kobject/kobject-example.c` anchor.

## Purpose

Use this note when a same-lane Phase 5 change needs one current evidence anchor for the `kobject` packet before touching broader shared reminder surfaces.

Keep the lane narrow:

- stay inside the approved non-runtime `kobject` sample family
- record what this run could prove directly versus through public current-`master` fallback
- avoid widening into sysfs, `kernel_kobj`, uevents, or module-registration claims

## Current bounded packet on 2026-05-21

Fresh repo-first inspection in this run kept the roadmap-backed kobject packet visible, but the authenticated contents route was narrower than the newer shared reminder wording implied.

Authenticated contents readback in this run directly returned:

- `samples/zigux/kobject_example.zig`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_build.zig`

Fresh sample-root reread in the same run also directly returned `samples/zigux/kobject_example_attr_group_contract.zig` as the bounded attr-group companion for the same anchor.

The same run still confirmed these current `master` packet members through public GitHub file readback:

- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `zigux/tests/phase5_kobject_example_manifest.json`
- `zigux/tests/phase5_kobject_example_survey.zig`

That means the strongest honest current packet for this run is:

- the direct sample-root file, focused tests-root replay, shared build route, and attr-group companion are readable through the authenticated contents route used here
- the dedicated survey note, manifest-backed contract, and survey replay remain visible on public current `master` even though this run's authenticated contents route returned `404` for those three packet members
- same-lane reminder work should treat those authenticated-contents `404` results as current connector-local readback flakiness, not as proof that the broader kobject packet vanished from the repo

## Sample-backed cues this run kept explicit

This run still confirmed the current kobject packet is the bounded Phase 5 in-memory ownership-and-lifetime sample, not a runtime substrate claim.

Keep these sample-backed cues explicit when the lane reopens:

- `samples/zigux/kobject_example.zig` remains tied to the roadmap anchor `samples/kobject/kobject-example.c`
- `zigux/tests/phase5_kobject_example.zig` keeps the focused replay packet explicit around descriptor, registration, shared `baz` and `bar` dispatch, lifecycle boundaries, and teardown posture
- `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, and `zigux/tests/phase5_kobject_example_survey.zig` remain the packet-local survey-note, manifest-backed, and survey-replay companions even when this run had to prove those three through public current-`master` fallback instead of authenticated contents readback
- `samples/zigux/kobject_example_attr_group_contract.zig` remains the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract, the shared `0664` mode cue, the unnamed-group marker, and the NULL-terminated attribute-list slot without turning that companion into a fifth Phase 5 sample
- `zigux/tests/phase5_build.zig` remains part of the same packet on the direct authenticated contents route
- non-goals stay unchanged: no sysfs file creation parity, no `kernel_kobj` integration, no uevents, and no loadable module registration claim

## Slot 425 Follow-Through

Fresh same-slot rereads kept the direct-versus-public split above stable instead of widening it.

The authenticated contents route still directly returned `zigux/tests/phase5_build.zig`, while separate same-slot direct reads still returned `404` for:

- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `zigux/tests/phase5_kobject_example_manifest.json`
- `zigux/tests/phase5_kobject_example_survey.zig`

The same slot then compared the broader shared Phase 5 reminder packet against this note and found that most shared reminder surfaces had already caught up to the narrower kobject split recorded here. `Documentation/zigux/README.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` now keep the direct sample-root file, focused tests-root replay, direct shared build-route companion, public-tree-backed survey note and manifest companions, and bounded attr-group companion aligned with this note.

The surviving same-lane follow-through targets are now narrower:

- `Documentation/zigux/review-checklist.md`, which still phrases `Documentation/zigux/phase5-kobject-sample-survey.md` and `zigux/tests/phase5_kobject_example_manifest.json` as current direct evidence in this runtime even though this note keeps them in the public-tree-backed companion bucket
- `scripts/zigux/check-phase5-review-guide-surface.py`, which still exact-requires that older review-checklist wording instead of the narrower direct-versus-public split recorded here

## Review posture

When a future same-lane repair touches shared Phase 5 reminder surfaces, use this note to keep the kobject packet truthful in one bounded step at a time.

Prefer follow-through in this order:

1. reread `Documentation/zigux/review-checklist.md` and `scripts/zigux/check-phase5-review-guide-surface.py` together first, because the broader docs-root, guide, sequencing, sample-root, scripts-root, and tests-root packet has already caught up and the remaining drift is now concentrated in that checklist-plus-guard pair
2. land one dedicated repair across that narrower pair only if a fresh reread still shows the checklist overstating `Documentation/zigux/phase5-kobject-sample-survey.md` or `zigux/tests/phase5_kobject_example_manifest.json` as direct authenticated evidence, or still leaves the shipped guard exact-requiring the older wording

Avoid widening from this note into sample behavior changes unless the sample, focused test, manifest, or survey replay actually changes.

## Next bounded step

Compare this note against `Documentation/zigux/review-checklist.md` and `scripts/zigux/check-phase5-review-guide-surface.py` first the next time the lane reopens.

If a fresh reread still leaves that checklist-plus-guard pair overstating the survey note or manifest-backed contract as direct authenticated proof, reopen the lane for that one bounded repair only. Leave the lane parked if those two surfaces catch up to the narrower split recorded here.
