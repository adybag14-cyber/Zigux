# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This note is the commit-pinned public-read fallback companion for the shipped `virtio_scsi` packet inside the active Phase 12 release surface.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-scsi-raw-github-fallback-catalog`
- commit pin: `ee64eec272a352da1d967999c99bb3c3560c9b97`
- commit-pin role: this is the last raw-read replay point explicitly rechecked through this catalog, not an implied claim that every newer unrelated `master` edit has already been reread here
- packet role: read-only fallback artifact for public inspection when normal repository reads are degraded
- survey-backed anchor: `zigux/tests/phase12_virtio_scsi_manifest.json`
- release companions: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`
- fallback overview companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- verifier and replay companions: `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`
- `make -C zigux phase12-validate`

## Commit-Pinned Paths
Base raw URL prefix:
`https://raw.githubusercontent.com/adybag14-cyber/Zigux/ee64eec272a352da1d967999c99bb3c3560c9b97/`

- starter: `drivers/scsi/virtio_scsi.zig`
- slice note: `Documentation/zigux/phase12-virtio-scsi-slice.md`
- survey note: `Documentation/zigux/phase12-virtio-scsi-survey.md`
- docs-root reminder: `Documentation/zigux/README.md`
- tests-root reminder: `zigux/tests/README.md`
- scripts-root reminder: `scripts/zigux/README.md`
- shared build wiring: `zigux/tests/phase12_build.zig`
- direct smoke replay: `zigux/tests/phase12_virtio_scsi.zig`
- direct syntax-lab replay: `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- survey replay: `zigux/tests/phase12_virtio_scsi_survey.zig`
- manifest anchor: `zigux/tests/phase12_virtio_scsi_manifest.json`
- Linux-style route owner: `zigux/Makefile`

## Current-Master Survey Drift Since Commit Pin
- current `master` now also carries `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` as shared-tree current-master survey companions for the newer bounded queue-submit-completion-and-recovery packet
- those current-master survey companions now name `captureHostLimitSummary()`, `captureQueueDepthSummary()`, `captureRequestSubmitSequencingSummary()`, `captureCompletionHandbackSummary()`, `captureCommandBufferOwnershipSummary()`, `captureIoQueueMapSummary()`, `recoveryQueuePlan()`, `recoveryQueueDepthSummary()`, `recoveryIoQueueMapSummary()`, `recoveryEventBufferOwnershipSummary()`, and `recoveryHostScanSummary()` as landed bounded review surfaces on current `master`
- this catalog remains pinned to `ee64eec272a352da1d967999c99bb3c3560c9b97` for direct raw replay, so treat those newer queue-submit, completion-handback, command-buffer, io-map, and host-scan restore summaries as shared-tree current-master survey companions rather than as claims that the older pinned raw replay already exposes every one of those later functions

## Roadmap Gap Snapshot
- The roadmap still treats `drivers/scsi/virtio_scsi.c` as a complex production-driver target rather than a small helper lane.
- The pinned direct raw replay still covers a bounded in-memory `drivers/scsi/virtio_scsi.zig` starter around queue-family planning and probe-config snapshot coverage.
- Current `master` now extends that bounded packet through shared-tree survey companions that cover host-limit clamping, queue-depth clamping, request-submit sequencing, completion-handback sequencing, command-buffer ownership planning, io-map summaries, repeated transport-reset recovery-generation accounting, restore queue rebind ordering, recovery event rearm ordering, restore-time event-buffer ownership, host-scan restore ordering, and rollback-facing recovery summaries without claiming live DMA-backed request execution.
- That packet is still intentionally below the roadmap's deeper driver surface: no live command submission or completion helpers, no TMF or async notification handling, no virtqueue buffer ownership or kick flow, no `scsi_add_host()` or `scsi_scan_host()` lifecycle parity, no blk-mq queue mapping, and no DMA-backed request or response buffer handling.
- Treat this catalog as the degraded-read pointer for that bounded gap, not as evidence that the broader SCSI host and transport-delivery roadmap work has landed.

## Review Use
- use this file only as a read-only fallback index; it does not add a new replay surface
- keep the same smoke-first release order explicit beside this catalog: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`
- keep the focused full replay explicit too: `zigux/tests/phase12_virtio_scsi.zig` remains the direct bounded starter replay that the shared `test` step layers in after the smoke shard
- keep the current smoke shard explicit too: `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` are the shipped driver-local raw-read anchors inside the current `smoke` step
- keep the fallback split honest: this file is the only commit-pinned direct replay artifact, while the newer `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` remain shared-tree current-master survey companions for the widened queue-submit-completion-and-recovery packet, `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than commit-pinned fallback artifacts, and the shipped `make -C zigux phase12-validate` route keeps `scripts/zigux/validate-phase12.py` plus `scripts/zigux/check-phase12-release-readiness-packet.py` inside the validator-first support bundle rather than turning them into standalone direct replay routes
- keep `zigux/tests/phase12_build.zig`, `scripts/zigux/check-build-only-phase12-surface.py`, and `.github/workflows/zigux-bootstrap.yml` visible as shared-tree raw-read anchors for the shipped smoke-first packet rather than treating them as extra commit-pinned artifacts
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening any PMO wording around this artifact

## Boundaries
- this note must not treat the shipped `make -C zigux phase12-validate` route as a second direct replay packet, a focused `virtio_scsi`-only replay, a cross-build replay, or a promotion of the `scripts/zigux/validate-phase12.py` helper beyond the validator-first support bundle
- this note must not imply a broader shared `check-phase12-*.py` family beyond `scripts/zigux/check-build-only-phase12-surface.py` and `scripts/zigux/check-phase12-release-readiness-packet.py`
- this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- this note is a public-read pointer catalog only, not a release-closure claim and not a second survey note

## Current-Master Evidence Snapshot
- the exact-blob readback below is the last explicit historical current-master snapshot captured for this catalog on `2026-05-15`, not a standing claim that the live branch head still matches those same SHAs after later same-family survey-packet edits
- current authoritative packet truth now lives in the shared-tree survey companions and validator surfaces reread for this lane: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `scripts/zigux/check-phase12-virtio-scsi-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`
- this exact-evidence section is therefore a historical fallback snapshot for the pinned raw-read packet, while the newer shared-tree survey companions above remain the truthful source for live current-master packet state
- the same fifteen covered packet paths were present in that historical `2026-05-15` snapshot beside this commit-pinned raw replay note:
  - `drivers/scsi/virtio_scsi.zig` -> blob `aef0c4205b7d99f7451ee6011adf63b6ac5220f5`
  - `Documentation/zigux/phase12-virtio-scsi-slice.md` -> blob `346ea74e682322135eeb56ee2532e663f32188b2`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md` -> blob `9b10ef0cc480198547fad347d8b137755f190d68`
  - `Documentation/zigux/README.md` -> blob `38f2dd1097c630b5b7cc1b602b004a21911741fc`
  - `zigux/tests/README.md` -> blob `65bcef0c2a72a2ac4ca240b5085ea69e3fecb810`
  - `scripts/zigux/README.md` -> blob `00cea585750e34173e0a29982443b2a0a85b1d22`
  - `zigux/tests/phase12_build.zig` -> blob `817e868e544a63e021253d0f5b029ea8f751e6b2`
  - `zigux/tests/phase12_virtio_scsi.zig` -> blob `f829de9b39576c67e81e75fe1e9d849e583db62f`
  - `zigux/tests/phase12_virtio_scsi_syntax_lab.zig` -> blob `89173ebd7f2c66d9673375e8d15f32cb645b60db`
  - `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig` -> blob `0dcdfea49684b4af523c82a277a54e4362b308cd`
  - `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` -> blob `2d2582f7607a255ce8bd9ccdd6ed5d52b5c8ecca`
  - `zigux/tests/phase12_virtio_scsi_packet.zig` -> blob `db3fa0bb1ab8d4288ec95c48a76a8725b766b4d5`
  - `zigux/tests/phase12_virtio_scsi_survey.zig` -> blob `a74d5ff9c3fe97575f78b784af0459ec2468930a`
  - `zigux/tests/phase12_virtio_scsi_manifest.json` -> blob `dec20bc8cce036aef1a0a9353ed7370f3b681eb4`
  - `zigux/Makefile` -> blob `767510ae3aa2a2ad0e574e6ad2cddc5adb4ff40e`
- the same historical snapshot also recorded these support-material blobs:
  - `scripts/zigux/check-phase12-release-readiness-packet.py` -> blob `196cc338346d7ce39e88c8c45bb49cc04d2b08a1`
  - `scripts/zigux/validate-phase12.py` -> blob `6f95fa12c8813c494cace0e66cb06178c12ee9fb`
  - `.github/workflows/zigux-bootstrap.yml` -> blob `1ee77591a9bbf6b3b36060ba44f56f6e2fd929a0`
- keeping this distinction explicit preserves the existing split: this catalog stays pinned to `ee64eec272a352da1d967999c99bb3c3560c9b97` for direct raw replay, while the survey note, manifest, survey gate, packet checker, shared validator, and shared build surfaces above carry live current-master packet truth forward
