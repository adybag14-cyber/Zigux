# Phase 2 Kconfig Bridge Gap Survey

## Purpose

This note records the current repo-backed gap between the Phase 2 roadmap target for the `scripts/kconfig/conf.c` / `confdata.c` bridge lane and the scaffolding that currently ships in Zigux.

Lane scope for this survey:
- `scripts/zigux/kconfig/conf_bridge.zig`
- `scripts/zigux/kconfig/confdata_bridge.zig`
- `scripts/zigux/check-kconfig-bridge.py`
- `zigux/tests/fixtures/kconfig_bridge/`

Roadmap anchor:
- Phase 2 requires a wrapper-first path for parser-heavy tooling, selected dual implementations, deterministic artifact checks, and Linux-style replayable validation around the future `conf` and `confdata` bridge surfaces.

Ledger anchor:
- bootstrap ledger item 20 already landed the bounded kconfig bridge scaffolding packet, so the useful question is no longer whether the lane exists, but which same-family gaps still keep it from being a stronger roadmap-backed bridge.

## Current Shipped Scaffold

The current repo already carries meaningful bridge scaffolding instead of placeholder churn.

Directly readable shipped surfaces:
- `scripts/zigux/kconfig/conf_bridge.zig` covers the current 16-mode `conf` request-plan surface, explicit `allconfig` handling, `randconfig` tunables, `syncconfig` env shaping, and helper-local tests.
- `scripts/zigux/kconfig/confdata_bridge.zig` covers bounded `.config` parsing plus `auto.conf` and autoconf-header export shaping with helper-local tests.
- `scripts/zigux/check-kconfig-bridge.py` replays the fixture packet, manifest packet, determinism checks, and self-test packet.
- `zigux/tests/fixtures/kconfig_bridge/cases.json`, `conf_manifest.json`, and `confdata_manifest.json` keep the shipped replay packet explicit.

This means the lane has already cleared the roadmap’s anti-churn bar for bridge scaffolding.

## Current Repo-Backed Gaps

### 1. Upstream source-anchor gap

The roadmap’s primary Linux targets are `scripts/kconfig/conf.c` and `scripts/kconfig/confdata.c`, but current authenticated repo reads still do not expose those C sources on `master`.

That leaves the current bridge packet in an indirect state:
- the Zig bridge helpers are replayable
- the fixture packet is explicit
- same-tree parity against current in-repo C sources is still unavailable

For this lane, that is the most important remaining structural gap.

### 2. Reminder-surface drift risk around the live allconfig packet

The live fixture packet now treats these modes as explicit `allconfig` override cases:
- `allnoconfig`
- `allyesconfig`
- `allmodconfig`
- `alldefconfig`
- `randconfig`

The shipped manifest packet also records an empty `allconfig_sentinel_packet`, which matches that fully explicit override roster.

That makes the next same-family risk a reminder-surface truthfulness problem rather than a bridge-runtime implementation gap: every alignment guard that describes the `allconfig` roster must match the live packet exactly or it becomes weaker than the bridge scaffold it is supposed to protect.

### 3. Differential replay remains fixture-backed, not source-backed

`check-kconfig-bridge.py` currently proves determinism and manifest alignment against the shipped fixture packet. That is useful and real.

What it still cannot do in current repo reality is compare the Zig bridge packet directly against in-repo `conf.c` / `confdata.c` behavior, because those C sources are not presently available as current-tree anchors.

## What Is Not The Gap

This survey does not treat the following as missing work:
- the `conf_bridge.zig` mode surface itself
- the `confdata_bridge.zig` parser/export helper itself
- the existing kconfig fixture roster
- the existing deterministic replay checker

Those pieces already exist and should be preserved as the stable base for the next bounded step.

## Highest-Value Next Bounded Step

The next same-lane step should stay narrow:
- refresh any kconfig reminder or alignment checker that still describes the pre-current `allconfig` packet, especially where the live case roster and manifest now treat `allyesconfig` as an explicit override case and leave the sentinel packet empty

After that narrow truthfulness pass lands, the next stronger roadmap-backed step would be:
- add a direct provenance or differential anchor for `conf.c` / `confdata.c` once those C sources are readable in-tree again on current `master`

## Lane Decision

For current repo reality, the highest-value reading is:
- item 20 from the ledger is substantively present
- the lane’s remaining work is now provenance and reminder-surface hardening
- the smallest honest follow-through is to fix same-family guard drift before widening Phase 2 kconfig claims
