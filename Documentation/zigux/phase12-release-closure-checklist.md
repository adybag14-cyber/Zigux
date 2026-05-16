# Phase 12 Release Closure Checklist

This checklist is the tranche-closure companion for the active Phase 12 packet.

It is a PMO release artifact only. It does not claim that Phase 12 is already closed, and it does not create a new replay route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- lane owner: `pmo-release`
- shared sequencing companion: `Documentation/zigux/phase12-release-sequencing.md`
- shared readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- shared coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared fallback companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`
- support-bundle cross companion: `scripts/zigux/check-phase12-cross.py`
- validator-first support route: `scripts/zigux/validate-phase12.py` and `make -C zigux phase12-validate`
- shared replay wiring: `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`

## Closure Gates

Keep Phase 12 marked open until every item below is true on current `master`:

- The shared PMO packet stays aligned across `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, this checklist, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.
- The shipped validator-first support bundle still reruns as `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-cross.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, and `make -C zigux phase12-validate`.
- The shared smoke-first replay packet still stays wired through `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`.
- The active shared replay packet stays bounded to the starter-present `virtio_net` direct and syntax-lab packet, the bounded `virtio_net_transmit_recycle` and `virtio_net_queue_resume` reviewability follow-ups, and the shipped `virtio_scsi` smoke-first plus rollback-lab packet.
- The bounded driver-local `nvme_pci` foothold stays explicit as a published-but-still-unwired packet outside the shared smoke-first route rather than being silently promoted into the shared replay set.
- The parked libbpf heavy-consumer packet stays explicit through `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` rather than being rounded up into a shipped shared replay claim.
- The fallback split stays truthful: one commit-pinned `virtio_scsi` replay catalog, one current-master `nvme_pci` gap-inventory companion, and two shared-tree anchors.
- Phase 12 wording still stays below DMA-safe receive ownership, refill execution, live queue restart parity, transport-backed queue flow, NAPI, XDP, XSK, RSS programming, control-virtqueue runtime traffic, and full `net_device` lifecycle claims.
- `Documentation/zigux/freeze-map.md` still remains the boundary owner for deeper `skbuff`, `workqueue`, and `ring_buffer` anchors.

## Current Open Blockers

Keep the checklist in the open state while these Phase 12 closure blockers remain true:

- `virtio_net` is starter-present and reviewable, but it is still not a release-closed complex-driver packet.
- `virtio_scsi` remains a smoke-first and rollback-lab packet, not a deeper runtime-delivery or transport-complete packet.
- `nvme_pci` remains driver-local and outside the shared `phase12` smoke-and-test route.
- The libbpf Phase 12 packet remains parked behind survey, snapshot, and verify-shard reminder surfaces rather than a shipped direct replay bundle.
- Degraded GitHub contents reads in this runtime still make some shared replay support files readback-limited even when the public tree and companion notes show they are present on `master`.

## Degraded Validation Path

If `zig` is unavailable on `PATH`, keep the same validator-first then smoke-first order and rerun only the shipped Make routes with `ZIG=<attached-zig-path>`:

1. `make -C zigux phase12-validate`
2. `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
3. `make -C zigux phase12 ZIG=<attached-zig-path>`

Do not invent a focused libbpf-only replay, a cross-build replay, or another unshipped closure route while using the degraded path.

## Re-Read Before Changing Closure State

Before changing this checklist from open to closed, reread these files together:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase12-release-sequencing.md`
- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
- `Documentation/zigux/phase12-virtio-net-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
- `Documentation/zigux/phase12-nvme-pci-slice.md`
- `Documentation/zigux/phase12-nvme-pci-survey.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase12-cross.py`
- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `zigux/tests/README.md`

## Non-Goals

- This checklist does not close the Phase 12 tranche by itself.
- This checklist does not widen Phase 12 into new driver implementation work.
- This checklist does not change the freeze-map posture.
- This checklist does not promote driver-local or parked libbpf evidence into the shared replay route.