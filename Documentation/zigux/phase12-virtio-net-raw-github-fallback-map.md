# Phase 12 Virtio Net Raw GitHub Fallback Map

This note records the bounded Phase 12 `virtio_net` packet that is directly inspectable on current `master` when a full repo checkout is unavailable.

It is the current-master public-read fallback companion for the shipped split-helper `virtio_net` packet, not a commit-pinned replay catalog and not a claim that the whole complex-driver tranche is complete.

## Status

- `PHASE12_DIRECT_PACKET_ON_MASTER=split_helper_packet_shared_route_and_syntax_lab_present`
- lane owner: `P12-L07`
- roadmap anchor: `drivers/net/virtio_net.c`
- packet scope: keep the queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, survey-gate, manifest, and standalone syntax-lab compile-smoke surfaces reviewable without claiming live DMA-safe receive ownership, transport-backed queue execution, interrupt-backed completion handling, or measured runtime throughput delivery
- fallback overview companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- survey companion: `Documentation/zigux/phase12-virtio-net-survey.md`
- syntax-lab companion: `Documentation/zigux/phase12-virtio-net-syntax-lab.md`
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- support checker bundle: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-build-inventory.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig`

## Direct Packet

- driver shard: `drivers/net/virtio_net_queue_resume.zig`
- driver shard: `drivers/net/virtio_net_receive_refill_replay.zig`
- driver shard: `drivers/net/virtio_net_transmit_recycle.zig`
- driver shard: `drivers/net/virtio_net_post_reset_replay.zig`
- driver shard: `drivers/net/virtio_net_throughput_parity.zig`
- directly coupled replay: `zigux/tests/phase12_virtio_net_queue_resume.zig`
- directly coupled replay: `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`
- directly coupled replay: `zigux/tests/phase12_virtio_net_transmit_recycle.zig`
- directly coupled replay: `zigux/tests/phase12_virtio_net_post_reset_replay.zig`
- directly coupled replay: `zigux/tests/phase12_virtio_net_throughput_parity.zig`
- survey gate: `zigux/tests/phase12_virtio_net_survey.zig`
- manifest anchor: `zigux/tests/phase12_virtio_net_manifest.json`
- standalone syntax lab: `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- standalone syntax-lab build route: `zigux/tests/phase12_virtio_net_syntax_lab_build.zig`
- shared build anchor: `zigux/tests/phase12_build.zig`
- shared route owner: `zigux/Makefile`
- current shared route shape: `zigux/tests/phase12_build.zig` wires the queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate sextet through shared `smoke` and shared `test`, while current `zigux/Makefile` ships `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, `make -C zigux phase12`, `make -C zigux phase12-virtio-net-syntax-lab-test`, and `make -C zigux phase12-virtio-net-throughput-parity-test`

## Current-Master Raw Path Map

Base raw URL prefix:
`https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/`

- driver raw path: `drivers/net/virtio_net_queue_resume.zig`
- driver raw path: `drivers/net/virtio_net_receive_refill_replay.zig`
- driver raw path: `drivers/net/virtio_net_transmit_recycle.zig`
- driver raw path: `drivers/net/virtio_net_post_reset_replay.zig`
- driver raw path: `drivers/net/virtio_net_throughput_parity.zig`
- replay raw path: `zigux/tests/phase12_virtio_net_queue_resume.zig`
- replay raw path: `zigux/tests/phase12_virtio_net_receive_refill_replay.zig`
- replay raw path: `zigux/tests/phase12_virtio_net_transmit_recycle.zig`
- replay raw path: `zigux/tests/phase12_virtio_net_post_reset_replay.zig`
- replay raw path: `zigux/tests/phase12_virtio_net_throughput_parity.zig`
- survey raw path: `zigux/tests/phase12_virtio_net_survey.zig`
- manifest raw path: `zigux/tests/phase12_virtio_net_manifest.json`
- syntax-lab raw path: `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- syntax-lab build raw path: `zigux/tests/phase12_virtio_net_syntax_lab_build.zig`
- survey note raw path: `Documentation/zigux/phase12-virtio-net-survey.md`
- syntax-lab note raw path: `Documentation/zigux/phase12-virtio-net-syntax-lab.md`
- keep this current-master raw-path map as a browser-side routing aid for the real shipped packet; it does not turn this note into a commit-pinned replay artifact

## Current-Master Support Raw Path Map

Base raw URL prefix:
`https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/`

- build-only checker raw path: `scripts/zigux/check-build-only-phase12-surface.py`
- build inventory checker raw path: `scripts/zigux/check-phase12-build-inventory.py`
- complex-driver packet checker raw path: `scripts/zigux/check-phase12-complex-driver-lane-packet.py`
- cross-compile smoke checker raw path: `scripts/zigux/check-phase12-cross-compile-smoke.py`
- release-readiness checker raw path: `scripts/zigux/check-phase12-release-readiness-packet.py`
- validator raw path: `scripts/zigux/validate-phase12.py`
- scripts-root reminder raw path: `scripts/zigux/README.md`
- workflow raw path: `.github/workflows/zigux-bootstrap.yml`
- shared build raw path: `zigux/tests/phase12_build.zig`
- shared route owner raw path: `zigux/Makefile`
- keep this support raw-path map bounded to review routing and fallback inspection; it does not promote the bounded `virtio_net` note into broader release-closure proof by itself

## Current-Master Evidence Snapshot

