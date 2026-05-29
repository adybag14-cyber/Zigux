# Phase 10 Stale Wrapper Cleanup Survey

This survey records the current Phase 10 churn-control boundary for the virtio lab-driver lane. It is intentionally evidence-local: it does not add driver wrappers, transport behavior, or new validation routes.

## Current Repo Reality

- `scripts/zigux/validate-phase10.py` is the shared Phase 10 gate and still requires the Phase 10 closure packet, core, ring, input, MMIO, harness, tests-root, closure-manifest, bootstrap-route, and freeze-boundary checkers.
- `Documentation/zigux/phase10-closure-evidence.md` still treats `scripts/zigux/README.md`, `scripts/zigux/check-phase10-core-packet.py`, `scripts/zigux/check-phase10-closure-manifest-counts.py`, `scripts/zigux/validate-phase10.py`, `scripts/zigux/validate-phase10-closure.py`, and `zigux/Makefile` as current shared reminder evidence.
- `zigux/Makefile` still exposes the shared `phase10-validate`, `phase10-test`, and `phase10` route family, so Phase 10 is active repo reality rather than a historical wrapper-only packet.
- The current scripts-root reminder surface is a churn hotspot: recent readback emphasized other phase packets while older continuity still expected the Phase 10 shared checker roster there.

## Cleanup Boundary

- Keep Phase 10 cleanup bounded to truthfulness repairs around shipped checker and route surfaces.
- Do not generate new wrapper files only to make the tree larger.
- Do not promote risky transport, IRQ delivery, DMA behavior, remove lifecycle closure, or real input-device registration as complete from this lane.
- Treat `P10-L22` as the live owner for the bounded virtio-input packet; this `P10-L13` lane should only touch shared churn-cleanup evidence when it contradicts current repo reality.
- Treat Phase 3 wrapper-generator cleanup as adjacent evidence only unless a current Phase 10 surface directly depends on it.

## Hotspot Checklist

A future stale-wrapper cleanup pass should reread these files together before editing:

- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase10.py`
- `scripts/zigux/validate-phase10-closure.py`
- `scripts/zigux/check-phase10-core-packet.py`
- `scripts/zigux/check-phase10-closure-manifest-counts.py`
- `Documentation/zigux/phase10-closure-evidence.md`
- `Documentation/zigux/phase10-virtio-driver-lane-sequencing.md`
- `zigux/tests/phase10_closure_manifest.json`
- `zigux/Makefile`

## Next Bounded Step

If this survey needs follow-through, the safest next step is checker-local: teach an existing Phase 10 shared checker to fail when the scripts-root reminder loses the shipped Phase 10 checker roster. That should be done only after rereading current `master`, because broad whole-file writes to `scripts/zigux/README.md` have previously caused neighboring reminder-section churn.
