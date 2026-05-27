# Phase 12 Cross Compile Smoke

This note records the current-master compile-smoke reading for the shared Phase 12 cross-target packet.

It stays roadmap-aligned to the Phase 12 complex-driver tranche by describing only the bounded smoke-and-test route and the surviving syntax-lab successor packet, not deeper driver delivery.

## Status

- `PHASE12_STATUS=shared-virtio-net-smoke-sextet-present`
- `PHASE12_LANE=P12-L06`
- scope: keep the shared compile-smoke note truthful around the six-file `virtio_net` smoke-and-test packet, the returned wrapper routes, and the surviving syntax-lab successor evidence including its isolated rerun hook without reopening driver behavior
- roadmap anchor: `drivers/net/virtio_net.c`
- shared packet companions: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, and `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- support checker: `scripts/zigux/check-phase12-cross-compile-smoke.py`

## Current-master reading

- current shared reminder surfaces now agree that the active shared `virtio_net` compile-smoke packet is the six-file bundle in `zigux/tests/phase12_build.zig`: `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`
- current `zigux/Makefile` directly exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, `make -C zigux phase12`, and `make -C zigux phase12-virtio-net-syntax-lab-test`
- current `Documentation/zigux/phase12-virtio-net-survey.md` confirms the older monolithic syntax-lab packet has been replaced by the split helper family and the shared survey gate
- that same survey note also keeps `zigux/tests/phase12_virtio_net_syntax_lab.zig` and `zigux/tests/phase12_virtio_net_syntax_lab_build.zig` explicit as surviving standalone compile-smoke companions outside the shared six-file `phase12-validate` / `phase12-smoke` / `phase12-test` route
- the isolated syntax-lab rerun handles are `zig build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all` and `make -C zigux phase12-virtio-net-syntax-lab-test`, so the companion stays reviewable without joining the shared packet
- current `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` also keeps the older `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig` vocabulary out of the live packet on `master`
- substantive same-family lab progress has therefore landed since the earlier cross-note packet: the shared route is now the six-file split-helper smoke-and-test sextet with returned wrapper evidence rather than the older syntax-lab-era shape
- the shipped cross-compile checker now keeps that returned wrapper wording plus the isolated syntax-lab rerun hook fail-closed across this note and `zigux/Makefile`

## Boundaries

- this note does not claim DMA-safe receive ownership, page-pool refill execution, interrupt-backed completion handling, queue restart parity, or full `net_device` lifecycle parity
- this note does not reopen the shared checker bodies, the `virtio_scsi` rollback-lab packet, the NVMe foothold packet, or the parked libbpf packet
- this note treats the split-helper `virtio_net` sextet as compile-smoke and reviewability evidence only
- this note treats the isolated syntax-lab rerun as standalone compile-smoke coverage only, not as a signal that the older monolithic starter returned

## Next Bounded Step

Leave this note parked unless the shared six-file `virtio_net` smoke-and-test packet changes again across `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `zigux/Makefile`, or `zigux/tests/phase12_build.zig`.

If the shared packet changes again, leave the next same-lane follow-through note-local and rerun `scripts/zigux/check-phase12-cross-compile-smoke.py` before widening compile-smoke claims again.

If only the standalone syntax-lab companion drifts, repair just the isolated rerun hook around `zigux/tests/phase12_virtio_net_syntax_lab_build.zig`, `zigux/Makefile`, and this note instead of widening the shared packet.
