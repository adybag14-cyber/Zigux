# Phase 12 Virtio SCSI Survey

This note records the current-master verification result for the bounded Phase 12 lane around `drivers/scsi/virtio_scsi.c`.

## Status
* `PHASE12_STATUS=rollback-evidence-only-live-starter-missing`
* `PHASE12_SLICE=virtio-scsi-roadmap-gap-survey`
* `PHASE12_LANE=P12-L09`
* scope: keep the virtio_scsi survey packet truthful when current `master` carries only survey, fallback, fixture, checker, dedicated survey-build, and shared support-bundle evidence while the driver-local starter and replay gates are absent
* verified on: `2026-05-24`
* repo-truth boundary:
  * `Documentation/zigux/phase12-virtio-scsi-slice.md`
  * `Documentation/zigux/phase12-virtio-scsi-survey.md`
  * `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
  * `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`
  * `zigux/tests/phase12_virtio_scsi_manifest.json`
  * `zigux/tests/phase12_virtio_scsi_survey.zig`
  * `zigux/tests/phase12_virtio_scsi_survey_build.zig`
  * `scripts/zigux/check-phase12-virtio-scsi-packet.py`
  * `zigux/tests/phase12_build.zig`
  * `zigux/Makefile`

## Why this lane still matters

The Phase 12 roadmap still names `drivers/scsi/virtio_scsi.c` as a complex production-driver target.
That anchor still needs DMA-safe abstractions, queueing correctness, throughput and recovery parity, and segmented rollout before any honest live-storage claim.

## Current-master verification
* current `master` still carries the survey note, slice note, fallback catalog, fixture manifest, survey manifest, survey gate, dedicated survey-build route, packet checker, shared `phase12` build bundle, and `zigux/Makefile`
* current `master` no longer serves `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, or `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`
* the dedicated `zigux/tests/phase12_virtio_scsi_survey_build.zig` route now reruns the rollback-only survey packet directly without claiming that any driver-local replay family has returned on `master`
* the shared `zigux/tests/phase12_build.zig` route still covers only the `virtio_net` queue-resume, receive-refill replay, transmit-recycle, post-reset replay, throughput-parity, and survey-gate tests as support-bundle evidence rather than replaying a `virtio_scsi` lane-local packet
* `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` therefore remains archival raw-read evidence only, not proof that current `master` still exposes the older direct replay family
* `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/fixtures/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, and `scripts/zigux/check-phase12-virtio-scsi-packet.py` now keep that rollback-only split machine-checkable

## Rollback and Reversible Delivery
* rollback owner: `P12-L09` keeps the active virtio_scsi survey packet, rollback-owner wording, and reversible-delivery evidence explicit while neighboring verification, implementation, and shared Phase 12 maintenance stay in their separate lanes
* fallback path: `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` remains the read-only degraded-read companion for the older direct replay packet and must not be treated as a current-master replay route
* reversible-delivery evidence: current `master` preserves the survey note, fixture manifest, survey manifest, survey gate, dedicated survey-build route, checker, shared build bundle, and `zigux/Makefile` as rollback evidence while the driver-local starter and replay gates remain absent
* rollback drill: when this packet moves, reread the survey note, slice note, fallback catalog, fixture manifest, survey manifest, survey gate, dedicated survey-build route, shared build route, and `zigux/Makefile`, then rerun `python3 scripts/zigux/check-phase12-virtio-scsi-packet.py`, `zig build test --build-file zigux/tests/phase12_virtio_scsi_survey_build.zig --summary all`, `zig test zigux/tests/phase12_virtio_scsi_survey.zig`, `make -C zigux phase12-validate`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-smoke`, `zig build test --build-file zigux/tests/phase12_build.zig --summary all`, `make -C zigux phase12-test`, and `make -C zigux phase12` before claiming that any driver-local replay surface has returned

## Truthful boundary

The truthful current boundary is:
* the roadmap still wants a bounded `virtio_scsi` lane in Phase 12
* current `master` preserves only rollback evidence for that lane through the survey note, fallback catalog, fixture manifest, survey manifest, survey gate, checker, dedicated survey-build route, and shared support-bundle surfaces
* current `master` does not currently serve the driver-local starter, direct replay, syntax lab, repeated replan gate, or repeated rollback gate that older documentation snapshots described
* current `master` still does not claim live DMA-safe request submission, descriptor population, virtqueue kicks, request completion handling, blk-mq tag wiring, `scsi_host` registration, TMF execution, event-queue runtime handling, or transport-backed host-scan recovery
* current `master` still does not claim throughput parity, reset replay parity, or a live storage data path

## Non-goals

This note does not claim:
* a current `drivers/scsi/virtio_scsi.zig` starter on `master`
* a current direct `zigux/tests/phase12_virtio_scsi.zig` replay or rollback gate family on `master`
* a current DMA-safe buffer ownership or sg-chain implementation
* a current blk-mq or `scsi_host` registration path
* a current transport-backed event, TMF, or host-scan execution path
* a current throughput benchmark or measured recovery parity result

## Next bounded step

The next honest same-lane move is a rollback-evidence tightening or one bounded rebuild of the missing driver-local file family, not a runtime storage-path jump.

The next bounded step is:
1. leave this packet parked while current `master` remains rollback-evidence only
2. keep using the dedicated survey build route for bounded reruns while the packet stays parked
3. if one bounded driver-local `virtio_scsi` file returns, rebuild the survey packet around that returned surface and rerun the checker-backed validation before widening scope
4. otherwise keep using the fallback catalog as archival evidence only and avoid claiming that the older direct replay family is still present on `master`
