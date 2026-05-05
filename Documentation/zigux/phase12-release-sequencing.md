# Phase 12 Release Sequencing

This note records the ordered release path for the active bounded Phase 12 tranche.

It is a release-coordination artifact, not a closure claim.

## Current posture

- `PHASE12_STATUS=active`
- `PHASE12_RELEASE_CLOSED=no`
- shared validator entrypoint: `python3 scripts/zigux/validate-phase12.py`
- Linux-style validate entrypoint: `make -C zigux phase12-validate`
- Linux-style replay entrypoint: `make -C zigux phase12`
- approved non-native smoke targets: `x86_64-linux-musl`, `aarch64-linux-musl`, `riscv64-linux-musl`
- current public fallback split: two commit-pinned artifacts (`nvme_pci`, `virtio_scsi`) and two shared-tree-only anchors (`virtio_net`, `libbpf`)

## Release order

1. Run the dedicated PMO packet guard first.
   - `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`
   - `python3 scripts/zigux/check-phase12-release-readiness-packet.py`
   - This keeps the active-not-closed posture, approved musl smoke set, mixed fallback split, and review-checklist summary fail-closed before broader replay claims.

2. Run the shared validator path.
   - `python3 scripts/zigux/validate-phase12.py`
   - `make -C zigux phase12-validate`
   - This is the shared release gate for the four bounded roadmap anchors plus the current cross-smoke and degraded-workflow packet.

3. Reconfirm the non-native smoke packet.
   - `python3 scripts/zigux/check-phase12-cross.py --zig <zig-path>`
   - This stays limited to the approved `x86_64-linux-musl`, `aarch64-linux-musl`, and `riscv64-linux-musl` replay set.

4. Reconfirm the focused libbpf-only shard.
   - `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py`
   - `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all`
   - This keeps the narrower heavy-helper replay visible before the broader shared Phase 12 replay runs.

5. Run the shared Phase 12 build replay.
   - `zig build test --build-file zigux/tests/phase12_build.zig --summary all`
   - This is the current tranche-wide Zig replay surface for the bounded `virtio_net`, `nvme_pci`, `virtio_scsi`, and libbpf survey packet.

6. Run the combined Linux-style entrypoint last.
   - `make -C zigux phase12`
   - This should remain the summary entrypoint rather than the only place release coordination is inferred.

## Owner map

- `Network Driver Lane`: bounded `virtio_net` packet against `drivers/net/virtio_net.c`
- `Storage Driver Lane`: bounded `nvme_pci` and `virtio_scsi` packets against `drivers/nvme/host/pci.c` and `drivers/scsi/virtio_scsi.c`
- `BPF Tooling Lane`: bounded libbpf helper packet against `tools/lib/bpf/libbpf.c`
- `PMO / Release Management`: release-facing survey, checklist, sequencing, and tranche-readiness coordination artifacts

## Current blocker to closure

The dedicated PMO release packet is already landed through:

- `Documentation/zigux/phase12-release-readiness-survey.md`
- `Documentation/zigux/phase12-release-coordination-matrix.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/check-phase12-release-readiness-packet.py`
- `scripts/zigux/README.md`

The remaining release-discipline gap is narrower:

- `scripts/zigux/check-phase12-release-readiness-packet.py` still does not fail closed on `Documentation/zigux/phase12-release-coordination-matrix.md` and the paired `zigux/tests/README.md` PMO handoff sentence.
- That means one compact PMO summary surface can still drift without the dedicated release packet guard catching it first.

## Closure conditions

Phase 12 should not be described as release-closed until all of the following are true:

1. The shared validator carries the dedicated PMO checker and release-readiness survey exactly once.
2. The dedicated release checker, survey note, docs-root summary, scripts-root helper index, and review checklist still agree on the same active-not-closed reading.
3. The approved three-target musl smoke packet remains explicit and green.
4. The focused libbpf-only replay shard and the shared Phase 12 build replay both remain explicit and green.
5. The public fallback split is still described honestly rather than rounded up into implied commit-pinned coverage for every anchor.

## Next bounded PMO step

Harden `scripts/zigux/check-phase12-release-readiness-packet.py` so it requires:

- `Documentation/zigux/phase12-release-coordination-matrix.md`
- the paired `zigux/tests/README.md` PMO handoff sentence

as fail-closed release-packet surfaces, then rerun the dedicated checker self-test before widening to any broader shared-validator promotion.
