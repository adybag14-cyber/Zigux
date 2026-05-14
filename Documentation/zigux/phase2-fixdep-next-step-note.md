# Phase 2 fixdep next step note

Lane: `P2-Y02`

Current `master` now carries one more direct `fixdep` artifact case without reopening parser code.

## Current repo evidence

- `scripts/zigux/check-phase2-fixdep-gate.py` validates the live twelve-case packet, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_output_write`, `sample_comment_only_stdout_full`, and `sample_missing_dep_stdout_full`.
- `zigux/tests/fixtures/fixdep/cases.json` names that same twelve-case packet and uses `stdout_mode: "dev_full"` on the three bounded `/dev/full` write-failure replays.
- `scripts/zigux/fixdep.zig` already holds the helper-local replay coverage for embedded NUL truncation, plain escaped-newline dependency continuation, concatenated target entries, escaped colon and hash tokens, preserved stdout prefixes on failure, and output-write error mapping.

## Survey result

- The direct fixdep artifact packet now carries the additional plain escaped-newline dependency continuation case through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `zigux/tests/fixtures/fixdep/cases.json`, while the broader shared reminder surfaces can be retold separately if they need to mention the new case count.
- The honest remaining work for this file family is smaller: keep the direct gate, diff checker, and fixture packet truthful when one of those surfaces changes, and only widen into the shared reminder docs if they need to call out the new case count explicitly.

## Next safe step

1. Keep this lane parked unless current `master` shows a new fixdep-local truthfulness drift in `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, or `zigux/tests/fixtures/fixdep/cases.json`.
2. When a writable checkout with Zig is available, re-run `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig` so the dedicated gate and the direct replay stay aligned as one packet.

## Boundary

Stay inside the `fixdep` lane only. Do not reopen parser behavior in `scripts/zigux/fixdep.zig`, shared Phase 2 route inventory, `genksyms`, or the kconfig bridge packet unless a new fixdep-local drift appears.
