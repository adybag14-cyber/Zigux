# Phase 10 Virtio Ring Survey

This document tracks the bounded Phase 10 survey lane around `drivers/virtio/virtio_ring.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-ring-survey`
- lane: `P10-L07`
- surveyed commit: `e42103fc02f544e1bd23a5ec2e5b584734f5af7d`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: survey manifest, dedicated survey gate, the shared Phase 10 core, input, and MMIO packet guards, the shared core, ring, input, and MMIO survey manifests, the shared tests-root review companion, shared Phase 10 build wiring, the shared reset-queue, driver-id, and input status-drain replays, the Linux-style replay route, and a lane-level note that records the current landed ring and adjacent MMIO footholds plus the remaining transport-facing gap against the roadmap
- product boundary:
  - `zigux/tests/phase10_virtio_ring_manifest.json`
  - `zigux/tests/phase10_virtio_ring_survey.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`
  - `Documentation/zigux/phase10-virtio-ring-slice.md`
  - `Documentation/zigux/phase10-virtio-ring-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_ring.c` as a primary anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo already has a bounded `drivers/virtio/virtio.zig` core starter with queue callback bookkeeping, descriptor-shape metadata, and notification accounting. This survey started by making the missing ring-helper gap explicit, and it now records that the first `drivers/virtio/virtio_ring.zig` lab slice has landed plus small used-buffer polling, callback re-enable, delayed-callback pacing, broken-queue discipline follow-ups, a reset-readiness preflight, and notify-prepare bookkeeping without pretending queue lifecycle parity is complete. The adjacent MMIO packet has also advanced beyond an older register-window-only foothold and now records bounded queue-size, feature-word, config-window, config-write-plan, config-write-disposition, and probe-preflight helpers as landed, alongside the shorter-restage stale-data replay proof.

## Survey findings

- `drivers/virtio/virtio_ring.c` is present on `master` at 3940 lines and spans split rings, packed rings, descriptor state, DMA mapping helpers, callback toggling, notification bookkeeping, queue reset, resize, and break or unbreak handling.
- the live repo already ships `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, `zigux/tests/phase10_virtio_ring_survey.zig`, `zigux/tests/phase10_virtio_input.zig`, `zigux/tests/phase10_virtio_input_manifest.json`, `zigux/tests/phase10_virtio_input_survey.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `zigux/tests/phase10_virtio_mmio_survey.zig`, `zigux/tests/phase10_build.zig`, `Documentation/zigux/phase10-virtio-core-slice.md`, `Documentation/zigux/phase10-virtio-core-survey.md`, `Documentation/zigux/phase10-virtio-ring-slice.md`, `Documentation/zigux/phase10-virtio-input-slice.md`, `Documentation/zigux/phase10-virtio-input-module-slice.md`, `Documentation/zigux/phase10-virtio-input-survey.md`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, and `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`.
- the current Zigux VirtIO ring surface now includes a bounded `drivers/virtio/virtio_ring.zig` helper for queue registration, layout metadata, outstanding-chain accounting, used-buffer polling, callback re-enable bookkeeping, delayed-callback pacing, broken-queue discipline that blocks fresh publish, kick, poll, and callback snapshots, a reset-readiness preflight, and notify-prepare bookkeeping.
- the live Phase 10 packet now also records the adjacent `drivers/virtio/virtio_mmio.zig` footholds as landed: a tiny register window, queue-size staging, one bounded feature-word selector and read window, one small config-word window rooted in staged MMIO config bytes, one bounded config-write-plan summary that keeps config mutations out of scope, one bounded config-write-disposition summary that reports the changed-byte mask and prepared window end offset without mutating config space, and one bounded probe-preflight summary for the earliest `virtio_mmio_probe()`-style checks. The dedicated MMIO replay also proves that a shorter restaged config window clears stale second-word data instead of leaving old bytes readable.
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
- the landed `phase10-notify-prepare-helper`
- the landed `phase10-broken-queue-poll-guard`
- the landed `phase10-queue-reset-readiness-helper`
- the landed `phase10-mmio-register-window-helper`
- the landed `phase10-mmio-queue-size-helper`
- the landed `phase10-mmio-feature-word-selector-helper`
- the landed `phase10-mmio-config-window-helper`
- the landed `phase10-mmio-config-write-plan-helper`
- the landed `phase10-mmio-config-write-disposition-helper`
- the landed `phase10-mmio-probe-preflight-helper`
- the still-blocked `phase10-mmio-lifecycle-and-irq-paths`
- the landed `phase10-virtio-ring-slice-note`

