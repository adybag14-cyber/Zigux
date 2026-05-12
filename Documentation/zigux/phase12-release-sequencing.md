# Phase 12 Release Sequencing

This note is the release-order companion for the active Phase 12 packet.

It records the shared smoke-first order for the shipped `virtio_scsi` build-only packet on current `master` without claiming release closure, while keeping the broader Phase 12 planning and fallback notes explicitly separate from that wired replay surface.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- scope: keep the shipped Phase 12 release packet reviewable through the same smoke-first build-only contract already named by the docs root, checklist, scripts root, tests root, workflow, and Makefile surfaces while keeping the roadmap's DMA-safe, queueing, throughput, segmented-rollout, and recovery boundaries explicit beside the still-unwired broader Phase 12 notes
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
- build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- shared replay wiring: `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`

## Shared Release Order
1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`
5. If `zig` is unavailable on `PATH`, keep that same smoke-first order and rerun only the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing `phase12-validate`, a focused libbpf-only route, or another unshipped Phase 12 replay surface.

Keep the degraded-workflow checker pair explicit beside that same order too:
- `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
- `python3 scripts/zigux/check-build-only-phase12-surface.py`

## Packet Reading
- The active shared packet on current `master` is the docs-root, checklist, scripts-root, tests-root, workflow, Makefile, and `zigux/tests/phase12_build.zig` bundle that now wires only the shipped `virtio_scsi` tranche replay.
- The active smoke-first direct shard is `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, and `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, because those are the files the current `smoke` step actually runs.
- The shipped full replay then adds `zigux/tests/phase12_virtio_scsi.zig`, while the broader `nvme_pci`, `virtio_net`, and libbpf Phase 12 notes remain planning, fallback, or parked reviewability surfaces until new build wiring and direct replay files actually land on `master`.
- Current `master` does not expose `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/phase12_virtio_scsi_manifest.json`, the earlier `phase12_nvme_pci*` or `phase12_virtio_net*` direct replay files, or the parked libbpf replay files as shipped build outputs, so this sequencing note must not describe them as part of the wired release packet.
- There is still no shipped shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, focused libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route on current `master`, so this sequencing note must keep naming only the shipped checker pair, smoke shard, full test replay, and Linux-style `phase12` route.

## Fallback Split
- Only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned fallback artifacts.
- `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than implied commit-pinned fallback artifacts.
- During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain shared-tree raw-read anchors for the smoke-first packet and should stay visible here without being promoted into extra commit-pinned fallback artifacts.
- `Documentation/zigux/phase12-raw-github-coverage-survey.md` is the compact reminder for that two-versus-two split and should stay aligned with this note whenever fallback wording changes.

## Boundaries
- This note is a release-order record, not a release-closure claim.
- DMA-safe, queueing, segmented-rollout, throughput, rollback, and recovery wording must stay bounded to the shipped driver-local `virtio_scsi` packet, the shared release-planning packet, the parked broader Phase 12 notes, and the lab-only reversible-delivery evidence already documented for `virtio_scsi`.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper transport and queueing anchors, so this sequencing note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.

## Next Bounded Step
When the shipped Phase 12 packet changes, reread this note beside `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`, then rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening PMO release wording. Current `master` already keeps the compact release-coordination matrix, release-readiness note, closure checklist, and tests-root summary explicit about the dedicated `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, the parked `nvme_pci`, `virtio_net`, and libbpf boundaries, and the same smoke-first packet, so the next honest same-lane follow-through is the one-file scripts-root truthfulness sync that stops `scripts/zigux/README.md` from presenting the absent direct `phase12_nvme_pci`, `phase12_virtio_net`, and `phase12_libbpf_segments` replay families as shipped release-packet surfaces before reopening broader docs-root, checker, or fallback wording.