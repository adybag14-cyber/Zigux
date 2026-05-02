# Phase 12 Virtio Net Raw GitHub Fallback Map

This note records the smallest public-read fallback packet for lane `P12-L04`.

It does not claim a live-head replay catalog. It only maps the archived Phase 12 virtio_net survey packet to stable GitHub tree views and raw blob URLs pinned to `c23f1e76c2c0cdb2526d252689e68cc4dbee505d`.

The map exists so future scheduled runs can recover the bounded `virtio_net` survey surface when connector-backed reads are flaky, without borrowing the storage-lane fallback notes or overstating current-head validation.

## Scope

- `PHASE12_LANE_KEY=P12-L04`
- `PHASE12_SURVEYED_COMMIT=c23f1e76c2c0cdb2526d252689e68cc4dbee505d`
- bounded packet:
  - `drivers/net/virtio_net.c`
  - `drivers/net/virtio_net.zig`
  - `zigux/tests/phase12_virtio_net.zig`
  - `zigux/tests/phase12_virtio_net_manifest.json`
  - `zigux/tests/phase12_virtio_net_survey.zig`
  - `zigux/tests/phase12_virtio_net_syntax_lab.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `scripts/zigux/validate-phase12.py`
  - `zigux/Makefile`

## Tree Readback Roots

- `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/net`
- `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`
- `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`

## Raw Pinned URLs

- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/c23f1e76c2c0cdb2526d252689e68cc4dbee505d/drivers/net/virtio_net.c`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/c23f1e76c2c0cdb2526d252689e68cc4dbee505d/drivers/net/virtio_net.zig`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/c23f1e76c2c0cdb2526d252689e68cc4dbee505d/zigux/tests/phase12_virtio_net.zig`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/c23f1e76c2c0cdb2526d252689e68cc4dbee505d/zigux/tests/phase12_virtio_net_manifest.json`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/c23f1e76c2c0cdb2526d252689e68cc4dbee505d/zigux/tests/phase12_virtio_net_survey.zig`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/c23f1e76c2c0cdb2526d252689e68cc4dbee505d/zigux/tests/phase12_virtio_net_syntax_lab.zig`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/c23f1e76c2c0cdb2526d252689e68cc4dbee505d/zigux/tests/phase12_build.zig`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/c23f1e76c2c0cdb2526d252689e68cc4dbee505d/Documentation/zigux/phase12-virtio-net-survey.md`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/c23f1e76c2c0cdb2526d252689e68cc4dbee505d/scripts/zigux/validate-phase12.py`
- `https://raw.githubusercontent.com/adybag14-cyber/Zigux/c23f1e76c2c0cdb2526d252689e68cc4dbee505d/zigux/Makefile`

## Use

- Start with the tree readback roots when the connector can still show the current repo structure but a lane reviewer needs a public fallback path.
- Use the raw pinned URLs when the exact archived Phase 12 virtio_net packet text matters more than the moving `master` tip.
- Leave current-head replay evidence to the owner lanes for the shared validator, the shared build, or a dedicated current-replay catalog.

## Non-goals

- no `current_master_replay_head`
- no shared-validator outcome snapshot
- no shared-build outcome snapshot
- no claim that `c23f1e76c2c0cdb2526d252689e68cc4dbee505d` is the current `master` tip
