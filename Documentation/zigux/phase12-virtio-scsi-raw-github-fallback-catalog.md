# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This catalog records the exact read-only GitHub fallback coverage I verified for `P12-L09` when connector-backed reads are flaky or incomplete.

## Verified head

- lane: `P12-L09`
- phase: `Phase 12`
- verified_master_head: `6d4ca61ad174d69a6afe637a1fe39963c1872bd8`
- verification_scope: commit-pinned raw file reads plus the three public tree entry points needed to inspect the bounded `virtio_scsi` lane

## Tree entry points

- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/scsi`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`

## Commit-pinned raw coverage

- `drivers/scsi/virtio_scsi.c`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6d4ca61ad174d69a6afe637a1fe39963c1872bd8/drivers/scsi/virtio_scsi.c`
  - bytes: `29183`
  - sha256: `b5c783aa262dea9a3eb235ed41b026ad96e12a58eafeee833aaa86daae4bf688`
- `drivers/scsi/virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6d4ca61ad174d69a6afe637a1fe39963c1872bd8/drivers/scsi/virtio_scsi.zig`
  - bytes: `13785`
  - sha256: `25e96fa13df487f40880900328ac411b0c9498ddabcb7c2ada3689d83081f3c1`
- `zigux/tests/phase12_virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6d4ca61ad174d69a6afe637a1fe39963c1872bd8/zigux/tests/phase12_virtio_scsi.zig`
  - bytes: `14139`
  - sha256: `eb8b048d8ae06844e7da6655ddee49714b09007b82d5ee5cfa95e0a87465ce57`
- `zigux/tests/phase12_virtio_scsi_manifest.json`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6d4ca61ad174d69a6afe637a1fe39963c1872bd8/zigux/tests/phase12_virtio_scsi_manifest.json`
  - bytes: `7511`
  - sha256: `5e51889282f325b716fd6bd950145dee7e5f669259d24b2be0b84036caa9db4b`
- `zigux/tests/phase12_virtio_scsi_survey.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6d4ca61ad174d69a6afe637a1fe39963c1872bd8/zigux/tests/phase12_virtio_scsi_survey.zig`
  - bytes: `23854`
  - sha256: `8dd96c55fd846b528bad08bf0e8ca64d3c367417f2fa287af62440f74eef1055`
- `zigux/tests/phase12_build.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6d4ca61ad174d69a6afe637a1fe39963c1872bd8/zigux/tests/phase12_build.zig`
  - bytes: `7155`
  - sha256: `9be3b9c1d1896f4cf70511d37ccf956e2d0561624d06d7c47223dd9b34fb6030`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6d4ca61ad174d69a6afe637a1fe39963c1872bd8/Documentation/zigux/phase12-virtio-scsi-slice.md`
  - bytes: `2242`
  - sha256: `5e763869076a06bf66ba409cb74a96226f0feebe048f032dda699bb3b79508f0`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6d4ca61ad174d69a6afe637a1fe39963c1872bd8/Documentation/zigux/phase12-virtio-scsi-survey.md`
  - bytes: `6508`
  - sha256: `5775b0b183598774dd8df2671c2a8622438c4348948cd28ead9e1701ae9a23ac`
- `scripts/zigux/validate-phase12.py`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6d4ca61ad174d69a6afe637a1fe39963c1872bd8/scripts/zigux/validate-phase12.py`
  - bytes: `17504`
  - sha256: `c112e63de625dfa70b4dfeaff6fcae4c39410542eda0972943fb820f026dc31a`
- `zigux/Makefile`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/6d4ca61ad174d69a6afe637a1fe39963c1872bd8/zigux/Makefile`
  - bytes: `7050`
  - sha256: `f634f1871808edcea9e070ff6f3a8b1a60463ba6525d2d73333e5bdbda6f768c`

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

## Observed degraded-mode behavior

- inspected_master_head: `6d4ca61ad174d69a6afe637a1fe39963c1872bd8`
- shared_validator_command: `python3 scripts/zigux/validate-phase12.py`
- shared_validator_result: `PHASE12_VALIDATION=fail`
- shared_validator_missing_marker: `phase12_virtio_net_manifest.json:gap_count`
- focused_survey_command: `zig test zigux/tests/phase12_virtio_scsi_survey.zig`
- focused_survey_result: `All 1 tests passed.`