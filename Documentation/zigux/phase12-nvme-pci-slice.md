# Phase 12 NVMe PCI Slice

This bounded Phase 12 slice adds the first Zigux `nvme pci` starter anchored to `drivers/nvme/host/pci.c`.

The starter stays intentionally narrow:

- validates queue depth, SQ entry size, page size, and doorbell stride for a lab-only queue pair planner
- computes SQ and CQ byte counts plus rounded DMA page demand without claiming real DMA mapping or PRP setup
- assigns monotonic admin and I/O queue identifiers with predictable SQ and CQ doorbell offsets
- freezes queue planning during reset and clears planned I/O queue numbering only after reset completion

This slice does not claim PCI probe or remove wiring, interrupt registration, controller enable or shutdown sequences, live MMIO, PRP list construction, blk-mq integration, tagset setup, or hardware-backed recovery.

The next honest bounded step inside the same Phase 12 lane is to add one tiny PRP-or-SGL-facing buffer-shape helper or a narrow admin-timeout recovery summary before any live DMA or blk-mq behavior is attempted.
