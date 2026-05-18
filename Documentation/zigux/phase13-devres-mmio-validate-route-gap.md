# Phase 13 devres MMIO Validate Route Gap

## Status
- `PHASE13_STATUS=active`
- `PHASE13_LANE=P13-L02`
- `PHASE13_SCOPE=iomap-mmio-safety-route-gap`
- `PHASE13_READBACK=master-readback-2026-05-18`

## Packet Reading
- The Phase 13 roadmap still keeps `lib/devres.c` inside bounded shared-helper delivery, so the current devres MMIO packet should stay reviewable through helper-first evidence instead of stale validator-first or stale Makefile-route names.
- `Documentation/zigux/phase13-devres-slice.md` and `zigux/tests/phase13_devres_dma_coherent.zig` now keep the surviving devres packet narrow on current `master`: one direct replay surface remains, while the broader survey, helper, manifest, and older direct replay packet stay explicit repo-reality gaps.
- `scripts/zigux/README.md` now records the same current route picture from the scripts root: `zigux/Makefile` is present on current `master`, but it still does not expose `make -C zigux phase13-validate` or blocked convenience route `make -C zigux phase13`, and current `master` still does not materialize `scripts/zigux/validate-phase13-release.py` or `scripts/zigux/check-phase13-devres-packet-alignment.py`.
- That makes the current gap route-local and narrower than the older draft `P13-L02` story: current `master` does not ship a shared Phase 13 rerun hook for the surviving devres MMIO evidence at all, so the truthful next move is to keep that absence explicit until a fresh shared route packet lands.

## Next Bounded Step
Refresh one shared Phase 13 rerun packet only after rereading `scripts/zigux/README.md`, `zigux/Makefile`, `.github/workflows/zigux-bootstrap.yml`, `Documentation/zigux/phase13-devres-slice.md`, and `zigux/tests/phase13_devres_dma_coherent.zig` together so any returned route names the current surviving devres packet instead of the older missing validator-first surfaces.
