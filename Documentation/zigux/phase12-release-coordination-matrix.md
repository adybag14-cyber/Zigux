# Phase 12 Release Coordination Matrix

This note is the compact PMO handoff view for the active Phase 12 release packet on `master`.

It does not replace the deeper survey and contract notes. Its job is narrower: keep the current owner split, status bucket, validation gate, rollback owner, and public-read fallback mode visible in one place while the tranche remains active rather than closed.

## Shared status

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- `PHASE12_ROADMAP_ANCHOR_COUNT=4`
- `PHASE12_APPROVED_CROSS_TARGET_COUNT=3`
- `PHASE12_COMMIT_PINNED_RAW_FALLBACK_COUNT=2`
- `PHASE12_SHARED_TREE_ONLY_FALLBACK_COUNT=2`
- shared validator-first route: `python3 scripts/zigux/check-phase12-raw-github-coverage.py --self-test`, `python3 scripts/zigux/check-phase12-raw-github-coverage.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `python3 scripts/zigux/check-phase12-shared-replay-contract.py --self-test`, `python3 scripts/zigux/check-phase12-shared-replay-contract.py`, `python3 scripts/zigux/validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12`
- approved non-native smoke packet: `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl`

## Anchor matrix

| Roadmap anchor | Owner lane | Status bucket | Validation gate | Rollback owner | Public-read fallback mode | Primary release evidence |
| --- | --- | --- | --- | --- | --- | --- |
| `drivers/net/virtio_net.c` | `Network Driver Lane` | active bounded starter plus survey packet | shared Phase 12 PMO stack through `check-phase12-release-readiness-packet.py`, `check-phase12-shared-replay-contract.py`, `validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12` | `Network Driver Lane` | shared-tree-only fallback through the roots published in `Documentation/zigux/phase12-raw-github-coverage-survey.md` | `Documentation/zigux/phase12-virtio-net-survey.md` |
| `drivers/nvme/host/pci.c` | `Storage Driver Lane` | active bounded starter plus survey-and-slice packet | shared Phase 12 PMO stack through `check-phase12-release-readiness-packet.py`, `check-phase12-shared-replay-contract.py`, `validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12` | `Storage Driver Lane` | commit-pinned fallback through `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md` | `Documentation/zigux/phase12-nvme-pci-survey.md` and `Documentation/zigux/phase12-nvme-pci-slice.md` |
| `drivers/scsi/virtio_scsi.c` | `Storage Driver Lane` | active bounded starter plus survey-and-slice packet with a dedicated recovery-state replay | shared Phase 12 PMO stack through `check-phase12-release-readiness-packet.py`, `check-phase12-shared-replay-contract.py`, `validate-phase12.py`, `make -C zigux phase12-validate`, and `make -C zigux phase12` | `Storage Driver Lane` | commit-pinned fallback through `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md` | `Documentation/zigux/phase12-virtio-scsi-survey.md`, `Documentation/zigux/phase12-virtio-scsi-slice.md`, and `zigux/tests/phase12_virtio_scsi_recovery_state.zig` |
| `tools/lib/bpf/libbpf.c` | `BPF Tooling Lane` | active bounded heavy-helper survey packet with a focused libbpf-only replay shard | shared Phase 12 PMO stack plus `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py`, `zig build --build-file zigux/tests/phase12_libbpf_only_build.zig phase12-libbpf-focused-replay --summary all`, and `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all` | `BPF Tooling Lane` | shared-tree-only fallback through the roots published in `Documentation/zigux/phase12-raw-github-coverage-survey.md` | `Documentation/zigux/phase12-libbpf-segment-survey.md` |

## Release packet interpretation

Use this matrix together with these shared PMO packet notes when reading Phase 12 for release coordination:

- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-shared-replay-contract.md`
- `Documentation/zigux/phase12-cross-compile-smoke.md`
- `Documentation/zigux/phase12-raw-github-coverage-survey.md`
- `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`
- `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`

The PMO reading should stay the same across those files:

- the tranche is active, not closed
- the owner split is three-way rather than one vague driver bucket
- two anchors have commit-pinned public fallback artifacts today
- two anchors still rely on shared-tree fallback reads today
- the mixed fallback split is backed by `scripts/zigux/check-phase12-raw-github-coverage.py`, `zigux/tests/phase12_raw_github_coverage_manifest.json`, and `zigux/tests/phase12_raw_github_coverage_survey.zig` instead of living only in prose notes
- `make -C zigux phase12-validate` remains the rollback drill before `make -C zigux phase12`

## Shared surface alignment

Before treating the Phase 12 PMO packet as reviewable, keep these summary surfaces aligned with the same release story:

- `Documentation/zigux/README.md` should keep this matrix, the active-not-closed Phase 12 posture, and the validator-first replay route visible from the docs root
- `scripts/zigux/README.md` should keep the same owner split, focused libbpf replay shard, and validate-before-replay route visible from the scripts root
- `zigux/tests/README.md` should explicitly name this matrix plus `Documentation/zigux/phase12-nvme-pci-raw-github-fallback-map.md`, `Documentation/zigux/phase12-virtio-scsi-raw-github-fallback-catalog.md`, `zigux/tests/phase12_raw_github_coverage_manifest.json`, and `zigux/tests/phase12_raw_github_coverage_survey.zig` so the tests root carries the same two commit-pinned versus two shared-tree-only fallback split and the same paired manifest-backed raw-coverage evidence instead of leaving the mixed mode implicit

## Review use

Use this matrix when a release-facing change needs a quick answer to any of these questions:

- which lane currently owns this Phase 12 anchor
- whether the anchor is still starter-only and survey-backed rather than release-closed
- which gate must stay green before the shared replay can be trusted
- who owns rollback for the packet if one anchor regresses
- whether degraded public review is commit-pinned or still shared-tree-only for that anchor
