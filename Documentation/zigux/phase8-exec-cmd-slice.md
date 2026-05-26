# Phase 8 Exec-Cmd Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/subcmd/exec-cmd.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=exec-cmd-deferred-exec-packet`
- scope: path-resolution, injected environment setup, `get_pwd_cwd()`-style cwd choice plus bounded setup-path wrappers that consume stat-identity proof, null-terminated command-vector preparation, pure `execl_cmd()`-style argv collection, and pure deferred `execv_cmd()` / `execl_cmd()` handoff carriers only
- product boundary:
  - `tools/lib/subcmd/exec-cmd.zig`
  - `zigux/tests/phase8_exec_cmd.zig`
  - `zigux/tests/phase8_exec_cmd_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly calls for `tools/lib/subcmd/*.zig` as the first product foothold in repo-hosted userspace-adjacent tooling.

`exec-cmd.zig` remains the bounded helper-first port for the `exec-cmd.c` side of that roadmap target. The sibling `help.zig` slice now exists too, so this note is no longer tracking the first Zig foothold under `tools/lib/subcmd/`; it is tracking the parked `exec-cmd` subcmd slice specifically.

That keeps the lane honest: `exec-cmd` now covers the smallest reviewable setup, argv-preparation, and deferred-handoff planning surface from the C helper without widening into direct process-launch side effects or sibling `help.c` behavior.

The roadmap boundary matters here too: Phase 8 is the repo-hosted tooling tranche, while `kernel/workqueue.c` remains a Phase 14 boundary-study target. So this slice can model argument preparation and environment setup for later deferred execution, and it can package launch-free `execv_cmd()` and `execl_cmd()` handoff plans for later use, but it must stop before `execvp()` side effects, scheduler-facing transport ownership, or anything that reads like a workqueue-style execution substrate.

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/subcmd/exec-cmd.zig`

2. run the focused shared exec-cmd gate
- `zig build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all`

3. run the shared Phase 8 validation route
- `make -C zigux phase8-validate`

4. run the broader Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

5. run the convenience targets
- `make -C zigux phase8-exec-cmd-test`
- `make -C zigux phase8`

## Current parity surface

The current parked slice covers:

- absolute-versus-prefixed `system_path()` resolution
- `get_argv_exec_path()` precedence across explicit path, environment path, and configured fallback, including the C helper's preserved explicit-empty exec-path sentinel
- `extract_argv0_path()` splitting for directory-prefixed tool invocations, including directory-only and root-only empty-command sentinels that must not inject blank search-path segments
- injected `exec_cmd_init()` and `set_argv_exec_path()` environment propagation for `PREFIX` and the configured exec-path variable
- `setup_path()`-adjacent path assembly plus `PATH` environment updates via relative-to-cwd normalization, including the inherited-empty-`PATH` trailing-`:` shape from the C helper, the skipped empty explicit exec-path segment when only `argv0_path` remains, and the root-cwd `//relative` output shape that the C helper preserves
- a pure `choosePwdCwd()` helper that models the `get_pwd_cwd()` decision boundary when the caller proves whether `PWD` and `cwd` resolve to the same location and still ignores an explicitly empty `PWD`
- a tiny `FileIdentity` plus `sameFileLocation()`, `samePathIdentity()`, `choosePwdCwdFromFileIdentity()`, and `choosePwdCwdFromIdentities()` layer that mirrors the C helper's stat-backed same-location proof without introducing direct filesystem calls
- `setupPathWithPwd()` as the bounded wrapper that applies that stat-backed `PWD` proof directly to `setupPath()` before relative search-path normalization
- `prepare_exec_cmd()`-style argv prefixing with a trailing null slot for later `execv()` plumbing
- `buildDeferredExecvCall()` as the launch-free `execv_cmd()` handoff that packages the prepared argv vector for later use without claiming any direct `execvp()` side effect
- a pure `collectExeclArgs()` helper that models the `execl_cmd()` argument collector, including the C helper's legacy post-fetch `MAX_ARGS` overflow guard where a terminating null that lands in slot `MAX_ARGS` still fails, plus its required trailing null terminator, without claiming any direct process-launch behavior
- `buildDeferredExeclCall()` plus the tiny `DeferredExecCall` carrier so the `execl_cmd()` path can now hand off one fully prepared future `execvp()` argv packet without launching a process, waiting for completion, or claiming any queue ownership

## Current roadmap gap

Against the Phase 8 roadmap, the current slice is a helper-first deferred-execution foothold, not a complete tooling-substrate delivery.

What is landed today is the argument and environment preparation packet plus the launch-free deferred carriers.
What remains intentionally outside this slice is the work needed to turn those carriers into live execution behavior.

The still-open gap stays bounded and explicit:

- no direct `execvp()` parity, child launch, exit-status collection, or process waiting
- no retry scheduling, timer-backed backoff, timeout handling, or poll-loop ownership around deferred execution
- no file-descriptor, token, or environment-lifetime ownership beyond the helper-local preparation packet
- no queue ownership, wakeup routing, worker-pool control, or scheduler-visible execution substrate
- no handoff into `kernel/workqueue.c`, `kernel/trace/ring_buffer.c`, or any other Phase 14 core-adjacent study-only anchor

That comparison is the lane guardrail: the current Phase 8 packet proves Zigux can prepare and carry deferred execution inputs inside repo-hosted tooling, but it does not yet prove that Zigux owns a deferred-execution runtime, a broader task queue, or any workqueue-style execution substrate.

Future follow-up in this lane should therefore stay inside `tools/lib/subcmd/*.zig` reviewability, shared reminder truthfulness, or other helper-first Phase 8 tooling surfaces unless the roadmap explicitly promotes a larger execution owner.

## Non-goals

This slice still does not claim:

- direct `execvp()` parity or process-launch behavior
- process waiting, retry scheduling, or queue ownership
- deferred execution ownership, queueing, or scheduler-facing transport behavior
- any handoff into `kernel/workqueue.c` or other Phase 14 boundary-study ownership
- direct OS environment reads or writes
- the terminal/help listing surface from `tools/lib/subcmd/help.c`
- the larger Phase 8 anchors in `tools/lib/symbol/` or `tools/lib/bpf/`
