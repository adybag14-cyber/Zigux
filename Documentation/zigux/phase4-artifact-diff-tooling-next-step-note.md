# Phase 4 Artifact-Diff Tooling Next Step Note

## Status
- `PHASE4_ARTIFACT_DIFF_TOOLING_NEXT_STEP_STATUS=docs_root_reminder_follow_through_pending`
- scope: record the smallest honest same-lane follow-through for the shipped Phase 4 artifact-diff tooling packet
- current repo reality:
  - `scripts/zigux/artifact_diff.py`
  - `scripts/zigux/check-artifact-diff-contract.py`
  - `scripts/zigux/check-phase4-artifact-diff-determinism.py`
  - `scripts/zigux/validate-phase4.py`
  - `Documentation/zigux/artifact-diff.md`
  - `Documentation/zigux/phase4-artifact-diff-tooling-survey.md`
  - `Documentation/zigux/README.md`

## Current Readback

Current `master` already closes the Phase 4 artifact-diff tooling slice through the shipped helper, the outward contract checker, the determinism checker, and the validator-first route recorded in `Documentation/zigux/artifact-diff.md` and `Documentation/zigux/phase4-artifact-diff-tooling-survey.md`.

The smallest open same-lane gap is now reminder-surface truthfulness in `Documentation/zigux/README.md` only. The docs-root Phase 4 note still names the shared validator, the atomic64 wrapper handoff, the bitmap rollback gate, and the shared `phase4_build.zig` entrypoint, but it does not yet restate the broader tooling packet that `scripts/zigux/check-phase4-artifact-diff-determinism.py` already treats as fail-closed docs-root evidence: the shared artifact-diff contract checker, the deterministic catalog checker, the workflow-route-count checker, the exact-readback gate, and the Linux-style `make -C zigux phase4-validate`, `make -C zigux phase4-runtime-atomic64-diff-survey`, `make -C zigux phase4-bitmap-diff-survey`, `make -C zigux phase4-bitmap-diff`, `make -C zigux phase4-bitmap-live-helper-replay`, and `make -C zigux phase4` routes.

## Exact Next Safe Step
- update `Documentation/zigux/README.md` only
- add one docs-root reminder line that mirrors the current tooling packet already required by `scripts/zigux/check-phase4-artifact-diff-determinism.py`
- keep the follow-through scoped to the shipped artifact-diff helper, its checker packet, and the validator-first replay route
- do not widen into `zigux/tests/atomic64_diff.zig` behavior, the local-only perf-baseline packet, the shared remaining-gap matrix packet, or the parked `kprobe_example` and `test_fsmount` starter-gap surveys

## Direct Replay Surface
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
- `python3 scripts/zigux/check-artifact-diff-contract.py --self-test`
- `python3 scripts/zigux/check-artifact-diff-contract.py`
- `python3 scripts/zigux/validate-phase4.py`
- `make -C zigux phase4-validate`

## Boundary
- this note records one tooling-only docs-root follow-through for the existing artifact-diff packet
- reopen this lane only if the docs-root reminder, tooling survey, artifact-diff closure note, or determinism checker drifts again inside the same packet
