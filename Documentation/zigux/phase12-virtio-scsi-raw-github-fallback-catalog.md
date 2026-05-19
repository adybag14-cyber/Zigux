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
- reminder-only validator wrapper vocabulary until it returns: `make -C zigux phase12-validate`

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
- those current-master survey companions now name `captureHostLimitSummary()`, `captureQueueDepthSummary()`, `captureControlPathGovernanceSummary()`, `captureRequestSubmitSequencingSummary()`, `captureCompletionHandbackSummary()`, `captureCommandBufferOwnershipSummary()`, `captureIoQueueMapSummary()`, `recoveryQueuePlan()`, `recoveryQueueDepthSummary()`, `recoveryIoQueueMapSummary()`, `recoveryEventBufferOwnershipSummary()`, `recoveryControlPathGovernanceSummary()`, `recoveryRequestQueueRestoreSummary()`, and `recoveryHostScanSummary()` as landed bounded review surfaces on current `master`
- this catalog remains pinned to `ee64eec272a352da1d967999c99bb3c3560c9b97` for direct raw replay, so treat those newer control-path-governance, queue-submit, completion-handback, command-buffer, io-map, request-queue-restore, and host-scan restore summaries as shared-tree current-master survey companions rather than as claims that the older pinned raw replay already exposes every one of those later functions

## Roadmap Gap Snapshot
- The roadmap still treats `drivers/scsi/virtio_scsi.c` as a complex production-driver target rather than a small helper lane.
- The pinned direct raw replay still covers a bounded in-memory `drivers/scsi/virtio_scsi.zig` starter around queue-family planning and probe-config snapshot coverage.
- Current `master` now extends that bounded packet through shared-tree survey companions that cover host-limit clamping, queue-depth clamping, control-path governance, request-submit sequencing, completion-handback sequencing, command-buffer ownership planning, io-map summaries, repeated transport-reset recovery-generation accounting, restore queue rebind ordering, restore-time control-path governance review, recovery event rearm ordering, restore-time event-buffer ownership, request-queue restore ordering, host-scan restore ordering, and rollback-facing recovery summaries without claiming live DMA-backed request execution.
- That packet is still intentionally below the roadmap's deeper driver surface: no live command submission or completion helpers, no TMF or async notification handling, no virtqueue buffer ownership or kick flow, no `scsi_add_host()` or `scsi_scan_host()` lifecycle parity, no blk-mq queue mapping, and no DMA-backed request or response buffer handling.
- Treat this catalog as the degraded-read pointer for that bounded gap, not as evidence that the broader SCSI host and transport-delivery roadmap work has landed.

## Review Use
- use this file only as a read-only fallback index; it does not add a new replay surface
- keep the same shared Phase 12 route vocabulary explicit beside this catalog: `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, and `make -C zigux phase12`; on current `master` those shared routes are support-bundle evidence only and no longer imply that the `virtio_scsi` raw-read anchors themselves are wired through `zigux/tests/phase12_build.zig`
- keep the focused full replay explicit too: `zigux/tests/phase12_virtio_scsi.zig` remains the direct bounded starter replay companion even though the current shared `test` step in `zigux/tests/phase12_build.zig` now targets only the `virtio_net` queue-resume and transmit-recycle packet
- keep the current `virtio_scsi` fallback anchors explicit too: `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` remain directly readable driver-local raw-read anchors for this packet, but current `zigux/tests/phase12_build.zig` no longer places them inside the shared `smoke` step
- keep the fallback split honest: this file is the only commit-pinned direct replay artifact, while the newer `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` remain shared-tree current-master survey companions for the widened queue-submit-completion-and-recovery packet, `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than commit-pinned fallback artifacts, and the reminder-only `make -C zigux phase12-validate` wrapper vocabulary keeps `scripts/zigux/validate-phase12.py` plus `scripts/zigux/check-phase12-release-readiness-packet.py` inside the validator-first support bundle rather than turning them into standalone direct replay routes while current `zigux/Makefile` still omits that wrapper on `master`
- keep `zigux/tests/phase12_build.zig`, `scripts/zigux/check-build-only-phase12-surface.py`, and `.github/workflows/zigux-bootstrap.yml` visible as shared-tree raw-read anchors for the shipped support bundle rather than treating them as extra commit-pinned artifacts or as proof that the shared `phase12-smoke` and `phase12-test` routes still replay the `virtio_scsi` shard
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening any PMO wording around this artifact

