# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This catalog records the exact read-only GitHub fallback coverage I verified for `P12-L09` when connector-backed reads are flaky or incomplete.

## Verified head

- lane: `P12-L09`
- phase: `Phase 12`
- verified_master_head: `3920e2311110994e4bd1e5e4dc2210494dab4641`
- verification_scope: commit-pinned raw file reads plus the three public tree entry points needed to inspect the bounded `virtio_scsi` lane

## Tree entry points

- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/scsi`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`

## Commit-pinned raw coverage

- `drivers/scsi/virtio_scsi.c`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/3920e2311110994e4bd1e5e4dc2210494dab4641/drivers/scsi/virtio_scsi.c`
  - bytes: `29183`
  - sha256: `b5c783aa262dea9a3eb235ed41b026ad96e12a58eafeee833aaa86daae4bf688`
- `drivers/scsi/virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/3920e2311110994e4bd1e5e4dc2210494dab4641/drivers/scsi/virtio_scsi.zig`
  - bytes: `10775`
  - sha256: `9d3a7c30fa81d564039bc204a8a7ae28b0910d47d4dd04c09dd9215249a4d647`
- `zigux/tests/phase12_virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/3920e2311110994e4bd1e5e4dc2210494dab4641/zigux/tests/phase12_virtio_scsi.zig`
  - bytes: `10853`
  - sha256: `ef8bf4bc4f55a7175b66cd5cd48de90d345ac2d01c0b39f0ba94f3cfbc54e15e`
- `zigux/tests/phase12_virtio_scsi_manifest.json`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/3920e2311110994e4bd1e5e4dc2210494dab4641/zigux/tests/phase12_virtio_scsi_manifest.json`
  - bytes: `6773`
  - sha256: `39b8cb2d96d732e7e3eff3373ea7b36ae2a12c799fdde53608f13c3fbefd0a47`
- `zigux/tests/phase12_virtio_scsi_survey.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/3920e2311110994e4bd1e5e4dc2210494dab4641/zigux/tests/phase12_virtio_scsi_survey.zig`
  - bytes: `16069`
  - sha256: `bc1bc951fa2b8b7b59d02731302a19f81edf0eb598d77574e92d5047961fe77d`
- `zigux/tests/phase12_build.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/3920e2311110994e4bd1e5e4dc2210494dab4641/zigux/tests/phase12_build.zig`
  - bytes: `6805`
  - sha256: `0b5ea4c22ea293ef58b06bb686ff6005d30b930c27a64110491ce5de95f349cb`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/3920e2311110994e4bd1e5e4dc2210494dab4641/Documentation/zigux/phase12-virtio-scsi-slice.md`
  - bytes: `1864`
  - sha256: `1aa16b0de4715ad9e6da5740d4e42a59603000da135e1bb41557216ea33f952b`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/3920e2311110994e4bd1e5e4dc2210494dab4641/Documentation/zigux/phase12-virtio-scsi-survey.md`
  - bytes: `5314`
  - sha256: `b158e65c17afc09ac362614596b21d87b704290a3df932aa12174dd8533f0809`
- `scripts/zigux/validate-phase12.py`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/3920e2311110994e4bd1e5e4dc2210494dab4641/scripts/zigux/validate-phase12.py`
  - bytes: `11709`
  - sha256: `7730d2c763e5668280bc9128e6df2cbca5926c971c8345db4831e1c9367fbd4c`
- `zigux/Makefile`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/3920e2311110994e4bd1e5e4dc2210494dab4641/zigux/Makefile`
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