# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This note is the commit-pinned public-read fallback companion for the older `virtio_scsi` direct replay packet.

## Status
- `PHASE12_STATUS=archival-raw-read-fallback`
- `PHASE12_SLICE=virtio-scsi-raw-github-fallback-catalog`
- commit pin: `ee64eec272a352da1d967999c99bb3c3560c9b97`
- commit-pin role: this is the last raw-read replay point explicitly rechecked through this catalog, not a claim that current `master` still serves the same driver-local file family
- packet role: read-only fallback artifact for public inspection when normal repository reads are degraded
- survey-backed anchor: `zigux/tests/phase12_virtio_scsi_manifest.json`
- fallback overview companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- verifier and replay companions on current `master`: `scripts/zigux/check-phase12-virtio-scsi-packet.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`

## Commit-Pinned Paths
Base raw URL prefix:
`https://raw.githubusercontent.com/adybag14-cyber/Zigux/ee64eec272a352da1d967999c99bb3c3560c9b97/`

- historical starter: `drivers/scsi/virtio_scsi.zig`
- historical direct replay: `zigux/tests/phase12_virtio_scsi.zig`
- historical syntax lab: `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- historical repeated replan gate: `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`
- historical repeated rollback gate: `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`
- survey note: `Documentation/zigux/phase12-virtio-scsi-survey.md`
- slice note: `Documentation/zigux/phase12-virtio-scsi-slice.md`
- fixture manifest: `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`
- survey manifest: `zigux/tests/phase12_virtio_scsi_manifest.json`
- survey replay: `zigux/tests/phase12_virtio_scsi_survey.zig`
- survey gate: `scripts/zigux/check-phase12-virtio-scsi-packet.py`
- shared build wiring: `zigux/tests/phase12_build.zig`
- Linux-style route owner: `zigux/Makefile`

## Current-Master Evidence Snapshot
- exact coverage evidence refreshed on `2026-05-21` against live current `master`
- current `master` still carries this fallback catalog, the survey note, the slice note, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `scripts/zigux/check-phase12-virtio-scsi-packet.py`, `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`
- current `master` no longer serves `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, or `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`
- `zigux/tests/phase12_build.zig` now wires the `virtio_net` queue-resume, transmit-recycle, receive-refill replay, post-reset replay, throughput-parity, and survey-gate tests through both shared `smoke` and shared `test`
- `.github/workflows/zigux-bootstrap.yml` now replays the current shared Phase 12 support bundle in the exact order `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `python3 scripts/zigux/validate-phase12.py`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, then `make -C zigux phase12`
- current authoritative packet truth now lives in the shared-tree survey companions and validator surfaces reread for this lane

## Roadmap Gap Snapshot
- the roadmap still treats `drivers/scsi/virtio_scsi.c` as a complex production-driver target rather than a small helper lane
- the pinned raw replay still documents a bounded historical starter around queue layout and recovery planning
- current `master` now keeps only rollback evidence for that packet and does not currently serve a driver-local starter, direct replay, syntax lab, or rollback gates
- current `master` still does not claim live command submission or completion helpers, TMF or async notification handling, virtqueue buffer ownership or kick flow, `scsi_add_host()` or `scsi_scan_host()` lifecycle parity, blk-mq queue mapping, or DMA-backed request or response buffer handling
- treat this catalog as archival fallback evidence, not as proof that the broader SCSI host or transport-delivery roadmap work has landed on current `master`

## Review Use
- use this file only as a read-only archival index; it does not add a new replay surface
- keep the fallback split explicit: this file is archival commit-pinned history only for the historical replay artifact, while the current-master survey note, fixture manifest, survey manifest, survey replay, survey gate, validator, shared build route, and `zigux/Makefile` are rollback evidence only
- rerun `python3 scripts/zigux/check-phase12-virtio-scsi-packet.py` before widening any PMO wording around this artifact
- exact current shared support-bundle and replay order is `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-build-only-phase12-surface.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `python3 scripts/zigux/validate-phase12.py`, `make -C zigux phase12-smoke`, `make -C zigux phase12-test`, then `make -C zigux phase12`
- `make -C zigux phase12-validate` stays reminder-only validator wrapper vocabulary until that wrapper returns on current `master`

## Boundaries
- this note must not imply that current `master` still ships the historical `virtio_scsi` driver-local replay family
- this note must not treat the archival raw URL set as a current-master validation route
- this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- this note is a public-read pointer catalog only, not a release-closure claim and not a second survey note
