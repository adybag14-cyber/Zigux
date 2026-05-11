# Phase 12 Virtio SCSI Raw GitHub Fallback Catalog

This note is the commit-pinned public-read fallback companion for the shipped `virtio_scsi` slice inside the active Phase 12 release packet.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_SLICE=virtio-scsi-raw-github-fallback-catalog`
- commit pin: `a1b9a70eb33a41cdefdece794fb381b66f286432`
- packet role: read-only fallback artifact for public inspection when normal repository reads are degraded
- release companions: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`
- fallback overview companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- verifier and replay companions: `scripts/zigux/check-build-only-phase12-surface.py`, `zigux/tests/phase12_build.zig`, `zigux/Makefile`

## Commit-Pinned Paths
Base raw URL prefix:
`https://raw.githubusercontent.com/adybag14-cyber/Zigux/a1b9a70eb33a41cdefdece794fb381b66f286432/`

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

## Review Use
- use this file only as a read-only fallback index; it does not add a new replay surface
- keep this note aligned with the same smoke-first release order already recorded in `Documentation/zigux/phase12-release-sequencing.md`
- keep the fallback split honest: this file is commit-pinned, while `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than commit-pinned fallback artifacts
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening any PMO wording around this artifact

## Boundaries
- this note must not imply a shared `validate-phase12.py`, `check-phase12-*.py`, focused `virtio_scsi`-only replay, cross-build replay, or `phase12-validate` route that current `master` does not ship
- this note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`
- this note is a public-read pointer catalog only, not a release-closure claim
