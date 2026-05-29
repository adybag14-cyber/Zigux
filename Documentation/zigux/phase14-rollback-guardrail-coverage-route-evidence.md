# Phase 14 Rollback Guardrail Coverage Route Evidence

Lane: `P14-L17`
Phase: `Phase 14`
Owner: `Repo Tooling Pod`
Status bucket: `study_only`
Rollback owner: `Repo Tooling Pod`

This note records the current `master` rollback-threshold automation boundary after the dedicated rollback/guardrail coverage checker landed. It is evidence for the next validation-tightening step; it does not promote a broader Phase 14 delivery route, a `phase14-smoke` Makefile target, a `phase14-test` Makefile target, or an aggregate `phase14` route.

## Current Readback

- `scripts/zigux/check-phase14-rollback-guardrail-coverage.py`: blob `0188132746cb51b3bbfa39526af8f73915f21af6`
- `scripts/zigux/validate-phase14.py`: blob `c1f45e1b6029c5435c0bcc13b1e45dff9d86d246`
- `zigux/Makefile`: blob `b590ef1bb4a3ddd6a817734ee2241442e8935927`
- `.github/workflows/zigux-bootstrap.yml`: blob `5bdb136b8b6710c08c19566879d5a9da42b63445`

The returned shared gate remains `make -C zigux phase14-validate`. The workflow still runs that gate through `Run current Phase 14 validate route`, and the Makefile route still directly replays the shared smoke route checker, tests README checker, `validate-phase14.py`, rollback-threshold sequencing checker, skbuff stay-in-C guardrail, RCU rollback guardrail, and release-boundary exact-count checker.

The dedicated rollback/guardrail coverage checker is present and self-testable, but the current route evidence shows it is not yet a direct `phase14-validate` Makefile command and is not yet listed as a `validate-phase14.py` subchecker. That is the bounded validation gap this lane should close before claiming the coverage checker is gate-enforced.

## Acceptance Boundary

A future validation-tightening commit may claim this gap closed only when all of these are true on current `master`:

- `zigux/Makefile` runs `scripts/zigux/check-phase14-rollback-guardrail-coverage.py --self-test` from `phase14-validate`.
- `zigux/Makefile` runs `scripts/zigux/check-phase14-rollback-guardrail-coverage.py` from `phase14-validate`.
- `scripts/zigux/validate-phase14.py` includes the coverage checker in its required files or subchecker coverage, with fixture-backed self-test evidence.
- The single returned shared gate remains `make -C zigux phase14-validate`.
- The broader `phase14-smoke`, `phase14-test`, and aggregate `phase14` Makefile targets remain absent unless a separate roadmap-backed lane proves they are ready.

## Rollback Evidence

If this packet drifts before the gate wiring lands, roll back only the route-evidence claim or the checker wiring that drifted. Do not roll back the existing rollback-threshold sequencing checker, skbuff stay-in-C guardrail, RCU rollback guardrail, release-boundary exact-count checker, or shared smoke route checker unless their own lane-local evidence is invalid.

If the coverage checker becomes gate-enforced and later breaks, the rollback threshold remains `0` tolerated same-packet drifts: return the coverage checker to a blocked/evidence-only state and keep `make -C zigux phase14-validate` fail-closed until either the checker and route agree again or a fresh Phase 14 note records the blocked state explicitly.
