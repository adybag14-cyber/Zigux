# Phase 12 Release Sequencing

This note is the release-order companion for the active Phase 12 packet.
It records the shared validator-first then smoke-first order for the starter-present `virtio_net` packet plus the shipped `virtio_scsi` build-only packet on current `master` without claiming release closure, while keeping the broader Phase 12 planning and fallback notes explicitly separate from that wired replay surface, from the newer driver-local `virtio_scsi` survey companions, and from the now-published but still-unwired driver-local NVMe foothold.

## Status
  * `PHASE12_STATUS=active`
  * `PHASE12_RELEASE_CLOSED=no`
  * scope: keep the shipped Phase 12 release packet reviewable through the same current validator-first then smoke-first contract while keeping the roadmap's DMA-safe, queueing, throughput, segmented-rollout, rollback, and recovery boundaries explicit beside the still-unwired broader Phase 12 notes, the newer driver-local `virtio_scsi` rollback-lab survey packet, and the published-but-still-unwired NVMe starter packet
  * closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
  * readiness companion: `Documentation/zigux/phase12-release-readiness-survey.md`
  * coordination companion: `Documentation/zigux/phase12-release-coordination-matrix.md`
  * complex-driver anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
  * shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
  * shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
  * verify-shard companion: `Documentation/zigux/phase12-libbpf-verify-shard-note.md`
  * build-only contract checker: `scripts/zigux/check-build-only-phase12-surface.py`
  * driver-local NVMe reopen companion: `Documentation/zigux/phase12-nvme-pci-reopen-governance.md`
  * readiness-note support checker: `scripts/zigux/check-phase12-release-readiness-packet.py`
  * shared replay wiring: `zigux/tests/phase12_build.zig`, `.github/workflows/zigux-bootstrap.yml`, and `zigux/Makefile`

## Shared Release Order
1. `make -C zigux phase12-validate`
2. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
3. `make -C zigux phase12-smoke`
4. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
5. `make -C zigux phase12`
6. If `zig` is unavailable on `PATH`, keep that same validator-first then smoke-first order and first rely on the repo-local `.zig-toolchain` fallback exposed by `zigux/Makefile`; if that local fallback is also absent, rerun only the shipped Make routes as `make -C zigux phase12-validate`, `make -C zigux phase12-smoke ZIG=<attached-zig-path>`, and `make -C zigux phase12 ZIG=<attached-zig-path>` instead of inventing a focused libbpf-only route, a cross-build route, or another unshipped Phase 12 replay surface.

Current repo-reality override: `zigux/Makefile` no longer exposes `phase12-validate`, `phase12-smoke`, or `phase12` on current `master`, so the Make-route names retained in this section are stale reminder vocabulary rather than shipped wrapper proof until same-lane work rematerializes them. The directly readable rerun surfaces in the shared packet are `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `scripts/zigux/validate-phase12.py`, `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`, and `zig build test --build-file zigux/tests/phase12_build.zig --summary all`.

Keep the degraded-workflow validation trio explicit beside that same order too:

  * `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test`
  * `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
  * `make -C zigux phase12-validate`

## Packet Reading
  * The active shared packet on current `master` is the docs-root, checklist, scripts-root, tests-root, workflow, Makefile, and `zigux/tests/phase12_build.zig` bundle that now wires the starter-present `virtio_net` direct and syntax-lab packet beside the shipped `virtio_scsi` tranche replay, while `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, and `zigux/tests/phase12_virtio_net_survey.zig` stay explicit as the adjacent shared review surface for that same starter-present packet rather than as extra build outputs.
  * The active smoke-first direct shard set is `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi_repeated_replan_gate.zig`, `zigux/tests/phase12_virtio_scsi_repeated_rollback_gate.zig`, and `zigux/tests/phase12_virtio_scsi_packet.zig`, because those are the files the current `smoke` step actually runs.
  * `zigux/tests/phase12_build.zig` also wires `zigux/tests/phase12_virtio_net_transmit_recycle.zig` and `zigux/tests/phase12_virtio_net_queue_resume.zig` through both `smoke` and `test`, so the shared release packet should keep those bounded transmit-recycle disposition and queue-resume replays explicit beside the starter-present `virtio_net` direct and syntax-lab packet without rounding them up into live interrupt-backed transmit completion parity or queue-restart parity.
  * The shipped full replay then adds `zigux/tests/phase12_virtio_net.zig` and `zigux/tests/phase12_virtio_scsi.zig` on top of that smoke shard set, while the broader shared release route still keeps the bounded `nvme_pci` starter-plus-verifier-plus-direct-replay-plus-slice-plus-survey packet outside the wired smoke-and-test path and keeps the libbpf Phase 12 notes as planning, fallback, or parked reviewability surfaces until new build wiring actually lands on `master`.
  * Current `master` now also carries `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, and `zigux/tests/phase12_virtio_scsi_survey.zig` as machine-checkable driver-local rollback-lab companions for the same bounded `virtio_scsi` packet; those survey surfaces now keep command-buffer ownership, control-path governance, request-submit sequencing, completion-handback ordering, io-map recovery, event-buffer ownership, and host-scan restore ordering explicit as lab-only reversible-delivery evidence, but they are not extra shared smoke-step or full-replay build outputs on their own.
  * Current `master` now exposes the bounded driver-local `phase12_nvme_pci` direct replay, slice, survey, survey gate, manifest packet, and `Documentation/zigux/phase12-nvme-pci-reopen-governance.md` owner-map companion outside the wired shared release route, while the parked libbpf replay files still do not ship as shared build outputs, so this sequencing note must keep NVMe explicit as a driver-local published foothold without describing either family as part of the wired release packet.
  * Current `master` now keeps the degraded-workflow validator-side support packet explicit through `scripts/zigux/validate-phase12.py` and `scripts/zigux/check-phase12-release-readiness-packet.py`, while `make -C zigux phase12-validate` remains stale reminder vocabulary until same-lane work rematerializes the wrapper; there is still no focused libbpf-only replay or cross-build replay on current `master`, so this sequencing note must keep that validator-first support packet ahead of the smoke-first direct replay order instead of treating it as broader driver delivery evidence by itself. Current repo-reality override: `zigux/Makefile` no longer exposes a shared `phase12-validate` wrapper on current `master`, so keep that route name as stale reminder vocabulary beside the directly readable scripts-side support packet until same-lane work rematerializes the wrapper instead of treating it as shipped wrapper proof today.

