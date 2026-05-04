# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This catalog records the exact read-only GitHub fallback coverage first verified for the historical `P12-L09` packet and still retained by the active `P12-L12` survey lane when connector-backed reads are flaky or incomplete.

## Verified head

- active_survey_lane: `P12-L12`
- historical_fallback_lane: `P12-L09`
- phase: `Phase 12`
- verified_master_head: `7d653d8c5e57207763c07c1b1d020b514738c7f3`
- verification_scope: commit-pinned raw file reads plus the three public tree entry points needed to inspect the bounded `virtio_scsi` lane

This packet is archival rather than live-head truth. As of the latest `P12-L12` degraded-mode recheck, public `master` had already advanced to `0bd402fd6ca83ba2ace6b21e9e57459401b631cd`, so the URLs, byte counts, and hashes below should be read as the last commit-pinned fallback evidence, not as the newest repo state. Exact head and hash refreshes belong to the dedicated fallback-evidence lanes.

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

## Rollback And Reversible Delivery

- owner: `Storage Driver Lane`
- rollback owner: `Storage Driver Lane`
- fallback path: keep `drivers/scsi/virtio_scsi.c` as the source of truth, keep this raw GitHub fallback packet pinned to its inspected commit for degraded readback, and if the shared storage-driver packet regresses, remove the direct `phase12-virtio-scsi-tests` plus `phase12-virtio-scsi-survey-tests` entries from `zigux/tests/phase12_build.zig` before widening any repair.
- reversible delivery evidence: this fallback packet is bounded to three public tree entry points, ten commit-pinned raw file reads, and archived validator plus survey replay notes around the existing C anchor, so degraded readback can be refreshed or narrowed again without inventing a second storage-driver implementation path or mutating the Linux source of truth.
- rollback drill: run `python3 scripts/zigux/validate-phase12.py`; if the shared packet only drifted in degraded-readback evidence, refresh `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` plus `Documentation/zigux/phase12-virtio-scsi-survey.md` first, otherwise remove the `phase12-virtio-scsi-tests` and `phase12-virtio-scsi-survey-tests` entries from `zigux/tests/phase12_build.zig`, keep `drivers/scsi/virtio_scsi.c` plus the bounded Zig starter unchanged, then rerun `make -C zigux phase12-validate` followed by `zig build test --build-file zigux/tests/phase12_build.zig --summary all`.

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

## Last bounded replay note

These fields record the last bounded replay note captured for this pinned fallback packet. They are historical replay evidence, not live-head truth for newer `master` commits, so treat any `PHASE12_VALIDATION=fail` marker or unavailable-toolchain note below as scoped to the exact replay head named here until a dedicated fallback-evidence lane refreshes it.

- current_master_replay_head: `9dab85059c6f56865ef2f981d2303049775c5001`
- current_shared_validator_command: `python3 scripts/zigux/validate-phase12.py`
- current_shared_validator_result: `PHASE12_VALIDATION=fail`
- current_shared_validator_missing_markers:
  - `docs_root_readme:Phase 12 notes`
  - `docs_root_readme:Documentation/zigux/phase12-virtio-net-survey.md`
  - `docs_root_readme:Documentation/zigux/phase12-nvme-pci-survey.md`
  - `docs_root_readme:Documentation/zigux/phase12-nvme-pci-slice.md`
  - `docs_root_readme:Documentation/zigux/phase12-virtio-scsi-survey.md`
  - `docs_root_readme:Documentation/zigux/phase12-virtio-scsi-slice.md`
  - `docs_root_readme:Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
  - `docs_root_readme:the active Phase 12 network-driver survey packet now keeps the bounded `drivers/net/virtio_net.zig` probe snapshot, queue-recovery summary, queue-resume summary, `hdr_len`, receive-path, and mergeable-refill helpers visible from the top-level docs index`
  - `docs_root_readme:the same top-level Phase 12 packet now also keeps the bounded `drivers/nvme/host/pci.zig` queue planner, PRP buffer-shape helper, and pointer-selection helper visible from the top-level docs index`
  - `docs_root_readme:the active Phase 12 storage-driver survey packet now keeps the bounded `drivers/scsi/virtio_scsi.zig` queue-layout, recovery, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map starters visible from the top-level docs index`
  - `docs_root_readme:`zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12` now keep that same storage-driver survey packet reviewable through the shared Phase 12 tranche`
  - `review_checklist:if the change is a Phase 12 complex-driver or heavy-helper slice, do `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, the four Phase 12 manifests, and the four Phase 12 survey notes still agree on the same bounded tranche, exact surveyed commits, approved roadmap destinations, shared replay contract, and explicit DMA versus object-model blocker posture?`
  - `review_checklist:if the change touches the shared Phase 12 degraded-workflow packet, do the workflow path, README notes, review checklist, and `zigux/tests/phase12_virtio_scsi_survey.zig` still agree that `make -C zigux phase12` runs the validator before the shared Zig replay?`
  - `review_checklist:if the change touches the shared Phase 12 tooling path, do `scripts/zigux/check-phase12-build-inventory.py`, `zigux/tests/phase12_build.zig`, `zigux/tests/fixtures/phase12_build_inventory.json`, and the shared Phase 12 manifests still agree on the exact shared build inventory instead of leaving the replay shape implicit?`
  - `review_checklist:if the change touches the shared Phase 12 libbpf snapshot packet, do `scripts/zigux/check-phase12-libbpf-snapshot.py`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, and `tools/lib/bpf/zigux_segments/manifest.json` still agree on the same bounded five-file reproducibility packet and exact surveyed commit instead of leaving repeat-run stability in run memory only?`
  - `phase12_build_fixture:expected_test_count_mismatch`
  - `phase12_nvme_pci_manifest.json:survey_note:surveyed_commit`
  - `phase12_libbpf_snapshot_fixture:sha256:tools/lib/bpf/zigux_segments/manifest.json`
