# Phase 15 Scripts-Root Tooling Gap

This note records the current Phase 15 scripts-root tooling gap on `master`.

## Status

- `PHASE15_STATUS=scripts_root_tooling_gap_recorded`
- `PHASE15_LANE_KEY=repo-tooling`
- `PHASE15_SLICE=scripts-root-phase15-gap`
- `PHASE15_PROVENANCE_MODE=dated_master_readback`
- surveyed against dated current-master readback marker `current-master-readback-2026-05-16`
- role: keep the current scripts-root Phase 15 mismatch explicit so repo-hosted tooling reads stay truthful until the parked validator-and-build packet is materialized again

## Why this note exists

The roadmap keeps repo-hosted tooling and deterministic validation surfaces as real product infrastructure, not background decoration.

Current `master` still carries Phase 15 reminder language in `Documentation/zigux/README.md`, `zigux/tests/README.md`, and the shipped `scripts/zigux/check-phase15-scripts-readme-alignment.py` checker. But the scripts root itself has not caught up: `scripts/zigux/README.md` still stops at earlier phases, while the broader Phase 15 validator-and-build packet the checker expects is not fully present on current `master`.

That makes the smallest honest repo-tooling step evidence, not expansion: record the scripts-root gap directly and fail closed until the scripts-root summary plus the parked validator-and-build packet are rematerialized together.

## Current repo reality

The current scripts-root-adjacent evidence that does exist on `master` is:

- `scripts/zigux/README.md`
- `scripts/zigux/check-phase15-scripts-readme-alignment.py`
- `Documentation/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/phase15-architecture-council-review-process.md`

The scripts-root Phase 15 packet that is currently missing or incomplete on `master` is:

- `scripts/zigux/README.md` does not carry a `Phase 15 flow` section
- `scripts/zigux/validate-phase15.py`
- `zigux/tests/phase15_build.zig`
- `zigux/tests/phase15_architecture_council_review_process_manifest.json`

The live mismatch is therefore:

- `Documentation/zigux/README.md` still names `scripts/zigux/check-phase15-scripts-readme-alignment.py` and the `make -C zigux phase15-*` routes in its Phase 15 summary
- `zigux/tests/README.md` still names the same scripts-root checker and Phase 15 routes in the tests-root review packet
- `scripts/zigux/check-phase15-scripts-readme-alignment.py` still hard-codes `Phase 15 flow`, `make -C zigux phase15-validate`, `make -C zigux phase15-test`, `make -C zigux phase15`, `scripts/zigux/validate-phase15.py`, `zigux/tests/phase15_build.zig`, and `zigux/tests/phase15_architecture_council_review_process_manifest.json` as required current-repo markers
- `scripts/zigux/README.md` does not yet provide that Phase 15 scripts-root packet, and the validator-plus-build paths above still do not materialize through authenticated current-master contents readback

## Recovery rule

Treat the Phase 15 scripts-root tooling packet as incomplete until the scripts root and the parked validator-and-build packet can be reread together on current `master`.

Until that happens:

- do not treat `scripts/zigux/README.md` as shipped Phase 15 scripts-root evidence
- do not assume `scripts/zigux/check-phase15-scripts-readme-alignment.py` represents a fully materialized validator-first route
- use this note as the lane-local reminder that the scripts-root summary and its required validator-and-build companions must be narrowed or rematerialized before they are reused as direct current-`master` evidence

## Non-goals

This note does not claim:

- a rebuilt `scripts/zigux/validate-phase15.py`
- a rebuilt `zigux/tests/phase15_build.zig`
- a rebuilt `zigux/tests/phase15_architecture_council_review_process_manifest.json`
- ownership of the broader Phase 15 governance packet outside the scripts-root tooling mismatch recorded here

## Next bounded step

If a future repo-tooling or governance-maintenance lane rereads a coherent Phase 15 scripts-root packet on current `master`, narrow or retire this note immediately.

The next honest follow-through is one bounded scripts-root step:

- either rematerialize a truthful `scripts/zigux/README.md` Phase 15 section together with the validator-and-build packet it cites
- or narrow `scripts/zigux/check-phase15-scripts-readme-alignment.py` so it only enforces the Phase 15 surfaces that actually exist on current `master`
