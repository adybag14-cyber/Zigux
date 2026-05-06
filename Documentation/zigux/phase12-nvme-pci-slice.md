# Phase 12 NVMe PCI Slice

This bounded Phase 12 slice adds the first Zigux `nvme pci` starter anchored to `drivers/nvme/host/pci.c`.

The starter stays intentionally narrow:

- validates queue depth, SQ entry size, page size, and doorbell stride for a lab-only queue pair planner
- computes total queue footprint plus host-side DMA demand, including the reduced host-memory pressure when a submission queue is planned in CMB, without claiming real DMA mapping or PRP setup
- assigns monotonic admin and I/O queue identifiers with predictable SQ and CQ doorbell offsets
- freezes queue planning during reset and clears planned I/O queue numbering only after reset completion
- records one bounded PRP buffer shape by capturing first-page offset, first PRP coverage, rounded span, tail-page count, and PRP list bound checks without constructing live PRP lists or touching submission flow
- records one bounded PRP metadata helper by quantifying command-inline data pointers, PRP-list-covered pages, extra descriptor DMA footprint, total DMA bytes, and reset-time descriptor rebuild need without claiming live PRP allocation or DMA mapping

Ownership boundary:
- `P12-Y02` owns only the queue-planning, PRP buffer-shape, and PRP metadata starter surface
- blocked DMA and recovery transport work stays outside this starter and remains owned by the broader Phase 12 transport substrate until the roadmap explicitly approves a deeper follow-up

This slice does not claim PCI probe or remove wiring, interrupt registration, controller enable or shutdown sequences, live MMIO, PRP list construction, blk-mq integration, tagset setup, or hardware-backed recovery.

The shared Phase 12 packet now keeps the direct smoke preflight explicit here too: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all` and `make -C zigux phase12-smoke` rerun this bounded `nvme pci` starter before the broader survey-backed replay, so the slice should stay aligned with that smoke-plus-build order instead of leaving it implicit in `zigux/tests/phase12_build.zig`, `zigux/Makefile`, or `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` alone.

The next honest bounded step inside the same Phase 12 lane is to keep the packet parked until an explicitly approved transport-facing follow-up is ready beyond the now-landed queue-planning, PRP buffer-shape, and PRP metadata helpers, without widening into live DMA mapping, blk-mq, or PCI lifecycle work.
