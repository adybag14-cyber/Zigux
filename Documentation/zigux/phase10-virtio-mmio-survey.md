# Phase 10 Virtio MMIO Survey

This document records the bounded Phase 10 survey lane around `drivers/virtio/virtio_mmio.c`.

## Status
- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-mmio-survey`
- lane family: `Phase 10 virtio MMIO`
- lane key: `P10-L11`
- surveyed against current `master` readback on `2026-05-20`
- roadmap destinations: `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`
- scope: keep the current `drivers/virtio/virtio_mmio.zig` helper surface reviewable without claiming transport-backed queue setup, IRQ delivery, DMA, or probe/remove lifecycle parity
- product boundary:
  - `drivers/virtio/virtio_mmio.zig`
  - `drivers/virtio/virtio_mmio_verify.zig`
  - `zigux/tests/phase10_virtio_mmio.zig`
  - `zigux/tests/phase10_virtio_mmio_manifest.json`
  - `Documentation/zigux/phase10-virtio-mmio-survey.md`
  - `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md`
  - `Documentation/zigux/phase10-virtio-mmio-slice.md`
  - `zigux/tests/phase10_virtio_mmio_survey.zig`
  - `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig`
  - `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig`
  - `zigux/tests/phase10_build.zig`
  - `Documentation/zigux/phase10-closure-evidence.md`
  - `Documentation/zigux/freeze-map.md`

## Why this slice exists

The Phase 10 roadmap keeps `drivers/virtio/virtio_mmio.c` inside the VM-friendly lab-driver stage. In that stage, honest progress is bounded wrapper and validation work, not transport-backed lifecycle claims.

Current `master` already contains a real helper foothold in `drivers/virtio/virtio_mmio.zig`. The current helper packet covers transport identity readback, probe preflight gating, selected-queue readiness, interrupt-ack disposition review, staged config-write plan freshness, staged config-write planning, config-write apply observation, config-write disposition reporting, and feature-negotiation deltas that keep shared bits and mismatches explicit without claiming that feature negotiation executed against a live device.

This survey exists to make that current helper packet explicit and reviewable on its own terms while keeping the larger risky transport bridge parked.

## Survey findings
- `drivers/virtio/virtio_mmio.zig` is present on current `master` and exposes `TransportIdentitySummary`, `ProbePreflightSummary`, `SelectedQueueReadinessSummary`, `InterruptAckDispositionSummary`, `ConfigWritePlanFreshnessSummary`, `ConfigWritePlanSummary`, `ConfigWriteDispositionSummary`, and `FeatureNegotiationSummary` as bounded MMIO lab surfaces.
- `drivers/virtio/virtio_mmio_verify.zig` keeps the wrapper-facing transport-identity, queue-readiness, interrupt-ack-disposition, config-write-plan-freshness, and config-write-disposition proof explicit beside the helper-local packet.
- `VirtioMmioLab` stays in-memory and lab-oriented: it stages config bytes and feature words, tracks queue selection and queue readiness, and reports helper summaries without claiming a live hardware transport.
- the config-write plan freshness helper reports whether a staged plan is unavailable, fresh, or stale because its generation no longer matches the current config generation, which keeps disposition readiness explicit without widening into config application.
- the config-write disposition helper reports `relative_end_offset`, `absolute_end_offset`, `previous_value`, `planned_value`, `changed_byte_mask`, and `has_changes`, which makes a staged config-window change reviewable at byte granularity.
- the feature-negotiation helper now reports `negotiated_feature_word`, `device_only_feature_word`, `driver_only_feature_word`, and `feature_words_match`, which keeps the shared word and both mismatch directions explicit while remaining purely observational.
- the helper-local tests inside `drivers/virtio/virtio_mmio.zig` cover zero-valued known feature words, shared-versus-mismatched feature bits, interrupt-ack disposition accounting, stale-plan invalidation after a config-generation bump, stale-plan invalidation after config-byte restaging, explicit plan-freshness availability classes, legacy guest-page-size probe gating, and non-mutating config-write disposition reporting.
- `zigux/tests/phase10_virtio_mmio.zig` now gives the MMIO survey packet one dedicated MMIO lab replay for probe gating, queue readiness, interrupt-ack disposition, feature negotiation, config-write plan freshness, and config-write disposition below risky transport claims.
- `zigux/tests/phase10_virtio_mmio_manifest.json` keeps the helper-local MMIO lab gate, dedicated apply-observation replay, dedicated survey gate, and blocked risky-transport posture explicit beside the helper and verify replay.
- `Documentation/zigux/phase10-virtio-mmio-slice.md` remains the packet-local slice companion for the broader MMIO wrapper ladder and should stay aligned with this survey note, the config-write companion, the manifest, and the dedicated survey gate.
- `zigux/tests/phase10_virtio_mmio_apply_observation_replay.zig` now gives the MMIO lane one dedicated apply-observation replay that keeps changed-byte coverage, no-op planning, and stale-plan rejection explicit beside the helper-local MMIO lab replay without widening into transport-backed execution.
- `zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig` now gives that dedicated apply-observation replay a standalone build shard so the wrapper-local observation packet can be rerun without widening into the broader shared Phase 10 build graph.
- `zigux/tests/phase10_virtio_mmio_survey.zig` now gives the MMIO lane one dedicated survey replay that rereads this survey note together with the shared build gate and the standalone apply-observation replay shard instead of treating the dedicated survey surface as missing repo reality.
- `zigux/tests/phase10_build.zig` remains part of the shared Phase 10 review packet and now runs the helper-local MMIO tests through the shared `phase10-virtio-mmio-tests` route, the dedicated MMIO lab replay through the shared `phase10-virtio-mmio-lab-tests` route, the wrapper-facing MMIO verify replay through the shared `phase10-virtio-mmio-verify-tests` route, and the dedicated MMIO survey replay through the shared `phase10-virtio-mmio-survey-tests` route. The shared gate should still be read as helper-local MMIO coverage plus one direct lab replay, one wrapper-facing verify replay, and one survey replay rather than a broader transport-backed replay.
- `Documentation/zigux/phase10-virtio-mmio-config-write-disposition-companion.md` remains the packet-local companion for the config-write disposition rung and should stay aligned with this broader survey note.

## Freeze boundary
- `Documentation/zigux/freeze-map.md` remains the governing boundary note for this survey.
- `freeze_boundary_status` stays `aligned` and `freeze_status_change_claimed` stays `false`.
- `architecture_council_reopen_required` stays `true` and `architecture_council_reopen_attached` stays `false`.
- allowed evidence kinds stay limited to `driver_local_lab_slices`, `survey_manifests`, and `shared_validation_gates`.
- allowed roadmap destinations stay limited to `drivers/virtio/*.zig`, `zigux/kernel/`, and `zigux/helpers/`.
- forbidden transport claims remain `queue_setup_reset_paths`, `queue_reset_execution`, `irq_parity`, `dma_paths`, `probe_remove_lifecycle`, and `freeze_restore_lifecycle`.
- this survey stays inside `drivers/virtio/*.zig` and shared validation surfaces.
- this survey does not reopen `kernel/workqueue.c` or `kernel/trace/ring_buffer.c`, which remain study-only anchors.
- this survey also does not claim ownership of the freeze-in-C anchors `kernel/sched/core.c`, `mm/page_alloc.c`, `kernel/rcu/tree.c`, or `net/core/skbuff.c`.

## Non-goals
This survey does not claim:
- transport-backed queue setup or queue reset execution
- shared IRQ delivery parity
- DMA-facing behavior
- probe, remove, freeze, restore, or device-lifecycle closure
- an Architecture Council reopen or a freeze-map status change

## Gates
Current `master` keeps this MMIO lane reviewable through these bounded surfaces:
1. helper-local tests inside `drivers/virtio/virtio_mmio.zig`
2. the dedicated MMIO lab replay: `zig test zigux/tests/phase10_virtio_mmio.zig`
3. the dedicated apply-observation replay: `zig build test --build-file zigux/tests/build.phase10_virtio_mmio_apply_observation_replay.zig --summary all`
4. the dedicated survey replay: `zig test zigux/tests/phase10_virtio_mmio_survey.zig`
5. `zigux/tests/phase10_build.zig`, `make -C zigux phase10-test`, and `make -C zigux phase10` remain shared Phase 10 reminder routes, and the current build file now runs the shared `phase10-virtio-mmio-tests`, `phase10-virtio-mmio-lab-tests`, `phase10-virtio-mmio-verify-tests`, and `phase10-virtio-mmio-survey-tests` routes together so the helper-local MMIO tests, the dedicated MMIO lab replay, the wrapper-facing MMIO verify replay, and the dedicated MMIO survey replay stay visible in one VM-friendly lab validation packet, while the standalone apply-observation build shard keeps that narrower wrapper-local observation packet independently rerunnable.

These gates should be read as helper-local review evidence, direct lab-driver validation, and shared packet reminders only, not as proof of a transport-backed MMIO driver or a dedicated MMIO lifecycle replay.

## Next bounded step
Keep the broader Phase 10 MMIO lane parked unless fresh repo inspection finds one directly coupled follow-through. The next honest same-lane step is one additional checker-backed packet-local or shared reminder surface repair around the already-landed MMIO helper packet while lifecycle-and-IRQ transport work stays blocked.
