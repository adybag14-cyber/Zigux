# Phase 10 Closure Evidence

This document records the current closure evidence for the active bounded Phase 10 virtio tranche without claiming that all Phase 10 roadmap work is closed.

## Status

- `PHASE10_STATUS=active`
- `PHASE10_TRANCHE=virtio-lab-bundle`
- `PHASE10_CLOSURE_EVIDENCE=verified`
- scope: current virtio core, virtio ring, virtio input, and virtio MMIO starter plus survey evidence only
- product boundary:
  - `drivers/virtio/virtio.zig`
  - `drivers/virtio/virtio_ring.zig`
  - `drivers/virtio/virtio_input.zig`
  - `drivers/virtio/virtio_mmio.zig`
  - `zigux/tests/phase10_build.zig`
  - `zigux/tests/phase10_virtio_core.zig`
  - `zigux/tests/phase10_virtio_core_survey.zig`
  - `zigux/tests/phase10_virtio_ring.zig`
  - `zigux/tests/phase10_virtio_ring_reset_reuse.zig`
  - `zigux/tests/phase10_virtio_ring_survey.zig`
  - `zigux/tests/phase10_virtio_input.zig`
  - `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`
  - `zigux/tests/phase10_virtio_input_survey.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`
  - `zigux/tests/phase10_virtio_mmio_survey.zig`
  - `zigux/tests/phase10_closure_manifest.json`
  - `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`
  - `scripts/zigux/check-phase10-harness-coverage.py`
  - `scripts/zigux/check-phase10-closure-inventory.py`
  - `scripts/zigux/validate-phase10-closure.py`
  - `Documentation/zigux/phase10-closure-evidence.md`

## Why this record exists

The Phase 10 roadmap is still active, but the live repo already carries enough bounded virtio evidence that review should no longer depend on manually checking scattered slice notes, manifests, and test entrypoints.

This record closes that hygiene gap by naming the exact current evidence set and the exact checks that must stay green before the current Phase 10 tranche can keep claiming reviewable progress.

## Current Evidence Set

The current bounded Phase 10 evidence set is:

