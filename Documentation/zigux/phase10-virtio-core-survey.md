# Phase 10 Virtio Core Survey

This document tracks the bounded Phase 10 governance lane around `drivers/virtio/virtio.c`.

## Status

- `PHASE10_STATUS=parked`
- `PHASE10_SLICE=virtio-core-survey`
- lane: `P10-L01`
- surveyed inspected `master` head: connector-visible current-`master` readback on `2026-05-19`; this lane did not recover an exact head SHA
- scope: compare the Phase 10 core lane's current repo-visible evidence against the roadmap's lab-driver target and the bootstrap ledger's tranche discipline, then keep this survey aligned with the narrower current packet without widening into ring, MMIO, input, or transport-facing lifecycle work
- product boundary:
  - `drivers/virtio/virtio.zig`
  - `Documentation/zigux/phase10-virtio-core-survey.md`

## Why this slice exists

The Phase 10 roadmap names `drivers/virtio/virtio.c` as the first virtio-core anchor and keeps the phase focused on VM-friendly lab-driver proof before riskier transport work.

Current `master` does still ship a bounded `drivers/virtio/virtio.zig` helper under the recommended `drivers/virtio/*.zig` destination. What it does not currently ship is the broader manifest-backed core governance packet that older survey wording described as already landed. The bootstrap ledger also stops earlier in the commit train and does not yet record a dedicated Phase 10 core tranche, so this survey needs to stay honest about the gap between roadmap intent and current repo-visible proof.

This lane therefore remains useful as a truthfulness surface rather than as proof that the full core packet has returned. The right job here is to keep the core survey aligned with current repo reality until a fresh core-local manifest, checker, slice note, and replay set materially land together.

## Survey findings

- `drivers/virtio/virtio.c` remains the roadmap's Phase 10 core anchor, and current `master` does directly expose `drivers/virtio/virtio.zig`
- current `master` does not expose the broader core packet that earlier survey prose treated as already returned: connector-visible reads and public tree inspection both fail to materialize `Documentation/zigux/phase10-virtio-core-slice.md`, `scripts/zigux/check-phase10-core-packet.py`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, and `zigux/tests/phase10_virtio_driver_id.zig`
- because those companions are absent, the current core lane cannot honestly claim the earlier manifest-backed `lab-only driver validation` packet or the earlier helper-parity replay ladder as current repo-visible evidence
- the roadmap still keeps the core lane in scope as part of Phase 10's virtio proof, but the present repo-visible proof is narrower than the broader closure note and adjacent ring, input, and MMIO packets: it is currently a starter helper presence signal, not a complete core survey packet
- the bootstrap ledger still matters here as tranche discipline: it establishes how bounded Zigux phases are supposed to become reviewable, but it does not yet record a dedicated Phase 10 core commit train entry that would close this lane by itself
- the remaining honest gap is therefore not risky transport closure and not missing ring, MMIO, or input evidence owned by other lanes; it is the absence of core-local governance surfaces that would make this lane machine-checkable again without overstating today's repo reality

## Recorded gaps

Current `master` keeps these same-lane gaps explicit:

- missing core slice note: `Documentation/zigux/phase10-virtio-core-slice.md`
- missing core checker: `scripts/zigux/check-phase10-core-packet.py`
- missing core manifest: `zigux/tests/phase10_virtio_core_manifest.json`
- missing core survey gate: `zigux/tests/phase10_virtio_core_survey.zig`
- missing core helper replays: `zigux/tests/phase10_virtio_core.zig`, `zigux/tests/phase10_virtio_core_reset_queue.zig`, `zigux/tests/phase10_virtio_core_interrupt_compound_ack.zig`, and `zigux/tests/phase10_virtio_driver_id.zig`
- missing core helper companions: `drivers/virtio/virtio_driver_id.zig` and `drivers/virtio/virtio_verify.zig`
- still-blocked transport-facing bridge: dual implementations for risky transport paths plus probe, full remove, reset, IRQ, DMA, and broader transport-backed lifecycle work remain outside the currently visible core packet

This keeps the lane concrete without pretending that roadmap-backed lab validation has already returned for the core path. The current evidence is a narrow helper foothold plus an explicit list of the core packet companions that still need to rematerialize before stronger closure claims become honest.

## Non-goals

This survey slice does not claim:

- probe, full remove, or transport-backed reset lifecycle parity
- real virtqueue wrappers from `virtio_ring.c`
- real MMIO register-window or IRQ behavior from `virtio_mmio.c`
- broader transport-backed registration or teardown work
- that the bootstrap ledger already closes a Phase 10 core tranche

## Gates

The honest current lane checks are repository-readback checks rather than runnable core validators:

1. confirm the roadmap anchor still names Phase 10 as virtio lab-driver work
- `agent_files/ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md`

2. confirm the bootstrap ledger still stops short of a dedicated Phase 10 core tranche
- `agent_files/BOOTSTRAP_COMMIT_LEDGER.md`

3. confirm current repo-visible core evidence remains narrow
- direct readback of `drivers/virtio/virtio.zig`
- direct readback failure or public-tree absence for `Documentation/zigux/phase10-virtio-core-slice.md`, `scripts/zigux/check-phase10-core-packet.py`, `zigux/tests/phase10_virtio_core_manifest.json`, `zigux/tests/phase10_virtio_core_survey.zig`, `drivers/virtio/virtio_driver_id.zig`, `drivers/virtio/virtio_verify.zig`, and the missing core replay files listed above

No dedicated Zig toolchain check is currently available in this lane because the core survey gate and core replay files are not present on current `master`.

## Next bounded step

Leave the Phase 10 virtio-core governance lane parked again unless a fresh reread shows one of two things:

- one missing core-local governance companion rematerializes and needs this survey updated to match current repo reality, or
- a bounded core-lane follow-through is ready to land, starting with exactly one missing governance surface such as `zigux/tests/phase10_virtio_core_manifest.json`, `scripts/zigux/check-phase10-core-packet.py`, or `Documentation/zigux/phase10-virtio-core-slice.md`

Any future helper or transport-facing work should stay in the owning adjacent lane unless the repo actually materializes the missing core packet locally and makes this lane reviewable again.