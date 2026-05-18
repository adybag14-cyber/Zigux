# Phase 1 String Roadmap-Ledger Gap

This note records the bounded `tools/lib/string.zig` follow-through between the Phase 1 plan and the currently readable `master` tree.

## Roadmap And Ledger Expectation

- `ROADMAP_PHASE1_TARGET=tools/lib/string.zig`
- `LEDGER_COMMIT6_TARGET=tools/lib/string.zig`
- the Phase 1 roadmap still lists `tools/lib/string.zig` as one of the four host-side helper ports that prove low-risk in-tree Zig delivery
- the bootstrap commit ledger still carries `tools/lib/string.zig` inside commit 6, `feat(tools/lib): start phase-1 helper ports`

## Current Repo Reality

- current live reads now recover `tools/lib/string.zig` on `master`
- the directly readable helper file still carries the Phase 1 string direct-anchor packet, including the helper-local sysfs review anchors named by `sysfsStreq()`, `sysfs_streq()`, `sysfsMatchString()`, and `sysfs_match_string()`
- current Phase 1 reminder surfaces still name `tools/lib/string.zig` as a direct-anchor helper in `Documentation/zigux/phase1-host-helper-lane-sequencing.md` and `zigux/tests/fixtures/phase1_helper_manifest.json`

## Current Lane Decision

- treat `tools/lib/string.zig` as both a roadmap-and-ledger target and direct current-`master` helper evidence again
- keep this lane on one string-only direct-anchor follow-through at a time instead of falling back to broader roadmap-only survey wording
- use the live helper file plus the existing manifest-backed string review packet as the trustworthy current Phase 1 string evidence

## Next Bounded Step

- reread the current Phase 1 string reminder packet one surface at a time and repair only the next string-only note or checker that still understates `tools/lib/string.zig` as direct current-`master` helper evidence
