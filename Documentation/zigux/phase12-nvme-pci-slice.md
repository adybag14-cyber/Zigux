# Phase 12 NVMe PCI Slice
This bounded Phase 12 slice adds the first Zigux `nvme pci` starter anchored to `drivers/nvme/host/pci.c`.

The starter stays intentionally narrow:
- validates queue depth, SQ entry size, page size, and doorbell stride for a lab-only queue pair planner
- computes total queue footprint plus host-side DMA demand, including the reduced host-memory pressure when a submission queue is planned in CMB, without claiming real DMA mapping
- assigns monotonic admin and I/O queue identifiers with predictable SQ and CQ doorbell offsets
- freezes queue planning during reset and clears planned I/O queue numbering only after reset completion
- records one tiny PRP buffer-shape summary with first-page offset, rounded span, and page-list bound checks without claiming live PRP chaining or DMA mapping
- records one tiny PRP metadata helper with command-inline data pointers, PRP-list-covered pages, extra descriptor DMA footprint, and reset-time descriptor rebuild need without claiming live PRP allocation or DMA mapping

This slice does not claim PCI probe or remove wiring, interrupt registration, controller enable or shutdown sequences, live MMIO, PRP or SGL descriptor allocation, blk-mq integration, tagset setup, or hardware-backed recovery.

The next honest bounded step inside the same Phase 12 lane is to keep the lane parked until the roadmap approves a transport-facing follow-up beyond the queue planner, PRP buffer-shape helper, and PRP metadata helper.
