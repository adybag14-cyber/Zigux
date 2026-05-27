# Phase 10 Freeze-Boundary Gap Survey

This note records the bounded freeze-boundary survey for the active Phase 10 virtio lab packet.

## Scope

Phase 10 stays inside the roadmap-backed virtio lab surface:
- `drivers/virtio/*.zig`
- bounded helper or boundary follow-through under `zigux/kernel/`
- bounded helper or boundary follow-through under `zigux/helpers/`

This survey exists so the shared Phase 10 closure packet can say exactly what is in scope and what remains blocked by the freeze map.

## Roadmap Alignment

The roadmap keeps Phase 10 in wrapper-first, lab-only driver validation.
That means the current Phase 10 packet may keep queue-local helper slices, survey manifests, and shared validation gates explicit, but it must not imply that risky transport, IRQ, DMA, or deeper lifecycle ownership has landed.

The active Phase 10 closure packet therefore stays aligned only when it keeps:
- `Documentation/zigux/freeze-map.md` explicit as the governing freeze source
- `zigux/tests/phase10_closure_manifest.json` explicit as the manifest-backed closure ledger for the virtio lab packet
- `scripts/zigux/check-phase10-shared-freeze-boundary.py` explicit as the fail-closed review gate for freeze-boundary drift
- the returned ring, input, and MMIO survey notes explicit as bounded Phase 10 evidence rather than transport-ready claims

## Current Exact Evidence

Direct current-`master` readback now shows the freeze boundary through the shared Phase 10 packet itself rather than through reminder prose alone:
- `zigux/tests/phase10_closure_manifest.json` records `freeze_map = Documentation/zigux/freeze-map.md`, `freeze_boundary_status = aligned`, `freeze_status_change_claimed = false`, `risky_transport_posture = blocked_on_risky_transport`, `architecture_council_reopen_required = true`, and `architecture_council_reopen_attached = false`
- that same manifest keeps `study_only_anchors = kernel/workqueue.c, kernel/trace/ring_buffer.c`, `freeze_in_c_anchors = kernel/sched/core.c, mm/page_alloc.c, kernel/rcu/tree.c, net/core/skbuff.c`, and `phase14_study_only_boundary.status = separate_phase14_lane`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md` keeps the shared reminder lane on `Documentation/zigux/phase10-freeze-boundary-gap-survey.md` and `scripts/zigux/check-phase10-shared-freeze-boundary.py`, while the queue-local ring packet stays on lane `P10-L10` and the adjacent freeze-boundary owner stays on `P10-L11`
- `zigux/tests/phase10_virtio_ring_manifest.json` keeps the ring-side freeze boundary explicit through `freeze_boundary_owner_lane = P10-L11`, `freeze_boundary_status = aligned`, `freeze_status_change_claimed = false`, and the still-blocked gap `phase10-ring-lab-driver-bridge`
- current ring-side evidence remains bounded to queue-local and wrapper-facing surfaces such as `drivers/virtio/virtio_ring_registration_summary.zig`, `drivers/virtio/virtio_ring_used_buffer_poll.zig`, `drivers/virtio/virtio_ring_publish_readiness.zig`, `zigux/tests/phase10_virtio_ring_reset_readiness.zig`, and `zigux/tests/phase10_virtio_ring_survey.zig`; none of those paths claim queue setup or reset execution, IRQ parity, DMA, or lifecycle closure
- the shared enforcement path stays replayable through `python3 scripts/zigux/check-phase10-shared-freeze-boundary.py`, `python3 scripts/zigux/validate-phase10-closure.py`, `make -C zigux phase10-validate`, `make -C zigux phase10-test`, and `make -C zigux phase10` as listed in `zigux/tests/phase10_closure_manifest.json`

## Freeze-Boundary Inventory

Freeze-in-C anchors that remain outside Phase 10 delivery:
- `kernel/sched/core.c`
- `mm/page_alloc.c`
- `kernel/rcu/tree.c`
- `net/core/skbuff.c`

Study-only anchors that remain outside Phase 10 delivery and stay parked in the separate Phase 14 family:
- `kernel/workqueue.c`
- `kernel/trace/ring_buffer.c`

Phase 10 may summarize those anchors only as boundary context.
It must not present them as active virtio closure evidence, bridge-readiness proof, or status-change candidates.

## Current Gap

The returned Phase 10 closure packet already records general freeze-map alignment, but without a dedicated survey note the shared closure packet can drift into shorthand wording that hides the roadmap boundary between:
- queue-local `virtio_ring` reviewability
- helper-local `virtio_mmio` reviewability
- blocked risky transport follow-through
- separate Phase 14 study-only ownership for `kernel/workqueue.c` and `kernel/trace/ring_buffer.c`

This note closes that reminder gap by making the Phase 10 freeze boundary itself reviewable.

## Allowed Evidence

Current Phase 10 evidence may include:
- driver-local lab slices
- survey manifests
- shared validation gates
- bounded replay witnesses for queue shape, notification planning, registration preflight, teardown preflight, status-drain, config-write observation, and related wrapper-facing review paths

Current Phase 10 evidence must not be used to claim:
- queue setup or reset execution parity
- IRQ parity
- DMA paths
- input registration lifecycle closure
- probe or remove lifecycle closure
- freeze or restore lifecycle closure
- Architecture Council reopen approval
- any freeze-map status change for Phase 14 study-only or freeze-in-C anchors

## Next Bounded Step

Keep this survey aligned with `zigux/tests/phase10_closure_manifest.json` and the shared freeze-boundary checker so future Phase 10 reminder refreshes fail closed if the virtio lab packet starts implying deep-core or study-only delivery progress.
