# Phase 12 NVMe PCI Raw GitHub Fallback Map

This note records the read-only public GitHub fallback packet for the bounded Phase 12 `nvme_pci` lane.

Use it when GitHub app reads are unavailable, incomplete, or rate-limited and reviewers still need to inspect the live `master` surfaces tied to `drivers/nvme/host/pci.c`.

It is a fallback-read map, not a closure claim and not a validator-first route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_LANE_KEY=P12-L05`
- `PHASE12_SLICE=nvme-pci-raw-github-fallback-map`
- scope: public tree and raw URL coverage for the shipped `nvme_pci` starter, direct verify shard, survey, build wiring, manifest, shared replay surfaces, and the PMO closure companion that now travels with the active release-order packet
- active owner lane: `P12-L05`

## Tree views

- driver starter: `https://github.com/adybag14-cyber/Zigux/blob/master/drivers/nvme/host/pci.zig`
- direct verify shard: `https://github.com/adybag14-cyber/Zigux/blob/master/drivers/nvme/host/pci_verify.zig`
- slice note: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-nvme-pci-slice.md`
- survey note: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-nvme-pci-survey.md`
- PMO closure companion: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/phase12-release-closure-checklist.md`
- shared tests index: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/README.md`
- shared build wiring: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_build.zig`
- direct test gate: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_nvme_pci.zig`
- survey gate: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_nvme_pci_survey.zig`
- survey manifest: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/tests/phase12_nvme_pci_manifest.json`
- scripts index: `https://github.com/adybag14-cyber/Zigux/blob/master/scripts/zigux/README.md`
- docs root packet: `https://github.com/adybag14-cyber/Zigux/blob/master/Documentation/zigux/README.md`
- Linux-style replay wiring: `https://github.com/adybag14-cyber/Zigux/blob/master/zigux/Makefile`

## Raw file views

- driver starter: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/nvme/host/pci.zig`
- direct verify shard: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/drivers/nvme/host/pci_verify.zig`
- slice note: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-nvme-pci-slice.md`
- survey note: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-nvme-pci-survey.md`
- PMO closure companion: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/phase12-release-closure-checklist.md`
- shared tests index: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/README.md`
- shared build wiring: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_build.zig`
- direct test gate: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_nvme_pci.zig`
- survey gate: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_nvme_pci_survey.zig`
- survey manifest: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/tests/phase12_nvme_pci_manifest.json`
- scripts index: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/scripts/zigux/README.md`
- docs root packet: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/Documentation/zigux/README.md`
- Linux-style replay wiring: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/master/zigux/Makefile`

## Shared replay reminder

The shipped Phase 12 packet on `master` still keeps a direct smoke-preflight build route paired with the shared replay order below:

- direct build preflight: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
- current nvme smoke packet surfaces: `zigux/tests/phase12_nvme_pci.zig` and `drivers/nvme/host/pci_verify.zig`

1. `make -C zigux phase12-smoke`
2. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
3. `make -C zigux phase12`

Use `Documentation/zigux/phase12-release-closure-checklist.md` as the PMO companion when judging whether those same shipped surfaces are close enough to describe the active Phase 12 tranche as release-closed.

The shared build-only release guard for that smoke-first order is `scripts/zigux/check-build-only-phase12-surface.py`, and `.github/workflows/zigux-bootstrap.yml` reruns that checker so this fallback wording stays aligned with the shipped PMO release packet.

This map should stay read-only and should not be used to imply an unshipped `validate-phase12.py`, any `check-phase12-*.py` packet, or a `make -C zigux phase12-validate` target.

## Update rule

If the bounded `nvme_pci` packet gains or drops a shipped Phase 12 surface, update this map in the same change so fallback inspection keeps matching the live reviewable packet on `master`.
