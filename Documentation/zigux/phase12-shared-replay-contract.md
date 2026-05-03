# Phase 12 Shared Replay Contract

This note records the current shared-versus-focused replay contract for the active Phase 12 complex-driver and heavy-helper tranche on `master`.

It is intentionally review-first documentation. It does not claim a fresh local replay result; it captures the live packet shape already wired through the shared validator, the shared build inventory, the bounded libbpf packet checkers, and the dedicated focused libbpf-only replay shard.

## Scope

- roadmap phase: `Phase 12: Complex Production Drivers and Heavy Helper Consumers`
- current bounded anchors: `drivers/net/virtio_net.c`, `drivers/nvme/host/pci.c`, `drivers/scsi/virtio_scsi.c`, and `tools/lib/bpf/libbpf.c`
- packet boundary: the shared validator-and-build packet stays inside `scripts/zigux/validate-phase12.py`, `zigux/tests/phase12_build.zig`, and `make -C zigux phase12`, while the bounded libbpf-only replay remains a separate focused shard under `scripts/zigux/check-phase12-libbpf-focused-replay.py` and `zigux/tests/phase12_libbpf_only_build.zig`

## Pre-Replay Checker Stack

Run these in the published validator-first order before trusting the shared replay packet:

- `python3 scripts/zigux/check-phase12-build-inventory.py --self-test`
- `python3 scripts/zigux/check-phase12-build-inventory.py`
- `python3 scripts/zigux/check-phase12-libbpf-snapshot.py --self-test`
- `python3 scripts/zigux/check-phase12-libbpf-snapshot.py`
- `python3 scripts/zigux/check-phase12-libbpf-packet.py --self-test`
- `python3 scripts/zigux/check-phase12-libbpf-packet.py`
- `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`
- `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py`
- `python3 scripts/zigux/check-phase12-raw-github-coverage.py --self-test`
- `python3 scripts/zigux/check-phase12-raw-github-coverage.py`
- `python3 scripts/zigux/validate-phase12.py`

The published wrapper remains `make -C zigux phase12-validate`.

The focused libbpf-only replay checker is intentionally part of that stack before the broader validator runs, so the dedicated shard can fail closed on its own build-root, review-note, Makefile, and workflow contract before the shared Phase 12 packet claims aligned evidence.

## Shared Replay Surface

The shared replay packet currently runs through these entrypoints:

- `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
- `make -C zigux phase12`

The current shared replay inventory explicitly keeps these packet families inside the broader Phase 12 tranche:

- `zigux/tests/phase12_virtio_net.zig` plus `zigux/tests/phase12_virtio_net_survey.zig`
- `zigux/tests/phase12_nvme_pci.zig` plus `zigux/tests/phase12_nvme_pci_survey.zig`
- `zigux/tests/phase12_virtio_scsi.zig` plus `zigux/tests/phase12_virtio_scsi_survey.zig`
- `zigux/tests/phase12_libbpf_segments.zig` plus `zigux/tests/phase12_libbpf_reviewability.zig`
- `zigux/tests/phase12_raw_github_coverage_survey.zig`

Those shared replay markers are the same ones tracked in `zigux/tests/fixtures/phase12_build_inventory.json` and checked by `scripts/zigux/check-phase12-build-inventory.py`.

## Focused Boundary

The bounded libbpf-only replay remains separate from the shared build packet:

- `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py --self-test`
- `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py`
- `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all`

That boundary is intentional. The focused shard keeps the heavy-helper lane reviewable without silently implying that every libbpf-facing replay already runs inside `zigux/tests/phase12_build.zig`, and it gives the repo one smaller replay surface for the landed `tools/lib/bpf/zigux_segments/` footing while the larger shared validator still carries the cross-anchor Phase 12 packet.

## Active Contract Gap

The current shared review packet is real but not fully symmetrical yet.

- `scripts/zigux/check-phase12-libbpf-focused-replay.py` and `scripts/zigux/check-phase12-libbpf-packet.py` already fail closed on the dedicated focused replay hook inside `Documentation/zigux/review-checklist.md` and the matching shared-validator surface.
- `scripts/zigux/validate-phase12.py` still needs its own direct exact-count follow-up for that same focused replay hook, so the shared validator runtime path can match the duplicate-drift protection that the narrower libbpf checkers already enforce.

This note exists partly to keep that remaining boundary explicit until the larger shared validator file can be updated through a lossless whole-file publish path.

## Contributor Sync Points

When the shared-versus-focused replay contract changes, keep these contributor-facing guidance surfaces aligned with this note:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `Documentation/zigux/phase12-libbpf-segment-survey.md`

Those surfaces are where contributors usually discover the Phase 12 route before they open the deeper packet notes, so any replay-contract change should stay explicit there as well.

## Review Use

Use this note when a complex-driver or heavy-helper change touches the shared Phase 12 test packet, the pre-replay checker stack, or the focused libbpf-only replay boundary.

The minimum agreement surface for that kind of change is:

- `scripts/zigux/validate-phase12.py`
- `scripts/zigux/check-phase12-build-inventory.py`
- `scripts/zigux/check-phase12-libbpf-snapshot.py`
- `scripts/zigux/check-phase12-libbpf-packet.py`
- `scripts/zigux/check-phase12-libbpf-focused-replay.py`
- `scripts/zigux/check-phase12-raw-github-coverage.py`
- `zigux/tests/phase12_build.zig`
- `zigux/tests/phase12_libbpf_only_build.zig`
- `zigux/tests/fixtures/phase12_build_inventory.json`
- `zigux/tests/phase12_libbpf_manifest.json`
- `Documentation/zigux/phase12-libbpf-segment-survey.md`
- `Documentation/zigux/phase12-virtio-net-survey.md`
- `Documentation/zigux/phase12-nvme-pci-survey.md`
- `Documentation/zigux/phase12-virtio-scsi-survey.md`

If those files drift apart, the Phase 12 delivery packet stops being reviewable even if individual Zig test files or survey notes still look plausible in isolation.
