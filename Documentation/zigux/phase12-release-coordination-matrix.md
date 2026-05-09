# Phase 12 Release Coordination Matrix

This matrix keeps the active Phase 12 release-facing packet explicit beside the longer sequencing, closure, and release-readiness notes without implying that the broader complex-driver tranche is closed.

## Release Posture

- `PHASE12_RELEASE_CLOSED=no`
- `PHASE12_STATUS=active`
- `PHASE12_TRANCHE=driver-and-libbpf-survey-bundle`
- the current release reading stays bounded to reviewable `virtio_net`, `nvme_pci`, `virtio_scsi`, and segmented `libbpf` evidence plus the shared smoke-first replay packet and the mixed raw-fallback packet
- release-order authority: `Documentation/zigux/phase12-release-sequencing.md`
- PMO closure companion: `Documentation/zigux/phase12-release-closure-checklist.md`
- adjacent release-readiness note: `Documentation/zigux/phase12-release-readiness-survey.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- driver-only anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shared libbpf anti-overlap companion: `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`
- shared reviewer, scripts-root, and tests-root packet reminders: `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md`
- freeze-boundary authority: `Documentation/zigux/freeze-map.md`
- the `libbpf` survey remains parked shared-helper evidence inside this active release packet, so PMO notes must keep both the survey, the dedicated `tools/lib/bpf/zigux_segments/verify.zig` shard, and the heavy-consumer anti-overlap companion explicit without implying a reopened helper-implementation lane
- deterministic libbpf artifact companions: `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, and `zigux/tests/phase12_libbpf_snapshot_determinism.zig` keep the tracked-helper snapshot bytes plus committed digest fixture and replay explicit inside that same parked shared-helper evidence
- the canonical deterministic replay remains `zigux/tests/phase12_libbpf_snapshot_determinism.zig`; only `zigux/tests/fixtures/phase12_libbpf_snapshot.json` and `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json` belong under `zigux/tests/fixtures/`, so compact PMO surfaces must not drift the replay back into the fixtures tree
- the landed `virtio_net` segmented-rollout boundary remains lane-local review evidence inside this active packet, so PMO notes must not round it up into DMA-safe transport readiness or live runtime-data-path progress
- the bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback drill remains lab-only reversible-delivery evidence inside this active packet, so PMO notes must not round it up into tranche-wide runtime recovery or release-closed proof
- that bounded storage packet specifically keeps repeated transport-reset generation plus restore queue rebind, request-queue restart, event rearm, event-buffer ownership, and rollback summaries reviewable as lab-only reversible-delivery scaffolding inside the active Phase 12 PMO packet
- this compact matrix must not round queueing, throughput, rollback, or recovery wording up into deep-core delivery claims that cross the freeze-map boundary

## Lane Ownership

| Anchor | Owner | Current bounded evidence |
| --- | --- | --- |
| `drivers/net/virtio_net.c` | Network Driver Lane | `Documentation/zigux/phase12-virtio-net-survey.md` |
| `drivers/nvme/host/pci.c` | NVMe PCI Lane | `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` |
| `drivers/scsi/virtio_scsi.c` | Virtio SCSI Lane | `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` |
| `tools/lib/bpf/libbpf.c` | BPF Tooling Lane | `Documentation/zigux/phase12-libbpf-segment-survey.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, and `tools/lib/bpf/zigux_segments/verify.zig` (parked shared-helper survey plus anti-overlap map with the dedicated verify shard and landed bridge-local helper foundations kept separate from deferred bridge and object-model work) |

## Fallback Split

| Fallback posture | Anchors | Evidence |
| --- | --- | --- |
| commit-pinned raw fallback artifact | `nvme_pci`, `virtio_scsi` | `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` |
| shared-tree-only public fallback anchors plus overview note | `virtio_net`, `libbpf` | `Documentation/zigux/phase12-raw-github-coverage-survey.md` (shared overview only), `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md` |

- `PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2`
- `PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md` stays the shared fallback overview for those two anchors, not a third shared-tree-only anchor.

## Smoke-Set Summary

- current shared direct smoke anchors: `zigux/tests/phase12_nvme_pci.zig`, `drivers/nvme/host/pci_verify.zig`, `zigux/tests/phase12_virtio_net.zig`, `zigux/tests/phase12_virtio_net_syntax_lab.zig`, `zigux/tests/phase12_virtio_scsi.zig`, and `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`
- `PHASE12_SHARED_SMOKE_SURFACE_COUNT=6`
- build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py` plus `.github/workflows/zigux-bootstrap.yml`

