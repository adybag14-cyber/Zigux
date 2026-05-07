# Phase 15 Readiness Gate Survey

This document records the bounded Phase 15 governance lane for checking whether the parked freeze-map packet is reviewable enough to stay in maintenance mode without implying any Architecture Council approval for a status change.

## Status

- `PHASE15_STATUS=maintenance_mode_ready`
- `PHASE15_LANE_KEY=P15-L08`
- `PHASE15_SLICE=phase15-readiness-gate-current-blocker-inventory`
- survey provenance refreshed against current `master` via the GitHub connector on May 6, 2026
- the shared replay surface is green on current `master` once this dedicated readiness note, its manifest, the focused `zigux/tests/phase15_readiness_gate.zig` guard, and the shipped `phase15-validate` checker stack are present together

## Roadmap Versus Ledger

- roadmap source: `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md` Phase 15, `Full-Parity Blockers and Long-Term Governance`
- roadmap-required Phase 15 bundle:
  - freeze map
  - Architecture Council review process
  - parity scorecard
  - policy for code that remains in C indefinitely
- bootstrap ledger anchor: `docs(zigux): add documentation root, review checklist, and freeze map`

## Current Repo Readiness

- the shared governance packet is present through `Documentation/zigux/README.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase15-architecture-council-review-process.md`, `Documentation/zigux/phase15-parity-scorecard.md`, `Documentation/zigux/phase15-indefinite-c-policy.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `zigux/tests/README.md`, the Phase 15 scripts-root checkers `scripts/zigux/check-phase15-scripts-readme-alignment.py` and `scripts/zigux/check-phase15-review-process-handoff.py`, `.github/workflows/zigux-bootstrap.yml`, the shared `zigux/tests/phase15_build.zig` replay, `make -C zigux phase15-validate`, and `make -C zigux phase15`
- `zigux/Makefile` still exposes `phase15-validate`, and that validator-first route still reruns both dedicated Phase 15 checker paths before the shared `zigux/tests/phase15_build.zig` replay, so the current governance packet carries explicit release evidence for the shipped review route instead of relying on the build replay alone
- `Documentation/zigux/phase15-handoff-next-steps-survey.md` keeps the bounded handoff record and parked next-step packet visible beside this readiness gate
- `Documentation/zigux/README.md` is the docs-root entry point for this parked governance packet, so `Documentation/zigux/phase15-readiness-gate-survey.md` must stay named there beside the freeze map, review process, parity scorecard, handoff note, and indefinite-C policy instead of leaving the maintenance-mode blocker inventory implicit
- maintenance-mode ready: the parked Phase 15 packet is reviewable and rerunnable, but no freeze-map status-change approval is recorded

## Current Deep-Core Blockers

- `kernel/sched/core.c`: blocked as `blocked_no_bounded_scheduler_seam`; the roadmap still limits this anchor to Phase 15 governance, and current repo reality still stops at `Documentation/zigux/freeze-map.md` plus `Documentation/zigux/phase15-parity-scorecard.md` without any narrower scheduler seam packet
- `mm/page_alloc.c`: blocked as `blocked_no_bounded_allocator_seam`; the roadmap still treats allocator work as freeze-in-C governance only, and current repo reality still stops at `Documentation/zigux/freeze-map.md` plus `Documentation/zigux/phase15-parity-scorecard.md` without any bounded allocator seam evidence
- `kernel/rcu/tree.c`: blocked as `blocked_phase14_followup_still_wider_than_allowed_rcu_seam`; the roadmap still requires long-term governance rather than a live port claim, and current repo reality still points at `Documentation/zigux/phase14-rcu-tree-survey.md` plus `Documentation/zigux/phase15-parity-scorecard.md` as the active blocker packet
- `net/core/skbuff.c`: blocked as `blocked_packet_lifetime_boundary_still_too_wide`; the roadmap still keeps skbuff in the freeze-in-C set, and current repo reality still points at `Documentation/zigux/phase14-skbuff-bridge-survey.md` plus `Documentation/zigux/phase15-parity-scorecard.md` as the active blocker packet

## Remaining Readiness Gaps

- `phase15-deep-core-status-change-blocker`: the freeze-in-C posture still holds because the four current deep-core blocker dispositions above have not changed on `master`

## Readiness Gate

1. Run the validator-first route: `make -C zigux phase15-validate`
2. Run the dedicated Phase 15 build: `zig build test --build-file zigux/tests/phase15_build.zig`
3. Run the convenience target: `make -C zigux phase15`

## Next bounded step

Keep the Phase 15 governance lane in maintenance mode unless the shared Phase 15 replay drifts again, the docs-root readiness pointer disappears, one of the two dedicated `phase15-validate` checker routes disappears, or one of the four recorded deep-core blocker dispositions changes.
