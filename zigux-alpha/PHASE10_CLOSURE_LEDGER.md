# Phase 10 Closure Ledger

This focused ledger records the current closure-evidence bundle for the active Phase 10 virtio tranche.

- `PHASE10_LEDGER_STATUS=active`
- `PHASE10_LEDGER_TRANCHE=virtio-lab-bundle`
- `PHASE10_LEDGER_SCOPE=virtio-core,virtio-ring,virtio-input,virtio-mmio-lab-bundle`
- `PHASE10_LEDGER_ROADMAP_ANCHORS=drivers/virtio/virtio.c,drivers/virtio/virtio_ring.c,drivers/virtio/virtio_input.c,drivers/virtio/virtio_mmio.c`
- `PHASE10_LEDGER_EVIDENCE=Documentation/zigux/phase10-closure-evidence.md`
- `PHASE10_LEDGER_CORE_PACKET_VALIDATE=scripts/zigux/check-phase10-core-packet.py`
- `PHASE10_LEDGER_TESTS_README_CORE_VALIDATE=scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- `PHASE10_LEDGER_VALIDATE=scripts/zigux/validate-phase10-closure.py`
- `PHASE10_LEDGER_HARNESS_COVERAGE_VALIDATE=scripts/zigux/check-phase10-harness-coverage.py`
- `PHASE10_LEDGER_SHARED_VALIDATE=scripts/zigux/validate-phase10.py`
- `PHASE10_LEDGER_MANIFEST=zigux/tests/phase10_closure_manifest.json`
- `PHASE10_LEDGER_CORE_SLICE_GAP=Documentation/zigux/phase10-virtio-core-slice.md`
- `PHASE10_LEDGER_CORE_SURVEY=Documentation/zigux/phase10-virtio-core-survey.md`
- `PHASE10_LEDGER_RING_SURVEY=Documentation/zigux/phase10-virtio-ring-survey.md`
- `PHASE10_LEDGER_INPUT_SURVEY=Documentation/zigux/phase10-virtio-input-survey.md`
- `PHASE10_LEDGER_MMIO_SURVEY=Documentation/zigux/phase10-virtio-mmio-survey.md`
- `PHASE10_LEDGER_REPO_REALITY_GAPS=Documentation/zigux/phase10-virtio-core-slice.md,Documentation/zigux/phase10-virtio-ring-slice.md,Documentation/zigux/phase10-virtio-input-slice.md,Documentation/zigux/phase10-virtio-input-module-slice.md,Documentation/zigux/phase10-virtio-mmio-slice.md`
- `PHASE10_LEDGER_CONTENTS_BRIDGE_GAPS=drivers/virtio/virtio_ring.zig,drivers/virtio/virtio_ring_verify.zig,zigux/tests/phase10_virtio_ring.zig,zigux/tests/phase10_virtio_ring_reset_reuse.zig,zigux/tests/phase10_virtio_ring_survey.zig,scripts/zigux/check-phase10-ring-packet.py`
- `PHASE10_LEDGER_PUBLIC_FALLBACK_CONFIRMED_RING_SURFACES=drivers/virtio/virtio_ring.zig,zigux/tests/phase10_virtio_ring_reset_reuse.zig`
- `PHASE10_LEDGER_MMIO_CONTENTS_BRIDGE_GAPS=drivers/virtio/virtio_mmio.zig,drivers/virtio/virtio_mmio_verify.zig,zigux/tests/phase10_build.zig,zigux/tests/phase10_virtio_mmio.zig,zigux/tests/phase10_virtio_mmio_survey.zig,zigux/tests/phase10_virtio_mmio_manifest.json`
- `PHASE10_LEDGER_CORE_LAB_GATE=zigux/tests/phase10_virtio_core.zig`
- `PHASE10_LEDGER_CORE_RESET_QUEUE_REPLAY=zigux/tests/phase10_virtio_core_reset_queue.zig`
- `PHASE10_LEDGER_CORE_SURVEY_GATE=zigux/tests/phase10_virtio_core_survey.zig`
- `PHASE10_LEDGER_DRIVER_ID_REPLAY=zigux/tests/phase10_virtio_driver_id.zig`
- `PHASE10_LEDGER_RING_SURVEY_GATE=contents_bridge_gap:zigux/tests/phase10_virtio_ring_survey.zig`
- `PHASE10_LEDGER_INPUT_QUEUE_CALLBACK_PREFLIGHT_REPLAY=zigux/tests/phase10_virtio_input_queue_callback_preflight.zig`
- `PHASE10_LEDGER_INPUT_STATUS_DRAIN_REPLAY=zigux/tests/phase10_virtio_input_status_drain.zig`
- `PHASE10_LEDGER_INPUT_PROBE_PREFLIGHT_REPLAY=zigux/tests/phase10_virtio_input_probe_preflight.zig`
- `PHASE10_LEDGER_INPUT_REGISTRATION_PREFLIGHT_REPLAY=zigux/tests/phase10_virtio_input_registration_preflight.zig`
- `PHASE10_LEDGER_INPUT_TEARDOWN_OBSERVATION_REPLAY=zigux/tests/phase10_virtio_input_teardown_observation.zig`
- `PHASE10_LEDGER_INPUT_SURVEY_GATE=zigux/tests/phase10_virtio_input_survey.zig`
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
- `PHASE10_LEDGER_SURVEY_MMIO_LANE=P10-L10`
- `PHASE10_LEDGER_SURVEY_CORE_COMMIT=c11221dc7a68d7511ae1c69d64b3f08528287ed8`
- `PHASE10_LEDGER_SURVEY_RING_COMMIT=bdfe88e865b94387b3c3bd41ca98054c452f78b9`
- `PHASE10_LEDGER_SURVEY_INPUT_COMMIT=7361ac51374149a96b7a7a2c6ea3c995d8cc1231`
- `PHASE10_LEDGER_SURVEY_MMIO_COMMIT=84f90e23ad1c28ae345905d5293a8c5395f37d43`
- `PHASE10_LEDGER_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed`
- `PHASE10_LEDGER_SCOREBOARD_VIRTQUEUE_EVIDENCE=zigux/tests/phase10_virtio_ring_manifest.json,Documentation/zigux/phase10-virtio-ring-survey.md,Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `PHASE10_LEDGER_ROADMAP_MMIO_WRAPPERS=starter_landed`
- `PHASE10_LEDGER_MMIO_WRAPPERS=starter_landed`
- `PHASE10_LEDGER_SCOREBOARD_MMIO_EVIDENCE=drivers/virtio/virtio_mmio.zig,zigux/tests/phase10_virtio_mmio.zig,drivers/virtio/virtio_mmio_verify.zig,zigux/tests/phase10_virtio_mmio_manifest.json,Documentation/zigux/phase10-virtio-mmio-survey.md`
- `PHASE10_LEDGER_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed`
- `PHASE10_LEDGER_SCOREBOARD_LAB_ONLY_DRIVER_VALIDATION_EVIDENCE=Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md,zigux/tests/phase10_build.zig,zigux/tests/phase10_virtio_core_reset_queue.zig,zigux/tests/phase10_virtio_driver_id.zig,drivers/virtio/virtio_verify.zig,drivers/virtio/virtio_input_verify.zig,zigux/tests/phase10_virtio_input_probe_preflight.zig,zigux/tests/phase10_virtio_input_registration_preflight.zig,zigux/tests/phase10_virtio_input_teardown_observation.zig,zigux/tests/phase10_virtio_input_queue_callback_preflight.zig,zigux/tests/phase10_virtio_input_status_drain.zig,drivers/virtio/virtio_mmio_verify.zig,zigux/tests/phase10_virtio_mmio.zig,zigux/tests/phase10_virtio_mmio_survey.zig,scripts/zigux/check-phase10-core-packet.py,scripts/zigux/check-phase10-input-packet.py,scripts/zigux/check-phase10-mmio-packet.py,scripts/zigux/check-phase10-mmio-freeze-boundary.py,scripts/zigux/check-phase10-harness-coverage.py,scripts/zigux/check-phase10-tests-readme-core-surfaces.py,zigux/Makefile,.github/workflows/zigux-bootstrap.yml`
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
- `PHASE10_LEDGER_EXACT_CHECK_1=python3 scripts/zigux/validate-phase10.py`
- `PHASE10_LEDGER_EXACT_CHECK_2=python3 scripts/zigux/validate-phase10-closure.py`
- `PHASE10_LEDGER_EXACT_CHECK_3=make -C zigux phase10-validate`
- `PHASE10_LEDGER_EXACT_CHECK_4=python3 scripts/zigux/check-phase10-core-packet.py`
- `PHASE10_LEDGER_EXACT_CHECK_5=python3 scripts/zigux/check-phase10-ring-packet.py`
- `PHASE10_LEDGER_EXACT_CHECK_6=python3 scripts/zigux/check-phase10-input-packet.py`
- `PHASE10_LEDGER_EXACT_CHECK_7=python3 scripts/zigux/check-phase10-mmio-packet.py`
- `PHASE10_LEDGER_EXACT_CHECK_8=python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py`
- `PHASE10_LEDGER_EXACT_CHECK_9=python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test`
- `PHASE10_LEDGER_EXACT_CHECK_10=python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
- `PHASE10_LEDGER_EXACT_CHECK_11=python3 scripts/zigux/check-phase10-harness-coverage.py --self-test`
- `PHASE10_LEDGER_EXACT_CHECK_12=python3 scripts/zigux/check-phase10-harness-coverage.py`
- `PHASE10_LEDGER_EXACT_CHECK_13=zig build test --build-file zigux/tests/phase10_build.zig --summary all`
- `PHASE10_LEDGER_EXACT_CHECK_14=make -C zigux phase10-test`
- `PHASE10_LEDGER_EXACT_CHECK_15=make -C zigux phase10`
- `PHASE10_LEDGER_NEXT_STEP=leave_parked_unless_shared_phase10_surfaces_need_another_small_truthfulness_sync_around_ring_or_mmio_contents_bridge_gaps_or_a_smaller_input_followup_splits_off_cleanly`
- `PHASE10_LEDGER_BLOCKERS=phase10-virtio-input-registration-lifecycle,phase10-mmio-lifecycle-and-irq-paths`
- `PHASE10_LEDGER_LANDED_CORE_HELPERS=phase10-queue-shape-bookkeeping-helper,phase10-config-generation-bookkeeping-helper,phase10-interrupt-ack-bookkeeping-helper,phase10-lifecycle-guard-bookkeeping-helper,phase10-driver-validation-narrowing-helper,phase10-reset-replay-bookkeeping-helper`
- `PHASE10_LEDGER_LANDED_RING_HELPERS=phase10-virtqueue-shape-helper,phase10-used-buffer-polling-helper,phase10-callback-enable-helper,phase10-callback-delay-helper,phase10-notify-prepare-helper,phase10-notification-data-summary-helper,phase10-broken-queue-poll-guard,phase10-queue-reset-helper,phase10-queue-reset-readiness-helper,phase10-ring-verify-replay,phase10-virtio-ring-slice-note`
- `PHASE10_LEDGER_LANDED_INPUT_HELPERS=phase10-virtio-input-capability-setup-helper,phase10-virtio-input-multitouch-slot-helper,phase10-virtio-input-teardown-observation-helper,phase10-virtio-input-registration-preflight-helper,phase10-virtio-input-queue-callback-preflight-helper,phase10-virtio-input-status-drain-helper`
- `PHASE10_LEDGER_LANDED_MMIO_HELPERS=phase10-mmio-register-window-helper,phase10-mmio-queue-size-helper,phase10-mmio-feature-word-selector-helper,phase10-mmio-feature-negotiation-summary-helper,phase10-mmio-config-window-helper,phase10-mmio-config-write-plan-helper,phase10-mmio-transport-identity-helper,phase10-mmio-probe-preflight-helper,phase10-mmio-config-write-disposition-helper,phase10-mmio-selected-queue-readiness-helper`

This ledger stays intentionally narrow.

It records the roadmap-backed closure packet and the current parked-next-step posture without claiming queue setup, reset, IRQ parity, DMA, probe or remove lifecycle, or input registration lifecycle parity. The roadmap-facing scoreboard is mirrored here from the shared closure manifest so the closure packet can be compared directly against the Phase 10 roadmap requirements without hopping between survey notes.

That shared scoreboard still reads `starter_landed` for virtqueue wrappers, MMIO wrappers, and lab-only validation, while risky dual implementations remain `blocked_on_risky_transport` until a smaller transport-facing helper lane is ready.

The ledger now also mirrors the exact supporting evidence lists for each roadmap-scoreboard row, so reviewers can confirm the current virtqueue, MMIO, lab-validation, and risky-transport claims directly from this tranche record instead of opening the JSON manifest just to recover those file families.

The same manifest also carries the survey-provenance packet for the current closure bundle, so this ledger now publishes the exact lane ownership and inspected heads behind the live core, ring, input, and MMIO survey notes instead of leaving that tranche evidence implicit.

The five older Phase 10 slice-note paths remain the true repo-reality gaps on current `master`, so this ledger keeps those note companions separate from readback-path flakiness instead of folding them together with authenticated contents misses.

Fresh authenticated rereads still returned `404` for the broader direct ring packet through the GitHub contents bridge: `drivers/virtio/virtio_ring.zig`, `drivers/virtio/virtio_ring_verify.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_ring_survey.zig`, and `scripts/zigux/check-phase10-ring-packet.py` all failed through that exact current-head read path. Public GitHub fallback rereads, however, still exposed at least `drivers/virtio/virtio_ring.zig` and `zigux/tests/phase10_virtio_ring_reset_reuse.zig` on current `master`. This ledger therefore records those ring paths as contents-bridge gaps rather than repo-reality gaps, while keeping the shared ring lane anchored to `zigux/tests/phase10_virtio_ring_manifest.json`, `Documentation/zigux/phase10-virtio-ring-survey.md`, and `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` until a later run can re-read the broader direct ring packet through one consistent path.

Fresh authenticated rereads in this slot also returned `404` for the broader direct MMIO packet through the same GitHub contents bridge: `drivers/virtio/virtio_mmio.zig`, `drivers/virtio/virtio_mmio_verify.zig`, `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_survey.zig`, and `zigux/tests/phase10_virtio_mmio_manifest.json` all failed through that exact current-head read path. The dedicated MMIO survey note remained directly readable on current `master`, and the shared MMIO checker pair stayed directly readable in the same run, so this ledger records those MMIO paths as contents-bridge gaps rather than repo-reality gaps, while keeping the MMIO lane anchored to `Documentation/zigux/phase10-virtio-mmio-survey.md`, `scripts/zigux/check-phase10-mmio-packet.py`, and `scripts/zigux/check-phase10-mmio-freeze-boundary.py` until a later run can re-read the broader direct MMIO packet through one consistent path.

The shared closure manifest-backed helper ladders now stay explicit here for all four bounded Phase 10 lanes, so reviewers can recover the current core, ring, input, and MMIO starter packet directly from this tranche record instead of stopping at older shorthand. For the ring lane specifically, that helper ladder is retained here as manifest-carried tranche provenance plus partial public-fallback confirmation, not as a claim that the entire direct ring helper, verify, survey, replay, and checker packet was freshly re-read through the authenticated contents bridge in this run. For the MMIO lane specifically, that helper ladder is retained here as manifest-carried tranche provenance plus the directly readable survey and shared-checker surfaces, not as a claim that the entire direct MMIO helper, verify, build, manifest, and survey packet was freshly re-read through the authenticated contents bridge in this run. The exact replay packet for the current closure bundle is:

1. `python3 scripts/zigux/validate-phase10.py`
2. `python3 scripts/zigux/validate-phase10-closure.py`
3. `make -C zigux phase10-validate`
4. `python3 scripts/zigux/check-phase10-core-packet.py`
5. `python3 scripts/zigux/check-phase10-ring-packet.py`
6. `python3 scripts/zigux/check-phase10-input-packet.py`
7. `python3 scripts/zigux/check-phase10-mmio-packet.py`
8. `python3 scripts/zigux/check-phase10-mmio-freeze-boundary.py`
9. `python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py --self-test`
10. `python3 scripts/zigux/check-phase10-tests-readme-core-surfaces.py`
11. `python3 scripts/zigux/check-phase10-harness-coverage.py --self-test`
12. `python3 scripts/zigux/check-phase10-harness-coverage.py`
13. `zig build test --build-file zigux/tests/phase10_build.zig --summary all`
14. `make -C zigux phase10-test`
15. `make -C zigux phase10`