- current_shared_build_command: `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- current_shared_build_result: `not replayed in this run because the attached Zig toolchain was unavailable`
- current_focused_survey_command: `zig test zigux/tests/phase12_virtio_scsi_survey.zig`
- current_focused_survey_result: `not replayed in this run because the attached Zig toolchain was unavailable`

## Latest repo-head recheck

This section preserves the last public-`master` comparison that was intentionally written back into this archival packet. It is historical maintenance evidence only, so newer `master` heads may exist even when the fields below still point at the then-current recheck.

Legacy validator compatibility note for the same bounded recheck:
- This section preserves the last connector-era `master` comparison that was intentionally written back into this archival packet.
- verification_method: connector-backed current-`master` reads of the same bounded lane packet, now expanded below with the paired public GitHub commit and tree reads.
- observed_behavior: current `master` still keeps this lane's degraded-readback contract archival rather than live-head truth; the fuller bullet below keeps the same archival boundary plus the preserved pinned heads and shared review surfaces explicit.
- replay_limit: this runtime could not clone the repository directly (`CONNECT tunnel failed, response 403`), so this recheck records exact live file-state evidence rather than a fresh local rerun of `python3 scripts/zigux/validate-phase12.py` or `zig test zigux/tests/phase12_virtio_scsi_survey.zig`.

- rechecked_public_master_head: `0bd402fd6ca83ba2ace6b21e9e57459401b631cd`
- verification_method: public GitHub `master` commit and tree reads plus connector-backed current-`master` blob reads of `drivers/scsi/virtio_scsi.zig` (`1654545a0295a9da5aa79b60b75cfaf752b818a6`), `zigux/tests/phase12_virtio_scsi_manifest.json` (`11fb71699b02373936609176f3a15ead1cede1fe`), `zigux/tests/phase12_virtio_scsi_survey.zig` (`4d672eed8445c561e035f86d5df575aee7a958c2`), `scripts/zigux/validate-phase12.py` (`d9a1f229ff22545a3b10bc86eb4c97b2d53764d8`), `zigux/tests/phase12_build.zig` (`c733b406ad12f0a84b44117b63cbe38a837942a7`), `zigux/tests/fixtures/phase12_build_inventory.json` (`9954a5c4d28491d1204515a64a167b543f1017a5`), `Documentation/zigux/README.md` (`4725cefc4d072a1613bd9c1bfd660e4c44f0343c`), `Documentation/zigux/review-checklist.md` (`ec040d79def34daf5de76a44197d2a80d1b05bf8`), `scripts/zigux/README.md` (`d89a0349bdd646ad17f1db0198f1e03f283e4de9`), and `zigux/Makefile` (`bb0a8f92950f8b1ede6499656109696c855971d7`)
- observed_behavior: public GitHub still exposes the same three tree entry points for `drivers/scsi`, `Documentation/zigux`, and `zigux/tests`; current `master` still keeps this lane's degraded-readback contract archival rather than live-head truth; the packet remains pinned to verified head `7d653d8c5e57207763c07c1b1d020b514738c7f3`; the preserved bounded replay note remains pinned to `9dab85059c6f56865ef2f981d2303049775c5001`; the current `drivers/scsi/virtio_scsi.zig` starter and paired `zigux/tests/phase12_virtio_scsi_manifest.json` still keep the same queue-layout, recovery, probe snapshot, host-limit summary, queue-depth summary, and io-queue-map surface explicit; the shared Phase 12 docs, checklist, Makefile, docs-root README, and scripts README still advertise the validator-first `make -C zigux phase12` flow; and `zigux/tests/fixtures/phase12_build_inventory.json` still records `Build Summary: 25/25 steps succeeded; 59/59 tests passed`.
- replay_limit: this runtime still could not clone the repository directly (`CONNECT tunnel failed, response 403`), and direct shell access to public raw GitHub URLs remained unavailable (`ENETUNREACH`), so this recheck combines public GitHub commit and tree reads with exact current file-state blob evidence instead of claiming a fresh local rerun of `python3 scripts/zigux/validate-phase12.py` or `zig test zigux/tests/phase12_virtio_scsi_survey.zig`.
- attached_zig_recovery_replay_head: `355b71d89807a217a6b7c405c996cbd623c48ca0`
- attached_zig_recovery_replay_command: `/workspace/.zig-local/p12-l11/zig-x86_64-linux-0.17.0-dev.87+9b177a7d2/zig build test --build-file /workspace/p12-l11-main-scratch/build.zig --summary all`
- attached_zig_recovery_replay_result: `historical scratch replay only; not rerun in this recheck`
- attached_zig_recovery_replay_scope: the last attached-zig recovery replay stayed bounded to the current `drivers/scsi/virtio_scsi.zig` queue-plan, queue-depth freeze or restore, and post-restore replanning surface with a scratch harness because this runtime still lacked a full repo-backed Phase 12 checkout; this latest recheck refreshed current-head file evidence only.