## Fallback Split
  * `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` is the only commit-pinned direct replay fallback artifact.
  * `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` remains the current-master gap-inventory companion for the shipped NVMe starter-plus-verifier-plus-direct-replay-plus-slice-plus-survey foothold, not a second commit-pinned direct replay artifact.
  * `Documentation/zigux/phase12-virtio-net-survey.md` and `Documentation/zigux/phase12-libbpf-segment-survey.md` remain shared-tree-only anchors rather than implied commit-pinned fallback artifacts.
  * During degraded GitHub contents reads, the intended shared-tree raw-read anchors are still `zigux/tests/phase12_build.zig` and `scripts/zigux/check-build-only-phase12-surface.py`, but they should stay visible here only as the older shared fallback pair rather than as current-`master` proof while direct contents reads for `zigux/tests/phase12_build.zig` still fail through the same bridge, even though `zigux/Makefile`, `scripts/zigux/check-phase12-release-readiness-packet.py`, `.github/workflows/zigux-bootstrap.yml`, and `scripts/zigux/README.md` are directly readable there now.
  * `Documentation/zigux/phase12-raw-github-coverage-survey.md` is the compact degraded-reality reminder for that one direct replay catalog plus one current-master gap-inventory companion plus two shared-tree-only anchors split and should stay aligned with this note whenever fallback wording changes.

## Boundaries
  * This note is a release-order record, not a release-closure claim.
  * DMA-safe, queueing, segmented-rollout, throughput, rollback, and recovery wording must stay bounded to the starter-present `virtio_net` packet, the shipped driver-local `virtio_scsi` packet, the driver-local `virtio_scsi` rollback-lab survey companions, the driver-local NVMe foothold, the shared release-planning packet, and the parked broader Phase 12 notes.
  * `Documentation/zigux/freeze-map.md` remains the boundary owner for deeper transport and queueing anchors, so this sequencing note must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`.

## Next Bounded Step
When the shipped Phase 12 packet or its shared reminder packet changes, reread this note beside `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-libbpf-verify-shard-note.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `zigux/tests/phase12_virtio_net_manifest.json`, `zigux/tests/phase12_virtio_net_survey.zig`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-survey.md`, `zigux/tests/phase12_virtio_scsi_manifest.json`, `zigux/tests/phase12_virtio_scsi_survey.zig`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-survey.md`, `zigux/tests/phase12_nvme_pci_manifest.json`, `zigux/tests/phase12_nvme_pci_survey.zig`, `scripts/zigux/README.md`, `scripts/zigux/check-phase12-release-readiness-packet.py`, and `zigux/tests/README.md`, then rerun `python3 scripts/zigux/check-build-only-phase12-surface.py` before widening PMO release wording.
Current `master` now keeps the release-order note truthful about the shipped validator-first then smoke-first packet, the adjacent starter-present `virtio_net` review surface, the newer driver-local `virtio_scsi` rollback-lab survey companions, and the published-but-still-unwired NVMe foothold.
The shared reminder packet has narrowed further on current `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` now mirror the shipped `phase12-validate` support bundle, the repo-local `.zig-toolchain` then attached-Zig degraded rerun order, and the dedicated `scripts/zigux/check-phase12-release-readiness-packet.py` guard.
The next honest same-lane follow-through is therefore to leave this sequencing note parked unless a fresh repo-first reread finds another equally small truthfulness drift across `Documentation/zigux/phase12-release-coordination-matrix.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `scripts/zigux/README.md`, or `zigux/tests/README.md` before widening into new driver-local behavior, fallback-catalog changes, or adjacent complex-driver wording.
