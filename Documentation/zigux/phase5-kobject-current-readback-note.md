# Phase 5 Kobject Current Readback Note

This note records the bounded 2026-05-21 readback state for the roadmap-backed `samples/kobject/kobject-example.c` anchor.

## Purpose

Use this note when a same-lane Phase 5 change needs one current evidence anchor for the `kobject` packet before touching broader shared reminder surfaces.

Keep the lane narrow:

- stay inside the approved non-runtime `kobject` sample family
- record what this run could prove directly versus through public current-`master` fallback
- avoid widening into sysfs, `kernel_kobj`, uevents, or module-registration claims

## Current bounded packet on 2026-05-21

Fresh repo-first inspection in this run kept the roadmap-backed kobject packet visible, and the direct authenticated contents route was broader than the narrower 2026-05-20 readback note.

Authenticated contents readback in this run directly returned:

- `Documentation/zigux/phase5-kobject-sample-survey.md`
- `samples/zigux/kobject_example.zig`
- `zigux/tests/phase5_kobject_example.zig`
- `zigux/tests/phase5_kobject_example_manifest.json`

Fresh sample-root reread in the same run also directly returned `samples/zigux/kobject_example_attr_group_contract.zig` as the bounded attr-group companion for the same anchor.

The same run also confirmed these current `master` packet members through public GitHub file readback:

- `zigux/tests/phase5_kobject_example_survey.zig`
- `zigux/tests/phase5_build.zig`

That means the strongest honest current packet for this run is:

- the dedicated survey note, sample-root file, focused tests-root replay, and manifest-backed contract are directly readable through the authenticated contents route used here
- the direct sample-root attr-group companion is readable too and should stay framed as bounded companion evidence for the same `kobject` anchor rather than as a fifth Phase 5 sample
- the survey replay and shared build route remain visible on public current `master`
- same-lane reminder work should treat authenticated contents `404` results on those two public-file members as current connector-local readback flakiness, not as proof that the broader kobject packet vanished from the repo

## Sample-backed cues this run kept explicit

This run still confirmed the current kobject packet is the bounded Phase 5 in-memory ownership-and-lifetime sample, not a runtime substrate claim.

Keep these sample-backed cues explicit when the lane reopens:

- `samples/zigux/kobject_example.zig` remains tied to the roadmap anchor `samples/kobject/kobject-example.c`
- `zigux/tests/phase5_kobject_example.zig` keeps the focused replay packet explicit around descriptor, registration, shared `baz` and `bar` dispatch, lifecycle boundaries, and teardown posture
- `zigux/tests/phase5_kobject_example_manifest.json` remains the manifest-backed contract for the same bounded packet
- `samples/zigux/kobject_example_attr_group_contract.zig` remains the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract, the shared `0664` mode cue, the unnamed-group marker, and the NULL-terminated attribute-list slot without turning that companion into a fifth Phase 5 sample
- `zigux/tests/phase5_kobject_example_survey.zig` and `zigux/tests/phase5_build.zig` remain part of the same packet even when this run had to prove them through public current-`master` fallback instead of the authenticated contents route
- non-goals stay unchanged: no sysfs file creation parity, no `kernel_kobj` integration, no uevents, and no loadable module registration claim

## Review posture

When a future same-lane repair touches shared Phase 5 reminder surfaces, use this note to keep the kobject packet truthful in one bounded step at a time.

Prefer follow-through in this order:

1. one shared reminder-surface reread across `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, because fresh repo-first comparison in this run found the shared checklist already carrying the mixed direct-versus-public-tree-backed kobject packet correctly
2. one dedicated kobject survey-note truthfulness repair if that broader shared reread exposes a surviving mismatch
3. one kobject survey or build-route wording repair tied to the existing packet

Avoid widening from this note into sample behavior changes unless the sample, focused test, manifest, or survey replay actually changes.

## Next bounded step

Compare this note against `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` the next time the lane reopens.

This run no longer found `Documentation/zigux/review-checklist.md` compressing which kobject packet members were directly readable in the 2026-05-21 packet. Reopen the lane only if that shared reread finds another one-file reminder drift inside the same mixed direct-plus-public-tree-backed packet; otherwise leave the Phase 5 kobject packet parked.
