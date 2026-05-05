# Phase 10 Closure Ledger

This focused ledger records the current closure-evidence bundle for the active Phase 10 virtio tranche.

- `PHASE10_LEDGER_STATUS=active`
- `PHASE10_LEDGER_TRANCHE=virtio-lab-bundle`
- `PHASE10_LEDGER_SCOPE=virtio-core,virtio-ring,virtio-input,virtio-mmio-lab-bundle`
- `PHASE10_LEDGER_ROADMAP_ANCHORS=drivers/virtio/virtio.c,drivers/virtio/virtio_ring.c,drivers/virtio/virtio_input.c,drivers/virtio/virtio_mmio.c`
- `PHASE10_LEDGER_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md`
- `PHASE10_LEDGER_INVENTORY_VALIDATE=scripts/zigux/check-phase10-closure-inventory.py`
- `PHASE10_LEDGER_CORE_PACKET_VALIDATE=scripts/zigux/check-phase10-core-packet.py`
- `PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py`
- `PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py`
- `PHASE10_LEDGER_SHARED_VALIDATE=scripts/zigux/validate-phase10.py`
- `PHASE10_LEDGER_MANIFEST=zigux/tests/phase10_closure_manifest.json`
- `PHASE10_LEDGER_CORE_SLICE=Documentation/zigux/phase10-virtio-core-slice.md`
- `PHASE10_LEDGER_CORE_SURVEY=Documentation/zigux/phase10-virtio-core-survey.md`
- `PHASE10_LEDGER_RING_SURVEY=Documentation/zigux/phase10-virtio-ring-survey.md`
- `PHASE10_LEDGER_INPUT_SURVEY=Documentation/zigux/phase10-virtio-input-survey.md`
- `PHASE10_LEDGER_MMIO_SURVEY=Documentation/zigux/phase10-virtio-mmio-survey.md`
- `PHASE10_LEDGER_CORE_LAB_GATE=zigux/tests/phase10_virtio_core.zig`
- `PHASE10_LEDGER_CORE_SURVEY_GATE=zigux/tests/phase10_virtio_core_survey.zig`
- `PHASE10_LEDGER_RING_RESET_REUSE_GATE=zigux/tests/phase10_virtio_ring_reset_reuse.zig`
- `PHASE10_LEDGER_RING_SURVEY_GATE=zigux/tests/phase10_virtio_ring_survey.zig`
- `PHASE10_LEDGER_INPUT_MULTITOUCH_PREFLIGHT_GATE=zigux/tests/phase10_virtio_input_multitouch_preflight.zig`
- `PHASE10_LEDGER_INPUT_REGISTRATION_BLOCKER_BUILD=zigux/tests/phase10_virtio_input_registration_blocker_build.zig`
- `PHASE10_LEDGER_INPUT_SURVEY_GATE=zigux/tests/phase10_virtio_input_survey.zig`
- `PHASE10_LEDGER_MMIO_QUEUE_ISOLATION_GATE=zigux/tests/phase10_virtio_mmio_queue_isolation.zig`
- `PHASE10_LEDGER_MMIO_SURVEY_GATE=zigux/tests/phase10_virtio_mmio_survey.zig`
- `PHASE10_LEDGER_CORE_MANIFEST=zigux/tests/phase10_virtio_core_manifest.json`
- `PHASE10_LEDGER_RING_MANIFEST=zigux/tests/phase10_virtio_ring_manifest.json`
- `PHASE10_LEDGER_INPUT_MANIFEST=zigux/tests/phase10_virtio_input_manifest.json`
- `PHASE10_LEDGER_MMIO_MANIFEST=zigux/tests/phase10_virtio_mmio_manifest.json`
- `PHASE10_LEDGER_ROADMAP_SCOREBOARD_SOURCE=zigux/tests/phase10_closure_manifest.json`
- `PHASE10_LEDGER_SURVEY_PROVENANCE_SOURCE=manifest_derived`
- `PHASE10_LEDGER_SURVEY_CORE_LANE=P10-L01`
- `PHASE10_LEDGER_SURVEY_RING_LANE=P10-L07`
- `PHASE10_LEDGER_SURVEY_INPUT_LANE=P10-L13`
- `PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L18`
- `PHASE10_LEDGER_SURVEY_CORE_COMMIT=d30cbe483a2f019ae797b309a29556bd58fe00d0`
- `PHASE10_LEDGER_SURVEY_RING_COMMIT=fe8a43ea2e186da0da152198b571dff57ea3c38c`
- `PHASE10_LEDGER_SURVEY_INPUT_COMMIT=f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21`
- `PHASE10_LEDGER_SURVEY_MMIO_COMMIT=0945df1cf664a3582d7241f859183a13f3f04adb`
- `PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed`
- `PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE=drivers/virtio/virtio_ring.zig,zigux/tests/phase10_virtio_ring.zig,zigux/tests/phase10_virtio_ring_manifest.json,Documentation/zigux/phase10-virtio-ring-survey.md`
- `PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS=starter_landed`
- `PHASE10_LEDGER_MMIO_WRAPPERS=starter_landed`
- `PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-slice.md,Documentation/zigux/phase10-virtio-mmio-survey.md`
- `PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed`
- `PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE=zigux/tests/phase10_build.zig,zigux/tests/phase10_virtio_ring_reset_reuse.zig,zigux/tests/phase10_virtio_input_multitouch_preflight.zig,zigux/tests/phase10_virtio_input_registration_blocker_build.zig,zigux/tests/phase10_virtio_mmio_queue_isolation.zig,scripts/zigux/check-phase10-harness-coverage.py,scripts/zigux/check-phase10-closure-inventory.py,scripts/zigux/validate-phase10.py,scripts/zigux/validate-phase10-closure.py,Documentation/zigux/phase10-closure-evidence.md,zigux/Makefile,.github/workflows/zigux-bootstrap.yml`
- `PHASE10_LEDGER_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport`
- `PHASE10_LEDGER_SCOREBOARD_DUAL_IMPLEMENTATIONS_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md,zigux/tests/phase10_virtio_core_manifest.json,zigux/tests/phase10_virtio_ring_manifest.json,zigux/tests/phase10_virtio_input_manifest.json,zigux/tests/phase10_virtio_mmio_manifest.json`
- `PHASE10_LEDGER_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/kernel/,zigux/helpers/`
- `PHASE10_LEDGER_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates`
- `PHASE10_LEDGER_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes`
- `PHASE10_LEDGER_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no`
- `PHASE10_LEDGER_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle`
- `PHASE10_LEDGER_PHASE14_STUDY_ONLY_ANCHORS=kernel/workqueue.c,kernel/trace/ring_buffer.c`
- `PHASE10_LEDGER_MAKEFILE=zigux/Makefile`
- `PHASE10_LEDGER_WORKFLOW=.github/workflows/zigux-bootstrap.yml`
- `PHASE10_LEDGER_ENTRYPOINTS=make -C zigux phase10-validate,make -C zigux phase10-test,make -C zigux phase10`
- `PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/check-phase10-closure-inventory.py`
- `PHASE10_LEDGER_EXACT_CHECK_2=python3 scripts/zigux/check-phase10-core-packet.py`
- `PHASE10_LEDGER_EXACT_CHECK_3=python3 scripts/zigux/validate-phase10.py`
- `PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-harness-coverage.py`
- `PHASE10_LEDGER_EXACT_CHECK_5=python3 scripts/zigux/validate-phase10-closure.py`
- `PHASE10_LEDGER_EXACT_CHECK_6=zig build test --build-file zigux/tests/phase10_build.zig --summary all`
- `PHASE10_LEDGER_EXACT_CHECK_7=make -C zigux phase10-validate`
- `PHASE10_LEDGER_EXACT_CHECK_8=make -C zigux phase10-test`
- `PHASE10_LEDGER_EXACT_CHECK_9=make -C zigux phase10`
- `PHASE10_LEDGER_NEXT_STEP=leave_parked_unless_phase10-core-probe-remove-lifecycle_or_phase10-virtio-input-registration-lifecycle_or_phase10-mmio-lifecycle-and-irq-paths_splits_smaller`
- `PHASE10_LEDGER_BLOCKERS=phase10-core-probe-remove-lifecycle,phase10-virtio-input-registration-lifecycle,phase10-mmio-lifecycle-and-irq-paths`
- `PHASE10_LEDGER_LANDED_CORE_HELPERS=phase10-config-generation-summary-helper,phase10-config-delivery-disposition-helper,phase10-config-driver-toggle-guard-helper`
- `PHASE10_LEDGER_LANDED_RING_HELPERS=phase10-virtqueue-shape-helper,phase10-used-buffer-polling-helper,phase10-callback-disable-helper,phase10-callback-enable-helper,phase10-callback-enable-prepare-helper,phase10-callback-delay-helper,phase10-notify-prepare-helper,phase10-queue-reset-guard-helper,phase10-queue-reset-helper,phase10-broken-queue-recovery-helper`
- `PHASE10_LEDGER_LANDED_INPUT_HELPERS=phase10-virtio-input-capability-setup-helper,phase10-virtio-input-multitouch-slot-helper,phase10-virtio-input-teardown-observation-helper,phase10-virtio-input-registration-preflight-helper,phase10-virtio-input-queue-callback-preflight-helper,phase10-virtio-input-probe-preflight-helper,phase10-virtio-input-registration-blocker-helper`
- `PHASE10_LEDGER_LANDED_MMIO_HELPERS=phase10-mmio-register-window-helper,phase10-mmio-queue-register-helper,phase10-mmio-queue-notify-helper,phase10-mmio-queue-address-helper,phase10-mmio-config-window-helper,phase10-mmio-config-write-helper,phase10-mmio-interrupt-ack-helper,phase10-mmio-probe-preflight-helper`

