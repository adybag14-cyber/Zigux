# Phase 10 Virtio Net Slice

Scope:
- bounded `drivers/net/virtio_net.zig` lab-driver work for probe-time queue layout and mergeable receive-buffer planning
- focused `zigux/tests/phase10_virtio_net.zig` coverage wired through the shared `zigux/tests/phase10_build.zig` entrypoint

Current starter:
- `VirtioNetProbeLab.captureProbeSnapshot()` keeps the existing queue-pair negotiation, control-queue index, and recovery posture in memory only
- `VirtioNetProbeLab.planMergeableReceiveBuffer()` now mirrors the bounded `get_mergeable_buf_len()` and `add_recvbuf_mergeable()` planning rules from `drivers/net/virtio_net.c` without entering DMA, page-pool allocation, skb ownership, NAPI poll, or netdev registration work
- the new helper records aligned room, requested receive-buffer length, requested allocation length, and whether the plan is using recycled room from a prior mergeable refill step

Validation:
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`
- the shared Phase 10 gate now includes `phase10-virtio-net-tests` beside the existing virtio core, ring, input, and survey checks

Non-goals:
- live DMA or `page_pool_alloc_va()` integration
- skb construction or receive completion
- NAPI callback scheduling
- netdev lifecycle or transport reset recovery
