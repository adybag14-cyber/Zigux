# Phase 12 NVMe PCI Raw GitHub Fallback Map

This note records the bounded Phase 12 NVMe PCI packet that is directly inspectable on `master` even when a full repo checkout is unavailable.

It is the current-master gap-note companion for the shipped NVMe foothold, not a commit-pinned replay catalog and not a shared build-route claim.

## Status

- `PHASE12_DIRECT_PACKET_ON_MASTER=starter_verifier_slice_note_direct_replay_survey_note_survey_gate_and_manifest_present_shared_build_unwired`
- lane owner: `P12-L08`
- roadmap anchor: `drivers/nvme/host/pci.c`
- packet scope: keep the current NVMe PCI starter reviewable without claiming live DMA mapping, PRP or SGL submission, blk-mq wiring, or transport-backed queue execution
- release-order companion: `Documentation/zigux/phase12-release-sequencing.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- fallback overview companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- driver-local reopen companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- support checker bundle: `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-nvme-pci-packet.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `scripts/zigux/validate-phase12.py`

## Direct Packet

- starter shard: `drivers/nvme/host/pci.zig`
- verifier shard: `drivers/nvme/host/pci_verify.zig`
- direct replay: `zigux/tests/phase12_nvme_pci.zig`
- slice note: `Documentation/zigux/phase12-nvme-pci-slice.md`
- survey note: `Documentation/zigux/phase12-nvme-pci-survey.md`
- survey gate: `zigux/tests/phase12_nvme_pci_survey.zig`
- manifest anchor: `zigux/tests/phase12_nvme_pci_manifest.json`
- `zigux/tests/phase12_build.zig` still does not wire the bounded NVMe direct replay into the shared `phase12-smoke` or `phase12` routes

## Current-Master Evidence Snapshot

- exact coverage evidence refreshed on `2026-05-22` against live current `master`
- current `master` still carries `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json`
- current `master` also directly reads the packet-local checker and shared support bundle through `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-nvme-pci-packet.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig`
- current `zigux/Makefile` now exposes `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, and `make -C zigux phase12` again
- current authoritative packet truth therefore stays split: this NVMe note is the bounded current-master gap-note companion for the driver-local foothold, while the shared release packet and degraded-read support bundle stay owned by the Phase 12 release companions listed above

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

This fallback map is read-only evidence for the bounded starter packet. It does not claim that the NVMe replay is part of the shared smoke-first Phase 12 route.

It still does not claim live DMA mapping, PRP or SGL construction, blk-mq submission ownership, interrupt-backed completion handling, transport-backed reset replay, or throughput evidence.

## Review Use

- reread this note beside `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, and `Documentation/zigux/phase12-release-coordination-matrix.md` whenever shared fallback wording changes
- reread it beside `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `zigux/tests/phase12_nvme_pci.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, and `zigux/tests/phase12_nvme_pci_manifest.json` before widening any driver-local PMO wording
- compare it beside contents-bridge reads of `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-nvme-pci-packet.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, and `zigux/tests/phase12_build.zig` before widening fallback claims or shared-route wording
- keep this file bounded as the current-master gap-note companion only; do not promote it into a commit-pinned replay artifact or a shared build-route proof
