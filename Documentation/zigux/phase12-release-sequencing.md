# Phase 12 Release Sequencing

This note is the release-order companion for the active Phase 12 packet.

It records the shared smoke-first order for the starter-present `virtio_net` packet plus the shipped `virtio_scsi` build-only packet on current `master` without claiming release closure, while keeping the broader Phase 12 planning and fallback notes explicitly separate from that wired replay surface and from the newer driver-local `virtio_scsi` survey companions.

## Status
- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- scope: keep the shipped Phase 12 release packet reviewable through the same smoke-first build-only contract already named by the docs root, checklist, scripts root, tests root, workflow, and Makefile surfaces while keeping the roadmap's DMA-safe, queueing, throughput, segmented-rollout, rollback, and recovery boundaries explicit beside the still-unwired broader Phase 12 notes and the newer driver-local `virtio_scsi` rollback-lab survey packet
- closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
- coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
- complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
- build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
- readiness-note support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`
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
- The active shared packet on current `master` is the docs-root, checklist, scripts-root, tests-root, workflow, Makefile, and `zigux/tests/phase12_build.zig` bundle that now wires the starter-present `virtio_net` direct and syntax-lab packet beside the shipped `virtio_scsi` tranche replay, while `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig` stay explicit as the adjacent shared review surface for that same starter-present packet rather than as extra build outputs.
- The active smoke-first direct shard set is `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig`, because those are the files the current `smoke` step actually runs.
- The shipped full replay then adds `zigux/tests/phase12_virtio_net.zig` and `zigux/tests/phase12_virtio_scsi.zig` on top of that smoke shard set, while the broader `nvme_pci` and libbpf Phase 12 notes remain planning, fallback, or parked reviewability surfaces until new build wiring and direct replay files actually land on `master`.
- Current `master` now also carries `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` as machine-checkable driver-local rollback-lab companions for the same bounded `virtio_scsi` packet; those survey surfaces now keep command-buffer ownership, control-path governance, request-submit sequencing, completion-handback ordering, io-map recovery, event-buffer ownership, and host-scan restore ordering explicit as lab-only reversible-delivery evidence, but they are not extra shared smoke-step or full-replay build outputs on their own.
- Current `master` still does not expose the earlier `phase12_nvme_pci*` direct replay files or the parked libbpf replay files as shipped build outputs, so this sequencing note must not describe them as part of the wired release packet.
- There is still no shipped shared `make -C zigux phase12-validate` route, wired validator-first replay packet, focused libbpf-only replay, or cross-build replay on current `master`; `scripts/zigux/validate-phase12.py` exists as an unwired helper and must not be treated as shipped release evidence by itself.

## Fallback Split
- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the only commit-pinned direct replay fallback artifact.
- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion for the shipped NVMe starter-plus-verifier foothold, not a second commit-pinned direct replay artifact.
- `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than implied commit-pinned fallback artifacts.
- During degraded GitHub contents reads, `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py` remain shared-tree raw-read anchors for the smoke-first packet and should stay visible here without being promoted into extra commit-pinned fallback artifacts.
- `Documentation/zigux/phase12-raw-github-coverage-survey.md` is the compact reminder for that one direct replay catalog plus one current-master gap-inventory companion plus two shared-tree-only anchors split and should stay aligned with this note whenever fallback wording changes.

## Boundaries
- This note is a release-order record, not a release-closure claim.
- DMA-safe, queueing, segmented-rollout, throughput, rollback, and recovery wording must stay bounded to the starter-present `virtio_net` packet, the shipped driver-local `virtio_scsi` packet, the driver-local `virtio_scsi` rollback-lab survey companions, the shared release-planning packet, and the parked broader Phase 12 notes.
- `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper transport and queueing anchors, so this sequencing note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.

## Next Bounded Step
When the shipped Phase 12 packet or its shared reminder packet changes, reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_net_survey.zig`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `scripts/zigux/README.md`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `zigux/tests/README.md`, then rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening PMO release wording. Current `master` now keeps the release-order note truthful about the smoke-first shared packet, the adjacent starter-present `virtio_net` review surface, and the newer driver-local `virtio_scsi` rollback-lab survey companions, but the broader docs-root, review-checklist, and tests-root reminders still do not all name the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` fallback-note guard that the readiness, coordination, closure, and scripts-root companions already treat as part of the bounded PMO packet. The next honest same-lane follow-through is therefore to refresh only that shared reminder packet before parking `P12-L07` again rather than widening into driver-local, fallback-catalog, or adjacent complex-driver wording.