1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`
5. If the local runtime does not provide `zig` on `PATH`, keep the same smoke-first order and rerun the shipped Make routes with an attached toolchain override instead of inventing a new Phase 12 entrypoint.
   - `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
   - `make -C zigux phase12 ZIG=<attached-zig-path>`
   - This is an environment override for the existing replay packet, not a validator-first or `phase12-validate` route.

- keep the direct PMO drift-control reruns explicit too: `python3 scripts/zigux/check-build-only-phase12-surface.py --self-test` and `python3 scripts/zigux/check-build-only-phase12-surface.py` remain part of the shipped build-only contract packet beside the workflow-backed replay and must not be rounded up into a validator-first, focused libbpf-only, raw-coverage, or `phase12-validate` route
- there is no shipped shared `scripts/zigux/validate-phase12.py`, no `check-phase12-*.py` packet, no focused libbpf-only replay route, no raw-coverage packet guard, no cross-build replay packet, and no `make -C zigux phase12-validate` target on `master`

## PMO Handoff Prompts

Before treating the packet as release-ready, confirm all of the following stay true together:

1. `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase12-release-sequencing.md`, `Documentation/zigux/phase12-release-closure-checklist.md`, `Documentation/zigux/phase12-release-readiness-survey.md`, this matrix, `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`, `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md`, `Documentation/zigux/phase12-raw-github-coverage-survey.md`, `Documentation/zigux/phase12-virtio-net-survey.md`, `Documentation/zigux/phase12-libbpf-segment-survey.md`, `tools/lib/bpf/zigux_segments/verify.zig`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase12_libbpf_snapshot.json`, `zigux/tests/fixtures/phase12_libbpf_snapshot_determinism.json`, `zigux/tests/phase12_libbpf_snapshot_determinism.zig`, `.github/workflows/zigux-bootstrap.yml`, `zigux/tests/phase12_build.zig`, and `zigux/Makefile` still name the same smoke-first Phase 12 packet.
2. Only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` still act as commit-pinned fallback artifacts, while `virtio_net` and `libbpf` remain shared-tree-only anchors.
3. `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` still keeps `virtio_net`, `nvme_pci`, and `virtio_scsi` separate from each other, while `Documentation/zigux/phase12-libbpf-heavy-consumer-lane-sequencing.md` still keeps shared reviewability, landed bridge-local helper foundations, deferred bridge and queue-routing work, and the blocked object-model wall distinct from the driver lanes and from each other.
4. The checker and workflow still read as build-only contract enforcement rather than as a validator-first route, a release-readiness packet guard, a raw-coverage packet guard, or a focused libbpf-only replay surface.
5. `Documentation/zigux/freeze-map.md` still keeps the frozen and boundary-study anchors explicit, the bounded `Documentation/zigux/phase12-virtio-net-survey.md` segmented-rollout boundary still reads as lane-local review evidence rather than DMA-safe transport or runtime-data-path proof, the bounded `Documentation/zigux/phase12-virtio-scsi-slice.md` rollback drill still reads as lab-only reversible-delivery evidence rather than tranche-wide runtime recovery or release-closed proof, that same bounded storage packet still keeps repeated transport-reset generation plus restore queue rebind, request-queue restart, event rearm, event-buffer ownership, and rollback summaries explicit as lab-only reversible-delivery scaffolding, and every shared Phase 12 PMO surface still keeps queueing, throughput, rollback, and recovery wording below that freeze-boundary line instead of rounding the active driver-and-libbpf packet up into deep-core delivery claims.

## Update Rule

- If the bounded Phase 12 packet changes lane ownership, fallback posture, smoke-set membership, or the parked release-readiness reading, update this matrix in the same change so the compact release view keeps matching live `master`.
- If a future validator-first, focused libbpf-only, raw-coverage guard, cross-build replay, or broader runtime-recovery route ever becomes real, land the actual shipped file and replay surface first, then add it here without rewriting the active smoke-first packet ahead of the evidence.
