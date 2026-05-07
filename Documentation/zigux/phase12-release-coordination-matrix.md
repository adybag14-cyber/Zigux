# Phase 12 Release Coordination Matrix

This matrix keeps the active Phase 12 release-facing packet explicit without implying that the broader complex-driver tranche is closed.

## Release Posture

- `PHASE12_RELEASE_CLOSED=no`
- `PHASE12_STATUS=active`
- `PHASE12_TRANCHE=driver-and-libbpf-survey-bundle`
- the current release reading stays bounded to reviewable `virtio_net`, `nvme_pci`, `virtio_scsi`, and segmented `libbpf` evidence plus the shared smoke-first build packet and the mixed fallback split
- queueing, throughput, and recovery wording in this compact PMO view stays bounded to the shipped driver-local and helper-local evidence and must not imply active delivery against `net/core/skbuff.c`, `kernel/workqueue.c`, or `kernel/trace/ring_buffer.c`

## Lane Ownership

| Anchor | Owner | Current bounded evidence |
| --- | --- | --- |
| `drivers/net/virtio_net.c` | Network Driver Lane | `Documentation/zigux/phase12-virtio-net-survey.md` |
| `drivers/nvme/host/pci.c` | NVMe PCI Lane | `Documentation/zigux/phase12-nvme-pci-survey.md`, `Documentation/zigux/phase12-nvme-pci-slice.md`, `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` |
| `drivers/scsi/virtio_scsi.c` | Virtio SCSI Lane | `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` |
| `tools/lib/bpf/libbpf.c` | BPF Tooling Lane | `Documentation/zigux/phase12-libbpf-segment-survey.md` |

## Fallback Split

| Fallback posture | Anchors | Evidence |
| --- | --- | --- |
| commit-pinned raw fallback artifact | `nvme_pci`, `virtio_scsi` | `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` |
| shared-tree-only public fallback reads | `virtio_net`, `libbpf` | `Documentation/zigux/phase12-raw-github-coverage-survey.md` |

- `PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2`
- `PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2`

## Shared Smoke Set

The shipped direct smoke packet remains:

- `zigux/tests/phase12_nvme_pci.zig`
- `drivers/nvme/host/pci_verify.zig`
- `zigux/tests/phase12_virtio_net.zig`
- `zigux/tests/phase12_virtio_net_syntax_lab.zig`
- `zigux/tests/phase12_virtio_scsi.zig`
- `zigux/tests/phase12_virtio_scsi_syntax_lab.zig`

- `PHASE12_SHARED_SMOKE_SURFACE_COUNT=6`

## Shared Replay Order

1. `zig build smoke --build-file zigux/tests/phase12_build.zig --summary all`
2. `make -C zigux phase12-smoke`
3. `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
4. `make -C zigux phase12`
5. If the local runtime does not provide `zig` on `PATH`, keep the same smoke-first order and rerun the shipped Make routes with an attached toolchain override instead of inventing a new Phase 12 entrypoint.
   - `make -C zigux phase12-smoke ZIG=<attached-zig-path>`
   - `make -C zigux phase12 ZIG=<attached-zig-path>`
   - This is an environment override for the existing replay packet, not a validator-first or `phase12-validate` route.

## PMO Handoff Prompts

Before treating the packet as release-ready, confirm all of the following stay true together:

1. `Documentation/zigux/phase12-release-sequencing.md` and `Documentation/zigux/phase12-release-closure-checklist.md` still say the tranche is active rather than closed.
2. `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` still keep the shared Phase 12 packet, the build-only checker, the smoke-first replay order, the fallback overview, and the driver-only anti-overlap map explicit.
3. `scripts/zigux/check-build-only-phase12-surface.py` remains the shipped build-only packet guard, and `.github/workflows/zigux-bootstrap.yml` still reruns both its self-test and its live check.
4. Only `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` and `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` are commit-pinned fallback artifacts, while `virtio_net` and `libbpf` remain shared-tree-only anchors.
5. `Documentation/zigux/phase12-complex-driver-lane-sequencing.md` still keeps `virtio_net`, `nvme_pci`, and `virtio_scsi` distinct from each other while this matrix remains a compact PMO companion.
6. There is still no shipped shared `scripts/zigux/validate-phase12.py`, `check-phase12-*.py`, focused libbpf-only replay route, raw-coverage packet guard, cross-build replay packet, or `make -C zigux phase12-validate` target on `master`.

## Shared Coordination Reminder

- compact PMO companions: `Documentation/zigux/phase12-release-sequencing.md` and `Documentation/zigux/phase12-release-closure-checklist.md`
- shared fallback overview: `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- driver-only anti-overlap companion: `Documentation/zigux/phase12-complex-driver-lane-sequencing.md`
- shipped build-only contract guard: `scripts/zigux/check-build-only-phase12-surface.py`
- workflow replay anchor: `.github/workflows/zigux-bootstrap.yml`

Use this compact view to keep the owner split, fallback split, smoke set, and replay order reviewable in one place without widening Phase 12 into removed validator-era surfaces or deeper transport claims.
