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

The same slot then compared the broader shared Phase 5 reminder packet against this note and found that these current shared surfaces still overstate the kobject packet in at least one of two ways: they either treat the survey note and manifest-backed contract as returned direct authenticated proof in this runtime, or they demote `zigux/tests/phase5_build.zig` back into public-tree-backed companion wording even though the authenticated contents route still returns that shared build file directly here.

Those surviving shared-surface follow-through targets are:

- `Documentation/zigux/README.md`
- `Documentation/zigux/phase5-sample-review-guide.md`
- `Documentation/zigux/phase5-sample-lane-sequencing.md`
- `Documentation/zigux/review-checklist.md`
- `samples/zigux/README.md`
- `scripts/zigux/README.md`

The same slot also confirmed that `zigux/tests/README.md` already keeps the narrower kobject split closer to the live readback packet, so the next same-lane repair can stay outside the tests-root reminder unless a fresh reread reopens that surface too.

## Review posture

When a future same-lane repair touches shared Phase 5 reminder surfaces, use this note to keep the kobject packet truthful in one bounded step at a time.

Prefer follow-through in this order:

1. one broader shared reminder-surface reread across `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase5-review-guide-surface.py`, because fresh repo-first comparison in this run showed that some shared surfaces still speak about the kobject packet as if the survey note, manifest, or survey replay are direct authenticated proof in this runtime
2. one dedicated shared reminder repair if that broader reread confirms the same mismatch, with whichever single shared surface still overstates `Documentation/zigux/phase5-kobject-sample-survey.md`, `zigux/tests/phase5_kobject_example_manifest.json`, or `zigux/tests/phase5_kobject_example_survey.zig` as direct authenticated evidence chosen as the next bounded follow-through

Avoid widening from this note into sample behavior changes unless the sample, focused test, manifest, or survey replay actually changes.

## Next bounded step

Compare this note against `Documentation/zigux/README.md`, `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase5-review-guide-surface.py` the next time the lane reopens.

If a fresh reread still leaves one shared reminder surface overstating the survey note, manifest, or survey replay as direct authenticated proof, or still leaves `zigux/tests/phase5_build.zig` mislabeled as companion-only evidence, reopen the lane for that one-file truthfulness repair only. Leave the lane parked if the shared packet has already caught up to this narrower direct-versus-public split.
