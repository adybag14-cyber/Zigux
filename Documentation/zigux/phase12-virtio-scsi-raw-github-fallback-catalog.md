# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This catalog records the exact read-only GitHub fallback coverage I verified for `P12-L09` when connector-backed reads are flaky or incomplete.

## Verified head

- lane: `P12-L09`
- phase: `Phase 12`
- verified_master_head: `5ecf3870d48d43e7a718b620b02ab9f60c0b969f`
- verification_scope: commit-pinned raw file reads plus the three public tree entry points needed to inspect the bounded `virtio_scsi` lane

## Tree entry points

- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/scsi`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`

## Commit-pinned raw coverage

- `drivers/scsi/virtio_scsi.c`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/5ecf3870d48d43e7a718b620b02ab9f60c0b969f/drivers/scsi/virtio_scsi.c`
  - bytes: `29183`
  - sha256: `b5c783aa262dea9a3eb235ed41b026ad96e12a58eafeee833aaa86daae4bf688`
- `drivers/scsi/virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/5ecf3870d48d43e7a718b620b02ab9f60c0b969f/drivers/scsi/virtio_scsi.zig`
  - bytes: `13785`
  - sha256: `25e96fa13df487f40880900328ac411b0c9498ddabcb7c2ada3689d83081f3c1`
- `zigux/tests/phase12_virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/5ecf3870d48d43e7a718b620b02ab9f60c0b969f/zigux/tests/phase12_virtio_scsi.zig`
  - bytes: `14139`
  - sha256: `eb8b048d8ae06844e7da6655ddee49714b09007b82d5ee5cfa95e0a87465ce57`
- `zigux/tests/phase12_virtio_scsi_manifest.json`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/5ecf3870d48d43e7a718b620b02ab9f60c0b969f/zigux/tests/phase12_virtio_scsi_manifest.json`
  - bytes: `7510`
  - sha256: `454b8bd717da024e1f740ce6947e1f95779ff45d4bd5deee61ce48703a7dd440`
- `zigux/tests/phase12_virtio_scsi_survey.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/5ecf3870d48d43e7a718b620b02ab9f60c0b969f/zigux/tests/phase12_virtio_scsi_survey.zig`
  - bytes: `22396`
  - sha256: `a00a49e482e0eebbdaed67659c2a9e91978d92c4a64a96022e22a7649ce2fbe5`
- `zigux/tests/phase12_build.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/5ecf3870d48d43e7a718b620b02ab9f60c0b969f/zigux/tests/phase12_build.zig`
  - bytes: `7155`
  - sha256: `9be3b9c1d1896f4cf70511d37ccf956e2d0561624d06d7c47223dd9b34fb6030`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/5ecf3870d48d43e7a718b620b02ab9f60c0b969f/Documentation/zigux/phase12-virtio-scsi-slice.md`
  - bytes: `2242`
  - sha256: `5e763869076a06bf66ba409cb74a96226f0feebe048f032dda699bb3b79508f0`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/5ecf3870d48d43e7a718b620b02ab9f60c0b969f/Documentation/zigux/phase12-virtio-scsi-survey.md`
  - bytes: `6284`
  - sha256: `3c28fd14b7272b80a5091616438eeee9b1f1019b66e4732da36e6b22415dfe36`
- `scripts/zigux/validate-phase12.py`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/5ecf3870d48d43e7a718b620b02ab9f60c0b969f/scripts/zigux/validate-phase12.py`
  - bytes: `17504`
  - sha256: `c112e63de625dfa70b4dfeaff6fcae4c39410542eda0972943fb820f026dc31a`
- `zigux/Makefile`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/5ecf3870d48d43e7a718b620b02ab9f60c0b969f/zigux/Makefile`
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

- inspected_master_head: `5ecf3870d48d43e7a718b620b02ab9f60c0b969f`
- shared_validator_command: `python3 scripts/zigux/validate-phase12.py`
- shared_validator_result: `PHASE12_VALIDATION=fail`
- shared_validator_missing_marker: `phase12_virtio_net_manifest.json:gap_count`
- focused_survey_command: `zig test zigux/tests/phase12_virtio_scsi_survey.zig`
- focused_survey_result: `All 1 tests passed.`