- `Documentation/zigux/phase10-virtio-core-slice.md`
- `Documentation/zigux/phase10-virtio-core-survey.md`
- `Documentation/zigux/phase10-virtio-ring-slice.md`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-virtio-input-slice.md`
- `Documentation/zigux/phase10-virtio-input-module-slice.md`
- `Documentation/zigux/phase10-virtio-input-survey.md`
- `Documentation/zigux/phase10-virtio-mmio-slice.md`
- `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `zigux/tests/phase10_virtio_core_manifest.json`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `zigux/tests/phase10_virtio_input_manifest.json`
- `zigux/tests/phase10_virtio_mmio_manifest.json`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`
- `zigux/tests/phase10_virtio_core.zig`
- `zigux/tests/phase10_virtio_core_survey.zig`
- `zigux/tests/phase10_virtio_ring.zig`
- `zigux/tests/phase10_virtio_ring_reset_reuse.zig`
- `zigux/tests/phase10_virtio_ring_survey.zig`
- `zigux/tests/phase10_virtio_input.zig`
- `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`
- `zigux/tests/phase10_virtio_input_survey.zig`
- `zigux/tests/phase10_virtio_mmio.zig`
- `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`
- `zigux/tests/phase10_virtio_mmio_survey.zig`

- `PHASE10_DOC_COUNT=9`
- `PHASE10_MANIFEST_COUNT=4`
- `PHASE10_DRIVER_COUNT=4`
- `PHASE10_TEST_COUNT=11`
- `PHASE10_HAS_VIRTIO_MMIO_ZIG=yes`

The shared closure manifest now carries explicit landed-helper evidence for the core config summaries plus the non-nestable driver-side config-toggle guard, the ring queue-discipline ladder through broken-queue recovery, the input capability-setup, multitouch-slot, teardown-observation, and preflight ladder through probe preflight, and the MMIO helper ladder through bounded interrupt acknowledgement plus probe preflight. The shared closure guards therefore keep the current ring, input, and MMIO helper ladders explicit at the shared-packet boundary, while the dedicated input survey packet and broader shared Phase 10 validator keep the newer registration-blocker helper reviewable without letting that parked lifecycle fence disappear.

The same closure packet now also keeps the already-landed focused harness coverage explicit: the ring drained-reset reuse replay, the multitouch-ready input preflight replay, and the MMIO multi-queue isolation replay, including the reset-clears-legacy-and-modern queue-address-plan pass after queue selection changes, are part of the Phase 10 evidence set rather than being left visible only from `zigux/tests/phase10_build.zig`, and the dedicated `scripts/zigux/check-phase10-harness-coverage.py` replay is now part of the exact closure contract instead of only indirect supporting evidence.

## Survey Provenance

- `PHASE10_SURVEY_PROVENANCE_SOURCE=manifest_derived`
- `PHASE10_SURVEY_CORE_LANE=P10-L01`
- `PHASE10_SURVEY_RING_LANE=P10-L07`
- `PHASE10_SURVEY_INPUT_LANE=P10-L13`
- `PHASE10_SURVEY_MMIO_LANE=P10-L18`
- `PHASE10_SURVEY_CORE_COMMIT=d30cbe483a2f019ae797b309a29556bd58fe00d0`
- `PHASE10_SURVEY_RING_COMMIT=fe8a43ea2e186da0da152198b571dff57ea3c38c`
- `PHASE10_SURVEY_INPUT_COMMIT=f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21`
- `PHASE10_SURVEY_MMIO_COMMIT=0945df1cf664a3582d7241f859183a13f3f04adb`

The shared closure manifest and the dedicated Phase 10 closure ledger already carry this provenance packet, but the main closure evidence note had still been leaving those exact lane owners and inspected heads implicit. Mirroring them here keeps the closure bundle reviewer-facing and self-contained, so the core, ring, input, and MMIO survey notes can be traced back to their bounded lane packets without hopping out to the JSON manifest first.

## Roadmap Parity Scoreboard

This scoreboard records the current parity evidence against the Phase 10 roadmap requirements rather than against full driver parity.

- `PHASE10_ROADMAP_PARITY_SCOREBOARD=present`
- `PHASE10_ROADMAP_SCOREBOARD_ROW_COUNT=4`
- `PHASE10_ROADMAP_VIRTQUEUE_WRAPPERS=starter_landed`
- `PHASE10_ROADMAP_MMIO_WRAPPERS=starter_landed`
- `PHASE10_ROADMAP_LAB_ONLY_DRIVER_VALIDATION=starter_landed`
- `PHASE10_ROADMAP_DUAL_IMPLEMENTATIONS_FOR_RISKY_AREAS=blocked_on_risky_transport`

The current roadmap-facing reading is:

- `virtqueue wrappers`: `starter_landed` through `drivers/virtio/virtio_ring.zig`, `zigux/tests/phase10_virtio_ring.zig`, `zigux/tests/phase10_virtio_ring_manifest.json`, and `Documentation/zigux/phase10-virtio-ring-survey.md`
- `MMIO wrappers`: `starter_landed` through `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio_manifest.json`, `Documentation/zigux/phase10-virtio-mmio-slice.md`, and `Documentation/zigux/phase10-virtio-mmio-survey.md`
- `lab-only driver validation`: `starter_landed` through `zigux/tests/phase10_build.zig`, `zigux/tests/phase10_virtio_ring_reset_reuse.zig`, `zigux/tests/phase10_virtio_input_multitouch_preflight.zig`, `zigux/tests/phase10_virtio_mmio_queue_isolation.zig`, `scripts/zigux/check-phase10-harness-coverage.py`, `scripts/zigux/check-phase10-closure-inventory.py`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, `Documentation/zigux/phase10-closure-evidence.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, and the shared `make -C zigux phase10-{validate,test}` entrypoints
- `dual implementations for risky areas`: `blocked_on_risky_transport` because the current core, ring, input, and MMIO manifests still keep MMIO lifecycle paths, queue setup or reset, IRQ parity, DMA-facing paths, input registration lifecycle, and probe or remove work out of scope until smaller helpers land first

