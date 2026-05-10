# Phase 12 Release Readiness Survey

This document records the current release-planning reading for the active bounded Phase 12 packet without claiming that the tranche is closed.

It is a PMO release artifact, not a new replay route.

## Status

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- scope: keep the shipped `nvme_pci`, `virtio_net`, `virtio_scsi`, and libbpf survey-backed packet reviewable through the current smoke-first build-only contract on `master`
- shared PMO companions: `Documentation/zigux/phase12-release-closure-checklist.md` and `Documentation/zigux/phase12-release-coordination-matrix.md`
- shared build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`
- shared replay wiring: `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`

## Shared Replay Order

1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`
5. If the local runtime does not provide `zig` on `PATH`, keep that same smoke-first order and rerun the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing a new Phase 12 validation entrypoint.

Keep the same degraded-workflow validation pair explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and `python3 scripts/zigux/check-build-only-phase12-surface.py` should run before or beside those attached-toolchain Make reruns so build-only contract drift still fails closed when the local runtime needs the fallback path.

## Current Release Reading

- The live shared release packet is the shipped docs-root, checklist, scripts-root, tests-root, workflow, Makefile, and `zigux/tests/phase12_build.zig` bundle already described by `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`.
- The active four-anchor evidence packet remains `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci_survey.zig`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_survey.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `zigux/tests/phase12_libbpf_manifest.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, `zigux/tests/phase12_libbpf_snapshot_determinism.zig`, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/manifest.json`.
- The release packet stays build-only and smoke-first on current `master`: there is no shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route, so release-planning notes must keep naming only the shipped checker pair, smoke shard, full test replay, and Linux-style `phase12` route.
- The `virtio_scsi` rollback discussion remains lab-only reversible-delivery evidence, and all queueing, throughput, rollback, and recovery wording must stay bounded to the existing driver-local packet plus the release-planning companions instead of implying deep-core delivery.

The public fallback split must stay explicit: `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are the only commit-pinned fallback artifacts, while `virtio_net` and `libbpf` remain shared-tree-only anchors.

## Boundaries

- This note is a release-readiness reading, not a release-closure claim.
- `tools/lib/bpf/zigux_segments/verify.zig` must stay explicit in the shared libbpf packet beside `zigux/tests/phase12_libbpf_segments.zig`, `zigux/tests/phase12_libbpf_reviewability.zig`, `zigux/tests/phase12_libbpf_manifest.json`, and `tools/lib/bpf/zigux_segments/manifest.json` so the release-facing libbpf evidence does not collapse back to manifest-only wording.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for the deeper queueing and transport anchors, so this PMO note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.

## Next Bounded Step

When the shipped Phase 12 packet changes, reread this note beside `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, then rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening PMO release wording.
