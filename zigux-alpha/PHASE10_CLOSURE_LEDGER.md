# Phase 10 Closure Ledger

This focused ledger records the current closure-evidence bundle for the active Phase 10 virtio tranche.

- `PHASE10_LEDGER_STATUS=active`
- `PHASE10_LEDGER_TRANCHE=virtio-lab-bundle`
- `PHASE10_LEDGER_SCOPE=virtio-core,virtio-ring,virtio-input,virtio-mmio-lab-bundle`
- `PHASE10_LEDGER_ROADMAP_ANCHORS=drivers/virtio/virtio.c,drivers/virtio/virtio_ring.c,drivers/virtio/virtio_input.c,drivers/virtio/virtio_mmio.c`
- `PHASE10_LEDGER_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md`
- `PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py`
- `PHASE10_LEDGER_MANIFEST=zigux/tests/phase10_closure_manifest.json`
- `PHASE10_LEDGER_RING_SURVEY=Documentation/zigux/phase10-virtio-ring-survey.md`
- `PHASE10_LEDGER_MMIO_SURVEY=Documentation/zigux/phase10-virtio-mmio-survey.md`
- `PHASE10_LEDGER_RING_MANIFEST=zigux/tests/phase10_virtio_ring_manifest.json`
- `PHASE10_LEDGER_MMIO_MANIFEST=zigux/tests/phase10_virtio_mmio_manifest.json`
- `PHASE10_LEDGER_MAKEFILE=zigux/Makefile`
- `PHASE10_LEDGER_WORKFLOW=.github/workflows/zigux-bootstrap.yml`
- `PHASE10_LEDGER_ENTRYPOINTS=make -C zigux phase10-validate,make -C zigux phase10-test,make -C zigux phase10`
- `PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/validate-phase10-closure.py`
- `PHASE10_LEDGER_EXACT_CHECK_2=zig build test --build-file zigux/tests/phase10_build.zig --summary all`
- `PHASE10_LEDGER_EXACT_CHECK_3=make -C zigux phase10-validate`
- `PHASE10_LEDGER_EXACT_CHECK_4=make -C zigux phase10-test`
- `PHASE10_LEDGER_EXACT_CHECK_5=make -C zigux phase10`
- `PHASE10_LEDGER_NEXT_STEP=leave_parked_unless_phase10-mmio-lifecycle-and-irq-paths_splits_smaller`
- `PHASE10_LEDGER_BLOCKERS=phase10-virtio-input-registration-lifecycle,phase10-mmio-lifecycle-and-irq-paths`

This ledger stays intentionally narrow. It records the roadmap-backed closure packet and the current parked-next-step posture without claiming queue setup, reset, IRQ parity, DMA, probe or remove lifecycle, or input registration lifecycle parity.

The exact replay packet for the current closure bundle is:

1. `python3 scripts/zigux/validate-phase10-closure.py`
2. `zig build test --build-file zigux/tests/phase10_build.zig --summary all`
3. `make -C zigux phase10-validate`
4. `make -C zigux phase10-test`
5. `make -C zigux phase10`