This keeps the closure packet aligned with the roadmap's real Phase 10 requirements: queue-facing lab wrappers are landed, the bounded MMIO register-window, queue-register, queue-notify, queue-address, config-window, config-write, interrupt-ack, and probe-preflight helpers are now landed, the lab validation gate is real, and risky transport expansion is still intentionally blocked.

## Cross-Phase Boundary

- `PHASE10_REFERENCE_SAMPLE_PARITY_OUT_OF_SCOPE=yes`
- `PHASE10_RUNTIME_STARTER_PARITY_OUT_OF_SCOPE=yes`
- `PHASE10_CROSS_PHASE_SCOREBOARD_BOUNDARY=phase5_reference_samples_and_phase9_runtime_starters_do_not_count_as_phase10_virtio_driver_evidence`

The current Phase 10 parity scoreboard only counts the bounded `drivers/virtio/*.zig` lane plus its dedicated `zigux/tests/phase10_*` manifests, survey gates, and closure packet.

This means the already-landed `samples/zigux/` reference samples from Phase 5 and the current manifest-backed Phase 9 runtime loader-gap ownership packet remain separate evidence families:

- `samples/zigux/` and `zigux/tests/phase5_build.zig` stay in the reviewable-sample lane
- `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `Documentation/zigux/phase9-runtime-loader-substrate-plan.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, `zigux/tests/runtime_trace_events_manifest.json`, `zigux/tests/phase9_build.zig`, `zigux/kernel/runtime_loader.zig`, `zigux/helpers/allocator_policy.zig`, `samples/zigux/runtime_atomic64_loader.zig`, `samples/zigux/runtime_bitmap_loader.zig`, `samples/zigux/runtime_kretprobe_loader.zig`, and the sample-only `samples/zigux/runtime_trace_events.zig` blocker surface stay in the bounded runtime-starter lane
- neither evidence family advances the Phase 10 virtio driver scoreboard unless a future roadmap-backed lane explicitly republishes the same behavior inside the Phase 10 driver-local evidence set

This keeps the current parity readout honest: the shipped samples and runtime starters still matter for review, but they do not count as Phase 10 virtio driver parity evidence.

## Exact Checks

The current Phase 10 tranche is only considered evidence-verified when all of the following stay green:

1. closure packet inventory validation
- `python3 scripts/zigux/check-phase10-closure-inventory.py`

2. bounded core packet validation
- `python3 scripts/zigux/check-phase10-core-packet.py`

3. shared Phase 10 validation
- `python3 scripts/zigux/validate-phase10.py`

4. focused harness coverage validation
- `python3 scripts/zigux/check-phase10-harness-coverage.py`

5. closure evidence validation
- `python3 scripts/zigux/validate-phase10-closure.py`

