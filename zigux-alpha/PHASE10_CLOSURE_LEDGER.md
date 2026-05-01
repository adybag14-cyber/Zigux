# Phase 10 Closure Ledger

This focused ledger records the current closure-evidence bundle for the active Phase 10 virtio tranche.

- `PHASE10_LEDGER_STATUS=active`
- `PHASE10_LEDGER_TRANCHE=virtio-lab-bundle`
- `PHASE10_LEDGER_SCOPE=virtio-core,virtio-ring,virtio-input,virtio-mmio-lab-bundle`
- `PHASE10_LEDGER_ROADMAP_ANCHORS=drivers/virtio/virtio.c,drivers/virtio/virtio_ring.c,drivers/virtio/virtio_input.c,drivers/virtio/virtio_mmio.c`
- `PHASE10_LEDGER_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md`
- `PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py`
- `PHASE10_LEDGER_SHARED_VALIDATE=scripts/zigux/validate-phase10.py`
- `PHASE10_LEDGER_MANIFEST=zigux/tests/phase10_closure_manifest.json`
- `PHASE10_LEDGER_CORE_SURVEY=Documentation/zigux/phase10-virtio-core-survey.md`
- `PHASE10_LEDGER_RING_SURVEY=Documentation/zigux/phase10-virtio-ring-survey.md`
- `PHASE10_LEDGER_INPUT_SURVEY=Documentation/zigux/phase10-virtio-input-survey.md`
- `PHASE10_LEDGER_MMIO_SURVEY=Documentation/zigux/phase10-virtio-mmio-survey.md`
- `PHASE10_LEDGER_CORE_MANIFEST=zigux/tests/phase10_virtio_core_manifest.json`
- `PHASE10_LEDGER_RING_MANIFEST=zigux/tests/phase10_virtio_ring_manifest.json`
- `PHASE10_LEDGER_INPUT_MANIFEST=zigux/tests/phase10_virtio_input_manifest.json`
- `PHASE10_LEDGER_MMIO_MANIFEST=zigux/tests/phase10_virtio_mmio_manifest.json`
- `PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE=zigux/tests/phase10_closure_manifest.json`
- `PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed`
- `PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS=starter_landed`
- `PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed`
- `PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport`
- `PHASE10_LEDGER_MMIO_SURVEY_GATE=zigux/tests/phase10_virtio_mmio_survey.zig`
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
- `PHASE10_LEDGER_LANDED_MMIO_HELPERS=phase10-mmio-register-window-helper,phase10-mmio-queue-register-helper,phase10-mmio-queue-notify-helper,phase10-mmio-queue-address-helper,phase10-mmio-config-window-helper,phase10-mmio-config-write-helper,phase10-mmio-interrupt-ack-helper`

This ledger stays intentionally narrow. It records the roadmap-backed closure packet and the current parked-next-step posture without claiming queue setup, reset, IRQ parity, DMA, probe or remove lifecycle, or input registration lifecycle parity.

The roadmap-facing scoreboard is mirrored here from the shared closure manifest so the closure packet can be compared directly against the Phase 10 roadmap requirements without hopping between survey notes. That shared scoreboard still reads `starter_landed` for virtqueue wrappers, MMIO wrappers, and lab-only validation, while risky dual implementations remain `blocked_on_risky_transport` until a smaller transport-facing helper lane is ready.

The shared closure manifest, the dedicated MMIO survey gate, the shared Phase 10 validator, and the dedicated MMIO survey now agree that the landed MMIO helper ladder reaches bounded interrupt acknowledgement, so this ledger keeps that reviewable helper-and-validation set explicit instead of collapsing the MMIO packet into only its remaining transport blocker.

The exact replay packet for the current closure bundle is:

1. `python3 scripts/zigux/validate-phase10-closure.py`
2. `zig build test --build-file zigux/tests/phase10_build.zig --summary all`
3. `make -C zigux phase10-validate`
4. `make -C zigux phase10-test`
5. `make -C zigux phase10`
