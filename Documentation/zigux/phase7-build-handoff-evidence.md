# Phase 7 Build Handoff Evidence

This note records the exact current `master` handoff from the Linux-style Phase 7
make routes into the shared Zig build graph and the helper-local package wiring.

## Status

- `PHASE7_STATUS=route_present_review_only`
- `PHASE7_SLICE=build-handoff-evidence`
- `PHASE7_LANE_KEY=P7-L15`
- `PHASE7_ADJACENT_SHARED_CONTROL_LANE=P7-Y05`

This note is intentionally narrower than the broader shared control-surface
packet on `P7-Y05`: it records the exact handoff evidence for the current build
route without reopening helper-local slice claims or treating route presence as
proof that the full four-helper bundle is green on current `master`.

## Roadmap Fit

Phase 7 in the roadmap is the first in-kernel leaf-helper tranche:

- `lib/string_helpers.zig`
- `lib/cmdline.zig`
- `lib/argv_split.zig`
- `lib/rbtree.zig`

The current build handoff stays inside that roadmap-backed scope. The shared
Phase 7 make route does not jump forward into Phase 8 tooling or Phase 9 runtime
module work; it still points at the dedicated Phase 7 helper bundle.

## Exact Handoff Chain

Fresh repo-first inspection shows this exact route chain on current `master`:

1. `zigux/Makefile` exposes the shared Phase 7 packet through:
`phase7-validate`, `phase7-string-helpers-survey`,
`phase7-string-helpers-sample-boundary`, `phase7-cmdline-survey`,
`phase7-argv-split-survey`, `phase7-rbtree-survey`, `phase7-test`, and
`phase7`.
2. `phase7-validate` reruns the validator-backed review route before any shared
   build replay:
`python3 scripts/zigux/validate-phase7.py --self-test`,
`python3 scripts/zigux/validate-phase7.py`,
`python3 scripts/zigux/check-phase7-build-wiring.py --self-test`, and
`python3 scripts/zigux/check-phase7-build-wiring.py`.
3. `phase7-test` hands off directly into the shared Zig build graph through:
`zig build test --build-file zigux/tests/phase7_build.zig --summary all`.
4. `phase7` stays a wrapper over the same bounded packet:
`phase7: phase7-validate phase7-test`.

That is the current handoff behavior: the Linux-style wrapper first reruns the
shared validator packet, then hands execution into the dedicated `phase7_build`
entrypoint instead of a helper-local ad hoc command.

## Package Wiring Evidence

`zigux/tests/phase7_build.zig` currently wires the shared helper bundle in four
direct helper-to-test pairs:

- `../../lib/string_helpers.zig` -> `phase7_string_helpers.zig`
- `../../lib/cmdline.zig` -> `phase7_cmdline.zig`
- `../../lib/argv_split.zig` -> `phase7_argv_split.zig`
- `../../lib/rbtree.zig` -> `phase7_rbtree.zig`

The same build file keeps the helper-local import aliases explicit:

- `string_helpers_root_module.addImport("string_helpers", string_helpers_module);`
- `cmdline_root_module.addImport("cmdline", cmdline_module);`
- `argv_split_root_module.addImport("argv_split", argv_split_module);`
- `rbtree_root_module.addImport("rbtree", rbtree_module);`

Those pairings are the current package wiring evidence for the shared Phase 7
helper bundle.

## Shared Build Graph Evidence

`zigux/tests/phase7_build.zig` also keeps the current summarized replay graph
explicit rather than leaving survey or helper-local routes implicit:

- direct helper-local test steps: `phase7-string-helpers-test`,
  `phase7-cmdline-test`, `phase7-argv-split-test`, and
  `phase7-rbtree-test`
- shared survey and boundary steps: `phase7-string-helpers-survey`,
  `phase7-string-helpers-sample-boundary`, `phase7-cmdline-survey`,
  `phase7-argv-split-survey`, and `phase7-rbtree-survey`
- shared aggregate step: `test`

The aggregate `test` step currently depends on all nine run artifacts above, so
the shared replay still fans in the direct helper-local tests plus the dedicated
survey and sample-boundary routes through one Phase 7 build entrypoint.

## Repo-Root Replay Boundary

The survey-style routes inside `zigux/tests/phase7_build.zig` keep repo-root
replay behavior explicit with:

- `run_string_helpers_survey_tests.setCwd(b.path("../.."));`
- `run_string_helpers_sample_boundary_tests.setCwd(b.path("../.."));`
- `run_cmdline_survey_tests.setCwd(b.path("../.."));`
- `run_argv_split_survey_tests.setCwd(b.path("../.."));`
- `run_rbtree_survey_tests.setCwd(b.path("../.."));`

That means the current handoff is not just "Makefile calls Zig." The shared
build file also preserves the repo-root working-directory assumption for the
survey-style review routes that need it.

## Evidence Boundary

This note records route presence and current build-graph wiring only.

- It does confirm that `zigux/Makefile` currently hands Phase 7 into
  `zigux/tests/phase7_build.zig`.
- It does confirm that `zigux/tests/phase7_build.zig` currently wires the four
  roadmap-backed Phase 7 helpers into direct tests, survey routes, and the
  string-helpers sample-boundary route.
- It does not claim that the full shared Phase 7 bundle is passing green on
  current `master`.

The next truthful follow-through for this lane is to keep this exact handoff
evidence aligned if the shared Makefile route, the validator-first wrapper, or
the helper-to-test package wiring changes.
