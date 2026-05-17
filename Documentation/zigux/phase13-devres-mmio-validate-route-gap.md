# Phase 13 devres MMIO Validate Route Gap

## Status
- `PHASE13_STATUS=active`
- `PHASE13_LANE=P13-L02`
- `PHASE13_SCOPE=iomap-mmio-safety-validate-route-gap`
- `PHASE13_READBACK=master-readback-2026-05-17`

## Packet Reading
- The Phase 13 roadmap still keeps `lib/devres.c` inside bounded shared-helper delivery, so the current devres MMIO packet should stay reviewable through the shipped helper-local checker surfaces rather than through stale validator-first names.
- `scripts/zigux/README.md` now treats `scripts/zigux/check-phase13-devres-mmio-packet.py` as shipped Phase 13 evidence and explicitly frames the older `scripts/zigux/validate-phase13-release.py` and `scripts/zigux/check-phase13-devres-packet-alignment.py` names as repo-reality gaps on current `master`.
- `zigux/Makefile` still routes `phase13-validate` through `scripts/zigux/validate-phase13-release.py` and `scripts/zigux/check-phase13-devres-packet-alignment.py`, while it does not call `scripts/zigux/check-phase13-devres-mmio-packet.py`.
- That leaves the current gap route-local rather than helper-local: the shipped MMIO checker exists, but the shared validation entrypoint still points at older devres validator names that the scripts-root packet now describes as absent repo-reality surfaces.

## Next Bounded Step
Refresh `zigux/Makefile` so `phase13-validate` points at the shipped devres MMIO packet guard, then reread `.github/workflows/zigux-bootstrap.yml` and the broader Phase 13 reminder notes together to keep the shared route truthful without widening into helper behavior, DMA ownership, or release-summary prose.
