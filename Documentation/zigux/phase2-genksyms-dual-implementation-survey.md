# Phase 2 genksyms dual-implementation survey

Lane: `P2-L07`

This note records the current `master` readback for the roadmap-backed `scripts/zigux/genksyms.zig` packet so Phase 2 review stays grounded in the live wrapper-first bridge instead of reviving either the older missing-tool story or an unshipped full direct-replay story.

## Roadmap target

- Phase 2 keeps `scripts/genksyms/genksyms.c` inside the parser-heavy tooling tranche.
- The roadmap requires selected dual implementations together with a wrapper-first path for parser-heavy tooling, and the recommended Zigux destination is `scripts/zigux/genksyms.zig`.
- The bootstrap ledger records both the earlier generic `feat(scripts/zigux): add genksyms dual implementation` milestone and the later narrower `feat(scripts/zigux): add bounded Phase 2 genksyms wrapper lane` follow-through, so the live packet should be judged against that bounded wrapper-first posture instead of against a missing full parser port.

## Current master readback

- `scripts/zigux/genksyms.zig` is present on `master` and already ships a bounded CLI bridge around `parseArgs()`, `renderGenksymsBridge()`, and `main()`.
- `zigux/tests/fixtures/genksyms_bridge/manifest.json` is present, marks the tool `closed`, records `mode: "wrapper-first bridge"`, and names the current 23-case external bridge packet.
- `scripts/zigux/check-genksyms-bridge.py` now matches that 23-case packet, including the committed `missing_dump_types_argument` process case and the external `version` bridge case that proves the same `-V` side effect before later argument parsing that `scripts/zigux/genksyms.zig` already anchors locally.
- `Documentation/zigux/phase2-toolchain-lane-sequencing.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` continue to describe the same bounded genksyms packet as fixture-backed bridge evidence rather than as a shipped direct `zig test scripts/zigux/genksyms.zig` replay.
- The external `version_expected.json` packet now proves the same version-side-effect behavior as the helper-local anchor `genksyms bridge keeps version as a side effect while parsing later options`, so the helper-local and external bridge packets are aligned on that behavior.

## Survey result

- Current `master` does not have a remaining roadmap gap at the level of genksyms wrapper scaffolding or version-side-effect proof. The bridge entrypoint, committed 23-case fixture packet, manifest, checker, and helper-local anchors are all present.
- The honest remaining follow-through is narrower and governance-shaped: refresh any coupled reminder surface that still undercounts the genksyms bridge packet or still describes the older pre-proof packet, then rerun the bounded validation routes from a writable checkout with Zig.
- Future reopening in this file family should therefore stay inside bridge-local proof, checker, manifest, or tightly coupled reminder-surface alignment work, not shared Phase 2 closure churn or revived parser/CRC ambitions.

## Next bounded step

1. Refresh the directly coupled Phase 2 reminder surface that still undercounts the genksyms bridge packet as `22-case`, then keep the dedicated checker wording aligned with that closure evidence.
2. When a writable checkout with Zig is available, re-run `python3 scripts/zigux/check-genksyms-bridge.py --self-test`, `python3 scripts/zigux/check-genksyms-bridge.py`, and `zig test scripts/zigux/genksyms.zig` so the bounded external packet and the helper-local packet stay aligned.

## Boundary

Stay inside the `genksyms` lane only. Do not reopen fixdep, kconfig, shared Phase 2 reminder surfaces, or broader parser-port ambitions unless a new genksyms-local mismatch proves one of those surfaces directly wrong.
