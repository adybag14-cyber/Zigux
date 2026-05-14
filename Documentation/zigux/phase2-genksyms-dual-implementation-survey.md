# Phase 2 genksyms dual-implementation survey

Lane: `P2-L07`

This note records the current `master` readback for the roadmap-backed `scripts/zigux/genksyms.zig` packet so Phase 2 review stays grounded in the live wrapper-first bridge instead of reviving either the older missing-tool story or an unshipped full direct-replay story.

## Roadmap target

- Phase 2 keeps `scripts/genksyms/genksyms.c` inside the parser-heavy tooling tranche.
- The roadmap requires selected dual implementations together with a wrapper-first path for parser-heavy tooling, and the recommended Zigux destination is `scripts/zigux/genksyms.zig`.
- The bootstrap ledger names the bounded wrapper lane directly through `feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane`, while the separate `genksyms_crc` artifact-tool milestone stays parked in the shared artifact-tools packet, so the live packet should be judged against that bounded wrapper-first posture instead of against a missing full parser port.

## Current master readback

- `scripts/zigux/genksyms.zig` is present on `master` and already ships a bounded CLI bridge around `parseArgs()`, `renderGenksymsBridge()`, and `main()`.
- `zigux/tests/fixtures/genksyms_bridge/manifest.json` is present, marks the tool `closed`, records `mode: "wrapper-first bridge"`, and names the current 23-case external bridge packet.
- `scripts/zigux/check-genksyms-bridge.py` now matches that 23-case packet, including the committed `missing_dump_types_argument` process case and the external `version` bridge case that proves the same `-V` side effect before later argument parsing that `scripts/zigux/genksyms.zig` already anchors locally.
- `scripts/zigux/validate-phase2.py`, `.github/workflows/zigux-bootstrap.yml`, and `Documentation/zigux/phase2-closure.md` keep `zig test scripts/zigux/genksyms.zig` explicit as the bounded direct replay, while `scripts/zigux/README.md` and `zigux/tests/README.md` intentionally keep the broader reminder packet centered on the committed bridge fixtures and checker surfaces instead of duplicating that direct replay command in every shared note.
- `Documentation/zigux/phase2-closure.md` keeps the same live `23-case` genksyms bridge packet explicit, so the earlier closure-note undercount that motivated the first follow-through is no longer present on current `master`.
- The external `version_expected.json` packet now proves the same version-side-effect behavior as the helper-local anchor `genksyms bridge keeps version as a side effect while parsing later options`, so the helper-local and external bridge packets are aligned on that behavior.

## Survey result

- Current `master` does not have a remaining roadmap gap at the level of genksyms wrapper scaffolding, version-side-effect proof, closure-note count, or bounded direct-replay ownership. The bridge entrypoint, committed 23-case fixture packet, manifest, checker, helper-local anchors, direct `zig test scripts/zigux/genksyms.zig` route, and checked reminder surfaces are all present.
- The next safe same-lane step is now parked-by-default maintenance only: reopen this lane only if a fresh reread finds new drift between the helper-local bridge, the committed fixture packet, the dedicated checker, and the directly coupled reminder surfaces.
- If a future reopen is wording-only, prefer one directly coupled genksyms note or closure correction before touching bridge code, fixtures, or broader Phase 2 reminder surfaces.

## Next bounded step

1. Leave this lane parked unless a fresh reread finds genksyms-local drift in `scripts/zigux/genksyms.zig`, `scripts/zigux/check-genksyms-bridge.py`, `zigux/tests/fixtures/genksyms_bridge/manifest.json`, `Documentation/zigux/phase2-closure.md`, or this survey note.
2. If the lane reopens on wording alone, land one directly coupled genksyms note or closure correction before reopening fixtures, checker logic, or shared Phase 2 reminder surfaces.

## Boundary

Stay inside the `genksyms` lane only. Do not reopen fixdep, kconfig, shared Phase 2 reminder surfaces, or broader parser-port ambitions unless a new genksyms-local mismatch proves one of those surfaces directly wrong.
