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
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_closure_manifest.json`
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

- `PHASE10_DOC_COUNT=9`
- `PHASE10_MANIFEST_COUNT=4`
- `PHASE10_DRIVER_COUNT=4`
- `PHASE10_TEST_COUNT=8`
- `PHASE10_HAS_VIRTIO_MMIO_ZIG=yes`

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
- `lab-only driver validation`: `starter_landed` through `zigux/tests/phase10_build.zig`, `scripts/zigux/validate-phase10-closure.py`, and the shared `make -C zigux phase10-{validate,test}` entrypoints
- `dual implementations for risky areas`: `blocked_on_risky_transport` because the current ring, input, and MMIO manifests still keep MMIO lifecycle paths, queue setup or reset, IRQ parity, DMA-facing paths, input registration lifecycle, and probe or remove work out of scope until smaller helpers land first

This keeps the closure packet aligned with the roadmap's real Phase 10 requirements: queue-facing lab wrappers are landed, the bounded MMIO register-window, queue-register, queue-notify, queue-address, and config-window helpers are now landed, the lab validation gate is real, and risky transport expansion is still intentionally blocked.

## Cross-Phase Boundary

- `PHASE10_REFERENCE_SAMPLE_PARITY_OUT_OF_SCOPE=yes`
- `PHASE10_RUNTIME_STARTER_PARITY_OUT_OF_SCOPE=yes`
- `PHASE10_CROSS_PHASE_SCOREBOARD_BOUNDARY=phase5_reference_samples_and_phase9_runtime_starters_do_not_count_as_phase10_virtio_driver_evidence`

The current Phase 10 parity scoreboard only counts the bounded `drivers/virtio/*.zig` lane plus its dedicated `zigux/tests/phase10_*` manifests, survey gates, and closure packet.

This means the already-landed `samples/zigux/` reference samples from Phase 5 and the `samples/zigux/runtime_*` starter surfaces from Phase 9 remain separate evidence families:

- `samples/zigux/` and `zigux/tests/phase5_build.zig` stay in the reviewable-sample lane
- `samples/zigux/`, `Documentation/zigux/phase9-runtime-loader-gap-survey.md`, `zigux/tests/runtime_loader_gap_manifest.json`, `zigux/tests/runtime_loader_gap_survey.zig`, and `zigux/tests/phase9_build.zig` stay in the bounded runtime-starter lane
- neither evidence family advances the Phase 10 virtio driver scoreboard unless a future roadmap-backed lane explicitly republishes the same behavior inside the Phase 10 driver-local evidence set

This keeps the current parity readout honest: the shipped samples and runtime starters still matter for review, but they do not count as Phase 10 virtio driver parity evidence.

## Exact Checks

The current Phase 10 tranche is only considered evidence-verified when all of the following stay green:

1. closure evidence validation
- `python3 scripts/zigux/validate-phase10-closure.py`

2. shared Phase 10 test build
- `zig build test --build-file zigux/tests/phase10_build.zig --summary all`

3. Linux-style Phase 10 validate entrypoint
- `make -C zigux phase10-validate`

4. Linux-style Phase 10 test entrypoint
- `make -C zigux phase10-test`

5. Linux-style combined Phase 10 entrypoint
- `make -C zigux phase10`

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
- `PHASE10_ALLOWED_ROADMAP_DESTINATIONS=drivers/virtio/*.zig,zigux/helpers/`
- `PHASE10_ALLOWED_EVIDENCE_KINDS=driver_local_lab_slices,survey_manifests,shared_validation_gates`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_REQUIRED=yes`
- `PHASE10_ARCHITECTURE_COUNCIL_REOPEN_ATTACHED=no`
- `PHASE10_FORBIDDEN_TRANSPORT_CLAIMS=queue_setup_reset_paths,irq_parity,dma_paths,input_registration_lifecycle,probe_remove_lifecycle`

The roadmap keeps Phase 10 inside bounded virtio delivery under `drivers/virtio/*.zig`, and the freeze map keeps the current deep-core anchors out of active Zigux delivery:

- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

The study-only boundary anchors also remain outside this Phase 10 tranche:

- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

This closure packet therefore records an aligned freeze-boundary reading rather than a status-change request:

- no Architecture Council status-change request is attached to this Phase 10 tranche
- any future freeze-boundary reopen would require an explicit Architecture Council record before this tranche can widen beyond the current lab-only destinations
- no parity scorecard entry is being used to reopen a freeze-in-C anchor
- the current virtio closure bundle stays limited to driver-local lab slices, survey manifests, and shared validation gates

## Current Tranche Reading

The exact current reading of the live repo is:

- `drivers/virtio/virtio.zig` is the bounded virtio-core starter
- `Documentation/zigux/phase10-virtio-core-survey.md`, `zigux/tests/phase10_virtio_core_manifest.json`, and `zigux/tests/phase10_virtio_core_survey.zig` record the already-landed core survey surface, including the config-generation summary helper that closes the last core-local starter gap before risky lifecycle work
- `drivers/virtio/virtio_ring.zig` is the bounded virtqueue helper starter
- `drivers/virtio/virtio_input.zig` is the bounded input-driver starter
- `drivers/virtio/virtio_mmio.zig`, `zigux/tests/phase10_virtio_mmio.zig`, and `Documentation/zigux/phase10-virtio-mmio-slice.md` now record the bounded MMIO register-window, queue-register, queue-notify, queue-address, and config-window starter surface
- `Documentation/zigux/phase10-virtio-mmio-survey.md` and `zigux/tests/phase10_virtio_mmio_manifest.json` keep the landed config-window helper plus the next config-write helper explicit while MMIO lifecycle and IRQ work remain blocked

This means the current evidence bundle is reviewable, but Phase 10 is not globally closed:

- the bounded MMIO register-window, queue-register, queue-notify, queue-address, and config-window helpers are landed; config-write planning is the next narrow transport-facing follow-up
- transport-backed queue setup, interrupt handling, DMA-facing paths, and broader lifecycle parity remain out of scope
- the blocked transport claim set stays explicit: `queue_setup_reset_paths`, `irq_parity`, `dma_paths`, `input_registration_lifecycle`, and `probe_remove_lifecycle`
- the current lane manifests may only point at `drivers/virtio/*.zig` and `zigux/helpers/` as roadmap destinations while the freeze-boundary status remains aligned
- `Documentation/zigux/freeze-map.md` and `Documentation/zigux/review-checklist.md` remain the shared guardrails for transport-facing claims in this tranche
- the current manifest-backed transport boundary stays explicit because the input survey advances only to the ready-next `phase10-virtio-input-registration-preflight-helper`, the MMIO survey packet records the landed `phase10-mmio-register-window-helper`, `phase10-mmio-queue-register-helper`, `phase10-mmio-queue-notify-helper`, `phase10-mmio-queue-address-helper`, and `phase10-mmio-config-window-helper`, the MMIO survey advances only to the ready-next `phase10-mmio-config-write-helper`, and `phase10-virtio-input-registration-lifecycle` plus `phase10-mmio-lifecycle-and-irq-paths` must stay `blocked_on_risky_transport` until those smaller helpers land first

## Boundary

This evidence record does not imply:

- full `drivers/virtio/virtio.c` parity
- full `drivers/virtio/virtio_ring.c` parity
- full `drivers/virtio/virtio_mmio.c` parity
- full `drivers/virtio/virtio_input.c` registration or lifecycle parity
- Phase 10 roadmap closure as a whole

It only means the current bounded virtio tranche now has an explicit, machine-checkable evidence record instead of relying on scattered documentation alone.
