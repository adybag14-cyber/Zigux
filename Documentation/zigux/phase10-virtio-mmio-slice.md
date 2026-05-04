# Phase 10 Virtio MMIO Slice

This document tracks the bounded `drivers/virtio/virtio_mmio.c` lab helper under Phase 10.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_SLICE=virtio-mmio-probe-preflight-helper`
- scope: bounded MMIO register offsets, transport-identity snapshots, probe-preflight summaries, device-feature page selection, driver-feature page writes, queue-select and queue-size planning, queue-ready bookkeeping, queue-notify snapshots, version-scoped queue-address planning, read-only config-window snapshots, in-memory config-write planning, bounded interrupt-state summaries, status and reset bookkeeping, config-generation tracking, interrupt-status acknowledge bookkeeping, focused multi-queue state-isolation coverage, dedicated Phase 10 MMIO tests, and a slice note only
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/Makefile`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio_mmio.c` as a primary transport anchor, but it also says to prove virtqueue wrappers before widening into MMIO or other risky transport work.

The live repo now has the virtio core, ring, and input lab footholds plus the earlier MMIO survey lane. This slice now records a small transport-identity snapshot plus a bounded probe-preflight summary alongside the landed interrupt-state summary and interrupt-ack rung after the earlier config-write helper, keeping the reviewable magic, version, device-id, vendor-id, and earliest probe-handoff gate explicit in memory without pretending to own shared IRQ delivery, queue setup, probe and remove lifecycle, or DMA-facing transport work.

## Landed starter surface

- module descriptor metadata anchored to `drivers/virtio/virtio_mmio.c`
- bounded register-offset constants for the device-features, driver-features, guest-page-size, queue-select, queue-size, queue-ready, queue-notify, queue-address, interrupt, status, and config-generation window
- transport-identity snapshots that keep the MMIO magic value, transport version support, device-id presence, and vendor-id bookkeeping reviewable without claiming probe parity
- probe-preflight summaries that keep the earliest magic, version, device, vendor, legacy guest-page-size intent, queue-register-window readiness, interrupt-ack readiness, and ready-for-probe-handoff checks reviewable without claiming real probe lifecycle behavior
- device-feature page selection and readback for the low and high 32-bit feature pages
- driver-feature page selection and write bookkeeping for the same bounded two-page feature window
- queue selection and queue-register summaries for a tiny in-memory queue window
- queue-size planning that rejects zero, unavailable, and out-of-range queue sizes and refuses resize while the selected queue is already ready
- queue-ready writes that require a configured queue size first and stay in-memory only
- queue-notify snapshots that require a configured ready queue, return the selected queue identity, and count in-memory notify events without claiming device-side side effects
- version-scoped queue-address planning that records either legacy guest-page-size, queue-align, and queue-PFN values or modern DESC, AVAIL, and USED addresses while the queue is configured but not yet ready
- focused queue-isolation coverage that switches between two queue slots and proves the first queue's legacy plan, the second queue's modern plan, and the shared notify counter stay isolated and reviewable across queue selection changes
- read-only config-window snapshots that return a bounded byte, halfword, or word from a tiny in-memory config window together with the current config-generation
- in-memory config-write planning that records previous and planned byte, halfword, and word values for bounded config-window updates without claiming device-side application
- bounded interrupt-state summaries that record whether queue and config interrupt bits are pending, whether the line would still read asserted, and which bits remain after explicit acknowledgements
- explicit status writes that reject reset-through-the-wrong-path and keep reset on its own helper branch
- dedicated reset bookkeeping that clears in-memory queue size, queue ready state, queue notify counts, queue-address planning state, and pending bounded interrupt bits without claiming queue teardown or IRQ-delivery parity
- in-memory config-generation snapshots and increment bookkeeping
- interrupt-status bookkeeping plus bounded interrupt acknowledge behavior for the reviewable queue and config interrupt bits only
- dedicated Phase 10 tests and build wiring for the helper

The same parked MMIO packet also participates in the shared closure evidence bundle through `Documentation/zigux/phase10-closure-evidence.md`, `zigux/tests/phase10_closure_manifest.json`, and `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`, so the current review path is broader than the dedicated MMIO test alone even though the landed helper surface remains transport-local.

## Ownership handoff

This slice note owns only the driver-local review surface that is already landed in `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`, `zigux/tests/phase10_build.zig`, and `zigux/Makefile`.

The still-blocked `phase10-mmio-lifecycle-and-irq-paths` follow-up remains owned by the adjacent survey and shared closure packet until a future run can split another transport-safe observation helper out of that broader transport mix:

- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `zigux/tests/phase10_virtio_mmio_survey.zig`
- `Documentation/zigux/phase10-closure-evidence.md`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`

This keeps the driver-local slice note from implying ownership of shared IRQ delivery, queue setup, probe, remove, or DMA-facing transport claims just because the bounded probe-preflight, interrupt-state, and interrupt-ack rungs are now landed.

## Non-goals

This slice does not yet claim:

- real MMIO pointer reads or writes
- queue setup and teardown parity
- full queue-address programming side effects across legacy PFN or modern DESC, AVAIL, and USED windows
- full config-space write parity or device-side application through `VIRTIO_MMIO_CONFIG`
- full config-field parity across the broader transport surface
- shared IRQ delivery, interrupt-handler parity, or transport-backed interrupt masking
- probe, remove, freeze, restore, or command-line device creation parity
- DMA-facing virtqueue setup, teardown, or interrupt delivery

## Gates

1. run the shared closure inventory gate
- `python3 scripts/zigux/check-phase10-closure-inventory.py`

2. run the dedicated validation guards
- `python3 scripts/zigux/validate-phase10-closure.py`
- `python3 scripts/zigux/check-phase10-harness-coverage.py`
- `make -C zigux phase10-validate`

3. run the dedicated Phase 10 build
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`

4. run the Linux-style Phase 10 test entrypoint
- `make -C zigux phase10-test`

This keeps the MMIO slice note aligned with the shared closure packet's exact test route instead of implying the direct build replay and convenience target are the only executable review surfaces for the current MMIO packet.

5. run the convenience target
- `make -C zigux phase10`

## Next bounded step

Leave the MMIO lane parked unless a future inspection can split the remaining `phase10-mmio-lifecycle-and-irq-paths` blocker into another transport-safe observation helper beyond this transport-identity plus probe-preflight packet, without claiming queue setup, shared IRQ delivery, probe, or remove parity.
