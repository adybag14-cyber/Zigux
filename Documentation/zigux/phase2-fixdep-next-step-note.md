# Phase 2 fixdep next step note

Lane: `P2-Y02`

Current `master` no longer carries the earlier fixdep-local truthfulness drift: the dedicated checker, direct fixture packet, and shared reminder notes now all describe the same live twelve-case surface.

## Current repo evidence

- `Documentation/zigux/artifact-diff.md` and `zigux/tests/fixtures/fixdep/cases.json` both describe the live twelve-case packet, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_output_write`, `sample_comment_only_stdout_full`, and `sample_missing_dep_stdout_full`.
- `Documentation/zigux/phase2-closure.md` repeats that same twelve-case fixdep packet and treats the shared note surface as aligned.
- `scripts/zigux/check-phase2-fixdep-gate.py` now matches that same twelve-case wording in both `PHASE2_FIXDEP_NEXT_STEP_MARKERS` and `ARTIFACT_DIFF_MARKERS`, so the dedicated checker no longer undercounts the live artifact-diff packet.
- `scripts/zigux/fixdep.zig` already holds the helper-local replay coverage for embedded NUL truncation, plain escaped-newline dependency continuation, concatenated target entries, escaped colon and hash tokens, preserved stdout prefixes on failure, and output-write error mapping.

## Survey result

- The earlier checker-only undercount is now closed, so there is no remaining fixdep-local truthfulness gap to land from this note.
- The honest next work for this file family is parked until a fresh reread finds a new drift inside the direct checker, diff checker, fixture packet, or directly coupled reminder notes.

## Next safe step

1. Keep this lane parked unless current `master` shows a new fixdep-local truthfulness drift in `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `zigux/tests/fixtures/fixdep/cases.json`, `Documentation/zigux/artifact-diff.md`, or `Documentation/zigux/phase2-closure.md`.
2. When a writable checkout with Zig is available, re-run `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig` so the dedicated gate and the direct replay stay aligned as one packet.

## Boundary

Stay inside the `fixdep` lane only. Do not reopen `scripts/zigux/fixdep.zig`, shared Phase 2 route inventory, `genksyms`, or the kconfig bridge packet unless a new fixdep-local drift appears.
