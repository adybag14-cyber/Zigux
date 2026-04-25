# Phase 8 Exec-Cmd Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/subcmd/exec-cmd.c`.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=exec-cmd-tooling-starter`
- scope: path-resolution and null-terminated command-vector preparation only
- product boundary:
  - `tools/lib/subcmd/exec-cmd.zig`
  - `zigux/tests/phase8_exec_cmd.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly calls for `tools/lib/subcmd/*.zig` as the first product foothold in repo-hosted userspace-adjacent tooling.

The live repo had no Zig slice under `tools/lib/subcmd/`, so the most valuable bounded step was to start `exec-cmd` with the helper-first surface that is easiest to validate without widening into process-launch side effects or unrelated `help.c` behavior.

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/subcmd/exec-cmd.zig`

2. run the dedicated Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig`

3. run the convenience target
- `make -C zigux phase8`

## Current parity surface

The current starter slice covers:

- absolute-versus-prefixed `system_path()` resolution
- `get_argv_exec_path()` precedence across explicit path, environment path, and configured fallback
- `extract_argv0_path()` splitting for directory-prefixed tool invocations
- `setup_path()`-adjacent path assembly via relative-to-cwd normalization
- `prepare_exec_cmd()`-style argv prefixing with a trailing null slot for later `execv()` plumbing

The current tests check:

- path fallback precedence stays stable
- relative search-path entries become absolute against the current working directory input
- directory-prefixed `argv[0]` values split cleanly into path and command name
- prepared argv vectors start with the configured executable name and keep a trailing null terminator, including the empty-tail case

## Non-goals

This slice does not yet claim:

- direct `execvp()` parity or process-launch behavior
- environment mutation side effects from `exec_cmd_init()` or `setup_path()`
- the terminal/help listing surface from `tools/lib/subcmd/help.c`
- the larger Phase 8 anchors in `tools/lib/symbol/` or `tools/lib/bpf/`

## Next bounded step

Stay in `tools/lib/subcmd/exec-cmd.zig` and either add an injected environment wrapper for `setup_path()` and `exec_cmd_init()` semantics, or start the sibling `tools/lib/subcmd/help.zig` lane once this starter surface is accepted.
