# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This catalog records the exact read-only GitHub fallback coverage I verified for `P12-L09` when connector-backed reads are flaky or incomplete.

## Verified head

- lane: `P12-L09`
- phase: `Phase 12`
- verified_master_head: `658cf1efef9df701a00ee53d28a6ca3f49cbeb7d`
- verification_scope: commit-pinned raw file reads plus the three public tree entry points needed to inspect the bounded `virtio_scsi` lane

## Tree entry points

- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/scsi`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`

## Commit-pinned raw coverage

- `drivers/scsi/virtio_scsi.c`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/658cf1efef9df701a00ee53d28a6ca3f49cbeb7d/drivers/scsi/virtio_scsi.c`
  - bytes: `29183`
  - sha256: `b5c783aa262dea9a3eb235ed41b026ad96e12a58eafeee833aaa86daae4bf688`
- `drivers/scsi/virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/658cf1efef9df701a00ee53d28a6ca3f49cbeb7d/drivers/scsi/virtio_scsi.zig`
  - bytes: `13785`
  - sha256: `25e96fa13df487f40880900328ac411b0c9498ddabcb7c2ada3689d83081f3c1`
- `zigux/tests/phase12_virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/658cf1efef9df701a00ee53d28a6ca3f49cbeb7d/zigux/tests/phase12_virtio_scsi.zig`
  - bytes: `14139`
  - sha256: `eb8b048d8ae06844e7da6655ddee49714b09007b82d5ee5cfa95e0a87465ce57`
- `zigux/tests/phase12_virtio_scsi_manifest.json`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/658cf1efef9df701a00ee53d28a6ca3f49cbeb7d/zigux/tests/phase12_virtio_scsi_manifest.json`
  - bytes: `7511`
  - sha256: `778ad258a123e6cda87906f0ae93f4afe645e7b4a55747409f65f0dffa4ffeff`
- `zigux/tests/phase12_virtio_scsi_survey.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/658cf1efef9df701a00ee53d28a6ca3f49cbeb7d/zigux/tests/phase12_virtio_scsi_survey.zig`
  - bytes: `19832`
  - sha256: `78abfa4c5db436c5589e8147805df9989c13b680dd74b2975c19753e8c4fd478`
- `zigux/tests/phase12_build.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/658cf1efef9df701a00ee53d28a6ca3f49cbeb7d/zigux/tests/phase12_build.zig`
  - bytes: `7155`
  - sha256: `9be3b9c1d1896f4cf70511d37ccf956e2d0561624d06d7c47223dd9b34fb6030`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/658cf1efef9df701a00ee53d28a6ca3f49cbeb7d/Documentation/zigux/phase12-virtio-scsi-slice.md`
  - bytes: `2242`
  - sha256: `5e763869076a06bf66ba409cb74a96226f0feebe048f032dda699bb3b79508f0`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/658cf1efef9df701a00ee53d28a6ca3f49cbeb7d/Documentation/zigux/phase12-virtio-scsi-survey.md`
  - bytes: `5946`
  - sha256: `c24bb0a2b4c4846e1cc6e31b7fa14da818234a50195c6870f3276b114628f374`
- `scripts/zigux/validate-phase12.py`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/658cf1efef9df701a00ee53d28a6ca3f49cbeb7d/scripts/zigux/validate-phase12.py`
  - bytes: `17490`
  - sha256: `6e72ae7d73be1bd23c848ca79574a19bbfd34fc496fcc47f118632404ad415a4`
- `zigux/Makefile`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/658cf1efef9df701a00ee53d28a6ca3f49cbeb7d/zigux/Makefile`
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

- inspected_master_head: `658cf1efef9df701a00ee53d28a6ca3f49cbeb7d`
- shared_validator_command: `python3 scripts/zigux/validate-phase12.py`
- shared_validator_result: `PHASE12_VALIDATION=pass`
- shared_validator_manifest_count: `4`
- shared_validator_build_test_count: `8`
- shared_validator_depend_step_count: `8`
- shared_validator_expected_summary_line: `Build Summary: 17/17 steps succeeded; 34/34 tests passed`
- shared_validator_starter_status_count: `44`
- shared_validator_blocked_dma_status_count: `3`
- shared_validator_blocked_object_status_count: `2`
- focused_survey_command: `zig test zigux/tests/phase12_virtio_scsi_survey.zig`
- focused_survey_result: `All 1 tests passed.`