This ledger stays intentionally narrow. It records the roadmap-backed closure packet and the current parked-next-step posture without claiming queue setup, reset, IRQ parity, DMA, probe or remove lifecycle, or input registration lifecycle parity.

The roadmap-facing scoreboard is mirrored here from the shared closure manifest so the closure packet can be compared directly against the Phase 10 roadmap requirements without hopping between survey notes. That shared scoreboard still reads `starter_landed` for virtqueue wrappers, MMIO wrappers, and lab-only validation, while risky dual implementations remain `blocked_on_risky_transport` until a smaller transport-facing helper lane is ready.

The ledger now also mirrors the exact supporting evidence lists for each roadmap-scoreboard row, so reviewers can confirm the current virtqueue, MMIO, lab-validation, and risky-transport claims directly from this tranche record instead of opening the JSON manifest just to recover those file families.

The same manifest also carries the survey-provenance packet for the current closure bundle, so this ledger now publishes the exact lane ownership and inspected heads behind the live core, ring, input, and MMIO survey notes instead of leaving that tranche evidence implicit.

The live repo now also ships `python3 scripts/zigux/check-phase10-survey-provenance.py` as a supporting provenance readback that compares the shared closure manifest's core, ring, input, and MMIO lane keys plus surveyed commits back against the four lane manifests. Keeping that narrower checker explicit here makes the shared scoreboard easier to trust without pretending it is already part of the published exact shared replay packet.

