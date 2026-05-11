# Phase 12 Virtio Net Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/net/virtio_net.c`.

## Status

- `PHASE12_STATUS=parked`
- `PHASE12_SLICE=virtio-net-survey`
- scope: verify whether current `master` still carries a bounded `virtio_net` Zig starter, direct smoke shard, and survey-backed replay packet
- verified head: `2ad1529777a86b7b00576de9e6925b7b78d8e9cf`
- repo-truth boundary:
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `zigux-alpha/ZAR_TO_ZIGUX_PRODUCT_ROADMAP.md`
  - `zigux-alpha/BOOTSTRAP_COMMIT_LEDGER.md`
- public fallback posture: shared-tree-only anchor; unlike `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, this `virtio_net` note is not a commit-pinned raw GitHub fallback artifact.

## Why this lane still matters

The Phase 12 roadmap still names `drivers/net/virtio_net.c` as a complex production-driver target.

That anchor is still high value because `virtio_net.c` is a large production driver with probe-time negotiation, virtqueue management, recovery decisions, receive and transmit coordination, control-virtqueue work, RSS state, and full `net_device` lifecycle handling. The roadmap therefore still requires DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout before any honest live data-path claim.

## Current-master verification

- current `master` still carries the earlier Phase 10 virtio groundwork in `drivers/virtio/virtio.zig`, `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_input.zig`, and `zigux/tests/phase10_build.zig`
- current `master` does not carry `drivers/net/virtio_net.zig`
- current `master` does not carry `zigux/tests/phase12_virtio_net.zig`
- current `master` does not carry `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- current `master` does not carry `zigux/tests/phase12_virtio_net_survey.zig`
- current `master` does not carry `zigux/tests/phase12_virtio_net_manifest.json`
- current `master` does not carry `zigux/tests/phase12_build.zig`
- `python3 scripts/zigux/check-build-only-phase12-surface.py` currently fails and reports the entire shared Phase 12 replay packet as missing, including every virtio-net file named above

Those checks mean the present lane has no live compile target, no direct smoke shard, and no bounded recovery replay surface to execute. On current `master`, compile, throughput, and recovery verification for the old virtio-net packet stop at repo-truth inspection rather than runnable Zig validation.

## Truthful boundary

The older survey wording that described a landed `drivers/net/virtio_net.zig` probe starter, direct syntax-lab replay, repeated recovery-cycle evidence, and a ready-next transmit-recycle follow-up is not current-master truth today.

The truthful current boundary is narrower:

- the roadmap still wants a bounded `virtio_net` lane in Phase 12
- the Phase 10 virtio foundation still exists and remains the nearest reusable substrate
- the earlier Phase 12 virtio-net packet is absent from `HEAD`
- throughput and recovery parity remain blocked not only by roadmap requirements, but also by the absence of any current driver-local Zig packet to verify

## Non-goals

This note does not claim:

- a current `virtio_net` Zig compile target
- a current direct smoke shard for `virtio_net`
- a current survey-backed recovery replay
- transmit-recycle, refill-loop, or control-queue restore behavior on live `master`
- NAPI, page-pool DMA, XDP, XSK, control-virtqueue command traffic, RSS table programming, or `net_device` lifecycle parity

## Next bounded step

If this lane reopens, the next honest same-lane move is not a new recovery or throughput follow-up.

The next bounded step is:

1. reland a minimal `drivers/net/virtio_net.zig` probe-snapshot starter
2. reland the matching direct test packet under `zigux/tests/phase12_virtio_net*.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_build.zig`
3. rerun `python3 scripts/zigux/check-build-only-phase12-surface.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12` before reopening any transmit-recycle, throughput, or recovery wording

Until that reland happens, keep this lane parked and treat any stronger compile, throughput, or recovery claim as overstated.
