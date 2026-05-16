# Phase 11 Codegen and Manifest Tooling Gap Survey

This note records the current deterministic tooling posture for the shared Phase 11 simple-driver packet and names the smallest roadmap-aligned manifest or codegen gap that still remains.

Observed current-master baseline for this survey: `adbd16e93df72422c468738f2d06573e9330ea7a`.

## Roadmap Contract

Phase 11 exists to move from lab-only slices toward bounded simple production drivers while keeping review surfaces honest.

The roadmap still requires:
- direct-port or dual-implementation driver templates
- a hardware validation matrix
- teardown and failure-mode parity

For the shared tooling packet, that means reminder surfaces and replay routes must stay deterministic without reviving retired aggregate validators or pretending a stale manifest inventory still drives the current packet.

## Current Shared Deterministic Tooling Packet

Current shared Phase 11 tooling evidence on `master` centers on the surviving contract-and-build-backed packet:
- `scripts/zigux/check-phase11-shared-replay-contract.py`
- `scripts/zigux/check-phase11-shared-summary-surfaces.py`
- `zigux/Makefile` shared routes `phase11-contract` and `phase11`
- `zigux/tests/phase11_build.zig`
- the shared notes that describe those routes and the lane split

Packet-local deterministic evidence still exists beside that shared packet:
- watchdog and HVC lanes keep their own survey notes, validation matrices, manifests, and focused checkers where those surfaces still ship on current `master`
- the public header-boundary packet keeps its own checker-local deterministic surface instead of pretending to be a fifth driver lane

## Live Gap Versus The Roadmap

The shared packet now has deterministic reminder-surface checks and a shared build replay, but it no longer has one shared machine-readable manifest or generated summary surface that describes the surviving Phase 11 packet truthfully.

Current repo reality is narrower than the older Phase 11 tranche:
- there is no shared `scripts/zigux/validate-phase11.py`
- there is no shared `zigux/tests/fixtures/phase11_build_inventory.json`
- there is no shared `make -C zigux phase11-validate` route

That leaves one real shared tooling gap:
- there is no current aggregate manifest or generated survey surface that tells contributors which shared routes, packet-local manifests, validation matrices, and dedicated survey replays are intentionally still part of the live Phase 11 packet

Without that smaller shared surface, reminder notes can drift back toward the retired inventory-driven story or overclaim packet coverage even while the surviving contract and build routes stay green.

## Boundaries For Any Follow-Through

Keep the next deterministic tooling step narrow:
- do not revive the removed aggregate validator stack just to recreate old naming
- do not collapse packet-local watchdog, HVC, or header-boundary manifests into one fake green dashboard
- do not widen this tooling gap into driver behavior, runtime ownership, or speculative codegen beyond the current shared packet
- do not claim broader hardware validation closure than the packet-local matrices already prove

## Recommended Next Bounded Step

The next high-value follow-through should be one small shared contract manifest or generated summary that is derived from the surviving packet only:
- enumerate the shared routes `phase11-contract`, `phase11`, and `zigux/tests/phase11_build.zig`
- record which packet-local manifests or dedicated survey routes the shared notes are still allowed to name
- validate that surface with a fail-closed checker or self-test before wiring it into broader CI

That would close the current shared manifest or codegen truthfulness gap without reviving the retired validator story or crossing into neighboring driver-local lanes.
