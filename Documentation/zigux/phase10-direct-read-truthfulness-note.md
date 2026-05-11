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
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase10.py`
- `scripts/zigux/validate-phase10-closure.py`
- `scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- `scripts/zigux/check-phase10-harness-coverage.py`
- `zigux/tests/README.md`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/Makefile`

Those reads are enough to prove that current `master` already ships a directly readable lane-owner split for the active virtio bundle, a dedicated direct-core tests-root checker, a shared harness-coverage checker, and a dedicated `phase10-validate` route beside the shared `phase10-test` replay surface.

## Current Truthfulness Blocker

Representative packet-local reads still returned `404 Not Found` through that same authenticated bridge for paths such as:

- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `drivers/virtio/virtio.zig`
- `drivers/virtio/virtio_ring.zig`
- `zigux/tests/phase10_virtio_core_manifest.json`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-mmio-freeze-boundary.py`

Because the same bridge now confirms the shared closure note, the lane-sequencing note, the shared validation helpers, and the shared harness checker while still refusing representative packet-local paths, broad Phase 10 summary surfaces should stay honest about that mixed direct-read posture instead of implying either that every packet-local path is readable or that the shared validation route is still absent on current `master`.

## Roadmap Boundary

This note does not widen Phase 10 scope.

- risky transport work remains blocked
- queue setup, reset, IRQ, DMA, input registration lifecycle, and probe/remove lifecycle claims remain out of scope
- `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` remain separate Phase 14 study-only anchors

## Next Bounded Step

Refresh one shared Phase 10 reminder surface at a time so it stays truthful about three things at once:

1. `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` is directly readable on current `master`
2. `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, and `scripts/zigux/check-phase10-harness-coverage.py` are already shipped on current `master`
3. packet-local direct readability is still inconsistent across the authenticated contents bridge
