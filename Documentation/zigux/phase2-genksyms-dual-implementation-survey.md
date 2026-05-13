# Phase 2 genksyms dual-implementation survey

Lane: `P2-L07`

This note records the current `master` readback for the roadmap-backed `scripts/zigux/genksyms.zig` packet so Phase 2 review stays grounded in the live wrapper-first bridge instead of reviving either the older missing-tool story or an unshipped full direct-replay story.

## Roadmap target

- Phase 2 keeps `scripts/genksyms/genksyms.c` inside the parser-heavy tooling tranche.
- The roadmap requires selected dual implementations together with a wrapper-first path for parser-heavy tooling, and the recommended Zigux destination is `scripts/zigux/genksyms.zig`.
- The bootstrap ledger records both the earlier generic `feat(scripts/zigux): add genksyms dual implementation` milestone and the later narrower `feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane` follow-through, so the live packet should be judged against that bounded wrapper-first posture instead of against a missing full parser port.

## Current master readback

- `scripts/zigux/genksyms.zig` is present on `master` and already ships a bounded CLI bridge around `parseArgs()`, `renderGenksymsBridge()`, and `main()`.
- `zigux/tests/fixtures/genksyms_bridge/manifest.json` is present, marks the tool `closed`, records `mode: "wrapper-first bridge"`, and names the current 22-case external bridge packet.
- `scripts/zigux/check-genksyms-bridge.py` keeps that manifest-backed packet aligned with the current helper-local anchors, workflow markers, closure markers, and tests-root reminder markers.
- `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-lane-sequencing.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` already describe the same bounded genksyms packet as fixture-backed bridge evidence rather than as a shipped direct `zig test scripts/zigux/genksyms.zig` replay.
- The helper-local bridge packet already carries a stronger version-side-effect contract than the committed external fixture packet: `scripts/zigux/genksyms.zig` includes the anchor `genksyms bridge keeps version as a side effect while parsing later options`, while the external `version_expected.json` packet still proves only the one-shot version-print path.

## Survey result

- Current `master` does not have a remaining roadmap gap at the level of genksyms wrapper scaffolding. The bridge entrypoint, committed fixture packet, manifest, checker, and shared reminder surfaces are already present.
- The honest remaining dual-implementation gap is narrower: the external bridge packet still under-proves at least one behavior that the helper-local packet already treats as part of the contract, namely version output that survives later argument parsing. That is a better next genksyms-local follow-through than inventing a wider parser or CRC reopen.
- Future reopening in this file family should therefore stay inside bridge-local proof work such as fixture, expected-output, or tightly coupled helper-anchor alignment, not shared Phase 2 closure churn.

## Next bounded step

1. Update the committed `version` bridge case so `zigux/tests/fixtures/genksyms_bridge/cases.json` and `zigux/tests/fixtures/genksyms_bridge/version_expected.json` prove the same version-side-effect path that `scripts/zigux/genksyms.zig` already tests locally.
2. When a writable checkout with Zig is available, re-run `python3 scripts/zigux/check-genksyms-bridge.py --self-test`, `python3 scripts/zigux/check-genksyms-bridge.py`, and `zig test scripts/zigux/genksyms.zig` so the bounded external packet and the helper-local packet stay aligned.

## Boundary

Stay inside the `genksyms` lane only. Do not reopen fixdep, kconfig, shared Phase 2 reminder surfaces, or broader parser-port ambitions unless a new genksyms-local mismatch proves one of those surfaces directly wrong.
