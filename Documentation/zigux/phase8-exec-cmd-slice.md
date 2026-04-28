# Phase 8 Exec-Cmd Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/subcmd/exec-cmd.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=exec-cmd-tooling-starter`
- scope: path-resolution, injected environment setup, `get_pwd_cwd()`-style cwd choice plus stat-identity proof, null-terminated command-vector preparation, and pure `execl_cmd()`-style argv collection only
- product boundary:
  - `tools/lib/subcmd/exec-cmd.zig`
  - `zigux/tests/phase8_exec_cmd.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly calls for `tools/lib/subcmd/*.zig` as the first product foothold in repo-hosted userspace-adjacent tooling.

`exec-cmd.zig` remains the bounded helper-first port for the `exec-cmd.c` side of that roadmap target. The sibling `help.zig` slice now exists too, so this note is no longer tracking the first Zig foothold under `tools/lib/subcmd/`; it is tracking the parked `exec-cmd` subcmd slice specifically.

That keeps the lane honest: `exec-cmd` now covers the smallest reviewable setup and argv-preparation surface from the C helper without widening into direct process-launch side effects or sibling `help.c` behavior.

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/subcmd/exec-cmd.zig`

2. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig`

3. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current parked slice covers:

- absolute-versus-prefixed `system_path()` resolution
- `get_argv_exec_path()` precedence across explicit path, environment path, and configured fallback, including the C helper's preserved explicit-empty exec-path sentinel
- `extract_argv0_path()` splitting for directory-prefixed tool invocations
- injected `exec_cmd_init()` and `set_argv_exec_path()` environment propagation for `PREFIX` and the configured exec-path variable
- `setup_path()`-adjacent path assembly plus `PATH` environment updates via relative-to-cwd normalization, including the inherited-empty-`PATH` trailing-`:` shape from the C helper and the skipped empty explicit exec-path segment when only `argv0_path` remains
- a pure `choosePwdCwd()` helper that models the `get_pwd_cwd()` decision boundary when the caller proves whether `PWD` and `cwd` resolve to the same location
- a tiny `FileIdentity` plus `sameFileLocation()`, `samePathIdentity()`, `choosePwdCwdFromFileIdentity()`, and `choosePwdCwdFromIdentities()` layer that mirrors the C helper's stat-backed same-location proof without introducing direct filesystem calls
- `prepare_exec_cmd()`-style argv prefixing with a trailing null slot for later `execv()` plumbing
- a pure `collectExeclArgs()` helper that models the `execl_cmd()` argument collector, its required trailing null terminator, and its legacy `MAX_ARGS` guard without claiming any direct process-launch behavior

The current tests check:

- path fallback precedence stays stable, including the explicit-empty exec-path sentinel staying distinct from the configured fallback
- relative search-path entries become absolute against the current working directory input
- directory-prefixed `argv[0]` values split cleanly into path and command name
- the injected environment wrapper keeps `PREFIX`, the configured exec-path environment key, and the resulting `PATH` value aligned, including the inherited-empty-`PATH` trailing-`:` edge and the skipped empty explicit exec-path segment
- `choosePwdCwd()` prefers `PWD` only when the caller proves it matches the physical cwd
- the stat-identity helpers prefer `PWD` only when both injected identities match and fall back cleanly when the optional `PWD` stat shape is missing
- prepared argv vectors start with the configured executable name and keep a trailing null terminator, including the empty-tail case
- the pure `execl_cmd()` collector preserves the command head, stops at the first null terminator, rejects a missing terminator, and rejects the C helper's overflow shape before any real `execvp()` call exists

## Non-goals

This slice still does not claim:

- direct `execvp()` parity or process-launch behavior
- direct OS environment reads or writes
- the terminal/help listing surface from `tools/lib/subcmd/help.c`
- the larger Phase 8 anchors in `tools/lib/symbol/` or `tools/lib/bpf/`

## Next bounded step

Keep `tools/lib/subcmd/exec-cmd.zig` parked unless repo review finds one more tiny helper-only guard inside this file family; the `get_pwd_cwd()` stat-backed same-location proof and the empty explicit exec-path sentinel are now covered through the helper-local and shared validation layers, so future Phase 8 work should usually continue in sibling files instead.
