# Phase 12 Virtio Net Syntax Lab

`PHASE12_STATUS=syntax-lab-smoke-present`
`PHASE12_LANE=P12-L06`

This bounded Phase 12 syntax lab keeps roadmap-aligned `virtio_net` reviewability focused on compile-smoke evidence rather than runtime claims. The lab exercises header scatter selection, control-queue payload shaping, and queue-freeze or restore recovery summaries through `drivers/net/virtio_net.zig` without claiming live DMA-safe receive ownership, NAPI execution, page-pool refill loops, XDP or XSK flow, interrupt-backed completion handling, or `net_device` lifecycle coverage.

Current compile-smoke surface:

- `drivers/virtio/virtio.zig`
- `drivers/net/virtio_net.zig`
- `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- `zigux/tests/phase12_build.zig`
- `zigux/Makefile`

Focused validation route:

- `make -C zigux phase12-smoke`
- `make -C zigux phase12-test`

The syntax lab proves three bounded properties that match the Phase 12 roadmap's queueing-correctness and segmented-rollout discipline:

- control-queue payload shaping stays separate from runtime control command submission
- RSS payload shaping stays aligned with tunnel-header recovery summaries
- `VIRTIO_F_ANY_LAYOUT` and `VIRTIO_F_VERSION_1` header-scatter choices remain reviewable without widening into transport execution
