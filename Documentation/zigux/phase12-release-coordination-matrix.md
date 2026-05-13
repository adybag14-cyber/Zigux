# Phase 12 Release Coordination Matrix

This matrix is the compact PMO coordination companion for the active Phase 12 packet.

It is a release-planning artifact, not a closure claim and not a new replay route.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- shared-summary lane owner: `P12-Y07`
- scope: keep the active shared Phase 12 packet reviewable without implying a broader validator-first or deep-core delivery claim
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- sequencing companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- coverage companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- libbpf survey companion: `Documentation/zigux/phase12-libbpf-segment-survey.md`
- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
- build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- shared replay wiring: `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`

## Owner Split
- PMO / Release Management: keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, this matrix, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` aligned around the same active-not-closed release posture, the same smoke-first packet, and the same build-only checker pair. `P12-Y07` no longer has a live docs-root undercount to repair on current `master`: the docs root, shared `Documentation/zigux/review-checklist.md`, scripts root, and tests root already keep `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, the parked `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor, the shipped-but-unwired `scripts/zigux/validate-phase12.py` helper, and the starter-present direct `virtio_net` packet explicit beside the same smoke-first release packet. The next honest same-lane follow-through is therefore to leave `P12-Y07` parked until the shipped Phase 12 packet or one of those shared reminder surfaces moves again, then rerun `scripts/zigux/check-build-only-phase12-surface.py` and refresh only the smallest shared-summary drift instead of reopening already-landed docs-root, scripts-root, or tests-root syncs.
- Complex-driver packet: keep `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` explicit as the truthful `nvme_pci` boundary until live `master` lands dedicated `Documentation/zigux/phase12-nvme-pci-slice.md` and `Documentation/zigux/phase12-nvme-pci-survey.md` surfaces; keep `Documentation/zigux/phase12-virtio-net-survey.md`, `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig` aligned as the starter-present `virtio_net` packet while that family still lacks a separate slice note and still stays explicitly below live DMA-safe receive ownership, refill execution, transport-backed queue flow, NAPI, XDP, XSK, RSS table programming, control-virtqueue runtime traffic, or full `net_device` lifecycle claims; and keep `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` aligned with the shared smoke-first replay packet while that same driver-local rollback-lab companion packet stays explicit beside the direct replay files, while `zigux/tests/phase12_nvme_pci.zig` and `drivers/nvme/host/pci_verify.zig` stay explicit as unpublished or absent direct replay boundaries rather than implied shipped outputs on current `master`
- Shared libbpf heavy-consumer packet: keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` aligned around the same shared Phase 12 libbpf posture, with the survey note carrying the live helper-first foundations, the snapshot keeping the parked reviewability packet visible as a public-tree anchor, and the parked verify-shard note keeping the direct `phase12_libbpf_*` replay files, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/manifest.json` explicit as parked note-owned boundaries rather than implying a focused libbpf-only replay route or shipped smoke-first adoption on current `master`
- Shared fallback and anti-overlap packet: keep `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, and `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` aligned with the same active smoke-first packet, the same two-versus-two fallback split, and the same release-planning-only boundary

## Fallback Split
- commit-pinned public fallback artifacts:
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
  - `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- shared-tree-only anchors:
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
- shared-tree raw-read anchors during degraded contents reads:
  - `zigux/tests/phase12_build.zig`
  - `scripts/zigux/check-build-only-phase12-surface.py`
- rule: keep this two-versus-two split explicit in PMO release wording and do not promote the shared-tree anchors into commit-pinned fallback artifacts unless new dedicated files actually land
- keep the shared build anchor plus checker visible during degraded contents reads too, and do not promote any of those shared-tree surfaces into extra commit-pinned fallback artifacts unless new dedicated files actually land

## Smoke Set
1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`

If `zig` is unavailable on `PATH`, reuse the same smoke-first order through the shipped Make routes with `ZIG=<attached-zig-path>` instead of inventing a `phase12-validate` or other unshipped PMO replay surface.

Keep the degraded-workflow checker pair explicit beside that same order too:
- `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
- `python3 scripts/zigux/check-build-only-phase12-surface.py`
- Current `master` keeps the starter-present `virtio_net` syntax-lab smoke shard explicit through `zigux/tests/phase12_build.zig`: the shipped `smoke` step runs `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig`, before the `test` step layers in the direct `zigux/tests/phase12_virtio_net.zig` and `zigux/tests/phase12_virtio_scsi.zig` replays on top of that same smoke shard.

## Boundaries
- This matrix tracks only the shipped build-only contract and the active survey-backed packet on `master`.
- Current `master` now ships the unwired helper `scripts/zigux/validate-phase12.py`, but there is still no shared `check-phase12-*.py`, focused-libbpf-only replay, cross-build replay, or `make -C zigux phase12-validate` route, so release-planning notes should keep naming only the shipped smoke-first packet and the build-only checker.
- Queueing, throughput, rollback, and recovery wording must stay bounded to the driver-local packets and the lab-only reversible-delivery evidence already recorded in the shared Phase 12 docs; this PMO companion must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.

## Review Use
- reread this matrix beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever the shared Phase 12 packet changes
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening PMO wording
- treat this file as a compact owner-and-fallback summary, not as a substitute for the driver-local survey notes or the shared build packet
