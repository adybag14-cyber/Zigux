# Phase 14 Scripts-Root Productization Gap

## Status

- `PHASE14_GAP_KIND=scripts_root_productization_gap`
- `PHASE14_LANE_KEY=P14-L01`
- `PHASE14_PROVENANCE_MODE=current_master_readback`
- re-read against current `master` on 2026-05-29

## Roadmap Boundary

Phase 14 stays bounded to study-only, wrapper-first, or stay-in-C evidence.

The roadmap's Phase 14 product goal is to study or wrap critical shared infrastructure without claiming premature parity. The freeze map keeps `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in boundary-study-only posture and keeps `net/core/skbuff.c` plus `kernel/rcu/tree.c` in freeze-in-C or stay-in-C posture.

The attached ZAR runtime research archive is useful here only as absorption discipline: smoke sequencing, blocked-state vocabulary, rollback thresholds, and reviewability structure. It is not current Zigux delivery evidence for broad Phase 14 parity.

## Current Gap

`scripts/zigux/README.md` currently jumps from `## Phase 13` to `## Phase 15`.

That leaves the scripts-root contributor surface behind the returned Phase 14 productization packet. Current Phase 14 notes, manifests, and validators already keep the shared smoke route, release-boundary counts, rollback threshold, skbuff stay-in-C guardrail, skbuff compile-route checker, RCU compile-route checker, and RCU rollback guardrail visible, but the scripts-root summary does not yet give reviewers a Phase 14 entry point.

The current scripts-root gap is narrower than a missing Phase 14 implementation. The bounded productization issue is that the scripts-root reminder has not caught up with the existing study-only validation packet.

## Required Current Packet Reminders

When `scripts/zigux/README.md` is repaired, keep the Phase 14 entry bounded around these current surfaces:

- `scripts/zigux/check-phase14-shared-smoke-route.py`
- `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`
- `scripts/zigux/validate-phase14.py`
- `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`
- `scripts/zigux/check-phase14-skbuff-stay-in-c-guardrail.py`
- `scripts/zigux/check-phase14-skbuff-compile-route.py`
- `scripts/zigux/check-phase14-ring-buffer-compile-route.py`
- `scripts/zigux/check-phase14-rcu-compile-route.py`
- `scripts/zigux/check-phase14-rcu-rollback-guardrail.py`
- `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- `Documentation/zigux/phase14-productization-gap-survey.md`
- `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- `Documentation/zigux/phase14-release-boundary-survey.md`
- `Documentation/zigux/phase14-compile-shard-matrix-survey.md`
- `Documentation/zigux/phase14-workqueue-bridge-survey.md`
- `Documentation/zigux/phase14-ring-buffer-survey.md`
- `Documentation/zigux/phase14-skbuff-bridge-survey.md`
- `Documentation/zigux/phase14-rcu-tree-survey.md`
- `zigux/tests/phase14_end_to_end_smoke_manifest.json`
- `make -C zigux phase14-validate`

The scripts-root reminder should preserve the single live shared gate and should not restore `phase14-smoke`, `phase14-test`, or `phase14` as shipped wrapper claims unless current repo readback and Makefile evidence actually return those routes.

## Guardrail

`scripts/zigux/check-phase14-scripts-root-productization-gap.py` records this as a current gap rather than pretending the README has already been repaired.

The checker should pass while the scripts-root README still lacks a dedicated Phase 14 section and this note keeps the bounded productization markers above. When a later lane intentionally adds `## Phase 14` to `scripts/zigux/README.md`, update or retire the checker in the same change so the project does not keep a stale gap marker after the reminder surface is fixed.

## Next Bounded Step

Add the smallest `## Phase 14` section to `scripts/zigux/README.md`, using the current surfaces above, after fresh readback confirms the route split is still `make -C zigux phase14-validate` only.

Keep that follow-up documentation-only unless current repo evidence shows a separate machine-checkable Phase 14 route or validator drift.