## Boundaries
- this note must not treat the reminder-only `make -C zigux phase12-validate` wrapper vocabulary as a second direct replay packet, a focused `virtio_scsi`-only replay, a cross-build replay, or a promotion of the `scripts/zigux/validate-phase12.py` helper beyond the validator-first support bundle
- this note must not imply a broader shared `check-phase12-*.py` family beyond `scripts/zigux/check-build-only-phase12-surface.py` and `scripts/zigux/check-phase12-release-readiness-packet.py`
- this note must keep control-path governance and request-queue-restore coverage described as current-master survey-companion evidence only, not as proof that the older pinned raw replay already exposes those later recovery surfaces
- this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- this note is a public-read pointer catalog only, not a release-closure claim and not a second survey note

## Current-Master Evidence Snapshot
- exact coverage evidence refreshed on `2026-05-19` against live current `master`
- public GitHub blob-page readback still confirmed the core `virtio_scsi` packet files are present on `master`, including `drivers/scsi/virtio_scsi.zig` (`861 lines (782 loc) · 33.1 KB`), `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig`, even though direct raw-URL or contents-bridge reads for some of those paths were flaky in this runtime
- the current GitHub contents bridge directly reread these bounded support surfaces on `master`: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` -> blob `eefdae4bc9645e03ee6dfb93764fe4b27f13be3c`, `Documentation/zigux/phase12-virtio-scsi-slice.md` -> blob `f458ad27ad470c701b7644a5ea0fe90b85aeb84b`, `Documentation/zigux/README.md` -> blob `859b6b7b2feaa5bf16f0dacf21c960b18a065493`, `zigux/tests/README.md` -> blob `a56644cd37d334aae14b6b3a014d7761e1d980ae`, `scripts/zigux/README.md` -> blob `5b066d41b80c380e516b3c6afd878b85af593800`, `zigux/tests/phase12_build.zig` -> blob `18a1f2bfbb78a7c3b871fba93b33f88cacf710d7`, `zigux/Makefile` -> blob `79c077334a5e3c67868081f4c9ae71e0e3cde541`, `scripts/zigux/check-phase12-release-readiness-packet.py` -> blob `a2477ccf64a6874768662d5e8dae1b2b19c88371`, `.github/workflows/zigux-bootstrap.yml` -> blob `8f373d8734694964dd63d754c4889fe82bd558b9`, and `zigux/tests/phase12_virtio_scsi_survey.zig` -> blob `bc1e16139dd6db23a03579e779d591099a32be0f`
- that exact readback now shows a sharper split than the older `2026-05-15` snapshot: `zigux/tests/phase12_build.zig` blob `18a1f2bfbb78a7c3b871fba93b33f88cacf710d7` currently wires only `phase12_virtio_net_queue_resume.zig` and `phase12_virtio_net_transmit_recycle.zig` through both shared `smoke` and shared `test`, while `zigux/Makefile` blob `79c077334a5e3c67868081f4c9ae71e0e3cde541` still exposes `phase12-smoke`, `phase12-test`, and `phase12` and still omits `phase12-validate`
- current authoritative packet truth now lives in the shared-tree survey companions and validator surfaces reread for this lane: `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `scripts/zigux/check-phase12-virtio-scsi-packet.py`, `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`
- this exact-evidence section is therefore still a historical fallback snapshot for the pinned raw-read packet, while the refreshed bullets above now record the current support-bundle split truthfully beside the same pinned replay point
- keeping this distinction explicit preserves the existing split: this catalog stays pinned to `ee64eec272a352da1d967999c99bb3c3560c9b97` for direct raw replay, the direct `virtio_scsi` file family remains present as driver-local public-read anchors, and the shared current-master build or workflow bundle above is support evidence only rather than proof that the shared `phase12-smoke` or `phase12-test` routes currently replay the `virtio_scsi` raw-read shard
