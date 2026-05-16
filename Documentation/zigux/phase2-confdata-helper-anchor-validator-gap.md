# Phase 2 Confdata Helper-Anchor Validator Gap

## Status

- lane: `toolchain-kbuild`
- phase: `Phase 2`
- scope: shared toolchain, build-check, and kbuild-facing validation wiring
- current `master` still ships the bounded confdata helper-anchor checker `scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py`
- current `master` also still documents that checker inside the live shared Phase 2 scripts-root inventory in `scripts/zigux/README.md`
- the shared validator gate `scripts/zigux/validate-phase2.py` currently inventories the shared tests README, kconfig README, kconfig self-test alignment, fixdep gate, fixdep diff, cross compile, cross self-test alignment, tool-manifest packet, and toolchain pin-scope checks, but it does not yet carry the confdata helper-anchor checker in its command packet or required-file inventory

## Why This Note Exists

The roadmap and bootstrap ledger keep Phase 2 focused on toolchain pinning, build checks, and bounded kbuild integration rather than free-floating wrapper growth.

Current `master` already carries the kconfig bridge Zig files and the committed `zigux/tests/fixtures/kconfig_bridge/` packet, so the highest-value same-lane gap is no longer missing scaffold restoration. The remaining shared-validation gap is narrower: the confdata helper-anchor checker is present and documented, but it is not yet part of the shared Phase 2 validator inventory that the repo uses to keep the Phase 2 packet closed and reviewable.

That mismatch matters because it lets one live Phase 2 checker remain outside the main shared validator route even though the scripts-root inventory already treats it as part of the active Phase 2 packet.

## Observed Current-Master Evidence

- `scripts/zigux/README.md` lists `check-phase2-confdata-helper-anchor-alignment.py` among the live shared Phase 2 helpers on current `master`
- `Documentation/zigux/phase2-closure.md` keeps the bounded Phase 2 packet framed around shared validator, closure, cross-target, kconfig, fixdep, genksyms, and toolchain-pin routes
- `scripts/zigux/validate-phase2.py` currently does not include the confdata helper-anchor checker in the shared command inventory or required-file inventory
- the live tree still carries `scripts/zigux/kconfig/conf_bridge.zig`, `scripts/zigux/kconfig/confdata_bridge.zig`, and the committed `zigux/tests/fixtures/kconfig_bridge/` packet, so this note is about validator wiring drift, not a claim that the scaffold itself is absent

## Next Bounded Same-Lane Step

Wire `scripts/zigux/check-phase2-confdata-helper-anchor-alignment.py` into the shared Phase 2 validator packet by updating:

- `scripts/zigux/validate-phase2.py`
- `Documentation/zigux/phase2-closure.md`
- any shared route inventory that should explicitly track the added self-test and gate markers after the validator wiring lands

That follow-up should stay bounded to validator inventory and Phase 2 route documentation, then replay the shared Phase 2 validators on the resulting head.
