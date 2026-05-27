# Phase 10 Virtio Net Slice

Scope:
- bounded `drivers/net/virtio_net.zig` lab-driver work for probe-time queue layout and mergeable receive-buffer planning
- focused `zigux/tests/phase10_virtio_net.zig` coverage wired through the shared `zigux/tests/phase10_build.zig` entrypoint

Current starter:
- `VirtioNetProbeLab.captureProbeSnapshot()` keeps the existing queue-pair negotiation, control-queue index, and recovery posture in memory only
- `VirtioNetProbeLab.planMergeableReceiveBuffer()` now mirrors the bounded `get_mergeable_buf_len()` and `add_recvbuf_mergeable()` planning rules from `drivers/net/virtio_net.c` without entering DMA, page-pool allocation, skb ownership, NAPI poll, or netdev registration work
- the new helper records aligned room, requested receive-buffer length, requested allocation length, and whether the plan is using recycled room from a prior mergeable refill step
- `VirtioNetProbeLab.summarizeReceiveQueueRefill()` now turns the last bounded mergeable-buffer plan into an explicit refill-path summary so the lab slice can distinguish fresh mergeable allocation from recycled-room reuse without widening into page ownership or receive completion
- `VirtioNetProbeLab.planReceiveQueueRefillBatch()` now turns that same bounded refill summary into queue-slot and byte counts for one refill pass, including a clampable batch limit and a fail-closed overfill guard, without widening into DMA submission, kicks, or receive completion
- `VirtioNetProbeLab.reserveReceiveQueueRefillDescriptors()` now clamps one refill pass against the descriptors currently available on the receive queue, yielding one bounded reservation plan with pending-buffer carryover while still stopping short of live descriptor writes, DMA submission, or queue kicks
- `VirtioNetProbeLab.decideReceiveQueueRefillNotify()` now turns that bounded reservation plan into a queue-local notify decision that can trigger on empty-queue transitions or descriptor thresholds while still stopping short of live descriptor writes, DMA submission, or queue kicks

Validation:
- `zig build phase10-virtio-net-tests --build-file zigux/tests/phase10_build.zig --summary all`
- the shared Phase 10 gate now includes `phase10-virtio-net-tests` beside the existing virtio core, ring, input, and survey checks

Non-goals:
- live DMA or `page_pool_alloc_va()` integration
- skb construction or receive completion
- NAPI callback scheduling
- netdev lifecycle or transport reset recovery
