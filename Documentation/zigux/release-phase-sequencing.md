# Zigux Release Phase Sequencing

This note records the current release-order reading across the active later-phase Zigux packets. It exists so PMO review can read the live tranche sequence in one place without mistaking any single phase note for global release closure.

## Status

- `RELEASE_SEQUENCE_VERSION=1`
- `ACTIVE_RELEASE_SPAN=phase10-through-phase15`
- `GLOBAL_RELEASE_CLOSED=no`
- `PHASE10_STATUS=active-not-closed`
- `PHASE12_STATUS=active-not-closed`
- `PHASE13_STATUS=active-helper-release-packet`
- `PHASE14_STATUS=boundary-only-smoke`
- `PHASE15_STATUS=governance-freeze-gate`

## Sequencing rules

1. Phase 1 and Phase 2 remain closed baseline tranches. They stay important as already-landed build and helper foundations, but they are not the current late-phase release gating surface.
2. Phase 10 remains the earliest active late-phase closure packet. `Documentation/zigux/phase10-closure-evidence.md`, `python3 scripts/zigux/validate-phase10-closure.py`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` keep the parked virtio tranche explicit without claiming risky transport closure.
3. Phase 12 is the current release-facing complex-driver and heavy-helper packet. `Documentation/zigux/phase12-release-readiness-survey.md`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `python3 scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12` are the shared PMO path for that tranche.
4. Phase 13 follows as the shared-helper release-discipline packet, not as a replacement for the still-active Phase 10 or Phase 12 packets. `Documentation/zigux/phase13-release-notes-survey.md`, `python3 scripts/zigux/validate-phase13-release.py`, `make -C zigux phase13-validate`, and `make -C zigux phase13` keep that helper-first surface explicit.
5. Phase 14 remains a boundary-only smoke lane. `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `python3 scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, and `make -C zigux phase14` should be read as release-order reviewability only, not active subsystem delivery.
6. Phase 15 remains the freeze and governance gate. `Documentation/zigux/phase15-readiness-gate-survey.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `python3 scripts/zigux/validate-phase15.py`, `make -C zigux phase15-validate`, and `make -C zigux phase15` keep the reopen rules and deep-core stay-in-C posture explicit before any future release expansion.

## Current coordination map

- Phase 10 currently supplies the release-facing closure evidence for the active virtio tranche. Keep it active, bounded, and validator-first rather than describing it as globally closed.
- Phase 12 currently supplies the PMO release-readiness packet for the active complex-driver tranche. Keep its cross-compile smoke packet, mixed raw-GitHub fallback split, shared replay contract, and dedicated PMO checker visible together.
- Phase 13 currently supplies the helper-side release-discipline packet. Keep it framed as additive helper-first release work that follows the active driver-facing packets instead of replacing them.
- Phase 14 currently supplies the study-only smoke boundary between active helper delivery and governance-only freeze control. Keep it boundary-only.
- Phase 15 currently supplies the release-readiness gate for governance, freeze-map discipline, and handoff rules. Keep it as the final control surface before any deeper-core reopening claims.

## Active PMO gap

The current late-phase sequencing picture is real but still not globally closed. The smallest still-open PMO gap inside the active release path is in Phase 12: the dedicated PMO packet already exists, but the shared `scripts/zigux/validate-phase12.py` surface still needs to name `scripts/zigux/check-phase12-release-readiness-packet.py` and `Documentation/zigux/phase12-release-readiness-survey.md` directly so the broader validator matches the already-published release-facing note.

## Release handoff rule

Do not describe the active late-phase tranche as release-ready unless all of these remain explicit at the same time:

- Phase 10 stays bounded and active-not-closed.
- Phase 12 stays bounded and active-not-closed until the shared validator fully mirrors the dedicated PMO packet.
- Phase 13 stays helper-first and does not get used to imply deeper runtime or driver closure.
- Phase 14 stays a boundary-only smoke lane.
- Phase 15 stays the freeze and governance gate for any future reopening claims.

## Next bounded PMO steps

1. Promote the dedicated Phase 12 PMO packet into `scripts/zigux/validate-phase12.py` so the shared validator directly names the release-readiness survey, checker, docs-root marker, and checklist marker that are already live elsewhere.
2. Keep the Phase 10 closure note and the Phase 13 release-discipline note aligned with their validator-first routes whenever those shared entrypoints change.
3. Leave Phase 14 and Phase 15 in their current boundary and governance roles unless the roadmap itself changes.
