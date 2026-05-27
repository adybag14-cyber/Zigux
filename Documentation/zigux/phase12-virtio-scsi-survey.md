# Phase 12 virtio_scsi Survey
- `PHASE12_STATUS=rollback-evidence-only-live-starter-missing`
- `PHASE12_LANE=P12-L09`
- verified on: `2026-05-24`
- roadmap anchor: `drivers/scsi/virtio_scsi.c`

## Current-master reread
- current `master` still carries the rollback-note and fallback evidence surfaces for this lane: `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_virtio_scsi_survey_build.zig`, `scripts/zigux/check-phase12-virtio-scsi-packet.py`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile`
- current `master` no longer serves the earlier driver-local replay family: `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, and `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`
- rollback owner: `P12-L09` keeps the active virtio_scsi survey packet honest about that missing live surface instead of pretending the older bounded replay still ships on `master`

## Why this stays rollback-only
- the roadmap still places `drivers/scsi/virtio_scsi.c` in the Phase 12 complex-driver tranche, so DMA-safe request ownership, queueing correctness, throughput and recovery parity, and segmented rollout still need a returned driver-local starter before live Zigux storage claims are credible
- the shared `zigux/tests/phase12_build.zig` route now covers the `virtio_net` queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate tests together with one bounded NVMe direct replay as support-bundle evidence rather than replaying a `virtio_scsi` lane-local packet
- `make -C zigux phase12-validate`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-test`, and `make -C zigux phase12` are therefore support-bundle reminders for this lane, not proof that current `master` once again serves a direct `virtio_scsi` runtime replay

## What the survey packet now guards
- `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json` and `zigux/tests/phase12_virtio_scsi_manifest.json` keep the rollback-only file-presence contract explicit
- `zigux/tests/phase12_virtio_scsi_survey.zig` fails closed if current `master` starts claiming the old replay files are present again or if the surviving rollback evidence drifts out of sync
- `zigux/tests/phase12_virtio_scsi_survey_build.zig` keeps the dedicated survey-build replay machine-checkable
- `scripts/zigux/check-phase12-virtio-scsi-packet.py` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` keep the rollback-only split machine-checkable from the scripts side and the raw-read fallback side

## Next bounded step
- leave this lane in survey/fallback maintenance mode until current `master` regains one real `virtio_scsi` driver-local surface; when that happens, rebuild the packet around that returned surface instead of widening directly into speculative runtime storage work
