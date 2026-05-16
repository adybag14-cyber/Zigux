# Phase 2 fixdep next step note

Lane: `P2-Y02`

Current `master` still carries a coherent fixdep-local dual-implementation packet, and the broader workflow-backed fixdep coverage is aligned again.

## Current repo evidence

- `Documentation/zigux/artifact-diff.md` and `Documentation/zigux/phase2-closure.md` both describe the live twelve-case fixdep packet and keep the dedicated fixdep gate, diff, and direct replay entrypoints explicit.
- `scripts/zigux/check-phase2-fixdep-gate.py` validates the live twelve-case packet, including `sample_dependency_continuation`, `sample_comment_continuation`, `sample_output_write`, `sample_comment_only_stdout_full`, and `sample_missing_dep_stdout_full`.
- `zigux/tests/fixtures/fixdep/cases.json` names that same twelve-case packet and uses `stdout_mode: "dev_full"` on the three bounded `/dev/full` write-failure replays.
- The direct fixdep artifact packet now carries the additional plain escaped-newline dependency continuation case through `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, and `zigux/tests/fixtures/fixdep/cases.json`, while the broader shared reminder surfaces can be retold separately if they need to mention the new case count.
- `scripts/zigux/fixdep.zig` already holds the helper-local replay coverage for embedded NUL truncation, plain escaped-newline dependency continuation, concatenated target entries, escaped colon and hash tokens, preserved stdout prefixes on failure, and output-write error mapping.
- `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile` now all keep the dedicated `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig` packet explicit.

## Survey result

- The dedicated fixdep-local packet remains substantive and aligned with the Phase 2 roadmap’s dual-implementation goal.
- The earlier workflow-local gap is now closed, so this packet no longer needs a workflow-restore follow-through before it can stay parked again.
- Treat this survey lane as parked again unless a fresh fixdep-local or directly coupled workflow drift appears.

## Next safe step

1. Keep this lane parked unless current `master` shows a new fixdep-local or shared reminder-surface truthfulness drift in `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `zigux/tests/fixtures/fixdep/cases.json`, `Documentation/zigux/artifact-diff.md`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-fixdep-next-step-note.md`, `.github/workflows/zigux-bootstrap.yml`, or `scripts/zigux/README.md`.
2. When a writable checkout with Zig is available, re-run `python3 scripts/zigux/check-phase2-fixdep-gate.py --self-test`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py --self-test`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig` so the dedicated gate and the direct replay stay aligned as one packet.
3. If the lane reopens first, start by checking whether `scripts/zigux/check-phase2-fixdep-gate.py`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/phase2-closure.md`, and this note still describe the same dedicated workflow-backed fixdep packet before widening into any parser or fixture work.

## Boundary

Stay inside the `fixdep` lane only. Do not reopen `scripts/zigux/fixdep.zig`, shared Phase 2 route inventory, `genksyms`, or the kconfig bridge packet unless a new fixdep-local drift appears.
