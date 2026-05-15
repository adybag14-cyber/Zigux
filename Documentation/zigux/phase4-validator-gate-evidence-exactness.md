# Phase 4 Validator Gate-Evidence Exactness

This note records the dedicated validator-local exactness checker for the Phase 4 gate-evidence packet and the current reason it still sits outside the shared `phase4-validate` route.

## Status

- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_STATUS=dedicated_checker_landed_pending_validator_rewrite`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_CHECKER=scripts/zigux/check-phase4-validator-gate-evidence-exactness.py`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_VALIDATOR=scripts/zigux/validate-phase4.py`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_GATE_EVIDENCE_NOTE=Documentation/zigux/phase4-gate-evidence.md`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_EXPECTED_SELF_TEST_CASE_COUNT=33`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_EXPECTED_SHARED_TARGET_COUNT=19`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_EXPECTED_SHARED_SELF_TEST_CASE_COUNT=33`
- `PHASE4_VALIDATOR_GATE_EVIDENCE_EXACTNESS_SHARED_ROUTE_STATUS=not_yet_on_phase4_validate`

## Current Contract

The dedicated checker exists to fail closed when `scripts/zigux/validate-phase4.py` drifts away from the exact Phase 4 gate-evidence contract already pinned in `Documentation/zigux/phase4-gate-evidence.md`.

The exact contract today is:

- the validator must carry explicit exact-count constants for the gate-evidence self-test case count `33`, the shared validator target count `19`, and the shared validator self-test case count `33`
- the validator must keep the full shipped `PHASE4_GATE_EVIDENCE_SELF_TEST_CASES=` catalog explicit instead of treating it as a prefix-only marker
- the validator self-test fixture must keep the current exact gate-evidence lines rather than the older placeholder `21` and `16` values
- the validator-local exactness checker must keep the old prefix-only marker entries and the stale `21` / `16` placeholders forbidden

## Current Use

Run the checker directly when a Phase 4 review needs to confirm the exact validator-local contract:

```bash
python3 scripts/zigux/check-phase4-validator-gate-evidence-exactness.py --self-test
python3 scripts/zigux/check-phase4-validator-gate-evidence-exactness.py <repo-root>
```

This checker is intentionally not wired into `make -C zigux phase4-validate` yet. Current `master` still leaves the shared validator prefix-only for the exact gate-evidence case-count and shared-target markers, so wiring the checker into the shared route before the one-file validator rewrite lands would make the Phase 4 route fail for a known unfinished reason rather than for a newly introduced regression.

## Next Bounded Step

The next same-lane follow-through is still the validator-local one-file rewrite:

1. harden `scripts/zigux/validate-phase4.py` so it exact-checks the current `33` / `19` gate-evidence contract and the full shipped self-test catalog
2. rerun `python3 scripts/zigux/validate-phase4.py --self-test`
3. rerun `python3 scripts/zigux/check-phase4-validator-gate-evidence-exactness.py`
4. only then consider wiring the dedicated checker into `make -C zigux phase4-validate`
