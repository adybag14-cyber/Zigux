# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This catalog records the exact read-only GitHub fallback coverage originally verified for `P12-L09` when connector-backed reads are flaky or incomplete.

## Verified head

- lane: `P12-L09`
- phase: `Phase 12`
- verified_master_head: `a8daee106057a542aa03f2983662bec7c06584bb`
- verification_scope: commit-pinned raw file reads plus the three public tree entry points needed to inspect the bounded `virtio_scsi` lane

## Tree entry points

- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/scsi`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`

## Commit-pinned raw coverage

- `drivers/scsi/virtio_scsi.c`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/a8daee106057a542aa03f2983662bec7c06584bb/drivers/scsi/virtio_scsi.c`
  - bytes: `29183`
  - sha256: `b5c783aa262dea9a3eb235ed41b026ad96e12a58eafeee833aaa86daae4bf688`
- `drivers/scsi/virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/a8daee106057a542aa03f2983662bec7c06584bb/drivers/scsi/virtio_scsi.zig`
  - bytes: `16330`
  - sha256: `33e370bbec7c6bfaa6e51dffcea3950b011e64ecbd29175ee2743c7050bb1910`
- `zigux/tests/phase12_virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/a8daee106057a542aa03f2983662bec7c06584bb/zigux/tests/phase12_virtio_scsi.zig`
  - bytes: `20224`
  - sha256: `c2b854ef12e6388a790f6876b57b92241031cbb69c3ec7354512eab963ecb5ea`
- `zigux/tests/phase12_virtio_scsi_manifest.json`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/a8daee106057a542aa03f2983662bec7c06584bb/zigux/tests/phase12_virtio_scsi_manifest.json`
  - bytes: `8815`
  - sha256: `213188f223ac545d256c584a91f355246b06b530982084f5bac268d358ea4358`
- `zigux/tests/phase12_virtio_scsi_survey.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/a8daee106057a542aa03f2983662bec7c06584bb/zigux/tests/phase12_virtio_scsi_survey.zig`
  - bytes: `25900`
  - sha256: `36afefd118dfafb3e5971bdc882dace7c26964f760b3bc97d86c47a0a049655b`
- `zigux/tests/phase12_build.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/a8daee106057a542aa03f2983662bec7c06584bb/zigux/tests/phase12_build.zig`
  - bytes: `7155`
  - sha256: `9be3b9c1d1896f4cf70511d37ccf956e2d0561624d06d7c47223dd9b34fb6030`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/a8daee106057a542aa03f2983662bec7c06584bb/Documentation/zigux/phase12-virtio-scsi-slice.md`
  - bytes: `2909`
  - sha256: `c168ca3572f6c1756955ae9f01fcc56e39df477cc2fe1ee79a60be482b1fc5c0`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/a8daee106057a542aa03f2983662bec7c06584bb/Documentation/zigux/phase12-virtio-scsi-survey.md`
  - bytes: `7207`
  - sha256: `26803c0c43606afec316d8b6688b95a681c4b3123afd319e58702c3bc47c03de`
- `scripts/zigux/validate-phase12.py`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/a8daee106057a542aa03f2983662bec7c06584bb/scripts/zigux/validate-phase12.py`
  - bytes: `26729`
  - sha256: `755586ee8a39c29d0a575418233455176ebee5350f27eea20a14e56cb1aa48cd`
- `zigux/Makefile`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/a8daee106057a542aa03f2983662bec7c06584bb/zigux/Makefile`
  - bytes: `7885`
  - sha256: `9ed0e0c0e7f62626606226ddaf6af1d5236f17a6089b148016be691cf74772bd`

## Coverage summary

- raw_github_tree_fallback_count: `3`
- raw_github_file_fallback_count: `10`
- fallback_anchor_path: `drivers/scsi/virtio_scsi.c`
- fallback_anchor_only_raw_file: `drivers/scsi/virtio_scsi.c`
- fallback_lane_artifact_count: `9`
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

- inspected_master_head: `a8daee106057a542aa03f2983662bec7c06584bb`
- shared_validator_command: `python3 scripts/zigux/validate-phase12.py`
- shared_validator_result: `PHASE12_VALIDATION=fail`
- shared_validator_missing_markers:
  - `phase12_virtio_net_manifest.json:lane_key`
  - `phase12_libbpf_snapshot_fixture:bytes:zigux/tests/phase12_libbpf_segments.zig`
  - `phase12_libbpf_snapshot_fixture:sha256:zigux/tests/phase12_libbpf_segments.zig`
- focused_survey_command: `zig test zigux/tests/phase12_virtio_scsi_survey.zig`
- focused_survey_result: `All 1 tests passed.`

## Current replay note

These fields record the last replay performed for this pinned fallback packet. They can lag the live `master` head until `P12-L09` or `P12-L12` refreshes the exact inspected-head evidence again.

- current_master_replay_head: `a8daee106057a542aa03f2983662bec7c06584bb`
- current_shared_validator_command: `python3 scripts/zigux/validate-phase12.py`
- current_shared_validator_result: `PHASE12_VALIDATION=fail`
- current_focused_survey_command: `zig test zigux/tests/phase12_virtio_scsi_survey.zig`
- current_shared_validator_missing_markers:
  - `phase12_virtio_net_manifest.json:lane_key`
  - `phase12_libbpf_snapshot_fixture:bytes:zigux/tests/phase12_libbpf_segments.zig`
  - `phase12_libbpf_snapshot_fixture:sha256:zigux/tests/phase12_libbpf_segments.zig`
- current_focused_survey_result: `All 1 tests passed.`
