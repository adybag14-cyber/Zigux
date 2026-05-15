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
- current `master` now also carries `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` as shared-tree review surfaces for the newer bounded queue-submit-completion-and-recovery packet
- those current-master survey companions now name `captureHostLimitSummary()`, `captureQueueDepthSummary()`, `captureRequestSubmitSequencingSummary()`, `captureCompletionHandbackSummary()`, `captureCommandBufferOwnershipSummary()`, `captureIoQueueMapSummary()`, `recoveryQueuePlan()`, `recoveryQueueDepthSummary()`, `recoveryIoQueueMapSummary()`, `recoveryEventBufferOwnershipSummary()`, and `recoveryHostScanSummary()` as landed bounded review surfaces on current `master`
- this catalog remains pinned to `ee64eec272a352da1d967999c99bb3c3560c9b97` for direct raw replay, so treat those newer queue-submit, completion-handback, command-buffer, io-map, and host-scan restore summaries as current-master survey companions rather than as claims that the older pinned raw replay already exposes every one of those later functions

## Roadmap Gap Snapshot
- The roadmap still treats `drivers/scsi/virtio_scsi.c` as a complex production-driver target rather than a small helper lane.
- The pinned direct raw replay still covers a bounded in-memory `drivers/scsi/virtio_scsi.zig` starter around queue-family planning and probe-config snapshot coverage.
- Current `master` now extends that bounded packet through shared-tree survey companions that cover host-limit clamping, queue-depth clamping, request-submit sequencing, completion-handback sequencing, command-buffer ownership planning, io-map summaries, repeated transport-reset recovery-generation accounting, restore queue rebind ordering, recovery event rearm ordering, restore-time event-buffer ownership, host-scan restore ordering, and rollback-facing recovery summaries without claiming live DMA-backed request execution.
- That packet is still intentionally below the roadmap's deeper driver surface: no live command submission or completion helpers, no TMF or async notification handling, no virtqueue buffer ownership or kick flow, no `scsi_add_host()` or `scsi_scan_host()` lifecycle parity, no blk-mq queue mapping, and no DMA-backed request or response buffer handling.
- Treat this catalog as the degraded-read pointer for that bounded gap, not as evidence that the broader SCSI host and transport-delivery roadmap work has landed.

## Review Use
- use this file only as a read-only fallback index; it does not add a new replay surface
- keep the same smoke-first release order explicit beside this catalog: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`
- keep the focused direct packet explicit too: the current smoke shard for this driver is `zigux/tests/phase12_virtio_scsi.zig` plus `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- keep the fallback split honest: this file is the only commit-pinned direct replay artifact, while the newer `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` remain shared-tree current-master survey companions for the widened queue-submit-completion-and-recovery packet, `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than commit-pinned fallback artifacts, and the shipped `make -C zigux phase12-validate` route keeps `scripts/zigux/validate-phase12.py` plus `scripts/zigux/check-phase12-release-readiness-packet.py` inside the validator-first support bundle rather than turning them into standalone direct replay routes
- keep `zigux/tests/phase12_build.zig`, `scripts/zigux/check-build-only-phase12-surface.py`, and `.github/workflows/zigux-bootstrap.yml` visible as shared-tree raw-read anchors for the shipped smoke-first packet rather than treating them as extra commit-pinned artifacts
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening any PMO wording around this artifact

## Boundaries
- this note must not treat the shipped `make -C zigux phase12-validate` route as a second direct replay packet, a focused `virtio_scsi`-only replay, a cross-build replay, or a promotion of the `scripts/zigux/validate-phase12.py` helper beyond the validator-first support bundle
- this note must not imply a broader shared `check-phase12-*.py` family beyond `scripts/zigux/check-build-only-phase12-surface.py` and `scripts/zigux/check-phase12-release-readiness-packet.py`
- this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- this note is a public-read pointer catalog only, not a release-closure claim and not a second survey note

## Current-Master Exact Coverage Evidence
- public `master` packet rechecked immediately before this note refresh on `2026-05-15`; this run's contents read path did not expose one authoritative branch-head commit, so the evidence below records exact current blob SHAs instead.
- the same twelve covered current-master packet paths remain present beside this commit-pinned raw replay note:
  - `drivers/scsi/virtio_scsi.zig` -> blob `aef0c4205b7d99f7451ee6011adf63b6ac5220f5`
  - `Documentation/zigux/phase12-virtio-scsi-slice.md` -> blob `346ea74e682322135eeb56ee2532e663f32188b2`
  - `Documentation/zigux/phase12-virtio-scsi-survey.md` -> blob `a1fa942a65be4611e2fe008c84faa628ac8a092a`
  - `Documentation/zigux/README.md` -> blob `78a2a98c221831105b48986aad48e91d4884a1d4`
  - `zigux/tests/README.md` -> blob `bf048e32d25df0fb822789e7af1a30d91a3035d4`
  - `scripts/zigux/README.md` -> blob `4e47c9ed4a7d5c9398f58944237bcd302b49a073`
  - `zigux/tests/phase12_build.zig` -> blob `d5746e7fc71d926e8e72310f29bca9c9fcdad5fc`
  - `zigux/tests/phase12_virtio_scsi.zig` -> blob `f829de9b39576c67e81e75fe1e9d849e583db62f`
  - `zigux/tests/phase12_virtio_scsi_syntax_lab.zig` -> blob `89173ebd7f2c66d9673375e8d15f32cb645b60db`
  - `zigux/tests/phase12_virtio_scsi_survey.zig` -> blob `c99597ec217e9d456e658a9942ebb2eaef535203`
  - `zigux/tests/phase12_virtio_scsi_manifest.json` -> blob `6e0ed13c124baa6d2e845cd954ccdf93a148a4ca`
  - `zigux/Makefile` -> blob `3e19e8da0be49eaa7a4f75d29d324648261aad8e`
- current-master support-material boundary rechecked beside the same packet:
  - `scripts/zigux/check-phase12-release-readiness-packet.py` -> blob `524041f460157539a034f7dd9fd98ec1423d4f6a`
  - `scripts/zigux/validate-phase12.py` -> blob `c548ea93121984ab3926c38ab64fbaf1022c0343`
  - `.github/workflows/zigux-bootstrap.yml` -> blob `c345316a52e250a3eaf66b2d0b121a61872117f8`
- this exact-evidence recheck preserves the existing split: this catalog stays pinned to `ee64eec272a352da1d967999c99bb3c3560c9b97` for direct raw replay, while the blob list above records what the broader current-master packet looked like immediately before this note refresh.
