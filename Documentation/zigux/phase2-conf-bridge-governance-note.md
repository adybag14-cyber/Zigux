# Phase 2 Conf Bridge Governance Note

Scope: `scripts/zigux/kconfig/conf_bridge.zig` and its direct config and expected-output packet only.

Latest verified `master` readback for this bridge packet was recorded on 2026-05-08. That verified state already kept the following `conf_bridge` surfaces aligned:

- `scripts/zigux/kconfig/conf_bridge.zig`
- `zigux/tests/fixtures/kconfig_bridge/cases.json`
- `zigux/tests/fixtures/kconfig_bridge/helpnewconfig_expected.json`
- `scripts/zigux/check-kconfig-bridge.py`

That verified packet already included:

- `helpnewconfig` in the live `conf_bridge` mode surface
- a `helpnewconfig` fixture row in `cases.json`
- a committed `helpnewconfig_expected.json` expected-output artifact
- `helpnewconfig` in the checker's ordered required conf-case mode list

The Phase 2 roadmap and bootstrap ledger already treat `conf_bridge.zig`, its direct fixture matrix, and its checker as one bounded bridge packet. This note closes the remaining governance gap where the retired `helpnewconfig` reopen path existed only in lane memory instead of the repository itself.

Governance boundary for future same-family runs:

- do not reopen the older `helpnewconfig` expected-output gap unless a fresh `master` reread shows the mode, fixture row, expected artifact, or checker requirement has disappeared or drifted
- treat the current `helpnewconfig` packet as landed evidence, not as an open Phase 2 todo
- if this bridge lane reopens, prefer the smallest same-family follow-up only; the last explicitly unretired candidate on 2026-05-08 was the bounded mode-argument contract check around `defconfig` and `savedefconfig`

Reopen triggers limited to this bridge packet:

- `helpnewconfig` disappears from `scripts/zigux/kconfig/conf_bridge.zig`
- `zigux/tests/fixtures/kconfig_bridge/cases.json` drops the `helpnewconfig` row
- `zigux/tests/fixtures/kconfig_bridge/helpnewconfig_expected.json` disappears or stops matching the bridge packet
- `scripts/zigux/check-kconfig-bridge.py` stops requiring `helpnewconfig` in the ordered conf-case mode set

Until one of those triggers appears on a fresh repo reread, this lane should stay parked and avoid duplicating already-landed `helpnewconfig` work.
