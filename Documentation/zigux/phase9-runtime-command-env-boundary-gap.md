# Phase 9 Runtime Command and Environment Boundary Gap

This note records the current roadmap-backed gap around runtime command and environment plumbing on `master`.

## Status

- `PHASE9_STATUS=parked`
- `PHASE9_SURVEY=runtime-command-env-boundary-gap`
- survey checkpoint: refreshed against current `master` readback on 2026-05-25
- lane origin: scheduled `P6-L13` prompt narrowed to the nearest truthful command-and-environment packet instead of the unrelated Phase 6 leaf-helper tranche
- scope: shared-owner boundary evidence only

## Why this note exists

The roadmap keeps Phase 8 command-side tooling and Phase 9 runtime pilots separate.

That split matters because current `master` already carries bounded command and environment preparation on the Phase 8 side, and it already carries a runtime-loader boundary guard on the Phase 9 side, but it still does not carry shipped runtime command or environment activation control.

The honest current gap is therefore not missing reminder language alone. It is the still-deliberate boundary between:

- Phase 8 command and environment preparation that stays owned by repo-hosted tooling helpers, and
- Phase 9 runtime-loader request surfaces that prove those controls stay out of the shared runtime contract.

## Roadmap boundary

The roadmap places helper-first command and environment preparation under the repo-hosted tooling tranche before deeper runtime-substrate work.

Relevant roadmap-backed anchors and destinations:

- `tools/lib/subcmd/exec-cmd.c` -> `tools/lib/subcmd/exec-cmd.zig`
- `tools/lib/subcmd/help.c` -> helper-first tooling surfaces under `tools/lib/subcmd/`
- `tools/lib/bpf/libbpf.c` -> bounded helper-first bridge surfaces under `tools/lib/bpf/zigux_segments/`
- first runtime pilots stay under `zigux/tests/runtime_*` and `samples/zigux/runtime_*`

That means command lookup, exec-path policy, `PWD` versus `cwd` normalization, `PATH` shaping, and terminal display environment cues belong to the earlier tooling packet unless a later roadmap-backed runtime substrate explicitly adopts them.

## Current direct evidence on master

Current `master` directly keeps the command-side owner packet explicit through:

- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `tools/lib/subcmd/exec-cmd.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`

That packet already covers bounded preparation surfaces such as:

- exec-path selection and `PERF_EXEC_PATH` precedence
- `PWD` versus `cwd` choice after same-location proof
- `PATH` assembly and relative-path normalization
- deferred `execv` and `execl` handoff preparation without direct process launch

Current `master` also directly keeps the shared runtime-loader boundary packet explicit through:

- `Documentation/zigux/phase9-runtime-pilot-lane-sequencing.md`
- `zigux/kernel/runtime_loader_contract.zig`
- `zigux/kernel/runtime_loader.zig`
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig`
- `zigux/tests/runtime_loader_allocator_init_flow.zig`
- `zigux/tests/phase9_build.zig`

That returned Phase 9 packet proves the opposite side of the boundary:

- shared runtime-loader `LoadPlan` metadata stays bounded to module-family lifecycle and allocator/init-flow state
- command-name, exec-path, environment-mutation, `PATH`, `LINES`, and `COLUMNS` controls do not belong in the shared runtime-loader contract
- the dedicated command/environment boundary guard fail-closes if those Phase 8 control markers bleed into the loader contract or loader facade

## Current gap

The current roadmap gap is therefore precise:

1. Zigux now ships helper-first command and environment preparation.
2. Zigux now ships a runtime-loader guard that keeps those controls out of the shared loader packet.
3. Zigux still does not ship runtime command or environment activation control that would legally move those surfaces into a Phase 9 runtime contract.

Put another way: current `master` proves ownership separation, not runtime command/environment delivery.

## What this note does not claim

This note does not claim:

- live runtime process launch or activation control
- runtime-side ownership of `PERF_EXEC_PATH`, `PATH`, `PWD`, `LINES`, or `COLUMNS`
- runtime-loader adoption of deferred `execv` or `execl` handoff packets
- scheduler-facing execution substrate, workqueue ownership, or event-loop behavior
- blocked publication, install-root, or depmod completion

## Next bounded step

Keep this note parked unless a future current-`master` reread shows one of these moved:

- `tools/lib/subcmd/exec-cmd.zig` or its focused Phase 8 tests stop carrying the bounded command/environment preparation packet
- `zigux/kernel/runtime_loader_command_env_boundary_guard.zig` stops proving that the shared loader contract rejects command/environment bleed-through
- a new roadmap-backed runtime substrate lands that explicitly adopts part of the command/environment control surface

If the lane reopens, repair one reminder surface or one boundary note at a time before widening into helper semantics or runtime behavior.
