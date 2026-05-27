# Phase 12 Virtio Net Throughput Parity Slice

This note records one bounded Validation and Perf packet for the current Phase 12 `virtio_net` throughput-parity replay.

## Status

- `PHASE12_THROUGHPUT_PARITY_STATUS=helper-local-packet-present`
- lane owner: `P12-L04`
- scope: keep the review-only throughput parity helper and isolated replay explicit without widening into measured transport throughput, DMA-safe receive ownership, or interrupt-backed runtime completion claims
- anchor: `drivers/net/virtio_net.c`

## Packet

- `drivers/net/virtio_net_throughput_parity.zig`
- `zigux/tests/phase12_virtio_net_throughput_parity.zig`
- `zigux/tests/fixtures/phase12_virtio_net_throughput_parity_manifest.json`
- `scripts/zigux/check-phase12-virtio-net-throughput-parity-packet.py`

## Routes

- `python3 scripts/zigux/check-phase12-virtio-net-throughput-parity-packet.py --self-test`
- `python3 scripts/zigux/check-phase12-virtio-net-throughput-parity-packet.py --root .`
- `zig build phase12-virtio-net-throughput-parity --build-file zigux/tests/phase12_build.zig --summary all`
- `make -C zigux phase12-virtio-net-throughput-parity-test`

## Boundaries

- The helper keeps the bounded ratio, receive-refill readiness, transmit-recycle readiness, and post-reset replay checkpoint reviewable.
- It does not claim live transport execution, measured wire throughput, DMA-safe receive ownership, or interrupt-backed completion evidence.
- Future same-lane follow-through should stay narrowed to measured transport throughput replay or runtime completion only if this helper-local packet drifts on `master`.
