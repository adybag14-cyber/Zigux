# Phase 2 `confdata_bridge` Scaffolding Survey

This note keeps the current `scripts/zigux/kconfig/confdata_bridge.zig` lane honest against the Phase 2 roadmap and the bootstrap ledger.

## Roadmap Target

Phase 2 in `ZAR_TO_ZIGUX_PRODUCT_ROADMAP (1).md` calls for wrapper-first Kbuild enablement around `scripts/kconfig/conf.c` and `scripts/kconfig/confdata.c`.

Commit-train item 20 in `BOOTSTRAP_COMMIT_LEDGER.md` narrows that to bounded bridge scaffolding:

- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/check-kconfig-bridge.py`
- `zigux/tests/fixtures/kconfig_bridge/*`

The lane is therefore not a full `confdata.c` port. It is a reviewable bridge scaffold that can be replayed, diffed, and extended without claiming parser-complete parity.

## Current Repo State

Current `master` already ships a bounded `confdata_bridge` scaffold with three concrete pieces of product-facing evidence:

- `scripts/zigux/kconfig/confdata_bridge.zig` parses `.config`-style input into a deterministic JSON summary of `CONFIG_*` entries, counts, and value kinds.
- `scripts/zigux/check-kconfig-bridge.py` compiles the bridge, replays the fixture packet, and checks repeatable JSON output.
- `zigux/tests/fixtures/kconfig_bridge/cases.json` plus `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json` define the shipped bounded fixture roster for escaped strings, CRLF handling, duplicate assignment resolution, malformed quoted values, explicit empty assignments, and ownership-failure coverage.

That is real scaffolding progress because it gives Zigux a replayable, fixture-backed bridge around one narrow `confdata` surface instead of leaving the Phase 2 claim as prose only.

## Gap Versus Roadmap

The remaining gap is not “missing file” work. The remaining gap is scope clarity.

What the repo already proves:

- a deterministic config-summary parser scaffold exists
- the scaffold has fixture-backed replay coverage
- the scaffold is wired into the Phase 2 kconfig checker and closure packet

What the repo does not yet prove:

- a direct wrapper contract for the wider `scripts/kconfig/confdata.c` action surface beyond summary parsing
- a call-level bridge that models upstream `confdata` writeback or mode-specific side effects
- a narrower statement in docs that this lane is still bounded scaffolding rather than a deeper `confdata.c` parity claim

That difference matters because the roadmap asked for wrapper-first tooling enablement, not an unqualified declaration that `confdata.c` has been broadly replaced.

## Honest Lane Reading

Inside the current lane, `confdata_bridge.zig` should be read as:

- a bounded scaffold for `.config` state extraction and replay
- suitable evidence for Phase 2 bridge scaffolding
- not yet sufficient evidence for broader `confdata.c` behavioral parity

This keeps the Phase 2 story aligned with the roadmap’s wrapper-first discipline and avoids turning a useful parser scaffold into a larger claim than the repo currently supports.

## Next Bounded Step

The next same-lane step should stay small:

Add one explicit contract surface that names the supported `confdata` bridge boundary beyond raw parsing, such as a request/summary packet for the exact `confdata` operation family Zigux intends to replay first, and bind that packet to its own fixture-backed checker.

Until that lands, the current bridge should stay documented as bounded scaffolding rather than promoted as a wider `confdata.c` port.

## Evidence Packet

- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/check-kconfig-bridge.py`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `zigux/tests/fixtures/kconfig_bridge/confdata_manifest.json`
- `Documentation/zigux/phase2-closure.md`
