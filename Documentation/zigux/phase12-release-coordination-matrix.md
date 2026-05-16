# Phase 12 Release Coordination Matrix

This matrix is the compact PMO coordination companion for the active Phase 12 packet.

It is a release-planning artifact, not a closure claim and not a new replay route.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- shared-summary lane owner: `pmo-release`
- scope: keep the active shared Phase 12 packet reviewable without implying a broader validator-first or deep-core delivery claim
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- sequencing companion: `Documentation/zigux/phase12-release-sequencing.md`
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- coverage companion: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- libbpf survey companion: `Documentation/zigux/phase12-libbpf-segment-survey.md`
- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
- driver-local NVMe reopen companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
- build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- support-bundle cross companion: `scripts/zigux/check-phase12-cross.py`
- support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`
- validator-first support route: `scripts/zigux/validate-phase12.py` and `make -C zigux phase12-validate`
- shared replay wiring: `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`

## Owner Split
- PMO / Release Management: keep `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, this matrix, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` aligned around the same active-not-closed release posture and the same smoke-first packet. The shared `pmo-release` packet no longer has that older `virtio_scsi` rollback-lab checker undercount on current `master`: `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, and this matrix now keep `zigux/tests/phase12_virtio_scsi_manifest.json` plus `zigux/tests/phase12_virtio_scsi_survey.zig` explicit beside the direct replay files, and `scripts/zigux/check-build-only-phase12-surface.py` already carries the same rollback-lab companion pair through its required-file set plus the release-sequencing, release-coordination, and complex-driver marker checks. The dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` guard, the shipped `python3 scripts/zigux/check-phase12-cross.py --self-test` companion, the shipped `scripts/zigux/validate-phase12.py` helper, the shipped `make -C zigux phase12-validate` support bundle, the parked `zigux/tests/fixtures/phase12_libbpf_snapshot.json` anchor, the starter-present direct `virtio_net` packet, and the landed `drivers/net/virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `drivers/net/virtio_net_queue_resume.zig`, and `zigux/tests/phase12_virtio_net_queue_resume.zig` follow-ups all remain explicit beside the same smoke-first release packet, while those two `virtio_net` follow-ups stay framed as bounded transmit-disposition and queue-resume reviewability rather than live DMA or queue-restart parity, and broader docs-root, scripts-root, tests-root, fallback, or review-checklist reminder drift stays outside this one-file matrix note. The next honest same-lane follow-through is therefore to leave this matrix parked unless fresh repo-first inspection finds another equally small release-packet wording or checker gap that current `master` actually still shows.
- Complex-driver packet: keep `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` explicit as the current-master gap-inventory companion for the published driver-local `nvme_pci` starter-plus-verifier-plus-direct-replay-plus-slice-plus-survey packet, keep `Documentation/zigux/phase12-nvme-pci-reopen-governance.md` explicit as the driver-local owner map for that same bounded packet while it stays outside the shared smoke-first route, keep `Documentation/zigux/phase12-virtio-net-survey.md`, `drivers/net/virtio_net.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_net_survey.zig`, `drivers/net/virtio_net_transmit_recycle.zig`, `zigux/tests/phase12_virtio_net_transmit_recycle.zig`, `drivers/net/virtio_net_queue_resume.zig`, and `zigux/tests/phase12_virtio_net_queue_resume.zig` aligned as the starter-present `virtio_net` packet while that family still lacks a separate slice note and still stays explicitly below live DMA-safe receive ownership, refill execution, transport-backed queue flow, NAPI, XDP, XSK, RSS table programming, control-virtqueue runtime traffic, or full `net_device` lifecycle claims; keep the transmit-recycle and queue-resume follow-ups framed as bounded transmit-disposition and queue-resume reviewability rather than live DMA or queue-restart parity; and keep `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `drivers/scsi/virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig` aligned with the shared smoke-first replay packet while that same driver-local rollback-lab companion packet stays explicit beside the direct replay files, while `drivers/nvme/host/pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_nvme_pci.zig`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `zigux/tests/phase12_nvme_pci_manifest.json`, and `zigux/tests/phase12_nvme_pci_survey.zig` stay explicit as the bounded driver-local NVMe starter-plus-verifier-plus-direct-replay-plus-slice-plus-survey packet rather than as part of the shipped shared smoke-first route on current `master`
- Shared libbpf heavy-consumer packet: keep `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, and `zigux/tests/fixtures/phase12_libbpf_snapshot.json` aligned around the same shared Phase 12 libbpf posture, with the survey note carrying the live helper-first foundations, the snapshot keeping the parked reviewability packet visible as a public-tree anchor, and the parked verify-shard note keeping the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/verify.zig` and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` explicit as parked note-owned boundaries while `tools/lib/bpf/zigux_segments/manifest.json` stays explicit as the legacy helper catalog that is still readable on current `master`, rather than implying a focused libbpf-only replay route or shipped smoke-first adoption on current `master`; the direct `phase12_libbpf_*` replay files plus `tools/lib/bpf/zigux_segments/verify.zig` and `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` stay recorded only through the parked verify-shard packet until those files land again on current `master`, while `tools/lib/bpf/zigux_segments/manifest.json` remains present as that legacy helper catalog.
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

If `zig` is unavailable on `PATH`, keep the shipped degraded-workflow bundle plus that same smoke-first order explicit through the Make routes with `ZIG=<attached-zig-path>`: `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>`, instead of inventing a focused libbpf-only replay, a cross-build replay, or another unshipped PMO surface.

Keep the degraded-workflow validation quartet explicit beside that same order too:
- `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
- `python3 scripts/zigux/check-phase12-cross.py --self-test`
- `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
- `make -C zigux phase12-validate`
- Current `master` keeps the starter-present `virtio_net` syntax-lab smoke shard explicit through `zigux/tests/phase12_build.zig`: the shipped `smoke` step runs `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig`, before the `test` step layers in the direct `zigux/tests/phase12_virtio_net.zig` and `zigux/tests/phase12_virtio_scsi.zig` replays on top of that same smoke shard.
- Current `master` also keeps `zigux/tests/phase12_virtio_net_transmit_recycle.zig` and `zigux/tests/phase12_virtio_net_queue_resume.zig` wired through both `smoke` and `test` inside `zigux/tests/phase12_build.zig`, but this matrix should keep them framed as bounded transmit-disposition and queue-resume reviewability rather than live DMA or queue-restart parity.
- The same smoke shard also keeps `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig` explicit as the shipped rollback-lab drill inside `zigux/tests/phase12_build.zig` rather than leaving that gate implied by the broader `virtio_scsi` packet wording.

## Boundaries
- This matrix tracks only the shipped build-only contract and the active survey-backed packet on `master`.
- Current `master` now ships the degraded-workflow bundle `scripts/zigux/check-build-only-phase12-surface.py`, `scripts/zigux/check-phase12-cross.py`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `scripts/zigux/validate-phase12.py`, and `make -C zigux phase12-validate`, but it still does not expose a standalone Phase 12 cross-build replay, a focused-libbpf-only replay, or another shared cross-target route, so release-planning notes should keep that validator-first support packet distinct from the smoke-first direct replay packet.
- Queueing, throughput, rollback, and recovery wording must stay bounded to the driver-local packets and the lab-only reversible-delivery evidence already recorded in the shared Phase 12 docs; this PMO companion must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.

## Review Use
- reread this matrix beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `scripts/zigux/README.md`, and `zigux/tests/README.md` whenever the shared Phase 12 packet changes
- rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening PMO wording
- treat this file as a compact owner-and-fallback summary, not as a substitute for the driver-local survey notes or the shared build packet