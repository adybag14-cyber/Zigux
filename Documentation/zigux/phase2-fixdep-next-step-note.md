# Phase 2 fixdep next step note

Lane: `P2-Y02`

Current `master` still carries a coherent fixdep-local dual-implementation packet, but it no longer supports the broader claim that workflow-backed fixdep coverage is already aligned.

## Current repo evidence

- `Documentation/zigux/artifact-diff.md` and `zigux/tests/fixtures/fixdep/cases.json` both describe the live twelve-case packet, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_output_write`, `sample_comment_only_stdout_full`, and `sample_missing_dep_stdout_full`.
- `Documentation/zigux/phase2-closure.md` repeats that same twelve-case fixdep packet and keeps the dedicated fixdep gate, diff, and direct replay entrypoints explicit.
- `scripts/zigux/check-phase2-fixdep-gate.py` now matches that same twelve-case wording in both `PHASE2_FIXDEP_NEXT_STEP_MARKERS` and `ARTIFACT_DIFF_MARKERS`, so the dedicated checker no longer undercounts the live artifact-diff packet.
- `scripts/zigux/fixdep.zig` already holds the helper-local replay coverage for embedded NUL truncation, plain escaped-newline dependency continuation, concatenated target entries, escaped colon and hash tokens, preserved stdout prefixes on failure, and output-write error mapping.
- `scripts/zigux/README.md` still names the live fixdep checker and direct replay entrypoints as part of the shared Phase 2 helper inventory, but `.github/workflows/zigux-bootstrap.yml` still does not run `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, or `zig test scripts/zigux/fixdep.zig` as dedicated workflow steps.

## Survey result

- The dedicated fixdep-local packet remains substantive and aligned with the Phase 2 roadmap’s dual-implementation goal.
- The remaining repo gap is workflow-local rather than parser-local, fixture-local, or dedicated-note-local.
- Treat this survey lane as parked again after recording that workflow mismatch instead of widening into workflow edits from this note.

## Next safe step

1. Keep this lane parked unless current `master` shows a new fixdep-local or shared reminder-surface truthfulness drift in `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `zigux/tests/fixtures/fixdep/cases.json`, `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase2-closure.md`, or `scripts/zigux/README.md`.
2. When a writable checkout with Zig is available, re-run `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig` so the dedicated gate and the direct replay stay aligned as one packet.
3. The current next honest follow-up remains neighboring lane `P2-L05`: restore the missing workflow-local fixdep gate packet in `.github/workflows/zigux-bootstrap.yml`, then rerun the dedicated fixdep gate checker and direct `zig test` replay on a trustworthy checkout.

## Boundary

Stay inside the `fixdep` lane only. Do not reopen `scripts/zigux/fixdep.zig`, shared Phase 2 route inventory, `genksyms`, or the kconfig bridge packet unless a new fixdep-local drift appears.
