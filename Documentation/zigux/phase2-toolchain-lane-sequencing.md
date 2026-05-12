# Phase 2 Toolchain Lane Sequencing

This note keeps the active Phase 2 toolchain packet split into bounded lanes so shared reminder work does not collapse Makefile, fixdep, genksyms, and kconfig follow-up back into one noisy queue.

## Scope

Use this note when a Phase 2 change touches the shared toolchain packet recorded in `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `zigux/Makefile`.

Keep the current lane split explicit:
- shared sequencing lane `P2-Y10` owns only shared Phase 2 toolchain reminder and anti-overlap work
- shared backlog truthfulness lane `P2-Y12` owns turning current cross-family backlog evidence into one bounded next-safe-step correction when a shared reminder surface overclaims unshipped direct replays or wider checker coverage on current `master`
- Makefile toolchain lane `P2-X09` owns the repo-local `.zig-toolchain` fallback and the six Linux-style Phase 2 routes in `zigux/Makefile`
- fixdep lane `P2-Y02` owns fixdep-specific checker and closure wording around `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/`
- genksyms lane `P2-L10` owns the bounded genksyms bridge fixture and replay packet around `scripts/zigux/check-genksyms-bridge.py`, `scripts/zigux/genksyms.zig`, and `zigux/tests/fixtures/genksyms_bridge/`
- kconfig bridge behavior lane `P2-X05` owns `scripts/zigux/kconfig/conf_bridge.zig` behavior follow-up together with the committed `zigux/tests/fixtures/kconfig_bridge/cases.json` request packet
- kconfig bridge checker lane `P2-L16` owns checker and manifest truthfulness around `scripts/zigux/check-kconfig-bridge.py` plus `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- confdata survey lane `P2-L19` stays parked unless a new `scripts/zigux/kconfig/confdata_bridge.zig` or `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` drift appears on current `master`

The roadmap-backed toolchain tranche from the Phase 2 plan and the bootstrap ledger is already represented on current `master` by the shared route inventory, tool-manifest packet, cross-target packet, closure note, and bootstrap note above. Future Phase 2 toolchain work should therefore prefer owner-map and review-surface truthfulness over reopening already-split tool-local replay steps from the wrong lane.

## Owner Split

Keep the current owner map explicit:
- shared sequencing truthfulness under `P2-Y10` owns only cross-family reminder drift in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_cross_targets.json`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest-packets.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-kconfig-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, and `zigux/Makefile`
- shared backlog truthfulness under `P2-Y12` owns only the next-safe-step correction when the shared packet names wider direct replay coverage than the live Makefile and closure note actually ship; current evidence points specifically at `zigux/tests/README.md` plus `scripts/zigux/check-phase2-tests-readme-alignment.py`, not at tool-local behavior inside `fixdep.zig`, `genksyms.zig`, `conf_bridge.zig`, `confdata_bridge.zig`, or `mk_elfconfig.zig`
- `P2-X09` owns direct Makefile route or `.zig-toolchain` fallback drift only; it does not own fixdep, genksyms, conf bridge, or confdata replay expansion
- `P2-Y02` owns fixdep-local wording or replay drift only; shared sequencing lanes should not reopen the fixdep gate packet unless a multi-family route surface stops naming it correctly
- `P2-L10` owns genksyms-local fixture, expected-output, and replay drift only; shared sequencing lanes should not treat the genksyms bridge packet as the default next shared toolchain step
- `P2-X05` and `P2-L16` keep `conf_bridge` behavior follow-up separate from checker-or-manifest truthfulness so nearby runs do not mix request-shape work with review-surface repair in one lane
- `P2-L19` keeps `confdata_bridge` parked behind bridge-local evidence only; do not use the presence of the shared Phase 2 toolchain packet as a reason to reopen confdata survey work by default

## Current Backlog Evidence

Current `master` already keeps the shared Phase 2 toolchain packet bounded around the six Linux-style routes in `zigux/Makefile`, the closure wording in `Documentation/zigux/phase2-closure.md`, and the shared manifest plus checker packet. The remaining shared backlog evidence is narrower:
- `zigux/tests/README.md` still names direct `zig test` replays for `scripts/zigux/genksyms.zig`, `scripts/zigux/genksyms_crc.zig`, `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, and `scripts/zigux/mk_elfconfig.zig`
- current `zigux/Makefile` and `Documentation/zigux/phase2-closure.md` keep only `zig test scripts/zigux/fixdep.zig` explicit as the shipped direct Phase 2 Zig replay, while the broader genksyms, artifact-tool, and kconfig packet stays checker-backed and fixture-backed on current `master`
- the next safe shared correction is therefore a tests-root truthfulness repair only: realign `zigux/tests/README.md` and `scripts/zigux/check-phase2-tests-readme-alignment.py` with the already-landed Makefile and closure packet without reopening tool-local behavior, fixture expansion, or bridge-code work

## Shared Packet Surfaces

When a real cross-family Phase 2 toolchain change lands, keep these shared surfaces aligned:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`
- `zigux/tests/fixtures/phase2_tool_manifest.json`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `scripts/zigux/check-phase2-tool-manifest-packets.py`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-kconfig-readme-alignment.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `zigux/Makefile`
- `make -C zigux phase2-toolchain`
- `make -C zigux phase2-validate`
- `make -C zigux phase2-tools`
- `make -C zigux phase2-kconfig`
- `make -C zigux phase2-cross`
- `make -C zigux phase2`

## Sequencing Rules

Use this note to keep the bounded work order honest:
1. Prefer one Phase 2 lane at a time instead of batching Makefile, fixdep, genksyms, and kconfig follow-up into one mixed change.
2. Reopen `P2-Y10` only for shared route-inventory, reminder-surface, tool-manifest, cross-target, or validator alignment drift that affects more than one Phase 2 tool family at once.
3. Reopen `P2-Y12` only when current `master` evidence shows a shared backlog or review surface pointing at the wrong next step; keep that lane limited to the smallest owner-map, README, or checker truthfulness repair that turns the backlog into one bounded follow-through.
4. Keep `P2-X09` parked unless the repo-local `.zig-toolchain` fallback or the six Linux-style route inventory drifts in `zigux/Makefile` or the shared notes that restate it.
5. When a writable checkout with Zig is available, run direct tool-local replays inside the dedicated fixdep, genksyms, or kconfig lanes instead of treating that wider validation opportunity as a shared toolchain reopen cue.
6. If only one tool family drifts on current `master`, stay inside that tool family's lane even when the shared reminder packet also mentions it.
7. Prefer the smallest same-family reviewability, manifest, checker, or route-truthfulness repair before changing any tool behavior.
8. Do not use this note to revive already-closed `confdata` scaffolding or older `conf_bridge` survey language when current `master` already carries the newer shared packet.

## Non-Goals

This note does not widen Phase 2 into:
- direct parser or bridge-behavior implementation work across multiple tools in one lane
- speculative new Phase 2 checker scripts or replay routes beyond the shipped shared packet above
- reopening parked confdata survey work without a fresh bridge-local mismatch
- treating a shared reminder-surface edit as proof that a tool-local replay or checker follow-up already landed
