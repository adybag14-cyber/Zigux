# Phase 2 fixdep next step note

Lane: `P2-Y02`

Current `master` no longer carries the earlier fixdep-local truthfulness drift across the dedicated checker, direct fixture packet, artifact-diff note, and closure note, but one broader shared reminder surface still stays more general than the fixdep-local packet: `scripts/zigux/README.md` lists the fixdep checker and replay entrypoints without restating the same live twelve-case fixture surface.

## Current repo evidence

- `Documentation/zigux/artifact-diff.md` and `zigux/tests/fixtures/fixdep/cases.json` both describe the live twelve-case packet, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_output_write`, `sample_comment_only_stdout_full`, and `sample_missing_dep_stdout_full`.
- `Documentation/zigux/phase2-closure.md` repeats that same twelve-case fixdep packet and treats the shared note surface as aligned.
- `scripts/zigux/check-phase2-fixdep-gate.py` now matches that same twelve-case wording in both `PHASE2_FIXDEP_NEXT_STEP_MARKERS` and `ARTIFACT_DIFF_MARKERS`, so the dedicated checker no longer undercounts the live artifact-diff packet.
- `scripts/zigux/fixdep.zig` already holds the helper-local replay coverage for embedded NUL truncation, plain escaped-newline dependency continuation, concatenated target entries, escaped colon and hash tokens, preserved stdout prefixes on failure, and output-write error mapping.
- `scripts/zigux/README.md` now names the live fixdep checker and direct replay entrypoints as part of the shared Phase 2 helper inventory, but it still summarizes that slice at the checker-and-route level instead of restating the dedicated twelve-case packet described by the fixdep-local notes.

## Survey result

- The earlier checker-only undercount is now closed inside the dedicated fixdep-local packet, so there is no remaining fixdep-local truthfulness gap to land from this note.
- The only fresh drift visible on current `master` sits in the broader shared scripts index: `scripts/zigux/README.md` still reads as a shared helper inventory instead of repeating the dedicated twelve-case fixdep packet.
- Treat that scripts-root reminder gap as shared closure-evidence maintenance only; it does not justify reopening `scripts/zigux/fixdep.zig`, the fixture packet, or the dedicated fixdep checker family from this note.

## Next safe step

1. Keep this lane parked unless current `master` shows a new fixdep-local truthfulness drift in `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `zigux/tests/fixtures/fixdep/cases.json`, `Documentation/zigux/artifact-diff.md`, or `Documentation/zigux/phase2-closure.md`, or the broader shared scripts index is explicitly reopened for a reminder-surface pass.
2. When a writable checkout with Zig is available, re-run `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig` so the dedicated gate and the direct replay stay aligned as one packet.

## Boundary

Stay inside the `fixdep` lane only. Do not reopen `scripts/zigux/fixdep.zig`, shared Phase 2 route inventory, `genksyms`, or the kconfig bridge packet unless a new fixdep-local drift appears. If the shared scripts index is later reopened, keep that follow-up reminder-only and avoid reopening parser or fixture work.