# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This catalog records the exact read-only GitHub fallback coverage I verified for `P12-L09` when connector-backed reads are flaky or incomplete.

## Verified head

- lane: `P12-L09`
- phase: `Phase 12`
- verified_master_head: `6cdf1b24fad34b4ef67f0902da0aa8621383c7ee`
- verification_scope: commit-pinned raw file reads plus the three public tree entry points needed to inspect the bounded `virtio_scsi` lane

## Tree entry points

- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/scsi`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`

## Commit-pinned raw coverage

- `drivers/scsi/virtio_scsi.c`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6cdf1b24fad34b4ef67f0902da0aa8621383c7ee/drivers/scsi/virtio_scsi.c`
  - bytes: `29183`
  - sha256: `b5c783aa262dea9a3eb235ed41b026ad96e12a58eafeee833aaa86daae4bf688`
- `drivers/scsi/virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6cdf1b24fad34b4ef67f0902da0aa8621383c7ee/drivers/scsi/virtio_scsi.zig`
  - bytes: `10775`
  - sha256: `9d3a7c30fa81d564039bc204a8a7ae28b0910d47d4dd04c09dd9215249a4d647`
- `zigux/tests/phase12_virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6cdf1b24fad34b4ef67f0902da0aa8621383c7ee/zigux/tests/phase12_virtio_scsi.zig`
  - bytes: `10853`
  - sha256: `ef8bf4bc4f55a7175b66cd5cd48de90d345ac2d01c0b39f0ba94f3cfbc54e15e`
- `zigux/tests/phase12_virtio_scsi_manifest.json`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6cdf1b24fad34b4ef67f0902da0aa8621383c7ee/zigux/tests/phase12_virtio_scsi_manifest.json`
  - bytes: `7510`
  - sha256: `9911fda5d529ac60d1c82438fca04c4e3d8517fbb26a27c031f2ab29e6c91257`
- `zigux/tests/phase12_virtio_scsi_survey.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6cdf1b24fad34b4ef67f0902da0aa8621383c7ee/zigux/tests/phase12_virtio_scsi_survey.zig`
  - bytes: `19831`
  - sha256: `52250f55244961704dd6d72053218abbdfab6a5884414a3dc27e173c3aef3642`
- `zigux/tests/phase12_build.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6cdf1b24fad34b4ef67f0902da0aa8621383c7ee/zigux/tests/phase12_build.zig`
  - bytes: `6805`
  - sha256: `0b5ea4c22ea293ef58b06bb686ff6005d30b930c27a64110491ce5de95f349cb`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6cdf1b24fad34b4ef67f0902da0aa8621383c7ee/Documentation/zigux/phase12-virtio-scsi-slice.md`
  - bytes: `1864`
  - sha256: `1aa16b0de4715ad9e6da5740d4e42a59603000da135e1bb41557216ea33f952b`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6cdf1b24fad34b4ef67f0902da0aa8621383c7ee/Documentation/zigux/phase12-virtio-scsi-survey.md`
  - bytes: `5945`
  - sha256: `0b36e0bc774e0c16652380a5f882e66cf8084bb5be0332df9663a5d51c2f14e6`
- `scripts/zigux/validate-phase12.py`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6cdf1b24fad34b4ef67f0902da0aa8621383c7ee/scripts/zigux/validate-phase12.py`
  - bytes: `11786`
  - sha256: `dddfe63558b86bf68ddffffeeef8c34ba5a8d8562ad8557598b4a936490174c9`
- `zigux/Makefile`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6cdf1b24fad34b4ef67f0902da0aa8621383c7ee/zigux/Makefile`
  - bytes: `5300`
  - sha256: `761ed2df3cd21b0de60124c3d341dc8bf19dc21f982656005f941222becf8b00`

## Coverage summary

- raw_github_tree_fallback_count: `3`
- raw_github_file_fallback_count: `10`
- fallback_anchor_path: `drivers/scsi/virtio_scsi.c`
- fallback_lane_artifacts:
  - `drivers/scsi/virtio_scsi.zig`
  - `zigux/tests/phase12_virtio_scsi.zig`
  - `zigux/tests/phase12_virtio_scsi_manifest.json`
  - `zigux/tests/phase12_virtio_scsi_survey.zig`
  - `zigux/tests/phase12_build.zig`
  - `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - `scripts/zigux/validate-phase12.py`
  - `zigux/Makefile`
