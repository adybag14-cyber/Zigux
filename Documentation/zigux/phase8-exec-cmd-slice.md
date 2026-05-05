# Phase 8 Exec-Cmd Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/subcmd/exec-cmd.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=exec-cmd-tooling-starter`
- scope: path-resolution, injected environment setup, `get_pwd_cwd()`-style cwd choice, null-terminated command-vector preparation, and pure `execl_cmd()`-style argv collection only
- product boundary:
  - `tools/lib/subcmd/exec-cmd.zig`
  - `zigux/tests/phase8_exec_cmd.zig`
  - `zigux/tests/phase8_exec_cmd_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly calls for `tools/lib/subcmd/*.zig` as the first product foothold in repo-hosted userspace-adjacent tooling.

The live repo had no Zig slice under `tools/lib/subcmd/`, so the most valuable bounded step was to start `exec-cmd` with the helper-first surface that is easiest to validate without widening into process-launch side effects or unrelated `help.c` behavior.

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/subcmd/exec-cmd.zig`

2. run the focused exec-cmd shared replay
- `zig build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all`

3. run the bundled Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

4. run the focused convenience target
- `make -C zigux phase8-exec-cmd-test`

## Current parity surface

The current starter slice covers:

- absolute-versus-prefixed `system_path()` resolution
- `get_argv_exec_path()` precedence across explicit path, environment path, and configured fallback
- `extract_argv0_path()` splitting for directory-prefixed tool invocations
- injected `exec_cmd_init()` and `set_argv_exec_path()` environment propagation for `PREFIX` and the configured exec-path variable
- `setup_path()`-adjacent path assembly plus `PATH` environment updates via relative-to-cwd normalization
- a pure `choosePwdCwd()` helper for caller-provided same-location decisions plus a stat-backed `sameLocation()` and `choosePwdCwdFromFilesystem()` pair that mirror the C helper's logical-`PWD` acceptance rule without widening into broader process or environment side effects
- `prepare_exec_cmd()`-style argv prefixing with a trailing null slot for later `execv()` plumbing
- a pure `collectExeclArgs()` helper that models the `execl_cmd()` argument collector and its legacy `MAX_ARGS` guard without claiming any direct process-launch behavior

The current tests check:

- path fallback precedence stays stable
- relative search-path entries become absolute against the current working directory input
- empty inherited `PATH` values preserve the C helper's trailing-colon shape instead of silently falling back to default search roots
- directory-prefixed `argv[0]` values split cleanly into path and command name
- the injected environment wrapper keeps `PREFIX`, the configured exec-path environment key, and the resulting `PATH` value aligned
- `choosePwdCwd()` still supports caller-provided same-location proofs while the shared logical-`PWD` replay now proves that a symlinked alias to the same directory is accepted by the new filesystem-backed helper path
- prepared argv vectors start with the configured executable name and keep a trailing null terminator, including the empty-tail case
- the pure `execl_cmd()` collector preserves the command head, stops at the first null terminator, and rejects the C helper's overflow shape before any real `execvp()` call exists
- the focused `phase8_exec_cmd_only_build.zig` replay isolates the parked `exec-cmd` slice from the broader Phase 8 tooling packet when review needs a smaller build-backed proof, and the published `make -C zigux phase8-exec-cmd-test` wrapper now exposes that replay as a one-command route

## Non-goals

This slice still does not claim:

- direct `execvp()` parity or process-launch behavior
- direct OS environment reads or writes
- the terminal/help listing surface from `tools/lib/subcmd/help.c`
- the larger Phase 8 anchors in `tools/lib/symbol/` or `tools/lib/bpf/`

## Next bounded step

Keep `tools/lib/subcmd/exec-cmd.zig` parked unless repo review specifically wants one more bounded parity step around another tiny helper-only path-choice or argv-shape guard inside this file family; if the lane reopens on reviewability alone, keep it to one equally small update around the focused replay surface instead of widening into sibling Phase 8 anchors.
