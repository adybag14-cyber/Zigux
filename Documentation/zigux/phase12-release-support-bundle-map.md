# Phase 12 Release Support Bundle Map

This note is the compact PMO companion for the active Phase 12 release-planning packet.

It is a release-coordination artifact only. It does not close Phase 12, and it does not create a new replay route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- lane owner: `pmo-release`
- scope: keep the returned validator-side support packet explicit beside the shipped shared wrapper set without widening Phase 12 into deeper driver-delivery claims
- shared release companions: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared reminder companions: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- shared build evidence: `zigux/Makefile`, `zigux/tests/phase12_build.zig`, and `.github/workflows/zigux-bootstrap.yml`

## Returned Support Bundle

Current repo-first reads on `master` keep the Phase 12 PMO support packet explicit through these checker and validator surfaces:

- `scripts/zigux/validate-phase12.py`
- `scripts/zigux/check-build-only-phase12-surface.py`
- `scripts/zigux/check-phase12-build-inventory.py`
- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `scripts/zigux/check-phase12-complex-driver-lane-packet.py`
- `scripts/zigux/check-phase12-cross-compile-smoke.py`
- `scripts/zigux/check-phase12-libbpf-snapshot.py`
- `scripts/zigux/check-phase12-libbpf-lane-marker.py`
- `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`
- `scripts/zigux/check-phase12-virtio-scsi-libbpf-boundary.py`

Treat that set as the current shared PMO truthfulness packet for release planning on `master`.

## Shared Wrapper Set

Current repo-first reads also keep the shipped shared wrapper evidence explicit through `zigux/Makefile`:

- `make -C zigux phase12-validate`
- `make -C zigux phase12-smoke`
- `make -C zigux phase12-test`
- `make -C zigux phase12`

Those wrappers are current release-planning evidence again, but they do not by themselves close the broader complex-driver tranche.

## Packet Split

Keep the release-planning split explicit:

- the shared smoke-and-test route is still the six-file `virtio_net` packet wired through `zigux/tests/phase12_build.zig`
- the `virtio_scsi` packet remains survey-backed rollback evidence outside the shared route
- the `nvme_pci` packet remains a bounded driver-local foothold outside the shared route
- the libbpf packet remains parked behind survey, snapshot, and verify-shard reminder surfaces rather than a shared replay route

## Boundaries

- This note is a support-bundle map, not a closure claim.
- This note must stay below DMA-safe receive ownership, queue restart parity, throughput delivery, deeper recovery, and full transport lifecycle claims.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper `skbuff`, `workqueue`, and `ring_buffer` anchors.
- Do not promote the support bundle into proof that deeper driver delivery has landed.

## Next Bounded Step

If a later same-lane reread finds that `Documentation/zigux/README.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md` understates the returned support bundle or the shipped `phase12-*` wrapper set, refresh only the smallest reminder surface that drifted.
