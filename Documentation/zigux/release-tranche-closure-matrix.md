# Zigux Release Tranche Closure Matrix

This note gives PMO one late-phase release matrix for the active Zigux tranches. It is a coordination artifact, not a claim that the late phases are globally closed.

## Status

- `RELEASE_TRANCHE_MATRIX_VERSION=1`
- `ACTIVE_RELEASE_SPAN=phase10-through-phase15`
- `GLOBAL_RELEASE_CLOSED=no`
- `MATRIX_SOURCE_SET=phase10_closure_evidence,phase12_release_readiness_survey,phase13_release_notes_survey,phase14_release_boundary_survey,phase15_readiness_gate_survey`

## Late-phase matrix

### Phase 10

- phase: `Phase 10`
- tranche: `virtio-lab-bundle`
- status bucket: `active-not-closed`
- owner surface: `Virtio Driver Pod` through the core, ring, input, and MMIO survey lanes `P10-L01`, `P10-L07`, `P10-L13`, and `P10-L18`
- validation gate: `python3 scripts/zigux/check-phase10-closure-inventory.py`, `python3 scripts/zigux/validate-phase10-closure.py`, `python3 scripts/zigux/check-phase10-harness-coverage.py`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10`
- rollback owner: the same bounded Phase 10 virtio lane bundle; keep the current `drivers/virtio/*.zig` evidence lab-only and fall back to the existing `drivers/virtio/*.c` transport ownership whenever risky lifecycle, IRQ, or DMA scope would be implied
- release reading: the current queue-facing virtio lab evidence is real and verified, but risky transport closure remains blocked

### Phase 12

- phase: `Phase 12`
- tranche: `driver-and-libbpf-survey-bundle`
- status bucket: `active-not-closed`
- owner surface: `Network Driver Lane`, `NVMe PCI Lane`, `Virtio SCSI Lane`, and `BPF Tooling Lane`
- validation gate: `python3 scripts/zigux/validate-phase12.py`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py --self-test`, `python3 scripts/zigux/check-phase12-release-readiness-packet.py`, `make -C zigux phase12-validate`, `python3 scripts/zigux/check-phase12-cross.py --zig <zig-path>`, `python3 scripts/zigux/check-phase12-libbpf-focused-replay.py`, `zig build test --build-file zigux/tests/phase12_libbpf_only_build.zig --summary all`, and `make -C zigux phase12`
- rollback owner: the same four-way Phase 12 owner split; keep `drivers/net/virtio_net.c`, `drivers/nvme/host/pci.c`, `drivers/scsi/virtio_scsi.c`, and `tools/lib/bpf/libbpf.c` as the fallback anchors while DMA-backed queue ownership, full transport lifecycle, loader, relocation, and object-model claims remain blocked
- release reading: the shared release packet is active and release-facing, but it is still not closed and still carries the mixed two commit-pinned versus two shared-tree-only fallback split

### Phase 13

- phase: `Phase 13`
- tranche: `shared-helper-bundle`
- status bucket: `active-helper-release-packet`
- owner surface: manifest-backed anchor lanes `P13-L04`, `P13-L10`, `P13-L12`, and `P13-L16`, plus the adjacent notifier reviewability lane `P13-L19`
- validation gate: `python3 scripts/zigux/validate-phase13-release.py`, `python3 scripts/zigux/check-phase13-devres-packet.py`, `make -C zigux phase13-validate`, `zig build test --build-file zigux/tests/phase13_build.zig --summary all`, and `make -C zigux phase13`
- rollback owner: the same manifest-backed helper packet owners; keep the current helper-only posture and do not reopen DMA-backed mappings, scatterlist ownership, live Landlock enforcement, or notifier registration from the shared release note alone
- release reading: the shared-helper tranche is real and reviewable, but it stays helper-first and is not a replacement for the still-active driver-facing release packets

### Phase 14

- phase: `Phase 14`
- tranche: `core-adjacent study-only smoke packet`
- status bucket: `boundary-only-smoke`
- owner surface: the shared study-only boundary packet around `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, `kernel/rcu/tree.c`, and `net/core/skbuff.c`
- validation gate: `python3 scripts/zigux/validate-phase14.py`, `make -C zigux phase14-validate`, `make -C zigux phase14-smoke`, `zig build test --build-file zigux/tests/phase14_build.zig --summary all`, and `make -C zigux phase14`
- rollback owner: keep the current study-only and freeze-in-C boundary reading; Phase 14 is a reviewability lane, not an active delivery packet
- release reading: the smoke gate is real, but it exists only to hold the release boundary between active helper delivery and governance control

### Phase 15

- phase: `Phase 15`
- tranche: `tranche-readiness-gap-survey`
- status bucket: `governance-freeze-gate`
- owner surface: the Phase 15 governance bundle through the freeze map, Architecture Council review process, parity scorecard, indefinite-C policy, readiness survey, and handoff survey
- validation gate: `python3 scripts/zigux/validate-phase15.py`, `make -C zigux phase15-validate`, `zig build test --build-file zigux/tests/phase15_build.zig`, and `make -C zigux phase15`
- rollback owner: keep the current governance packet and deep-core stay-in-C posture until stronger evidence exists for any future status change
- release reading: the governance bundle is landed and aligned, but the late-phase release remains globally open because the deep-core reopen conditions are still blocked

## Sequencing and handoff

1. Phase 10 stays the earliest active late-phase closure packet. Do not treat later helper or governance notes as a substitute for its bounded virtio evidence.
2. Phase 12 remains the current PMO release-facing packet. Keep it active-not-closed until the shared validator fully mirrors the dedicated release-readiness packet.
3. Phase 13 follows as helper-first release discipline. It can tighten helper reviewability, but it must not be used to imply closure of the still-active Phase 10 or Phase 12 packets.
4. Phase 14 stays boundary-only. Its smoke gate keeps the sequencing honest, but it does not reopen active subsystem delivery.
5. Phase 15 stays the final freeze and governance gate. It records maintenance readiness, not a deep-core status change.

## Current release-wide blocker

The late-phase release picture is coordinated, but it is not closed. The smallest active PMO blocker still sits in Phase 12: the dedicated release-readiness packet is live, while the broader `scripts/zigux/validate-phase12.py` surface still trails that same release-facing packet.

## Next bounded PMO step

If this `pmo-release` lane reopens, prefer one of these bounded follow-ups in order:

1. promote the dedicated Phase 12 PMO packet into `scripts/zigux/validate-phase12.py` once a safe whole-file publication bridge exists
2. keep this matrix aligned whenever one of the Phase 10 through Phase 15 owner surfaces, validation gates, or release-status buckets changes
3. avoid widening this PMO lane into helper delivery, driver behavior, or governance policy creation unless the roadmap itself changes
