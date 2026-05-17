# Phase 1 String Roadmap-Ledger Gap

This note records the bounded `tools/lib/string.zig` gap between the Phase 1 plan and the currently readable `master` tree.

## Roadmap And Ledger Expectation

- `ROADMAP_PHASE1_TARGET=tools/lib/string.zig`
- `LEDGER_COMMIT6_TARGET=tools/lib/string.zig`
- the Phase 1 roadmap still lists `tools/lib/string.zig` as one of the four host-side helper ports that prove low-risk in-tree Zig delivery
- the bootstrap commit ledger still carries `tools/lib/string.zig` inside commit 6, `feat(tools/lib): start phase-1 helper ports`

## Current Repo Reality

- current public-tree readback of `tools/lib` shows `cmdline.zig` as the only directly readable `.zig` helper in that directory in this environment
- authenticated contents reads for `tools/lib/string.zig` on current `master` return missing
- current Phase 1 reminder surfaces still name `tools/lib/string.zig` as a direct-anchor helper in `Documentation/zigux/phase1-host-helper-lane-sequencing.md` and `zigux/tests/fixtures/phase1_helper_manifest.json`

## Current Lane Decision

- treat `tools/lib/string.zig` as a roadmap-and-ledger target that is not currently materialized on readable `master`
- keep this lane on repo-truthfulness survey work only until the helper file itself or a narrower current-master replacement surface is directly readable again
- do not present the current string manifest anchors as direct helper-file proof while `tools/lib/string.zig` remains unreadable on current `master`

## Next Bounded Step

- align the current Phase 1 reminder packet one surface at a time so it distinguishes the roadmap-ledger string target from direct current-master helper evidence
