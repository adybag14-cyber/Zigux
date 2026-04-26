# Phase 10 Virtio Input Module Slice

This bounded Phase 10 slice adds the first Zigux `virtio_input` lab driver starter anchored to `drivers/virtio/virtio_input.c`.

The starter stays intentionally narrow:

- snapshots the input identity/config surface around name, serial, phys, and device ids
- records bounded property-bit, event-bit, and ABS metadata summaries from the `virtio_input_config` surface
- models the fixed two-queue plan used by the Linux driver: events and status
- caps prequeued event buffers to the static 64-entry event pool used by the C driver
- keeps status sending in-memory only and suppresses `EV_MSC` plus `MSC_TIMESTAMP` loops when multitouch forwarding is enabled

This slice does not claim MMIO transport work, DMA-facing queue plumbing, input core capability registration, transport-backed config reads, or probe and remove lifecycle parity yet.

The next honest bounded step inside the same lane is to widen the lab model from config snapshots into capability-setup staging that can connect the recorded bitmap and ABS metadata to bounded `input_set_capability()` and `input_set_abs_params()` intent, while still avoiding MMIO and broader transport glue.