The shared closure manifest now also keeps the landed core helper packet explicit: the core survey surface has advanced beyond the earlier config-summary pair and now includes the non-nestable `phase10-config-driver-toggle-guard-helper` beside `phase10-config-generation-summary-helper` and `phase10-config-delivery-disposition-helper`, so this ledger mirrors that three-rung core packet instead of leaving the newest core-local parity step visible only in the manifest-backed survey files.

The same closure packet also keeps the landed ring helper packet explicit, while the dedicated input survey packet, the focused registration-blocker replay build, and the wider shared Phase 10 validator keep the landed input capability, multitouch-slot, teardown-observation, registration-preflight, queue-callback-preflight, probe-preflight, and registration-blocker helper ladder reviewable. Recording that split here keeps the active virtio tranche self-contained without overstating the shared landed-input scalar beyond the live closure manifest.

The same closure packet also stays reviewable through the dedicated core lab gate plus the dedicated core, ring, input, and MMIO survey gates, and now also the focused ring drained-reset reuse, multitouch-preflight, registration-blocker, and queue-isolation replays, so this ledger names the parked queue-handling and ready-state harness surface explicitly instead of letting those focused replays live only inside the shared build wiring.

The direct closure-inventory checker now also stays explicit beside the dedicated core-packet checker carried by the live `make -C zigux phase10-validate` route, the dedicated harness-coverage checker, the shared closure validator, and the wider Phase 10 validator, so the parked packet keeps its named docs, manifests, drivers, and tests reviewable even when the combined `make -C zigux phase10-validate` wrapper is not the only command under inspection.

The shared closure note and manifest also keep the roadmap-boundary packet explicit: Phase 10 stays limited to `drivers/virtio/*.zig` plus justified helper bridges in `zigux/kernel/` or `zigux/helpers/`, the allowed evidence stays limited to driver-local lab slices, survey manifests, and shared validation gates, and any future freeze-boundary status change still needs an Architecture Council reopen record before this tranche can widen.

The same freeze-boundary packet keeps `kernel/workqueue.c` and `kernel/trace/ring_buffer.c` in the separate Phase 14 study-only family, so this ledger now records those parked anchors directly instead of leaving them implicit in the companion closure note.

The shared closure manifest, the dedicated MMIO survey gate, the dedicated harness-coverage checker, the shared Phase 10 validator, the dedicated input registration-blocker replay build, and the dedicated MMIO survey now agree that the active virtio tranche keeps the risky input registration lifecycle fence explicit beside the landed MMIO helper ladder through bounded interrupt acknowledgement plus probe preflight, so this ledger keeps that reviewable helper-and-validation set explicit instead of collapsing the input and MMIO packets into only their remaining transport blockers.

The exact replay packet for the current closure bundle is:

1. `python3 scripts/zigux/check-phase10-closure-inventory.py`
2. `python3 scripts/zigux/check-phase10-core-packet.py`
3. `python3 scripts/zigux/validate-phase10.py`
4. `python3 scripts/zigux/check-phase10-harness-coverage.py`
5. `python3 scripts/zigux/validate-phase10-closure.py`
6. `zig build test --build-file zigux/tests/phase10_build.zig --summary all`
7. `make -C zigux phase10-validate`
8. `make -C zigux phase10-test`
9. `make -C zigux phase10`
