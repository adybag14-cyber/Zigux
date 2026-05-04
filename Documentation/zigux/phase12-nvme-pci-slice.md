# Phase 12 NVMe PCI Slice

This bounded Phase 12 slice adds the first Zigux `nvme pci` starter anchored to `drivers/nvme/host/pci.c`.

The starter stays intentionally narrow:

- validates queue depth, SQ entry size, page size, and doorbell stride for a lab-only queue pair planner
- negotiates a bounded controller-versus-planner I/O queue count summary before any live queue creation, so the packet can stay honest about controller queue caps versus the starter's own queue-id window
- computes total queue footprint plus host-side DMA demand, including the reduced host-memory pressure when a submission queue is planned in CMB, without claiming real DMA mapping or PRP setup
- assigns monotonic admin and I/O queue identifiers with predictable SQ and CQ doorbell offsets
- records one tiny doorbell-window helper that summarizes the bounded SQ and CQ register aperture across the admin queue and already-planned I/O queue pairs, including reset visibility, without claiming live MMIO or IRQ routing
- records one tiny queue-recovery replay helper with capped I/O queue replay, preserved admin geometry, aggregate host DMA demand, and reset-frozen visibility without claiming live queue recreation, MMIO, or IRQ-backed completion flow
- freezes queue planning during reset and clears planned I/O queue numbering only after reset completion
- records one tiny PRP buffer-shape summary with first-page offset, rounded span, and page-list bound checks without claiming live PRP chaining or DMA mapping
- records one tiny PRP metadata helper with command-inline data pointers, PRP-list-covered pages, extra descriptor DMA footprint, and reset-time descriptor rebuild need without claiming live PRP allocation or DMA mapping
- records one tiny PRP-versus-SGL selection summary around admin-versus-I/O queues, page-gap forcing, user-command forcing, integrity-segment forcing, and average-segment threshold preference without claiming live descriptor allocation or DMA mapping

This slice does not claim PCI probe or remove wiring, interrupt registration, controller enable or shutdown sequences, live MMIO, PRP or SGL descriptor allocation, blk-mq integration, tagset setup, or hardware-backed recovery.

The next honest bounded step inside the same Phase 12 lane is now to keep the lane parked on survey or validation evidence until the roadmap-approved DMA-safe transport substrate exists for a truthful follow-up beyond the queue planner, queue-count helper, doorbell-window helper, queue-recovery replay helper, PRP buffer-shape helper, PRP metadata helper, and pointer-selection helper.
