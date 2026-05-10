# Phase 10 Direct-Read Truthfulness Note

This note records the Phase 10 virtio lab surfaces that were directly readable through the authenticated GitHub contents bridge during the latest truthfulness recheck.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_TRANCHE=virtio-lab-bundle`
- `PHASE10_SCOPE=virtio lab-driver progress, virtqueue wrappers, MMIO wrappers, and VM-friendly lab validation`
- `PHASE10_RISKY_TRANSPORT_POSTURE=blocked_on_risky_transport`
- intent: keep shared Phase 10 reminder surfaces honest when direct repo reads do not agree on every packet-local path

## Directly Verified Reads

The following Phase 10 review surfaces were directly readable through the authenticated GitHub bridge on current `master`:

- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- `scripts/zigux/check-phase10-harness-coverage.py`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/Makefile`

Those reads are enough to prove that current `master` already ships both a dedicated direct-core tests-root checker and a focused Phase 10 harness-coverage checker, plus the shared `phase10-test` make route that invokes the packet guards and the broader Phase 10 build replay.

## Current Truthfulness Blocker

Representative packet-local reads still returned `404 Not Found` through that same authenticated bridge for paths such as:

- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `drivers/virtio/virtio.zig`
- `drivers/virtio/virtio_ring.zig`
- `zigux/tests/phase10_virtio_core_manifest.json`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-mmio-freeze-boundary.py`

Because the same bridge both confirms the shared reminder packet and refuses representative packet-local paths, broad Phase 10 summary surfaces should not overstate packet-local direct readability until that mismatch is reconciled.

## Roadmap Boundary

This note does not widen Phase 10 scope.

- risky transport work remains blocked
- queue setup, reset, IRQ, DMA, input registration lifecycle, and probe/remove lifecycle claims remain out of scope
- `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors

## Next Bounded Step

Refresh one shared Phase 10 reminder surface at a time so it stays truthful about two things at once:

1. `scripts/zigux/check-phase10-harness-coverage.py` is already shipped on `master`
2. packet-local direct readability is still inconsistent across the authenticated contents bridge
