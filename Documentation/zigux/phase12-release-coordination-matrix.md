# Phase 12 Release Coordination Matrix

This matrix keeps the active Phase 12 release-facing packet explicit without implying that the broader complex-driver tranche is closed.

## Release Posture

- `PHASE12_RELEASE_CLOSED=no`
- `PHASE12_STATUS=active`
- `PHASE12_TRANCHE=driver-and-libbpf-survey-bundle`
- the current release reading stays bounded to reviewable `virtio_net`, `nvme_pci`, `virtio_scsi`, and segmented `libbpf` evidence plus the shared cross-compile smoke and raw-fallback packets

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

## Cross-Compile Smoke Set

The approved non-native smoke set remains:

- `x86_64-linux-musl`
- `aarch64-linux-musl`
- `riscv64-linux-musl`

- `PHASE12_APPROVED_CROSS_TARGET_COUNT=3`
- replay surface: `python3 scripts/zigux/check-phase12-cross.py --zig <zig>` and `zigux/tests/phase12_cross_build.zig`

## PMO Handoff Prompts

Before treating the packet as release-ready, confirm all of the following stay true together:

1. `Documentation/zigux/phase12-release-readiness-survey.md` still says the tranche is active rather than closed.
2. `Documentation/zigux/review-checklist.md` still keeps the shared Phase 12 packet and its build-only, smoke, and fallback surfaces explicit.
3. `scripts/zigux/check-phase12-release-readiness-packet.py` remains the dedicated PMO packet guard beside `python3 scripts/zigux/validate-phase12.py`.
4. `zigux/tests/README.md` should name this matrix when it summarizes the active Phase 12 tests-root release packet so PMO review does not depend on the docs root alone.

## Shared Replay Reminder

- shared validator-first route: `python3 scripts/zigux/validate-phase12.py`
- make-level validation route: `make -C zigux phase12-validate`
- shared replay route: `make -C zigux phase12`
- focused libbpf replay route: `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py` and `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all`
- raw-fallback packet guard: `python3 scripts/zigux/check-phase12-raw-github-coverage.py`
