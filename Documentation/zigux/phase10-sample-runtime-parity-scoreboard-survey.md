# Phase 10 Sample and Runtime Parity Scoreboard Survey

This note records the bounded roadmap-facing sample and runtime predecessor evidence for the active Phase 10 virtio lab packet.

## Scope

This survey stays in the shared Phase 10 reminder lane only.
It does not reopen Phase 9 runtime behavior, Phase 10 driver helpers, risky transport, or any broader shared reminder file.

## Roadmap Alignment

The roadmap keeps the phases split on purpose:
- Phase 9 enters runtime kernels through tests and samples rather than production pressure.
- Phase 10 proves the virtio driver model on VM-friendly transports before harder hardware.

That means the honest Phase 10 scoreboard cannot treat missing runtime samples as the current blocker if the predecessor sample and runtime packet is already present on `master`.
The Phase 10 blocker has to stay where the roadmap puts it: risky transport, IRQ, DMA, and deeper lifecycle closure.

## Current Predecessor Evidence

Current shared reminder surfaces already describe a returned Phase 9 runtime packet on `master`.
That packet keeps these sample and runtime anchors explicit:
- `samples/zigux/runtime_trace_events.zig`
- `samples/zigux/runtime_trace_events_unregistered_gate.zig`
- `samples/zigux/runtime_trace_events_exit_rollback_guard.zig`
- `samples/zigux/runtime_trace_events_registration_reentry_gate.zig`
- `samples/zigux/runtime_trace_events_reinit_rollback_guard.zig`
- `samples/zigux/runtime_trace_events_reinit_reexit_guard.zig`
- `samples/zigux/runtime_bitmap.zig`
- `samples/zigux/runtime_bitmap_direct_init_contract.zig`
- `samples/zigux/runtime_bitmap_loader.zig`
- `samples/zigux/runtime_bitmap_top_bit_contract.zig`
- `samples/zigux/runtime_bitmap_cold_stage_guard.zig`
- `samples/zigux/runtime_kretprobe.zig`
- `samples/zigux/runtime_kretprobe_loader.zig`
- `samples/zigux/runtime_kretprobe_initialized_snapshot_guard.zig`
- `samples/zigux/runtime_kretprobe_registration_reentry_gate.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`
- `zigux/tests/phase9_build.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/runtime_bitmap_manifest.json`
- `zigux/tests/runtime_bitmap_survey.zig`
- `zigux/tests/runtime_bitmap_module.zig`
- `zigux/tests/runtime_bitmap_diff.zig`
- `zigux/tests/runtime_kretprobe_survey.zig`
- `zigux/tests/runtime_kretprobe_module.zig`
- `zigux/tests/runtime_first_loadable_parity_behavior.zig`

Those surfaces already satisfy the roadmap requirement that runtime entry happen through tests and samples.
They are predecessor evidence for Phase 10, not an unresolved absence inside the virtio lab packet itself.

## Scoreboard Reading

The honest current scoreboard for this boundary is:
- `phase9_runtime_samples=starter_landed`
- `phase9_runtime_loader_packet=partially_landed`
- `phase10_virtio_lab_packet=starter_landed`
- `phase10_sample_runtime_predecessor_evidence=present`
- `phase10_blocker=blocked_on_risky_transport`

## Remaining Gap

What is still missing is not sample-side or runtime-side existence.
What is still missing is one shared Phase 10 reminder surface that says the roadmap-backed predecessor packet is already present, so Phase 10 reminder wording does not drift into implying that runtime samples are still the gap.

## Next Bounded Step

If a future same-lane refresh is needed, align one shared Phase 10 reminder surface with this note so the predecessor evidence becomes enforced shared wording rather than standalone survey context.
