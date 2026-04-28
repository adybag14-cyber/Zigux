# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This catalog records the exact read-only GitHub fallback coverage I verified for `P12-L09` when connector-backed reads are flaky or incomplete.

## Verified head

- lane: `P12-L09`
- phase: `Phase 12`
- verified_master_head: `ec1f21e06c76ffea564156593196096c803a53e4`
- verification_scope: commit-pinned raw file reads plus the three public tree entry points needed to inspect the bounded `virtio_scsi` lane

## Tree entry points

- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/scsi`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`

## Commit-pinned raw coverage

- `drivers/scsi/virtio_scsi.c`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/drivers/scsi/virtio_scsi.c`
  - bytes: `29183`
  - sha256: `b5c783aa262dea9a3eb235ed41b026ad96e12a58eafeee833aaa86daae4bf688`
- `drivers/scsi/virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/drivers/scsi/virtio_scsi.zig`
  - bytes: `12227`
  - sha256: `132ed59e7c84858f5592c9e88c1bd76e8165b3e1dfe9f2c53bb6380f409f72ee`
- `zigux/tests/phase12_virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/zigux/tests/phase12_virtio_scsi.zig`
  - bytes: `12352`
  - sha256: `4a8130351358267982403aa88c43e8af0afff1b1d5fe3d2f7599495e6acaea4d`
- `zigux/tests/phase12_virtio_scsi_manifest.json`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/zigux/tests/phase12_virtio_scsi_manifest.json`
  - bytes: `7511`
  - sha256: `1c90a3ecd974fa486b5cd2569063341ac5a10a557d4fd5c85916bb6c49f9c607`
- `zigux/tests/phase12_virtio_scsi_survey.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/zigux/tests/phase12_virtio_scsi_survey.zig`
  - bytes: `19832`
  - sha256: `d69956d73315aba1f6ef6c4d8ce741275944e654a4d504ced9b5c1af2718ecba`
- `zigux/tests/phase12_build.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/zigux/tests/phase12_build.zig`
  - bytes: `6805`
  - sha256: `0b5ea4c22ea293ef58b06bb686ff6005d30b930c27a64110491ce5de95f349cb`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/Documentation/zigux/phase12-virtio-scsi-slice.md`
  - bytes: `1993`
  - sha256: `931cfb7fef011b617f5590195b1d47c663910eaea3f6fe8c5a964102f99706e8`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/Documentation/zigux/phase12-virtio-scsi-survey.md`
  - bytes: `5946`
  - sha256: `d64b2208fc07230eec94b708e499ccdcf5fa806cd6f331fe75768521a8603065`
- `scripts/zigux/validate-phase12.py`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/scripts/zigux/validate-phase12.py`
  - bytes: `11786`
  - sha256: `6813189c32aae8c7c7bb14799d8eff22fe36c842cf2134e3125fc8463c5f2a24`
- `zigux/Makefile`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/ec1f21e06c76ffea564156593196096c803a53e4/zigux/Makefile`
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
