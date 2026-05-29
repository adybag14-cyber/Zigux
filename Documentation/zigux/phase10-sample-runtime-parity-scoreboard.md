# Phase 10 Sample and Runtime Parity Scoreboard

This note records the current notes-only `P10-L18` scoreboard follow-up for the shared Phase 10 virtio lab bundle. It should move only when substantive parity evidence lands in the repo first.

## Current Scoreboard

- `PHASE10_SCOREBOARD_STATUS=active_shared_packet`
- `PHASE10_SCOREBOARD_LANE=P10-L18`
- `PHASE10_SCOREBOARD_SCOPE=sample-runtime-parity-notes-only`
- `PHASE10_SCOREBOARD_ROADMAP_ANCHORS=virtqueue-wrappers,mmio-wrappers,lab-only-driver-validation`
- `PHASE10_SCOREBOARD_RISKY_TRANSPORT=blocked_on_risky_transport`
- `PHASE10_SCOREBOARD_SHARED_VALIDATOR=scripts/zigux/validate-phase10.py`
- `PHASE10_SCOREBOARD_SHARED_VALIDATOR_CHECK_COUNT=11`
- `PHASE10_SCOREBOARD_SELF_TEST_CASE_COUNT=35`
- `PHASE10_SCOREBOARD_LOCAL_GUARD=scripts/zigux/check-phase10-sample-runtime-scoreboard.py`
- `PHASE10_SCOREBOARD_LOCAL_GUARD_SELF_TEST_CASE_COUNT=6`

## Substantive Parity Progress Recorded

The shared Phase 10 validator now includes `scripts/zigux/check-phase10-ring-manifest-destinations.py` in both the required-path set and live `CHECKS` route. That checker keeps the manifest-backed ring destinations explicit for the current virtqueue-wrapper packet, including callback-enable and reset-readiness wrapper destinations.

This is roadmap-aligned progress because it strengthens existing virtqueue wrapper evidence without claiming transport-backed queue discovery, IRQ delivery, DMA behavior, probe/remove lifecycle behavior, or risky dual-implementation parity.

## Evidence Surfaces

- `scripts/zigux/validate-phase10.py`
- `scripts/zigux/check-phase10-ring-manifest-destinations.py`
- `scripts/zigux/check-phase10-ring-packet.py`
- `scripts/zigux/check-phase10-sample-runtime-scoreboard.py`
- `zigux/tests/phase10_virtio_ring_manifest.json`
- `Documentation/zigux/phase10-virtio-ring-survey.md`
- `Documentation/zigux/phase10-closure-evidence.md`
- `zigux-alpha/PHASE10_CLOSURE_LEDGER.md`

## Parity Gate

`scripts/zigux/check-phase10-sample-runtime-scoreboard.py` keeps this notes-only scoreboard tied to the validator-backed evidence it summarizes. The guard fails closed if this note drops the shared Phase 10 validator route, the ring manifest destination checker, the closure evidence surface, or the explicit blocked risky-transport boundary.

The guard also checks `scripts/zigux/validate-phase10.py` for the `phase10-ring-manifest-destinations` live check so the scoreboard cannot keep advertising validator-backed evidence after the shared validator route has moved.

## Validation Commands

The parity scoreboard update is grounded in the validator route added on current `master`:

- `python3 scripts/zigux/validate-phase10.py --self-test`
- `python3 scripts/zigux/check-phase10-ring-manifest-destinations.py --self-test`
- `python3 scripts/zigux/validate-phase10.py`
- `python3 scripts/zigux/check-phase10-sample-runtime-scoreboard.py --self-test`
- `python3 scripts/zigux/check-phase10-sample-runtime-scoreboard.py`

`P10-L18` remains notes-only. Further implementation work should stay in the machine-readable owner lanes unless another substantive Phase 10 parity change lands and leaves the shared notes behind.
