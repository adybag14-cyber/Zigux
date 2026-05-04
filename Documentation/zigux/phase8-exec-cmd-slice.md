# Phase 8 Exec-Cmd Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/subcmd/exec-cmd.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=exec-cmd-tooling-parked`
- legacy validator alias: `PHASE8_SLICE=exec-cmd-tooling-starter`
- scope: path-resolution, injected environment setup, `get_pwd_cwd()`-style cwd choice plus a bounded setup-path wrapper that consumes stat-identity proof, null-terminated command-vector preparation, pure `execl_cmd()`-style argv collection, and launch-free deferred-exec handoff carriers that stop before direct process execution
- product boundary:
  - `tools/lib/subcmd/exec-cmd.zig`
  - `zigux/tests/phase8_exec_cmd.zig`
  - `zigux/tests/phase8_exec_cmd_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly calls for `tools/lib/subcmd/*.zig` as the first product foothold in repo-hosted userspace-adjacent tooling.

`exec-cmd.zig` remains the bounded helper-first port for the `exec-cmd.c` side of that roadmap target. The sibling `help.zig` slice now exists too, so this note is no longer tracking the first Zig foothold under `tools/lib/subcmd/`; it is tracking the parked `exec-cmd` subcmd slice specifically.

That keeps the lane honest: `exec-cmd` now covers the smallest reviewable setup and argv-preparation surface from the C helper without widening into direct process-launch side effects or sibling `help.c` behavior.

The Phase 8 roadmap also requires output-stable tooling behavior. For `exec-cmd`, that requirement stays intentionally indirect in the parked packet: this slice only prepares cwd, `PATH`, and deferred argv state for later subcommands, while human-facing output stability stays owned by sibling tooling packets such as `help.zig`. Keeping that split explicit prevents this note from overstating parity for command execution or smuggling queue-like transport claims into a preparation helper.

The roadmap boundary matters here too: Phase 8 is the repo-hosted tooling tranche, while `kernel/workqueue.c` remains a Phase 14 boundary-study target. So this slice can model argument preparation and environment setup for later deferred execution, but it must stop before `execv_cmd()` or `execvp()` side effects, scheduler-facing transport ownership, or anything that reads like a workqueue-style execution substrate.

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/subcmd/exec-cmd.zig`

2. run the focused shared exec-cmd gate
- `zig build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all`

3. run the broader Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

4. run the convenience targets
- `make -C zigux phase8-exec-cmd-test`
- `make -C zigux phase8`

## Current parity surface

The current parked slice covers:

- absolute-versus-prefixed `system_path()` resolution
- `get_argv_exec_path()` precedence across explicit path, environment path, and configured fallback, including the C helper's preserved explicit-empty exec-path sentinel
- `extract_argv0_path()` splitting for directory-prefixed tool invocations
- injected `exec_cmd_init()` and `set_argv_exec_path()` environment propagation for `PREFIX` and the configured exec-path variable
- `setup_path()`-adjacent path assembly plus `PATH` environment updates via relative-to-cwd normalization, including the inherited-empty-`PATH` trailing-`:` shape from the C helper, the skipped empty explicit exec-path segment when only `argv0_path` remains, and the single-slash root-cwd `/tools/bin:/scripts` shape that the Zig helper intentionally keeps stable at `/`
- a pure `choosePwdCwd()` helper that models the `get_pwd_cwd()` decision boundary when the caller proves whether `PWD` and `cwd` resolve to the same location and still ignores an explicitly empty `PWD`
- a tiny `FileIdentity` plus `sameFileLocation()`, `samePathIdentity()`, `choosePwdCwdFromFileIdentity()`, and `choosePwdCwdFromIdentities()` layer that mirrors the C helper's stat-backed same-location proof without introducing direct filesystem calls
- `setupPathWithPwd()` as the bounded wrapper that applies that stat-backed `PWD` proof directly to `setupPath()` before relative search-path normalization
- `prepare_exec_cmd()`-style argv prefixing with a trailing null slot for later `execv()` plumbing
- `buildDeferredExecvCall()` as the launch-free `execv_cmd()` handoff that packages the prepared argv vector for later use without claiming any direct `execvp()` side effect
- `planDeferredExecvCall()` as the combined launch-free wrapper that keeps rebuilt `PATH` state and the deferred `execv_cmd()` argv packet in one reviewable handoff without widening into scheduler-facing execution behavior
- `planDeferredExecvCallWithPwd()` as the matching launch-free wrapper that threads the stat-backed logical-`PWD` proof through the same deferred `execv_cmd()` packet so the combined helper path can stay aligned with `get_pwd_cwd()`-style location choice instead of silently dropping back to physical cwd handling
- a pure `collectExeclArgs()` helper that models the `execl_cmd()` argument collector, including the C helper's legacy post-fetch `MAX_ARGS` overflow guard where a terminating null that lands in slot `MAX_ARGS` still fails, plus its required trailing null terminator, without claiming any direct process-launch behavior
- `buildDeferredExeclCall()` plus the tiny `DeferredExecCall` carrier so the `execl_cmd()` path can now hand off one fully prepared future `execvp()` argv packet without launching a process, waiting for completion, or claiming any queue ownership
- `planDeferredExeclCall()` as the combined launch-free wrapper that keeps rebuilt `PATH` state and the deferred `execl_cmd()` argv packet in one reviewable handoff without widening into scheduler-facing execution behavior
- `planDeferredExeclCallWithPwd()` as the matching launch-free wrapper that keeps the deferred `execl_cmd()` handoff aligned with the same stat-backed logical-`PWD` proof before the packet reaches any future launch surface

The current tests check:

- path fallback precedence stays stable, including the explicit-empty exec-path sentinel staying distinct from the configured fallback
- relative search-path entries become absolute against the current working directory input
- directory-prefixed `argv[0]` values split cleanly into path and command name, including the root-directory `/perf` shape preserving the C helper's empty `argv0_path` sentinel without injecting a blank search-path segment and slash-terminated inputs such as `tools/perf/` or `/` preserving the C helper's empty command-name sentinel
- the injected environment wrapper keeps `PREFIX`, the configured exec-path environment key, and the resulting `PATH` value aligned, including the inherited-empty-`PATH` trailing-`:` edge, the inherited-missing-`PATH` fallback to `/usr/local/bin:/usr/bin:/bin`, the skipped empty explicit exec-path segment, the inherited-empty exec-path environment fallback to the configured path, the inherited relative exec-path environment segment being normalized against cwd only when rebuilding `PATH`, and the single-slash root-cwd `/tools/bin:/scripts` shape for relative entries
- `choosePwdCwd()` prefers `PWD` only when the caller proves it matches the physical cwd and still falls back cleanly when `PWD` is explicitly empty
- the stat-identity helpers prefer `PWD` only when both injected identities match and fall back cleanly for mismatched or missing optional `PWD` stat input
- `setupPathWithPwd()` reuses the logical `PWD` only when the injected stat identities match and otherwise falls back to the physical cwd before rebuilding `PATH`, including the empty-`PWD` case
- prepared argv vectors start with the configured executable name and keep a trailing null terminator, including the empty-tail case
- the deferred `execv_cmd()` handoff packages both populated and empty-tail argv vectors without widening into `execvp()` behavior
- the combined deferred `execv_cmd()` planner keeps rebuilt `PATH` state and the future argv packet aligned in one launch-free handoff without claiming direct execution or queue ownership
- the new PWD-aware deferred `execv_cmd()` planner keeps that same combined handoff aligned with logical `PWD` when the injected identities match instead of leaving the stat-backed `get_pwd_cwd()` proof trapped one helper layer lower
- the pure `execl_cmd()` collector preserves the command head, stops at the first null terminator, accepts only the last null-terminated shape that stays below `MAX_ARGS`, rejects the C helper's legacy null-slot overflow shape where the terminating null itself lands in slot `MAX_ARGS`, rejects a missing terminator, and still stops before any real `execvp()` call exists
- the deferred-exec handoff helper prepends the configured executable name to the collected `execl_cmd()` packet, keeps the trailing null terminator, preserves the empty-tail `execl_cmd(cmd, NULL)` shape, and stays launch-free so the reviewable surface stops before any real `execvp()` side effect
- the combined deferred `execl_cmd()` planner keeps rebuilt `PATH` state and the future argv packet aligned in one launch-free handoff without claiming direct execution or queue ownership
- the new PWD-aware deferred `execl_cmd()` planner keeps that same combined handoff aligned with the stat-backed logical-`PWD` proof and still falls back cleanly when the injected identities do not match
- helper-local `tools/lib/subcmd/exec-cmd.zig` tests own the detailed `setupPathWithPwd()`, `planDeferredExecvCallWithPwd()`, `planDeferredExeclCallWithPwd()`, and empty-tail `execl_cmd(cmd, NULL)` shapes, while the focused Phase 8 replay stays centered on one integrated deferred handoff plus docs, build wiring, and live `exec-cmd.c` anchor reviewability

## Non-goals

This slice still does not claim:

- direct `execvp()` parity or process-launch behavior
- process waiting, retry scheduling, or queue ownership
- deferred execution ownership, queueing, or scheduler-facing transport behavior
- any handoff into `kernel/workqueue.c` or other Phase 14 boundary-study ownership
- direct OS environment reads or writes
- the terminal/help listing surface from `tools/lib/subcmd/help.c`
- the larger Phase 8 anchors in `tools/lib/symbol/` or `tools/lib/bpf/`

## Next bounded step

Keep `tools/lib/subcmd/exec-cmd.zig` parked unless repo review finds one more tiny helper-only guard inside this file family; the `get_pwd_cwd()` stat-backed same-location proof now flows through both the helper-local choice layer, the bounded `setupPathWithPwd()` wrapper, and the combined deferred `execv_cmd()` plus `execl_cmd()` planners without widening into launch behavior, so future Phase 8 work should usually continue in sibling files instead of smuggling `execvp()` ownership, retry or queue semantics, or any `kernel/workqueue.c` boundary claim into this parked tooling slice.