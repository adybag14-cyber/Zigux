# Phase 12 NVMe PCI Raw GitHub Fallback Map

This note records the bounded Phase 12 NVMe PCI packet that is directly inspectable on `master` even when a full repo checkout is unavailable.

It is the current-master gap-note companion for the shipped NVMe foothold, not a commit-pinned replay catalog and not a shared build-route claim.

## Status

- `PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_slice_note_direct_replay_survey_note_survey_gate_manifest_support_bundle_and_shared_direct_replay_present`
- lane owner: `P12-L08`
- roadmap anchor: `drivers/nvme/host/pci.c`
- packet scope: keep the current NVMe PCI starter reviewable without claiming live DMA mapping, PRP or SGL submission, blk-mq wiring, or transport-backed queue execution
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- fallback overview companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- driver-local reopen companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- support checker bundle: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-nvme-pci-packet.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `scripts/zigux/README.md`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig`

## Direct Packet

- starter shard: `drivers/nvme/host/pci.zig`
- verifier shard: `drivers/nvme/host/pci_verify.zig`
- direct replay: `zigux/tests/phase12_nvme_pci.zig`
- slice note: `Documentation/zigux/phase12-nvme-pci-slice.md`
- survey note: `Documentation/zigux/phase12-nvme-pci-survey.md`
- survey gate: `zigux/tests/phase12_nvme_pci_survey.zig`
- survey-build route: `zigux/tests/phase12_nvme_pci_survey_build.zig`
- manifest anchor: `zigux/tests/phase12_nvme_pci_manifest.json`
- current `zigux/tests/phase12_build.zig` wires the bounded NVMe direct replay into the shared `phase12-smoke`, `phase12-test`, and `phase12` routes, while the verifier shard and survey gate stay packet-local

## Current-Master Raw Path Map

Base raw URL prefix:
`https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/`

- starter shard raw path: `drivers/nvme/host/pci.zig`
- verifier shard raw path: `drivers/nvme/host/pci_verify.zig`
- direct replay raw path: `zigux/tests/phase12_nvme_pci.zig`
- dedicated direct-build raw path: `zigux/tests/phase12_nvme_pci_build.zig`
- survey-build raw path: `zigux/tests/phase12_nvme_pci_survey_build.zig`
- slice note raw path: `Documentation/zigux/phase12-nvme-pci-slice.md`
- survey note raw path: `Documentation/zigux/phase12-nvme-pci-survey.md`
- survey gate raw path: `zigux/tests/phase12_nvme_pci_survey.zig`
- manifest anchor raw path: `zigux/tests/phase12_nvme_pci_manifest.json`
- reopen-governance raw path: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- keep this current-master raw-path map as a browser-side routing aid only; it does not turn the NVMe gap-note companion into a commit-pinned fallback artifact

## Current-Master Support Raw Path Map

Base raw URL prefix:
`https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/`

- packet checker raw path: `scripts/zigux/check-phase12-nvme-pci-packet.py`
- build-only checker raw path: `scripts/zigux/check-build-only-phase12-surface.py`
- cross-compile smoke checker raw path: `scripts/zigux/check-phase12-cross-compile-smoke.py`
- release-readiness checker raw path: `scripts/zigux/check-phase12-release-readiness-packet.py`
- validator raw path: `scripts/zigux/validate-phase12.py`
- scripts-root reminder raw path: `scripts/zigux/README.md`
- workflow raw path: `.github/workflows/zigux-bootstrap.yml`
- shared build raw path: `zigux/tests/phase12_build.zig`
- shared route owner raw path: `zigux/Makefile`
- keep this support raw-path map bounded to review routing and fallback inspection; it does not promote the NVMe note into a shared release-packet proof by itself

## Current-Master Evidence Snapshot

- exact coverage evidence refreshed on `2026-05-27` against live current `master`
- current `master` directly reads `drivers/nvme/host/pci.zig` `01f3c44cf3979f1708173869dea29d8d44dd5a6a`, `drivers/nvme/host/pci_verify.zig` `df9c3e2b667a053a58c6a6927c9a6ee6286d1c04`, `zigux/tests/phase12_nvme_pci.zig` `8f7412c50810e25b119b62cf06d6628f6dd0b791`, `zigux/tests/phase12_nvme_pci_build.zig` `ea80873f5838679983d7b2b2475e5b9529a7b57c`, `zigux/tests/phase12_nvme_pci_survey.zig` `2aa9d620b4c175cece71df5bf0f98dc5d25d887b`, `zigux/tests/phase12_nvme_pci_survey_build.zig` `e23452e271b674af90e9cc7f1919b250c3dcf7e4`, and `zigux/tests/phase12_nvme_pci_manifest.json` `deec33d9d750909556258f9278369db9f05817f5`
- current `master` also directly reads the packet-local checker and the shared support bundle through `scripts/zigux/check-phase12-nvme-pci-packet.py` `3515001b0ab59291df5272d7a12718cf5ba13b7d`, `scripts/zigux/check-build-only-phase12-surface.py` `5d4a081067b5abf4f9a313ddc7bbcc18c1505f67`, `scripts/zigux/check-phase12-cross-compile-smoke.py` `00c0722e44c20fd7b15b6651e949ea126cdb4889`, `scripts/zigux/check-phase12-release-readiness-packet.py` `ffb7c4da4b29efe963aac78d196732a156de5c76`, `scripts/zigux/validate-phase12.py` `57054fc16e24d74ded09d6e6f90aeb67b75c2368`, `scripts/zigux/README.md` `08ee52d0611719b13759088f325b1e98ba9f6af7`, `.github/workflows/zigux-bootstrap.yml` `3b8e39310e007e82b593bb094ca0eb38b4b98c63`, `zigux/Makefile` `09f92bc2f9903fc4fd58d6335e93da13e7f0793b`, and `zigux/tests/phase12_build.zig` `e0d297f50d2805948b93ca421ae9ec20ddfceafa`
- current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, `make -C zigux phase12`, `make -C zigux phase12-nvme-pci-direct-test`, and `make -C zigux phase12-nvme-pci-survey-test`
- current authoritative packet truth therefore stays split: this NVMe note is the bounded current-master gap-note companion for the driver-local foothold, while the shared release packet and degraded-read support bundle stay owned by the Phase 12 release companions listed above
- direct same-runtime `curl`, `wget`, `urllib`, and `git clone https://github.com/adybag14-cyber/Zigux.git` still fail in this runtime through the proxy tunnel with HTTP `403`, so exact same-runtime fallback verification remains GitHub-contents-driven here

