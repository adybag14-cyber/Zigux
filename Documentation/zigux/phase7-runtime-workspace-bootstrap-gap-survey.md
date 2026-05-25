# Phase 7 Runtime Workspace Bootstrap Gap Survey

This note keeps the Phase 7 shared-control workspace bootstrap glue reviewable against the roadmap without promoting the broader wrapper routes into current proof.

## Scope

- `PHASE7_STATUS=shared_control_workspace_bootstrap_gap_survey`
- `PHASE7_LANE_KEY=P7-L01`
- survey focus: roadmap-backed runtime leaf-library anchors versus current workspace/bootstrap glue on `master`

## Roadmap-backed Current State

- the Phase 7 roadmap anchors remain `lib/string_helpers.c`, `lib/cmdline.c`, `lib/argv_split.c`, and `lib/rbtree.c`
- current Zigux product paths now carry those anchors through `lib/string_helpers.zig`, `lib/cmdline.zig`, `lib/argv_split.zig`, and `lib/rbtree.zig`
- `zigux/tests/phase7_build.zig` wires all four returned helpers into the shared Phase 7 build graph
- `scripts/zigux/validate-phase7.py` plus `make -C zigux phase7-validate` keep one returned shared validation foothold explicit on current `master`

## Current Workspace Bootstrap Glue

- `.github/workflows/zigux-bootstrap.yml` self-tests `scripts/zigux/check-phase7-shared-control-gap.py` and `scripts/zigux/check-phase7-make-wrapper-selftest-alignment.py`
- the readable `zigux/Makefile` still exposes only `phase7-validate` for the shared Phase 7 packet
- `zigux/tests/phase7_build.zig` remains readable non-owner build evidence rather than a returned shared workspace route by itself, and current readback now shows that shard carrying helper-local survey, sample-boundary, and `string_helpers` format-boundary replays inside the shared build graph without turning those helper-local routes into returned shared-control wrappers

## Integration Gaps Versus Roadmap

- current `master` still does not materialize `phase7-test` or `phase7` in `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml` still omits direct `make -C zigux phase7-validate`, `make -C zigux phase7-test`, and `zig build test --build-file zigux/tests/phase7_build.zig --summary all` steps
- the roadmap-backed helper anchors are present, and the readable build shard now exposes extra helper-local survey and boundary replay evidence, but the shared workspace bootstrap glue still remains a narrow validation foothold rather than a returned end-to-end Phase 7 workspace route
- treat that gap as shared-control reminder debt, not as missing helper-local proof for `string_helpers`, `cmdline`, `argv_split`, or `rbtree`

## Next Bounded Step

- if a future shared-control lane widens bootstrap glue, reread `.github/workflows/zigux-bootstrap.yml`, `zigux/Makefile`, `zigux/tests/phase7_build.zig`, and `scripts/zigux/validate-phase7.py` together before promoting any broader Phase 7 route as returned current-`master` evidence
