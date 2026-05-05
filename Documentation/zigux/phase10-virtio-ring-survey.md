# Phase 10 Virtio Ring Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-ring-survey`
- scope: survey manifest, dedicated survey gate, shared Phase 10 build wiring, and a lane-level note that records what has now landed plus the remaining queue-wrapper gap against the roadmap
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `zigux/tests/phase10_virtio_ring_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-virtio-ring-slice.md`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter with queue callback bookkeeping, descriptor-shape metadata, and notification accounting. This survey started by making the missing ring-helper gap explicit, and it now records that the first `drivers/virtio/virtio_ring.zig` lab slice has landed plus small used-buffer polling, callback re-enable, delayed-callback pacing, and broken-queue discipline follow-ups without pretending queue lifecycle parity is complete. The adjacent MMIO packet has also advanced beyond an older register-window-only foothold and now records bounded queue-size, feature-word, and config-window helpers as landed.

## Survey findings

- `drivers/virtio/virtio_ring.c` is present on `master` at 3940 lines and spans split rings, packed rings, descriptor state, DMA mapping helpers, callback toggling, notification bookkeeping, queue reset, resize, and break or unbreak handling.
- the live repo already ships `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, and `Documentation/zigux/phase10-virtio-mmio-survey.md`.
- the current Zigux VirtIO ring surface now includes a bounded `drivers/virtio/virtio_ring.zig` helper for queue registration, layout metadata, outstanding-chain accounting, used-buffer polling, callback re-enable bookkeeping, delayed-callback pacing, broken-queue discipline that blocks fresh publish, kick, poll, and callback snapshots, and notify-prepare bookkeeping.
- the live Phase 10 packet now also records the adjacent `drivers/virtio/virtio_mmio.zig` footholds as landed: a tiny register window, queue-size staging, one bounded feature-word selector and read window, and one small config-word window rooted in staged MMIO config bytes.
- the live repo still does not model real descriptor tables, DMA helpers, interrupt callbacks, or transport-backed queue reset semantics.
- this leaves only the riskier MMIO lifecycle, IRQ, queue-discovery, and reset follow-up blocked behind the already-landed queue-wrapper and MMIO footholds.

## Recorded gaps

The survey manifest now records:

- the landed `phase10-build-gate`
- the landed `phase10-virtio-core-lab-starter`
- the landed `phase10-virtio-ring-survey-gate`
- the landed `phase10-virtio-ring-survey-note`
- the landed `phase10-virtqueue-shape-helper`
- the landed `phase10-used-buffer-polling-helper`
- the landed `phase10-callback-enable-helper`
- the landed `phase10-callback-delay-helper`
- the landed `phase10-broken-queue-poll-guard`
- the landed `phase10-mmio-register-window-helper`
- the landed `phase10-mmio-queue-size-helper`
- the landed `phase10-mmio-feature-word-selector-helper`
- the landed `phase10-mmio-config-window-helper`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`
- the landed `phase10-virtio-ring-slice-note`

This keeps the lane concrete and reviewable without overstating `virtio_ring` progress: the queue-shape foothold is real, used-buffer polling, callback re-enable, delayed-callback pacing, broken-queue discipline, and the bounded MMIO register, queue-size, feature-word, and config-window helpers are all landed, and the risky transport-facing lifecycle work is still intentionally blocked. That blocked MMIO lifecycle and IRQ follow-up remains owned by the adjacent `virtio_mmio` packet plus shared Phase 10 closure evidence, not by this queue-local ring survey note.

## Freeze boundary

- `Documentation/zigux/freeze-map.md` is the governing boundary note for this queue-local survey packet.
- freeze-boundary owner: `P10-L10`
- rollback owner: keep the shared Phase 10 closure packet aligned before widening this queue-local note.
- this ring survey stays inside `drivers/virtio/*.zig`; it does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain Phase 14 study-only anchors under the freeze map.
- the allowed evidence here is the ring survey note, its manifest, its focused survey gate, and the shared Phase 10 build packet; this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.

## Non-goals

This survey slice does not yet claim:

- real split-ring or packed-ring descriptor parity
- DMA mapping or unmapping wrappers
- `virtqueue_add_*`, `virtqueue_get_buf`, or `vring_interrupt` lifecycle behavior
- `virtio_mmio.c` transport glue beyond the already-landed bounded helper windows

## Gates

1. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

2. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Keep the broader Phase 10 virtio lane parked unless fresh repo inspection finds another one-file or tightly coupled survey, manifest, slice-note, or helper-test truthfulness repair before widening into interrupt acknowledgement, reset, queue discovery, or probe lifecycle work.
