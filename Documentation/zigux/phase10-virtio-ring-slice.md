# Phase 10 virtio_ring Slice

This bounded Phase 10 slice records the current queue-local `virtio_ring` review packet anchored to `drivers/virtio/virtio_ring.c`.

- `PHASE10_SLICE=virtio-ring-queue-wrapper-packet`
- reviewed against live `master` ring packet anchored by surveyed `e42103fc02f544e1bd23a5ec2e5b584734f5af7d`
- lane: `P10-L10`
- anchor: `drivers/virtio/virtio_ring.c`

## Current packet

- `zigux/tests/phase10_virtio_ring_manifest.json` is the direct packet-local source of truth for the ring lane on current `master`
- `Documentation/zigux/phase10-virtio-ring-survey.md` keeps the roadmap boundary, blocked MMIO-owned bridge, and current ring-lane scope explicit for reviewers
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` keeps the direct ring lane keyed as a bounded packet instead of flattening it into broad shared Phase 10 reminder churn
- `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`, and `Documentation/zigux/freeze-map.md` remain the adjacent shared reminder and boundary surfaces for this lane

## Repo-reality gaps

Current `master` does not currently expose these older ring packet paths, so this slice note must not treat them as shipped evidence:
- `drivers/virtio/virtio_ring.zig`
- `drivers/virtio/virtio_ring_verify.zig`
- `zigux/tests/phase10_virtio_ring.zig`
- `zigux/tests/phase10_virtio_ring_reset_reuse.zig`
- `zigux/tests/phase10_virtio_ring_survey.zig`
- `scripts/zigux/check-phase10-ring-packet.py`
- `zigux/tests/phase10_build.zig`

The direct ring helper ladder, verify replay, reset-reuse replay, dedicated survey gate, checker, and shared build route therefore remain repo-reality gaps on current `master` rather than landed queue-local wrapper evidence.

## Why this packet exists

- The Phase 10 roadmap still asks Zigux to prove virtqueue wrappers and lab-only driver validation before widening into transport-backed lifecycle work.
- The highest-value same-lane work right now is truthfulness: keep the manifest and packet-local notes aligned to the live tree instead of letting stale reminder text quietly overstate ring progress.
- This slice stays review-only and helper-first: it does not claim queue discovery, IRQ acknowledgement, DMA mapping, queue reset execution against a transport, or probe/remove lifecycle behavior.

## Parked boundary

- `phase10-ring-lab-driver-bridge` stays blocked on risky transport and remains owned by the adjacent MMIO packet.
- `Documentation/zigux/freeze-map.md` still governs the Phase 10 boundary for this queue-local slice.
- The roadmap's dual-implementation posture remains `blocked_on_risky_transport`, and no Architecture Council reopen is attached by this note.

## Next bounded step

Keep `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` aligned around current live repo reality. If the ring lane reopens, prefer one same-lane survey-note, owner-map, or direct-packet restoration step instead of widening into MMIO transport, IRQ, DMA, or lifecycle work.
