# Phase 12 Cross Compile Smoke

This note records the current-master compile-smoke reading for the shared Phase 12 cross-target packet.

It stays roadmap-aligned to the Phase 12 complex-driver tranche by describing only the bounded smoke-and-test route and the surviving syntax-lab successor packet, not deeper driver delivery.

## Status

- `PHASE12_STATUS=shared-virtio-net-smoke-sextet-present`
- `PHASE12_LANE=P12-L06`
- scope: keep the shared compile-smoke note truthful around the six-file `virtio_net` smoke-and-test packet, the returned wrapper routes, and the surviving syntax-lab successor evidence without reopening driver behavior
- roadmap anchor: `drivers/net/virtio_net.c`
- shared packet companions: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, and `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`

## Current-master reading

- current shared reminder surfaces now agree that the active shared `virtio_net` compile-smoke packet is the six-file bundle in `zigux/tests/phase12_build.zig`: `zigux/tests/phase12_virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig`, `zigux/tests/phase12_virtio_net_throughput_parity.zig`, and `zigux/tests/phase12_virtio_net_survey.zig`
- current `zigux/Makefile` directly exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12`
- current `.github/workflows/zigux-bootstrap.yml` keeps the same shared packet explicit through the build-only checker, the complex-driver lane checker, the release-readiness checker, `scripts/zigux/validate-phase12.py`, the `phase12-smoke` and `phase12-test` wrappers, the aggregate `phase12` route, and the adjacent throughput-parity anchor
- current `Documentation/zigux/phase12-virtio-net-survey.md` confirms the older monolithic syntax-lab packet has been replaced by the split helper family and the shared survey gate
- current `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` also keeps the older `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab.zig` vocabulary out of the live packet on `master`
- substantive same-family lab progress has therefore landed since the earlier cross-note packet: the shared route is now the six-file split-helper smoke-and-test sextet with returned wrapper evidence rather than the older syntax-lab-era shape
- the remaining same-family note drift is shared wording, not new compile-smoke scope: current contributor-facing reminder surfaces still disagree about whether `make -C zigux phase12-validate` should be treated as shipped current-master evidence or reminder-only vocabulary, so future same-family follow-through should resolve that shared reminder mismatch before widening compile-smoke claims again

## Boundaries

- this note does not claim DMA-safe receive ownership, page-pool refill execution, interrupt-backed completion handling, queue restart parity, or full `net_device` lifecycle parity
- this note does not reopen the shared checker bodies, the `virtio_scsi` rollback-lab packet, the NVMe foothold packet, or the parked libbpf packet
- this note treats the split-helper `virtio_net` sextet as compile-smoke and reviewability evidence only

## Next Bounded Step

Leave this note parked unless the shared six-file `virtio_net` smoke-and-test packet changes again across `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, or `zigux/tests/phase12_build.zig`.

If the shared packet stays stable and only the `phase12-validate` wording keeps drifting across contributor-facing reminder surfaces, keep the next same-lane follow-through note-local and align that shared reminder wording before reopening any checker or driver-local work.