This keeps the lane concrete and reviewable without overstating `virtio_ring` progress: the queue-shape foothold is real, used-buffer polling, callback re-enable, delayed-callback pacing, notify-prepare bookkeeping, broken-queue discipline, the reset-readiness preflight, and the bounded MMIO register, queue-size, feature-word, config-window, config-write-plan, config-write-disposition, and probe-preflight helpers are all landed, with the shorter-restage stale-data replay keeping that adjacent MMIO packet honest, and the risky transport-facing lifecycle work is still intentionally blocked. That blocked MMIO lifecycle and IRQ follow-up remains owned by the adjacent `virtio_mmio` packet plus the dedicated `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, and `scripts/zigux/check-phase10-mmio-packet.py` guards, the four shipped survey manifests, the shared tests-root review companion, the shared `zigux/tests/phase10_build.zig` and `zigux/Makefile` replay surface, the shared `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig` replays, and the Linux-style `make -C zigux phase10-test` and `make -C zigux phase10` routes, not by this queue-local ring survey note.

## Freeze boundary

- `Documentation/zigux/freeze-map.md` is the governing boundary note for this queue-local survey packet.
- freeze-boundary owner: `P10-L10`
- rollback owner: keep the shared `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, and `scripts/zigux/check-phase10-mmio-packet.py` guards plus the four shipped survey manifests, the shared tests-root review companion, the shared `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, `zigux/tests/phase10_virtio_input_status_drain.zig`, and `zigux/Makefile` replay routes aligned, including `make -C zigux phase10-test` and `make -C zigux phase10`, before widening this queue-local note.
- this ring survey stays inside `drivers/virtio/*.zig`; it does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain Phase 14 study-only anchors under the freeze map.
- the allowed evidence here is the ring survey note, its manifest, its focused survey gate, the shared `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-input-packet.py`, and `scripts/zigux/check-phase10-mmio-packet.py` guards, the four shipped survey manifests, the shared tests-root review companion, the shared `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_driver_id.zig`, and `zigux/tests/phase10_virtio_input_status_drain.zig` replays, the Linux-style `make -C zigux phase10-test` and `make -C zigux phase10` replay routes, and the roadmap-backed destination boundary through `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`; this survey does not claim a freeze-map status change or an attached Architecture Council reopen request.

## Non-goals

This survey slice does not yet claim:

- real split-ring or packed-ring descriptor parity
- DMA mapping or unmapping wrappers
- `virtqueue_add_*`, `virtqueue_get_buf`, or `vring_interrupt` lifecycle behavior
- `virtio_mmio.c` transport glue beyond the already-landed bounded helper windows

## Gates

1. run the dedicated ring survey gate
- `zig test zigux/tests/phase10_virtio_ring_survey.zig`

2. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig`

3. run the Linux-style Phase 10 test entrypoints
- `make -C zigux phase10-test`
- `make -C zigux phase10`

Taken together, these gates keep the bounded virtqueue-wrapper packet reviewable through the dedicated ring-survey replay, the direct build replay, the shipped Phase 10 core, input, and MMIO packet guards behind `make -C zigux phase10-test`, and the Linux-style Phase 10 test entrypoints on `master`.

## Next bounded step

Keep the broader Phase 10 virtio lane parked unless fresh repo inspection finds another one-file or tightly coupled survey, manifest, slice-note, or helper-test truthfulness repair before widening into interrupt acknowledgement, reset, queue discovery, or probe lifecycle work.
