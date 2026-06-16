# Phase 7 Argv Split Repo Reality Note

Lane key: `P7-L02`

Current directly readable sibling anchors on `master`:
- `Documentation/zigux/phase7-rbtree-direct-anchor-note.md`
- `Documentation/zigux/phase7-string-helpers-slice.md`
- `lib/string_helpers.zig`
- `zigux/tests/phase7_string_helpers.zig`
- `zigux/tests/phase7_rbtree_survey.zig`

Repo-reality warning for the missing dedicated `argv_split` packet on current `master`:
- `Documentation/zigux/phase7-argv-split-slice.md`
- `lib/argv_split.zig`
- `zigux/tests/phase7_argv_split.zig`
- `zigux/tests/phase7_argv_split_survey.zig`
- `zigux/tests/phase7_argv_split_manifest.json`
- `zigux/tests/fixtures/phase7_argv_split_vectors.zig`
- `scripts\zigux/check_phase7_argv_split_packet.zig`
- `scripts\zigux/validate_phase7.zig`
- `zigux/tests/phase7_build.zig`
- `zigux/Makefile`

Keep the current Phase 7 reminder surface narrow and truthful:
- `string_helpers` stays the only directly readable Phase 7 helper implementation packet on current `master`
- `cmdline` stays parked under the current Phase 1 helper packet
- `rbtree` stays reviewable through the direct anchor note and survey only
- do not present the missing dedicated `argv_split` packet or the broader shared Phase 7 control routes as directly readable current-`master` evidence again until a fresh same-lane reread or republish materializes them
