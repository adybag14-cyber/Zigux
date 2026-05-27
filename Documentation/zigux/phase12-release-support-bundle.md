# Phase 12 Release Support Bundle

This note is the compact PMO owner map for the shared validator-first support bundle that current Phase 12 release artifacts already depend on.

It is a release-planning artifact only. It does not widen Phase 12 into new driver delivery, and it does not claim tranche closure.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- lane owner: `pmo-release`
- primary shared packet companions: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md`
- fallback companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- shared build route evidence: `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`
- shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`

## Shared Support Bundle

Keep the shared validator-first support bundle explicit as:

- `scripts/zigux/validate-phase12.py`
- `scripts/zigux/check-build-only-phase12-surface.py`
- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `scripts/zigux/check-phase12-complex-driver-lane-packet.py`
- `scripts/zigux/check-phase12-cross-compile-smoke.py`
- `scripts/zigux/check-phase12-libbpf-snapshot.py`
- `scripts/zigux/check-phase12-libbpf-lane-marker.py`
- `scripts/zigux/check-phase12-libbpf-heavy-consumer-packet.py`

Those support surfaces are shared release-packet truthfulness evidence. They are not proof of deeper DMA, queue ownership, recovery, transport, or object-model delivery.

## Shared Route Reading

The active shared build packet on current `master` remains the six-file `virtio_net` follow-up sextet wired through `zigux/tests/phase12_build.zig`:

- `zigux/tests/phase12_virtio_net_queue_resume.zig`
- `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`
- `zigux/tests/phase12_virtio_net_transmit_recycle.zig`
- `zigux/tests/phase12_virtio_net_post_reset_replay.zig`
- `zigux/tests/phase12_virtio_net_throughput_parity.zig`
- `zigux/tests/phase12_virtio_net_survey.zig`

Keep the directly readable `virtio_scsi` rollback-lab packet, the bounded `nvme_pci` foothold, and the parked libbpf packet explicit as adjacent review surfaces outside that shared smoke-and-test route.

## Boundaries

- Treat this note as a PMO reminder surface, not as a new replay route.
- Keep `Documentation/zigux/freeze-map.md` as the owner for deeper `net/core/skbuff.c`, `kernel/workqueue.c`, and `kernel/trace/ring_buffer.c` boundary wording.
- If shared reminder surfaces drift, repair one smallest release-owned reminder or checker surface at a time rather than widening into driver-local implementation work.

## Next Bounded Step

Reread this note beside `scripts/zigux/README.md` and `zigux/tests/README.md` whenever the shared Phase 12 reminder packet changes. If either reminder surface understates the shared support bundle above, refresh that reminder surface without widening into fallback-only evidence refresh or driver-local survey edits.