## Shared Release-Order Reminder

Keep the current validator-first then smoke-first Phase 12 order explicit beside this driver-local gap note too:

1. shipped wrapper evidence on current `master`: `make -C zigux phase12-validate`
2. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
3. shipped wrapper evidence on current `master`: `make -C zigux phase12-smoke`
4. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
5. shipped wrapper evidence on current `master`: `make -C zigux phase12-test`
6. shipped wrapper evidence on current `master`: `make -C zigux phase12`

If `zig` is unavailable on `PATH`, keep that same order explicit and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, keep the same shipped validator wrapper plus shipped wrapper reruns explicit as `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, `make -C zigux phase12-test ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused NVMe-only replay route or another unshipped shared route.

## Boundary

This fallback map is read-only evidence for the bounded starter packet. It does not claim that the NVMe survey gate or verifier shard is part of the shared smoke-first Phase 12 route.

It still does not claim live DMA mapping, PRP or SGL construction, blk-mq submission ownership, interrupt-backed completion handling, transport-backed reset replay, or throughput evidence.

## Review Use

- reread this note beside `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` whenever shared fallback wording changes
- reread it beside `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, `zigux/tests/phase12_nvme_pci_survey_build.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json` before widening any driver-local PMO wording
- compare it beside contents-bridge reads of `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-cross-compile-smoke.py`, `scripts/zigux/check-phase12-nvme-pci-packet.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig` before widening fallback claims or shared-route wording
- keep this file bounded as the current-master gap-note companion only; do not promote it into a commit-pinned replay artifact or a shared build-route proof
