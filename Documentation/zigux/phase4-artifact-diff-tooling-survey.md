# Phase 4 Artifact-Diff Tooling Survey

## Status
- `PHASE4_ARTIFACT_DIFF_TOOLING_STATUS=roadmap_gap_closed_on_current_master`
- scope: record whether the roadmap-backed Phase 4 host-side artifact-diff tooling packet still lacks a deterministic checker or whether the current `scripts/zigux/` surface already closes that gap
- current repo reality:
  - `scripts/zigux/artifact_diff.py`
  - `scripts/zigux/check-artifact-diff-contract.py`
  - `scripts/zigux/check-phase4-artifact-diff-determinism.py`
  - `scripts/zigux/validate-phase4.py`
  - `Documentation/zigux/artifact-diff.md`
  - `Documentation/zigux/phase4-validation-matrix.md`
  - `zigux/Makefile`
  - `.github/workflows/zigux-bootstrap.yml`

## Roadmap Comparison

Phase 4 in `ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md` calls for artifact-diff checks for host-side tools and points the work toward `scripts/zigux/` diff and layout tooling.

Current `master` already closes the deterministic-check slice of that requirement:
- `scripts/zigux/artifact_diff.py` ships the bounded text, JSON, and SHA-256 comparison helper plus a deterministic `--self-test` packet.
- `scripts/zigux/check-artifact-diff-contract.py` replays the helper's outward CLI contract, including missing-argument, invalid-mode, missing-path, malformed-JSON, and repeat-run cases.
- `scripts/zigux/check-phase4-artifact-diff-determinism.py` separately rechecks the helper self-test catalog, the contract self-test catalog, the base-case catalog, the repeat-case catalog, and the full contract catalog so case-count or case-order drift fails closed.
- `scripts/zigux/validate-phase4.py` already treats both artifact-diff checkers as part of the shared Phase 4 validator-first route before the Zig rollback gates run.
- `zigux/Makefile` and `.github/workflows/zigux-bootstrap.yml` already expose the same validator-first replay surface through `make -C zigux phase4-validate` and the bootstrap workflow.

## Current Conclusion

The live Phase 4 artifact-diff tooling gap is not a missing deterministic checker anymore. The remaining work in this lane should stay limited to truthfulness and reminder-surface drift around the existing checker packet unless the helper contract or validator-first route changes again.

## Direct Replay Surface
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py --self-test`
- `python3 scripts/zigux/check-phase4-artifact-diff-determinism.py`
- `python3 scripts/zigux/check-artifact-diff-contract.py`
- `python3 scripts/zigux/validate-phase4.py`
- `make -C zigux phase4-validate`

## Boundary
- this survey closes only the roadmap-backed deterministic tooling question for the shared host-side artifact-diff packet
- this survey does not claim that the parked `samples/zigux/kprobe_example.zig` or `samples/zigux/test_fsmount.zig` starter gaps are closed
- this survey does not promote the dedicated local-only perf-baseline packet into shared CI perf coverage
- reopen this lane only for helper-contract drift, catalog drift, validator-route drift, or reminder-surface drift tied directly to the existing artifact-diff checker packet
