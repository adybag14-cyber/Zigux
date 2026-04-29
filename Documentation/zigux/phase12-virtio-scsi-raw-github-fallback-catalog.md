# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This catalog records the exact read-only GitHub fallback coverage verified for `P12-L09` when connector-backed reads are flaky or incomplete.

## Verified head

- lane: `P12-L09`
- phase: `Phase 12`
- verified_master_head: `7d653d8c5e57207763c07c1b1d020b514738c7f3`
- verification_scope: commit-pinned raw file reads plus the three public tree entry points needed to inspect the bounded `virtio_scsi` lane

## Tree entry points

- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/drivers/scsi`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/Documentation/zigux`
- `200` `https://github.com/adybag14-cyber/Zigux/tree/master/zigux/tests`

## Commit-pinned raw coverage

- `drivers/scsi/virtio_scsi.c`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/7d653d8c5e57207763c07c1b1d020b514738c7f3/drivers/scsi/virtio_scsi.c`
  - bytes: `29183`
  - sha256: `b5c783aa262dea9a3eb235ed41b026ad96e12a58eafeee833aaa86daae4bf688`
- `drivers/scsi/virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/7d653d8c5e57207763c07c1b1d020b514738c7f3/drivers/scsi/virtio_scsi.zig`
  - bytes: `16330`
  - sha256: `33e370bbec7c6bfaa6e51dffcea3950b011e64ecbd29175ee2743c7050bb1910`
- `zigux/tests/phase12_virtio_scsi.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/7d653d8c5e57207763c07c1b1d020b514738c7f3/zigux/tests/phase12_virtio_scsi.zig`
  - bytes: `20224`
  - sha256: `c2b854ef12e6388a790f6876b57b92241031cbb69c3ec7354512eab963ecb5ea`
- `zigux/tests/phase12_virtio_scsi_manifest.json`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/7d653d8c5e57207763c07c1b1d020b514738c7f3/zigux/tests/phase12_virtio_scsi_manifest.json`
  - bytes: `8815`
  - sha256: `b78911a5f739259b758ece4f7f43f09ea5cc7c75588b5a58a2d8fe45e691b8ad`
- `zigux/tests/phase12_virtio_scsi_survey.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/7d653d8c5e57207763c07c1b1d020b514738c7f3/zigux/tests/phase12_virtio_scsi_survey.zig`
  - bytes: `26571`
  - sha256: `e12401f490139958444c4a5be3dd35905ea6c381c81f8f5d5d231898a32408db`
- `zigux/tests/phase12_build.zig`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/7d653d8c5e57207763c07c1b1d020b514738c7f3/zigux/tests/phase12_build.zig`
  - bytes: `7155`
  - sha256: `9be3b9c1d1896f4cf70511d37ccf956e2d0561624d06d7c47223dd9b34fb6030`
- `Documentation/zigux/phase12-virtio-scsi-slice.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/7d653d8c5e57207763c07c1b1d020b514738c7f3/Documentation/zigux/phase12-virtio-scsi-slice.md`
  - bytes: `2909`
  - sha256: `c168ca3572f6c1756955ae9f01fcc56e39df477cc2fe1ee79a60be482b1fc5c0`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/7d653d8c5e57207763c07c1b1d020b514738c7f3/Documentation/zigux/phase12-virtio-scsi-survey.md`
  - bytes: `7411`
  - sha256: `adde5f101084dcd4c571bbc0b645d6fa95805e22b5a9f67828582e68664b8ad`
- `scripts/zigux/validate-phase12.py`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/7d653d8c5e57207763c07c1b1d020b514738c7f3/scripts/zigux/validate-phase12.py`
  - bytes: `26685`
  - sha256: `13bc19ceeb14f6807e01352f30f6fbed3e64ac34541aa4437ea28bc82e5674f8`
- `zigux/Makefile`
  - url: `https://raw.githubusercontent.com/adybag14-cyber/Zigux/7d653d8c5e57207763c07c1b1d020b514738c7f3/zigux/Makefile`
  - bytes: `8020`
  - sha256: `2a4fa2e382cb683d486fae1b503a8778d28b4d3862cb18b3c5cfcfb7618d941d`

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

- inspected_master_head: `7d653d8c5e57207763c07c1b1d020b514738c7f3`
- shared_validator_command: `python3 scripts/zigux/validate-phase12.py`
- shared_validator_result: `PHASE12_VALIDATION=fail`
- shared_validator_missing_markers:
  - `review_checklist:if the change touches the shared Phase 12 libbpf snapshot packet, do `scripts/zigux/check-phase12-libbpf-snapshot.py`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, and `tools/lib/bpf/zigux_segments/manifest.json` still agree on the same bounded five-file reproducibility packet and exact surveyed commit instead of leaving repeat-run stability in run memory only?`
  - `phase12_nvme_pci_manifest.json:lane_key`
  - `phase12_libbpf_snapshot_fixture:bytes:zigux/tests/phase12_libbpf_segments.zig`
  - `phase12_libbpf_snapshot_fixture:sha256:zigux/tests/phase12_libbpf_segments.zig`
- focused_survey_command: `zig test zigux/tests/phase12_virtio_scsi_survey.zig`
- focused_survey_result: `All 1 tests passed.`

## Current replay note

These fields record the last replay performed for this pinned fallback packet. They can lag the live `master` head until `P12-L09` or `P12-L12` refreshes the exact inspected-head evidence again.

- current_master_replay_head: `7d653d8c5e57207763c07c1b1d020b514738c7f3`
- current_shared_validator_command: `python3 scripts/zigux/validate-phase12.py`
- current_shared_validator_result: `PHASE12_VALIDATION=fail`
- current_focused_survey_command: `zig test zigux/tests/phase12_virtio_scsi_survey.zig`
- current_shared_validator_missing_markers:
  - `review_checklist:if the change touches the shared Phase 12 libbpf snapshot packet, do `scripts/zigux/check-phase12-libbpf-snapshot.py`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, and `tools/lib/bpf/zigux_segments/manifest.json` still agree on the same bounded five-file reproducibility packet and exact surveyed commit instead of leaving repeat-run stability in run memory only?`
  - `phase12_nvme_pci_manifest.json:lane_key`
  - `phase12_libbpf_snapshot_fixture:bytes:zigux/tests/phase12_libbpf_segments.zig`
  - `phase12_libbpf_snapshot_fixture:sha256:zigux/tests/phase12_libbpf_segments.zig`
- current_focused_survey_result: `All 1 tests passed.`
