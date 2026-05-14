# Phase 12 Release Coordination Matrix

This matrix is the compact PMO coordination companion for the active Phase 12 packet.

It is a release-planning artifact, not a closure claim and not a new replay route.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- shared-summary lane owner: `P12-L07`
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
- PMO / Release Management: keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, this matrix, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` aligned around the same active-not-closed release posture and the same smoke-first packet. `P12-L07` no longer has a live docs-root undercount to repair on current `master`: the docs root already keeps `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, the parked `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor, the shipped-but-unwired `scripts/zigux/validate-phase12.py` helper, the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` support checker, and the starter-present direct `virtio_net` packet explicit beside the same smoke-first release packet. The shared `Documentation/zigux/review-checklist.md` already keeps `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, the parked `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor, the shipped-but-unwired `scripts/zigux/validate-phase12.py` helper, and the starter-present direct `virtio_net` packet explicit too, and it now also names that dedicated support checker plus the shipped `make -C zigux phase12-validate` route as the validator-first support bundle rather than a second direct replay path. `scripts/zigux/README.md` still keeps the dedicated support checker explicit beside the parked snapshot anchor, the shipped-but-unwired `scripts/zigux/validate-phase12.py` helper, and the starter-present direct `virtio_net` packet, but it still does not yet name the shipped `make -C zigux phase12-validate` route. `zigux/tests/README.md` now keeps the parked snapshot anchor, the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` support checker, the shipped `make -C zigux phase12-validate` route, the shipped-but-unwired `scripts/zigux/validate-phase12.py` helper, and the starter-present direct `virtio_net` packet visible. The next honest same-lane follow-through is therefore to leave the already-aligned docs-root, review-checklist, tests-root, release-order, fallback, and starter-packet reminders parked and refresh only `scripts/zigux/README.md` when that broader shared reminder next picks up the shipped `phase12-validate` route, instead of reopening already-landed shared-summary claims or widening into driver-local churn first.
- Complex-driver packet: keep `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` explicit as the truthful `nvme_pci` boundary until live `master` lands dedicated `Documentation/zigux/phase12-nvme-pci-slice.md` and `Documentation/zigux/phase12-nvme-pci-survey.md` surfaces; keep `Documentation/zigux/phase12-virtio-net-survey.md`, `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig` aligned as the starter-present `virtio_net` packet while that family still lacks a separate slice note and still stays explicitly below live DMA-safe receive ownership, refill execution, transport-backed queue flow, NAPI, XDP, XSK, RSS table programming, control-virtqueue runtime traffic, or full `net_device` lifecycle claims; and keep `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` aligned with the shared smoke-first replay packet while that same driver-local rollback-lab companion packet stays explicit beside the direct replay files, while `zigux/tests/phase12_nvme_pci.zig` and `drivers/nvme/host/pci_verify.zig` stay explicit as unpublished or absent direct replay boundaries rather than implied shipped outputs on current `master`
- Shared libbpf heavy-consumer packet: keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` aligned around the same shared Phase 12 libbpf posture, with the survey note carrying the live helper-first foundations, the snapshot keeping the parked reviewability packet visible as a public-tree anchor, and the parked verify-shard note keeping the direct `phase12_libbpf_*` replay files, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/manifest.json` explicit as parked note-owned boundaries rather than implying a focused libbpf-only replay route or shipped smoke-first adoption on current `master`; the direct `phase12_libbpf_*` replay files, `tools/lib/bpf/zigux_segments/verify.zig`, and `tools/lib/bpf/zigux_segments/manifest.json` stay recorded only through the parked verify-shard packet until those files land again on current `master`.
- Shared fallback and anti-overlap packet: keep `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, and `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` aligned with the same active smoke-first packet, the same one-catalog plus one-gap-note plus two-anchor fallback split, and the same release-planning-only boundary

## Fallback Split
- commit-pinned direct replay catalog:
  - `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`
- driver-local current-master gap inventory companion:
  - `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- shared-tree-only anchors:
  - `Documentation/zigux/phase12-virtio-net-survey.md`
  - `Documentation/zigux/phase12-libbpf-segment-survey.md`
- shared-tree raw-read anchors during degraded contents reads:
  - `zigux/tests/phase12_build.zig`
  - `scripts/zigux/check-build-only-phase12-surface.py`
- rule: keep this one-catalog plus one-gap-note plus two-anchor split explicit in PMO release wording; only the `virtio_scsi` catalog is commit-pinned direct replay evidence, and neither the NVMe gap note nor the shared-tree anchors should be promoted into extra commit-pinned fallback artifacts unless new dedicated files actually land
- keep the shared build anchor plus checker visible during degraded contents reads too, and do not promote any of those shared-tree surfaces into extra commit-pinned fallback artifacts unless new dedicated files actually land

## Smoke Set
1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`

If `zig` is unavailable on `PATH`, keep the shipped degraded-workflow bundle plus that same smoke-first order explicit through the Make routes with `ZIG=<attached-zig-path>`: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke`, and `make -C zigux phase12`, instead of inventing a focused libbpf-only replay, a cross-build replay, or another unshipped PMO surface.

Keep the degraded-workflow checker pair explicit beside that same order too:
- `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
- `python3 scripts/zigux/check-build-only-phase12-surface.py`
- Current `master` keeps the starter-present `virtio_net` syntax-lab smoke shard explicit through `zigux/tests/phase12_build.zig`: the shipped `smoke` step runs `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig`, before the `test` step layers in the direct `zigux/tests/phase12_virtio_net.zig` and `zigux/tests/phase12_virtio_scsi.zig` replays on top of that same smoke shard.

## Boundaries
- This matrix tracks only the shipped build-only contract and the active survey-backed packet on `master`.
- Current `master` now ships the degraded-workflow bundle `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate`, but there is still no broader shared `check-phase12-*.py` family, focused-libbpf-only replay, or cross-build replay, so release-planning notes should keep that validator-first support packet distinct from the smoke-first direct replay packet.
- Queueing, throughput, rollback, and recovery wording must stay bounded to the driver-local packets and the lab-only reversible-delivery evidence already recorded in the shared Phase 12 docs; this PMO companion must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.

## Review Use
- reread this matrix beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever the shared Phase 12 packet changes
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening PMO wording
- treat this file as a compact owner-and-fallback summary, not as a substitute for the driver-local survey notes or the shared build packet