# Phase 12 NVMe PCI Slice

This bounded Phase 12 slice adds the first Zigux `nvme pci` starter anchored to `drivers/nvme/host/pci.c`.

The starter stays intentionally narrow:

- validates queue depth, SQ entry size, page size, and doorbell stride for a lab-only queue pair planner
- negotiates a bounded controller-versus-planner I/O queue count summary and can reserve that queue-id window in one checked batch before any live queue creation, so the packet can stay honest about controller queue caps versus the starter's own queue-id window
- computes total queue footprint plus host-side DMA demand, including the reduced host-memory pressure when a submission queue is planned in CMB, without claiming real DMA mapping or PRP setup
- assigns monotonic admin and I/O queue identifiers with predictable SQ and CQ doorbell offsets
- freezes queue planning during reset and clears planned I/O queue numbering only after reset completion
- can replay one stale reserved I/O queue window after reset by renegotiating the cached queue-id batch against the current controller cap, without claiming live queue creation, blk-mq mapping, or PCI transport recovery
- records one bounded PRP buffer shape by capturing first-page offset, first PRP coverage, rounded span, tail-page count, and chained PRP-list layout details such as descriptor-page count, link entries, and the final page's entry shape, without constructing live PRP lists or touching submission flow
- records one bounded PRP metadata helper by quantifying command-inline data pointers, PRP-list-covered pages, chained descriptor-page count, extra descriptor DMA footprint, total DMA bytes, and reset-time descriptor rebuild need without claiming live PRP allocation or DMA mapping
- records one bounded recovery replay helper by reporting reset-generation staleness for cached PRP metadata, admin-queue replay need, dropped I/O queue rebuild count, and post-reset queue numbering without claiming live timeout recovery, IRQ routing, or hardware-backed reset transport
- can now retire part of the dropped-I/O backlog after reset once the admin queue has been replayed and replacement queue plans have been made, while keeping that retirement as bookkeeping rather than claiming live queue creation or recovery completion

Ownership boundary:
- `P12-L05` owns only the queue-planning, queue-count reservation, queue-reservation replay, PRP buffer-shape, PRP metadata, and recovery replay starter surface
- blocked DMA and recovery transport work stays outside this starter and remains owned by the broader Phase 12 transport substrate until the roadmap explicitly approves a deeper follow-up
- bounded backlog retirement is still recovery-governance bookkeeping, not proof of DMA-safe transport parity, blk-mq parity, or shared Phase 12 recovery closure

This slice does not claim PCI probe or remove wiring, interrupt registration, controller enable or shutdown sequences, live MMIO, PRP list construction, blk-mq integration, tagset setup, or hardware-backed recovery.

The shared Phase 12 packet now keeps the direct smoke preflight explicit here too: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12-smoke` rerun this bounded `nvme pci` starter together with the focused `drivers/nvme/host/pci_verify.zig` shard before the broader survey-backed replay, so the slice should stay aligned with that smoke-plus-build order instead of leaving it implicit in `zigux/tests/phase12_build.zig`, `zigux/Makefile`, or `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` alone.

The next honest bounded step inside the same Phase 12 lane is to keep the packet parked unless a same-driver reopen lands one explicitly approved transport-facing descriptor, queueing, or recovery preflight that builds on the now-landed queue-planning, queue-count reservation, queue-reservation replay, PRP buffer-shape, PRP metadata, recovery replay, and rebuild-progress helpers without widening into live DMA mapping, blk-mq, or PCI lifecycle work.