6. shared Phase 10 test build
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`

7. Linux-style Phase 10 validate entrypoint
- `make -C zigux phase10-validate`

8. Linux-style Phase 10 test entrypoint
- `make -C zigux phase10-test`

9. Linux-style combined Phase 10 entrypoint
- `make -C zigux phase10`

These checks now fail closed on the direct closure-inventory packet, the bounded core packet, the wider shared `scripts/zigux/validate-phase10.py` gate, the dedicated harness-coverage replay, the shared closure packet reached through `scripts/zigux/validate-phase10-closure.py`, the input multitouch-ready preflight replay, the MMIO queue-isolation replay, and the current MMIO ladder through bounded interrupt acknowledgement plus probe preflight, so `zigux/tests/phase10_closure_manifest.json`, `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`, `Documentation/zigux/phase10-closure-evidence.md`, `Documentation/zigux/phase10-virtio-mmio-survey.md`, and `zigux/tests/phase10_virtio_mmio_manifest.json` stay machine-checked together at the same interrupt-ack and probe-preflight rung.

- `PHASE10_CLOSURE_INVENTORY_GATE=python3 scripts/zigux/check-phase10-closure-inventory.py`
- `PHASE10_CORE_PACKET_GATE=python3 scripts/zigux/check-phase10-core-packet.py`
- `PHASE10_SHARED_VALIDATE_GATE=python3 scripts/zigux/validate-phase10.py`
- `PHASE10_HARNESS_COVERAGE_GATE=python3 scripts/zigux/check-phase10-harness-coverage.py`
- `PHASE10_CLOSURE_GATE=python3 scripts/zigux/validate-phase10-closure.py`
- `PHASE10_BUILD_GATE=zig build test --build-file zigux/tests/phase10_build.zig --summary all`
- `PHASE10_VALIDATE_ENTRYPOINT=make -C zigux phase10-validate`
- `PHASE10_TEST_ENTRYPOINT=make -C zigux phase10-test`
- `PHASE10_COMBINED_ENTRYPOINT=make -C zigux phase10`

## Freeze Boundary Reading

- `PHASE10_FREEZE_MAP=Documentation/zigux/freeze-map.md`
- `PHASE10_FREEZE_BOUNDARY_STATUS=aligned`
- `PHASE10_FREEZE_STATUS_CHANGE_CLAIM=no`
- `PHASE10_FREEZE_IN_C_ANCHOR_COUNT=4`
- `PHASE10_STUDY_ONLY_ANCHOR_COUNT=2`
- `PHASE10_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/kernel/,zigux/helpers/`
- `PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no`
- `PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle`

The roadmap keeps Phase 10 inside bounded virtio delivery under `drivers/virtio/*.zig`, with justified bridge helpers in `zigux/kernel/` or `zigux/helpers/` where needed, and the freeze map keeps the current deep-core anchors out of active Zigux delivery:

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

The study-only boundary anchors also remain outside this Phase 10 tranche and stay owned by the separate Phase 14 core-adjacent study-only lane:

- `kernel/workqueue.c` stays in the Phase 14 boundary maps, concurrency audits, and explicit stay-in-C decisions where warranted packet, with `kernel/workqueue_bridge.zig` as the only named future Zigux destination
- `kernel/trace/ring_buffer.c` stays in the Phase 14 wrapper-first or study-only posture with the same boundary maps and concurrency audits packet, and `kernel/trace/ring_buffer.zig` remains only a future destination if years of evidence justify it

This closure packet therefore records an aligned freeze-boundary reading rather than a status-change request:

- no Architecture Council status-change request is attached to this Phase 10 tranche
- any future freeze-boundary reopen would require an explicit Architecture Council record before this tranche can widen beyond the current lab-only destinations
- no parity scorecard entry is being used to reopen a freeze-in-C anchor
- the current virtio closure bundle stays limited to driver-local lab slices, survey manifests, and shared validation gates

## Current Tranche Reading

The exact current reading of the live repo is:

- `drivers/virtio/virtio.zig` is the bounded virtio-core starter
- `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` record the already-landed core survey surface, including the `phase10-config-generation-summary-helper`, the `phase10-config-delivery-disposition-helper`, and the `phase10-config-driver-toggle-guard-helper`, which keep the last in-memory config-change branch outcome and the documented non-nestable driver-side config toggle rule explicit before risky lifecycle work
- `drivers/virtio/virtio_ring.zig` is the bounded virtqueue helper starter
- `zigux/tests/phase10_virtio_ring_reset_reuse.zig` keeps the drained-reset reuse review surface explicit beside the ring helper ladder so the already-landed queue-reset helper does not read like a prose-only claim
- `drivers/virtio/virtio_input.zig` is the bounded input-driver starter
- `zigux/tests/phase10_virtio_input_multitouch_preflight.zig` keeps the ready-state input preflight packet honest by proving multitouch slot metadata survives into the later queue-callback and probe handoff summaries
- `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio.zig`, and `Documentation/zigux/phase10-virtio-mmio-slice.md` now record the bounded MMIO register-window, queue-register, queue-notify, queue-address, config-window, config-write, interrupt-ack, and probe-preflight starter surface
- `zigux/tests/phase10_virtio_mmio_queue_isolation.zig` keeps the queue-address planning and notify bookkeeping honest across queue-selection changes instead of leaving that multi-queue boundary implicit inside the shared build only
- `Documentation/zigux/phase10-virtio-mmio-survey.md` and `zigux/tests/phase10_virtio_mmio_manifest.json` now agree that the interrupt-ack and probe-preflight helpers are landed while MMIO lifecycle and IRQ work remain blocked

This means the current evidence bundle is reviewable, but Phase 10 is not globally closed:

- the bounded MMIO register-window, queue-register, queue-notify, queue-address, config-window, config-write, interrupt-ack, and probe-preflight helpers are landed
- transport-backed queue setup, interrupt handling, DMA-facing paths, and broader lifecycle parity remain out of scope
- the blocked transport claim set stays explicit: `queue_setup_reset_paths`, `irq_parity`, `dma_paths`, `input_registration_lifecycle`, and `probe_remove_lifecycle`
- the current manifest-backed blockers are `phase10-core-probe-remove-lifecycle`, `phase10-virtio-input-registration-lifecycle`, and `phase10-mmio-lifecycle-and-irq-paths`
- the current lane manifests may only point at `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/` as roadmap destinations while the freeze-boundary status remains aligned
- `Documentation/zigux/freeze-map.md` and `Documentation/zigux/review-checklist.md` remain the shared guardrails for transport-facing claims in this tranche
- the shared closure manifest now records the landed ring queue-discipline ladder, the input capability-setup, multitouch-slot, teardown-observation, and preflight ladder through probe preflight, the dedicated input survey packet plus the shared Phase 10 validator keep the parked registration-blocker helper explicit, the dedicated harness-coverage checker, and the MMIO helper ladder directly alongside the core helper evidence, so the current manifest-backed transport boundary stays explicit because the core survey records the landed `phase10-config-generation-summary-helper`, `phase10-config-delivery-disposition-helper`, and `phase10-config-driver-toggle-guard-helper`, the ring manifest-backed packet records the landed `phase10-virtqueue-shape-helper`, `phase10-used-buffer-polling-helper`, `phase10-callback-disable-helper`, `phase10-callback-enable-helper`, `phase10-callback-enable-prepare-helper`, `phase10-callback-delay-helper`, `phase10-notify-prepare-helper`, `phase10-queue-reset-guard-helper`, `phase10-queue-reset-helper`, and `phase10-broken-queue-recovery-helper`, the dedicated input packet keeps the landed `phase10-virtio-input-capability-setup-helper`, `phase10-virtio-input-multitouch-slot-helper`, `phase10-virtio-input-teardown-observation-helper`, `phase10-virtio-input-registration-preflight-helper`, `phase10-virtio-input-queue-callback-preflight-helper`, `phase10-virtio-input-probe-preflight-helper`, and `phase10-virtio-input-registration-blocker-helper` reviewable, the MMIO manifest-backed packet records the landed `phase10-mmio-register-window-helper`, `phase10-mmio-queue-register-helper`, `phase10-mmio-queue-notify-helper`, `phase10-mmio-queue-address-helper`, `phase10-mmio-config-window-helper`, `phase10-mmio-config-write-helper`, `phase10-mmio-interrupt-ack-helper`, and `phase10-mmio-probe-preflight-helper`, and only `phase10-core-probe-remove-lifecycle`, `phase10-virtio-input-registration-lifecycle`, and `phase10-mmio-lifecycle-and-irq-paths` remain constrained

## Boundary

This evidence record does not imply:

- full `drivers/virtio/virtio.c` parity
- full `drivers/virtio/virtio_ring.c` parity
- full `drivers/virtio/virtio_mmio.c` parity
- full `drivers/virtio/virtio_input.c` registration or lifecycle parity
- Phase 10 roadmap closure as a whole

It only means the current bounded virtio tranche now has an explicit, reviewable evidence record instead of relying on scattered documentation alone.