- exact coverage evidence refreshed on `2026-05-27` against live current `master`
- current `master` directly reads `drivers/net/virtio_net_queue_resume.zig` `b5848b0f7a8d00e0856ea2b846e3085137c5b2fb`, `drivers/net/virtio_net_receive_refill_replay.zig` `2b196930c8129879777470f0fac1707694485402`, `drivers/net/virtio_net_transmit_recycle.zig` `3487e5e3f4ef44c642a09150043fd7ebe29f06ba`, `drivers/net/virtio_net_post_reset_replay.zig` `166c65f9af7a8144eff0137a8edab64c6b58677d`, and `drivers/net/virtio_net_throughput_parity.zig` `ca13510feeb5545645dfedb5ff31c3433aecfc5d`
- current `master` directly reads `zigux/tests/phase12_virtio_net_queue_resume.zig` `d3b0a853bc13b46e1a26469b24043adde8cfbeb6`, `zigux/tests/phase12_virtio_net_receive_refill_replay.zig` `59279fa25eee3307def48bb10b24ed30b17f729e`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig` `0f8c7031d1467aedbe7e4df9530a38b58c57eba5`, `zigux/tests/phase12_virtio_net_post_reset_replay.zig` `cf0ca432300fc38684a8b966a5328ffd452705e9`, `zigux/tests/phase12_virtio_net_throughput_parity.zig` `5080ed54e126b7bfc4af9c2ddbb35c6a9e642c13`, `zigux/tests/phase12_virtio_net_survey.zig` `af1625180cb63fac5df719e4eb89f610b1965a25`, `zigux/tests/phase12_virtio_net_manifest.json` `80b1eaa0ebfee8d60a146bfe7fa08cdd6b948c6d`, `zigux/tests/phase12_virtio_net_syntax_lab.zig` `9f82e9dc620ac1752e5aae609ed982548c794897`, and `zigux/tests/phase12_virtio_net_syntax_lab_build.zig` `70c49575c3f8d34391639c57f9bc1a2cabf8a1a7`
- current `master` also directly reads `Documentation/zigux/phase12-virtio-net-survey.md` `4897c1eaf95abe08bcfccc7d7e5231ef974f7dc9`, `Documentation/zigux/phase12-virtio-net-syntax-lab.md` `9cb5760ce58393d1ce620fa2a54d9d8c034c17e1`, `scripts/zigux/check-build-only-phase12-surface.py` `5d4a081067b5abf4f9a313ddc7bbcc18c1505f67`, `scripts/zigux/check-phase12-build-inventory.py` `8ff056b85ecf09b1aef552a5a74c48638fa556bf`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py` `6b894ae36ae70fcc44024a2d2c7e8b595a16513d`, `scripts/zigux/check-phase12-cross-compile-smoke.py` `00c0722e44c20fd7b15b6651e949ea126cdb4889`, `scripts/zigux/check-phase12-release-readiness-packet.py` `ffb7c4da4b29efe963aac78d196732a156de5c76`, `scripts/zigux/validate-phase12.py` `57054fc16e24d74ded09d6e6f90aeb67b75c2368`, `scripts/zigux/README.md` `08ee52d0611719b13759088f325b1e98ba9f6af7`, `.github/workflows/zigux-bootstrap.yml` `3b8e39310e007e82b593bb094ca0eb38b4b98c63`, `zigux/Makefile` `09f92bc2f9903fc4fd58d6335e93da13e7f0793b`, and `zigux/tests/phase12_build.zig` `e0d297f50d2805948b93ca421ae9ec20ddfceafa`
- browser-side raw GitHub readback in this run also returned representative current-master bodies for `drivers/net/virtio_net_queue_resume.zig`, `zigux/tests/phase12_virtio_net_survey.zig`, and `zigux/tests/phase12_virtio_net_syntax_lab_build.zig`
- direct same-runtime `curl`, `wget`, `urllib`, and `git clone https://github.com/adybag14-cyber/Zigux.git` still fail in this runtime through the proxy tunnel with HTTP `403`, so exact same-runtime fallback verification remains split between GitHub contents reads and browser-visible raw GitHub readback here

## Shared Release-Order Reminder

Keep the current validator-first then smoke-first Phase 12 order explicit beside this driver-local fallback map too:

1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`
2. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
3. shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`
4. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`
6. shipped wrapper evidence on current `master`: `make -C zigux phase12`

If `zig` is unavailable on `PATH`, keep that same order explicit and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the same shipped validator wrapper plus shipped wrapper reruns explicit as `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused `virtio_net`-only replay route or another unshipped shared route.

## Boundary

This fallback map is read-only evidence for the bounded split-helper `virtio_net` packet. It does not claim live DMA-safe receive ownership, page-pool refill execution, control-virtqueue command flow, IRQ-backed completion handling, transport-backed reset replay, or measured runtime throughput delivery.

It also does not reopen the older monolithic `drivers/net/virtio_net.zig` and `zigux/tests/phase12_virtio_net.zig` vocabulary that current `master` still keeps absent.

## Review Use

- reread this note beside `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-virtio-net-syntax-lab.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` whenever shared fallback wording changes
- reread it beside `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_net_survey.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_syntax_lab_build.zig`, and the five split driver shards before widening any driver-local PMO wording
- compare it beside contents-bridge reads of `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-build-inventory.py`, `scripts/zigux/check-phase12-complex-driver-lane-packet.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig` before widening fallback claims or shared-route wording
- keep this file bounded as the current-master fallback companion for the real split-helper packet; do not promote it into a commit-pinned replay artifact or a claim that the broader complex-driver delivery work is done
