# Phase 10 virtio_ring Slice

This bounded Phase 10 slice records the current queue-local `virtio_ring` wrapper packet anchored to `drivers/virtio/virtio_ring.c`.

- `PHASE10_SLICE=virtio-ring-queue-wrapper-packet`
- reviewed against live `master` ring packet anchored by surveyed `e42103fc02f544e1bd23a5ec2e5b584734f5af7d`
- lane: `P10-L07`
- anchor: `drivers/virtio/virtio_ring.c`

## Shipped packet

- `drivers/virtio/virtio_ring.zig` keeps the queue-local wrapper ladder explicit through `phase10-virtqueue-shape-helper`, `phase10-used-buffer-polling-helper`, `phase10-callback-enable-helper`, `phase10-callback-delay-helper`, `phase10-notify-prepare-helper`, `phase10-notification-data-summary-helper`, `phase10-broken-queue-poll-guard`, `phase10-queue-reset-helper`, and `phase10-queue-reset-readiness-helper`
- `drivers/virtio/virtio_ring_verify.zig` keeps the wrapper-facing verify replay explicit for reset-readiness blockers, delayed-callback pacing, clear-broken blocker exposure, and packed-ring event-index review
- `zigux/tests/phase10_virtio_ring.zig` keeps the direct queue-local helper replay explicit beside `zigux/tests/phase10_virtio_ring_reset_reuse.zig`
- `zigux/tests/phase10_virtio_ring_survey.zig` plus `zigux/tests/phase10_virtio_ring_manifest.json` keep the survey gate, surveyed commit, blocked risky-transport posture, and allowed evidence kinds pinned to the current packet
- `Documentation/zigux/phase10-virtio-ring-survey.md` keeps the queue-local survey rationale, current helper ladder, and MMIO-owned bridge boundary explicit for reviewers

## Why this packet exists

- The Phase 10 roadmap asks Zigux to prove virtqueue wrappers and lab-only driver validation before widening into transport-backed lifecycle work.
- Current `master` already carries substantive queue-local ring evidence, so the highest-value same-lane follow-through is to keep that packet reviewable through aligned packet-local survey, manifest, and slice-note metadata instead of leaving ring ownership on an older helper-lane label.
- This slice stays helper-first and in-memory only: it does not claim queue discovery, IRQ acknowledgement, DMA mapping, queue reset execution against a transport, or probe/remove lifecycle behavior.

## Parked boundary

- `phase10-ring-lab-driver-bridge` stays blocked on risky transport and remains owned by the adjacent MMIO packet.
- `Documentation/zigux/freeze-map.md` still governs the Phase 10 boundary for this queue-local slice.
- the roadmap's dual-implementation posture remains `blocked_on_risky_transport`, and no Architecture Council reopen is attached by this note.

## Next bounded step

Keep `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` aligned around the landed queue-local helper ladder. If the ring lane reopens, prefer one owner-map, checker, or survey-note truthfulness repair instead of widening into MMIO transport, IRQ, DMA, or lifecycle work.
