# Phase 12 NVMe PCI Slice

This bounded Phase 12 slice adds the first Zigux `nvme pci` starter anchored to `drivers/nvme/host/pci.c`.

The starter stays intentionally narrow:

- validates queue depth, SQ entry size, page size, and doorbell stride for a lab-only queue pair planner
- computes total queue footprint plus host-side DMA demand, including the reduced host-memory pressure when a submission queue is planned in CMB, without claiming real DMA mapping or PRP setup
- assigns monotonic admin and I/O queue identifiers with predictable SQ and CQ doorbell offsets
- freezes queue planning during reset and clears planned I/O queue numbering only after reset completion
- records one bounded PRP buffer shape by capturing first-page offset, first PRP coverage, rounded span, tail-page count, and PRP list bound checks without constructing live PRP lists or touching submission flow

This slice does not claim PCI probe or remove wiring, interrupt registration, controller enable or shutdown sequences, live MMIO, PRP list construction, blk-mq integration, tagset setup, or hardware-backed recovery.

The next honest bounded step inside the same Phase 12 lane is to keep the packet parked until an explicitly approved transport-facing follow-up is ready beyond the now-landed queue-planning and PRP-shape helpers, without widening into live DMA mapping, blk-mq, or PCI lifecycle work.
