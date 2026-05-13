# Phase 2 Toolchain Lane Sequencing

This note keeps the active Phase 2 toolchain packet split into bounded lanes so shared reminder work does not collapse Makefile, fixdep, genksyms, and kconfig follow-up back into one noisy queue.

## Scope

Use this note when a Phase 2 change touches the shared toolchain packet recorded in `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-lane-sequencing.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_cross_targets.json`, and `zigux/Makefile`.

Keep the current lane split explicit:
- shared sequencing lane `P2-Y10` owns only shared Phase 2 toolchain reminder and anti-overlap work
- shared backlog truthfulness lane `P2-Y12` owns turning current cross-family backlog evidence into one bounded next-safe-step correction when a shared reminder surface overclaims unshipped direct replays or wider checker coverage on current `master`
- Makefile toolchain lane `P2-X09` owns the repo-local `.zig-toolchain` fallback and the six Linux-style Phase 2 routes in `zigux/Makefile`
- fixdep lane `P2-Y02` owns fixdep-specific checker and closure wording around `scripts/zigux/check-phase2-fixdep-gate.py`, `scripts/zigux/check-fixdep-diff.py`, `scripts/zigux/fixdep.zig`, and `zigux/tests/fixtures/fixdep/`
- genksyms survey lane `P2-L07` owns reminder-surface truthfulness for the wrapper-first bridge packet recorded in `Documentation/zigux/phase2-genksyms-dual-implementation-survey.md`
- genksyms fixture lane `P2-L10` owns bounded genksyms bridge fixture and expected-output drift around `scripts/zigux/genksyms.zig`, `scripts/zigux/check-genksyms-bridge.py`, and `zigux/tests/fixtures/genksyms_bridge/`
- genksyms gate lane `P2-L11` owns workflow-backed replay or validator wiring for the already-landed genksyms bridge packet
- kconfig bridge behavior lane `P2-X05` owns `scripts/zigux/kconfig/conf_bridge.zig` behavior follow-up together with the committed `zigux/tests/fixtures/kconfig_bridge/cases.json` request packet
- kconfig bridge checker parity lane `P2-L18` owns the current `conf_bridge` checker-and-manifest helper-anchor parity around `scripts/zigux/check-kconfig-bridge.py` plus `zigux/tests/fixtures/kconfig_bridge/conf_manifest.json`
- confdata survey lane `P2-L19` stays parked as the scaffold-closed survey note under `Documentation/zigux/phase2-confdata-bridge-survey.md`
- confdata checker lane `P2-Y07` owns current checker-underflow repair around `scripts/zigux/check-kconfig-bridge.py` and `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- confdata bridge truthfulness lane `P2-L24` owns malformed-quote and helper-anchor follow-through inside `scripts/zigux/kconfig/confdata_bridge.zig` plus directly coupled checker or manifest wording when substantive bridge-local changes land

The roadmap-backed toolchain tranche from the Phase 2 plan and the bootstrap ledger is already represented on current `master` by the shared route inventory, tool-manifest packet, cross-target packet, closure note, bootstrap note, and lane-sequencing note above. Future Phase 2 toolchain work should therefore prefer owner-map and review-surface truthfulness over reopening already-split tool-local replay steps from the wrong lane.

## Owner Split

Keep the current owner map explicit:
- shared sequencing truthfulness under `P2-Y10` owns only cross-family reminder drift in `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`, `Documentation/zigux/phase2-closure.md`, `Documentation/zigux/phase2-toolchain-lane-sequencing.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/tests/fixtures/phase2_tool_manifest.json`, `zigux/tests/fixtures/phase2_cross_targets.json`, `scripts/zigux/check-phase2-toolchain-pin-scope.py`, `scripts/zigux/check-phase2-tool-manifest-packets.py`, `scripts/zigux/check-phase2-tests-readme-alignment.py`, `scripts/zigux/check-phase2-kconfig-readme-alignment.py`, `scripts/zigux/check-phase2-cross.py`, `scripts/zigux/check-phase2-cross-selftest-alignment.py`, `scripts/zigux/check-phase2-kconfig-selftest-alignment.py`, `scripts/zigux/validate-phase2.py`, `scripts/zigux/validate-phase2-closure.py`, and `zigux/Makefile`
- shared backlog truthfulness under `P2-Y12` owns only the next-safe-step correction when the shared packet names wider direct replay coverage than the live Makefile and closure note actually ship; current evidence still points specifically at `zigux/tests/README.md` plus `scripts/zigux/check-phase2-tests-readme-alignment.py`, not at tool-local behavior inside `fixdep.zig`, `genksyms.zig`, `conf_bridge.zig`, `confdata_bridge.zig`, or `mk_elfconfig.zig`
- `P2-X09` owns direct Makefile route or `.zig-toolchain` fallback drift only; it does not own fixdep, genksyms, conf bridge, or confdata replay expansion
- `P2-Y02` owns fixdep-local wording or replay drift only; shared sequencing lanes should not reopen the fixdep gate packet unless a multi-family route surface stops naming it correctly
- `P2-L07` owns genksyms survey-note or reminder-surface truthfulness, `P2-L10` owns genksyms fixture or expected-output drift, and `P2-L11` owns genksyms workflow-backed replay or validator wiring; shared sequencing lanes should not collapse those three follow-through shapes back into one generic genksyms reopen
- `P2-X05` owns `conf_bridge` behavior or expected-output drift only, while `P2-L18` owns the current checker-and-manifest parity packet; shared sequencing lanes should not steer nearby runs back toward older broad conf-bridge wording when the live gap is already narrowed to the checker-backed parity lane
- `P2-L19` stays parked as survey evidence only; `P2-Y07` owns the current confdata checker undercount and `P2-L24` owns bridge-local malformed-quote or helper-anchor truthfulness. Shared sequencing lanes should not treat the parked survey label as the active confdata maintenance lane.

## Current Backlog Evidence

Current `master` already keeps the shared Phase 2 toolchain packet bounded around the six Linux-style routes in `zigux/Makefile`, the closure wording in `Documentation/zigux/phase2-closure.md`, the shared manifest plus checker packet, and this dedicated owner-map note. The remaining shared anti-overlap risk is narrower:
- this sequencing note was still speaking in the older genksyms and kconfig lane split even though current same-family follow-through now lives across the separate `P2-L07` or `P2-L10` or `P2-L11` genksyms packet, the `P2-X05` versus `P2-L18` conf-bridge split, and the `P2-L19` versus `P2-Y07` or `P2-L24` confdata split
- current `master` already carries the separate genksyms dual-implementation survey, conf bridge survey, confdata survey, fixdep next-step note, and the newer bridge-checker or gate follow-through records, so the highest-value shared correction is owner-map truthfulness rather than reopening tests-root backlog wording or tool behavior from this lane
- the next safe shared correction is therefore a sequencing-note refresh only: realign this note with the currently visible survey, fixture, checker, and gate splits without touching Makefile routes, fixtures, bridge behavior, or shared validator logic

## Shared Packet Surfaces

When a real cross-family Phase 2 toolchain change lands, keep these shared surfaces aligned:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `Documentation/zigux/phase2-toolchain-lane-sequencing.md`
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
5. Keep the genksyms split explicit: use `P2-L07` for survey or reminder-surface undercounts, `P2-L10` for fixture or expected-output drift, and `P2-L11` for workflow-backed replay or validator wiring.
6. Keep `P2-X05` for `conf_bridge` behavior-to-expected-output drift and `P2-L18` for the current checker-and-manifest parity packet; do not reopen the shared lane for older broad conf-bridge wording when current repo evidence already narrowed the gap to one of those tool-local steps.
7. Keep `P2-L19` parked as survey-only evidence; use `P2-Y07` for confdata checker undercount and `P2-L24` for bridge-local malformed-quote or helper-anchor truthfulness if confdata reopens.
8. When a writable checkout with Zig is available, run direct tool-local replays inside the dedicated fixdep, genksyms, or kconfig lanes instead of treating that wider validation opportunity as a shared toolchain reopen cue.
9. If only one tool family drifts on current `master`, stay inside that tool family's lane even when the shared reminder packet also mentions it.
10. Prefer the smallest same-family reviewability, manifest, checker, or route-truthfulness repair before changing any tool behavior.
11. Do not use this note to revive already-closed `confdata` scaffolding, older `conf_bridge` survey language, or a generic one-lane genksyms packet when current `master` already carries the newer split packet.

## Non-Goals

This note does not widen Phase 2 into:
- direct parser or bridge-behavior implementation work across multiple tools in one lane
- speculative new Phase 2 checker scripts or replay routes beyond the shipped shared packet above
- reopening parked confdata survey work without a fresh bridge-local mismatch
- treating a shared reminder-surface edit as proof that a tool-local replay or checker follow-up already landed
