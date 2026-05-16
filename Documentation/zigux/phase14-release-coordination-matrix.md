# Phase 14 Release Coordination Matrix

This matrix is the compact PMO coordination companion for the active Phase 14 shared smoke packet.

It is a release-planning artifact, not a closure claim and not a freeze-map status-change request.

## Status

- `PHASE14_STATUS=active`
- `PHASE14_RELEASE_CLOSED=no`
- shared-summary owner: `PMO / Release Management`
- release-boundary companion: `Documentation/zigux/phase14-release-boundary-survey.md`
- traceability companion: `Documentation/zigux/phase14-core-boundary-traceability.md`
- smoke survey companion: `Documentation/zigux/phase14-end-to-end-smoke-survey.md`
- future-governance handoff companion: `Documentation/zigux/phase15-handoff-next-steps-survey.md`
- freeze-map boundary companion: `Documentation/zigux/freeze-map.md`
- validator bundle: `scripts/zigux/validate-phase14.py`, `scripts/zigux/check-phase14-docs-root-smoke-summary.py`, `scripts/zigux/check-phase14-tests-readme-smoke-summary.py`, `scripts/zigux/check-phase14-rollback-threshold-sequencing.py`, and `scripts/zigux/check-phase14-release-boundary-exact-counts.py`
- stable shared replay handle: `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `make -C zigux phase14-test`, and `make -C zigux phase14`
- scope: keep the shipped study-only Phase 14 packet reviewable as one release-facing bundle while keeping later freeze-map status work explicitly handed off to the parked Phase 15 governance packet instead of being implied here

## Owner Split

- PMO / Release Management: keep `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, this matrix, `Documentation/zigux/freeze-map.md`, and `Documentation/zigux/phase15-handoff-next-steps-survey.md` aligned around the same active-not-closed, study-only Phase 14 release packet. The coordination surface should stay release-facing and compact: it should describe the shipped validator-first plus smoke-and-test routes, the four anchor-local packets, and the explicit Phase 15 handoff without reopening deeper bridge or governance wording that current `master` already parks elsewhere.
- Core-adjacent packet: keep `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` framed as the two boundary-study-only anchors that can still receive same-phase bounded evidence maintenance, while `net/core/skbuff.c` and `kernel/rcu/tree.c` stay explicit as freeze-in-C anchors carried by the same shared smoke packet through `zigux/tests/phase14_skbuff_bridge_manifest.json`, `zigux/tests/phase14_rcu_tree_manifest.json`, their companion survey notes, and the shared `zigux/tests/phase14_build.zig` packet rather than as active delivery lanes.
- Phase 15 governance handoff: keep `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `Documentation/zigux/phase15-freeze-map-governance.md`, and the broader Phase 15 governance packet explicit as the owners of any later freeze-map status-change discussion, readiness-gate maintenance, or Architecture Council approval story. This Phase 14 coordination matrix should therefore stop at release-boundary sequencing and must not absorb a parity-scorecard, readiness, or approval claim.

## Release Handle

1. `make -C zigux phase14-validate`
2. `make -C zigux phase14-smoke`
3. `make -C zigux phase14-test`
4. `make -C zigux phase14`
5. If `zig` is unavailable on `PATH`, keep that same shipped order and rerun only the existing Make routes with the attached toolchain override: `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-smoke`, `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14-test`, and `ZIG=/absolute/path/to/attached-zig/zig make -C zigux phase14`. Do not invent a second Phase 14 release route.

## Coordination Checklist

1. Shared release surfaces still agree.
   `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, this matrix, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` must keep the same study-only packet and the same release-facing replay routes.
2. Phase 14 remains active but not closed.
   Release wording must keep `PHASE14_RELEASE_CLOSED=no`, must keep the shared smoke packet explicit, and must not imply a status change for `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `net/core/skbuff.c`, or `kernel/rcu/tree.c`.
3. The Phase 15 handoff stays explicit.
   The future-governance handoff to `Documentation/zigux/phase15-handoff-next-steps-survey.md` must stay visible whenever this matrix or the release-boundary note changes, so later PMO work does not treat the Phase 14 study packet as self-closing governance evidence.

## Boundaries

- This matrix tracks the release-facing coordination of the shipped Phase 14 smoke packet only.
- This matrix does not close the Phase 14 tranche.
- This matrix does not promote any Phase 14 anchor into active deep-core delivery.
- This matrix does not claim Architecture Council approval, a parity-scorecard result, or a freeze-map status change.

## Review Use

- reread this matrix beside `Documentation/zigux/phase14-release-boundary-survey.md`, `Documentation/zigux/phase14-end-to-end-smoke-survey.md`, `Documentation/zigux/phase14-core-boundary-traceability.md`, `Documentation/zigux/freeze-map.md`, `Documentation/zigux/phase15-handoff-next-steps-survey.md`, `scripts/zigux/validate-phase14.py`, `zigux/tests/phase14_end_to_end_smoke_manifest.json`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` whenever the shared Phase 14 release packet changes
- rerun `python3 scripts/zigux/validate-phase14.py` and `make -C zigux phase14-validate` before widening PMO release wording
- treat this file as the compact owner-and-handoff summary for the current Phase 14 packet, not as a substitute for the anchor-local survey notes or the parked Phase 15 governance packet
