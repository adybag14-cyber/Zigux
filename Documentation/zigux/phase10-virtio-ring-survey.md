# Phase 10 Virtio Ring Survey
This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-ring-survey`
- lane: `P10-L07`
- surveyed commit: `bdfe88e865b94387b3c3bd41ca98054c452f78b9`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: survey manifest, this survey note, the shared lane note, and one lane-level record that keeps the queue-local virtqueue foothold and the remaining roadmap lab-driver gap framed honestly against current repo reality
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`
  - `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor and asks Zigux to prove virtqueue wrappers before widening into transport-backed lifecycle work.

Fresh live tree inspection shows that the direct ring helper packet does materialize on current `master`: `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `scripts/zigux/check-phase10-ring-packet.py`, `zigux/tests/phase10_build.zig`, and `Documentation/zigux/phase10-virtio-ring-slice.md` are all present beside this survey note. This survey therefore exists to keep that queue-local foothold honest against the still-blocked lab-driver bridge instead of regressing back to absent-file claims.

## Survey findings
- `drivers/virtio/virtio_ring.c` is present on `master` and still spans split rings, packed rings, descriptor state, DMA mapping helpers, callback toggling, notification bookkeeping, queue reset, resize, and break or unbreak handling.
- the live repo materializes the direct ring helper packet: `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `scripts/zigux/check-phase10-ring-packet.py`, `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, and `Documentation/zigux/phase10-virtio-ring-survey.md`.
- the landed queue-local surface still stays bounded to in-memory wrapper discipline: queue shape, used-buffer polling, callback re-enable and delayed pacing, notify-prepare bookkeeping, broken-queue discipline, reset-readiness preflight, queue reset, and the verify replay's packed event-index checks are reviewable without claiming DMA, IRQ delivery, queue discovery, or probe/remove lifecycle parity.
- the remaining same-lane gap is smaller than the current manifest claimed: the helper packet does not yet expose a dedicated notification-data summary that makes split next-avail state and packed wrap-bit transitions reviewable through one explicit wrapper surface.
- the blocked transport-backed bridge still belongs to the adjacent `P10-L10` MMIO packet. This ring survey may name that dependency, but it does not absorb MMIO helper growth or MMIO next-step selection.

## Recorded gaps

Fresh repo inspection now supports these narrower conclusions:
- `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-ring-survey.md`, `scripts/zigux/check-phase10-ring-packet.py`, and `zigux/tests/phase10_build.zig` are present and keep the ring lane reviewable as a real helper packet rather than an absent-file checkpoint.
- `drivers/virtio/virtio_ring.zig` and `drivers/virtio/virtio_ring_verify.zig` are present and already cover queue-shape metadata, used-buffer polling, callback discipline, notify-prepare bookkeeping, broken-queue state, reset-readiness blockers, queue reset, and packed event-index review.
- the honest same-lane follow-through is now one bounded truthfulness step: keep the manifest, survey note, and survey gate aligned on the already-landed helper packet while leaving `phase10-notification-data-summary-helper` as the next queue-local reviewability step rather than a landed claim.

## Freeze boundary
- `Documentation/zigux/freeze-map.md` is the governing boundary note for this queue-local survey packet.
- freeze-boundary owner: `P10-L10`
- rollback owner: keep this survey note, `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`, and `Documentation/zigux/freeze-map.md` aligned before widening this queue-local note.
- this ring survey stays inside `drivers/virtio/*.zig`; it does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain Phase 14 study-only anchors under the freeze map.
- the Phase 15 freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c` also remain outside this lane; this survey does not claim scheduler, MM, RCU, or skbuff ownership, parity, or Architecture Council reopen authority.
- the allowed evidence here is the direct ring helper packet, the ring survey note, the ring manifest, the shared lane note, the freeze-map boundary note, and live tree readback; this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.

## Non-goals
This survey slice does not yet claim:
- real split-ring or packed-ring descriptor parity
- DMA mapping or unmapping wrappers
- `virtqueue_add_*`, `virtqueue_get_buf`, or `vring_interrupt` lifecycle behavior
- transport-backed queue discovery, IRQ acknowledgement, queue reset execution, or probe/remove lifecycle behavior
- a landed notification-data summary helper that covers split next-avail state and packed wrap-bit transitions through one dedicated wrapper surface

## Gates
Current `master` supports the full bounded ring packet again:
1. reread `zigux/tests/phase10_virtio_ring_manifest.json`
2. reread `Documentation/zigux/phase10-virtio-ring-survey.md`
3. run `python3 scripts/zigux/check-phase10-ring-packet.py --self-test`
4. run `python3 scripts/zigux/check-phase10-ring-packet.py`
5. run `zig test zigux/tests/phase10_virtio_ring.zig`
6. run `zig test zigux/tests/phase10_virtio_ring_survey.zig`
7. run `zig build test --build-file zigux/tests/phase10_build.zig`

Those gates keep the bounded ring-lane packet honest while the MMIO bridge remains blocked.

## Next bounded step
Keep the broader Phase 10 virtio lane parked unless fresh repo inspection finds another directly coupled drift inside the existing ring helper, verify replay, manifest, survey note, or survey gate. Inside this ring lane, the next honest bounded step is the queue-local `phase10-notification-data-summary-helper` reviewability surface or, if the gate still lags, one equally small survey-gate repair that marks that helper `ready_next` instead of landed. Do not reopen MMIO helper growth, DMA, interrupt delivery, queue discovery, reset execution, or probe/remove lifecycle work from this note.
