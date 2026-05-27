# Phase 12 Virtio Net Syntax Lab

`PHASE12_STATUS=standalone-syntax-lab-smoke-present`
`PHASE12_LANE=P12-L06`

This bounded Phase 12 syntax lab keeps `virtio_net` reviewability focused on compile-smoke evidence built from the helper surfaces already present on current `master`. It composes the existing `virtio` core, queue-resume, receive-refill replay, transmit-recycle, post-reset replay, and throughput-parity helpers without widening into DMA-safe receive ownership, page-pool refill execution, transport-backed submission, interrupt-backed completion handling, or full `net_device` lifecycle work.

Current standalone syntax-lab surface:

- `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- `zigux/tests/phase12_virtio_net_syntax_lab_build.zig`
- `drivers/virtio/virtio.zig`
- `drivers/net/virtio_net_queue_resume.zig`
- `drivers/net/virtio_net_receive_refill_replay.zig`
- `drivers/net/virtio_net_transmit_recycle.zig`
- `drivers/net/virtio_net_post_reset_replay.zig`
- `drivers/net/virtio_net_throughput_parity.zig`

Focused validation route:

- `zig build smoke --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all`
- `zig build test --build-file zigux/tests/phase12_virtio_net_syntax_lab_build.zig --summary all`
- `make -C zigux phase12-virtio-net-syntax-lab-test`

Current `master` exposes only the dedicated standalone test wrapper; smoke remains the direct build-file route so the shared Phase 12 sextet stays unchanged.

The shared `phase12` smoke-and-test sextet remains unchanged; this lab is a separate compile-smoke packet that proves three bounded properties:

- refill replay still blocks queue resume until restore budgets are back in range
- transmit recycle and post-reset ownership remain review-only until probe replay clears
- throughput parity stays in compile-smoke territory once the bounded replay cues line up