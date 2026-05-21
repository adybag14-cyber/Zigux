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
- `zigux/tests/phase5_build.zig`

Fresh sample-root reread in the same run also directly returned `samples/zigux/kobject_example_attr_group_contract.zig` as the bounded attr-group companion for the same anchor.

The same run still confirmed this current `master` packet member through public GitHub file readback:

- `zigux/tests/phase5_kobject_example_survey.zig`

That means the strongest honest current packet for this run is:

- the dedicated survey note, sample-root file, focused tests-root replay, manifest-backed contract, and shared build route are directly readable through the authenticated contents route used here
- the direct sample-root attr-group companion is readable too and should stay framed as bounded companion evidence for the same `kobject` anchor rather than as a fifth Phase 5 sample
- the survey replay remains visible on public current `master`
- same-lane reminder work should treat authenticated contents `404` results on that public-file member as current connector-local readback flakiness, not as proof that the broader kobject packet vanished from the repo

## Sample-backed cues this run kept explicit

This run still confirmed the current kobject packet is the bounded Phase 5 in-memory ownership-and-lifetime sample, not a runtime substrate claim.

Keep these sample-backed cues explicit when the lane reopens:

- `samples/zigux/kobject_example.zig` remains tied to the roadmap anchor `samples/kobject/kobject-example.c`
- `zigux/tests/phase5_kobject_example.zig` keeps the focused replay packet explicit around descriptor, registration, shared `baz` and `bar` dispatch, lifecycle boundaries, and teardown posture
- `zigux/tests/phase5_kobject_example_manifest.json` remains the manifest-backed contract for the same bounded packet
- `samples/zigux/kobject_example_attr_group_contract.zig` remains the direct sample-root companion for the bounded `foo`/`baz`/`bar` attribute-group contract, the shared `0664` mode cue, the unnamed-group marker, and the NULL-terminated attribute-list slot without turning that companion into a fifth Phase 5 sample
- `zigux/tests/phase5_build.zig` remains part of the same packet on the direct authenticated contents route, and `zigux/tests/phase5_kobject_example_survey.zig` remains part of the same packet even when this run had to prove that survey replay through public current-`master` fallback instead of the authenticated contents route
- non-goals stay unchanged: no sysfs file creation parity, no `kernel_kobj` integration, no uevents, and no loadable module registration claim

## Review posture

When a future same-lane repair touches shared Phase 5 reminder surfaces, use this note to keep the kobject packet truthful in one bounded step at a time.

Prefer follow-through in this order:

1. one broader shared reminder-surface reread across `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase5-review-guide-surface.py`, because fresh repo-first comparison now shows the already-landed shared checklist and guard are ahead of the sample root: `Documentation/zigux/review-checklist.md` and `scripts/zigux/check-phase5-review-guide-surface.py` already keep the current kobject survey-note inventory explicit, while `samples/zigux/README.md` still frames `zigux/tests/phase5_build.zig` as public-tree-backed companion evidence beside `zigux/tests/phase5_kobject_example_survey.zig` even though the newer guide and sequencing surfaces now treat that shared build route as directly readable for the current packet
2. one dedicated sample-root reminder repair if that broader reread confirms the same mismatch, with `samples/zigux/README.md` as the first same-lane follow-through surface and `scripts/zigux/check-phase5-review-guide-surface.py` as the matching guard only if its `SAMPLE_ROOT_MARKERS[0]` still exact-requires the older sample-root sentence before reopening survey-note, survey-replay, or build-route wording elsewhere

Avoid widening from this note into sample behavior changes unless the sample, focused test, manifest, or survey replay actually changes.

## Next bounded step

Compare this note against `Documentation/zigux/phase5-sample-review-guide.md`, `Documentation/zigux/phase5-sample-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `samples/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `scripts/zigux/check-phase5-review-guide-surface.py` the next time the lane reopens.

This run found the earlier checklist-and-checker follow-through note stale: `Documentation/zigux/review-checklist.md` and `scripts/zigux/check-phase5-review-guide-surface.py` already keep the current kobject survey-note inventory and shared guard explicit. The smaller surviving drift is now inside `samples/zigux/README.md`, which still frames `zigux/tests/phase5_build.zig` as public-tree-backed companion evidence for the current kobject split even though the newer guide and sequencing surfaces now treat that shared build route as directly readable for the same packet. Reopen the lane only for that one sample-root reminder repair, its matching guard marker if needed, or another equally small same-lane reminder drift that fresh repo-first comparison proves after that reread.
