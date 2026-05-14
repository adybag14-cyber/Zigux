# Phase 2 fixdep next step note

Lane: `P2-Y02`

Current `master` still carries one bounded fixdep-local truthfulness drift even though the direct fixture packet and the shared reminder notes already describe the live twelve-case surface.

## Current repo evidence

- `Documentation/zigux/artifact-diff.md` and `zigux/tests/fixtures/fixdep/cases.json` both describe the live twelve-case packet, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_output_write`, `sample_comment_only_stdout_full`, and `sample_missing_dep_stdout_full`.
- `Documentation/zigux/phase2-closure.md` repeats that same twelve-case fixdep packet and treats the shared note surface as already aligned.
- `scripts/zigux/check-phase2-fixdep-gate.py` still keeps older artifact-diff wording inside `ARTIFACT_DIFF_MARKERS`, where the marker for `Documentation/zigux/artifact-diff.md` still says `cases.json` keeps the current eleven-case fixdep packet reviewable even though the live fixture packet is twelve cases.
- `scripts/zigux/fixdep.zig` already holds the helper-local replay coverage for embedded NUL truncation, plain escaped-newline dependency continuation, concatenated target entries, escaped colon and hash tokens, preserved stdout prefixes on failure, and output-write error mapping.

## Survey result

- The remaining drift is now smaller and tool-local: it is no longer a `fixdep.zig` parser or fixture gap, but a dedicated checker expectation that still undercounts the artifact-diff packet by one case.
- Because this lane is note-only in the current run, the honest output is to keep the next checker follow-through explicit instead of widening into parser code, shared Phase 2 route inventory, `genksyms`, or the kconfig bridge packet.

## Next safe step

1. Update only the `ARTIFACT_DIFF_MARKERS` entry in `scripts/zigux/check-phase2-fixdep-gate.py` so its `Documentation/zigux/artifact-diff.md` expectation names the same live twelve-case packet already described by the artifact-diff note, the closure note, and `zigux/tests/fixtures/fixdep/cases.json`.
2. When a writable checkout with Zig is available, re-run `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig` so the checker wording and the direct replay packet are aligned again.

## Boundary

Stay inside the `fixdep` lane only. Do not reopen `scripts/zigux/fixdep.zig`, shared Phase 2 route inventory, `genksyms`, or the kconfig bridge packet unless a new fixdep-local drift appears beyond this checker wording mismatch.
