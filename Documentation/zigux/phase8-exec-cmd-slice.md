# Phase 8 Exec-Cmd Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/subcmd/exec-cmd.c`.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=exec-cmd-deferred-exec-packet`
- roadmap posture: prove Zigux inside serious repo-hosted tooling, not just tiny helpers
- scope: path-resolution, injected environment setup, `get_pwd_cwd()`-style cwd choice, null-terminated command-vector preparation, pure deferred `execv_cmd()`-style handoff planning, and pure `execl_cmd()`-style argv collection and handoff planning only
- product boundary:
  - `tools/lib/subcmd/exec-cmd.zig`
  - `zigux/tests/phase8_exec_cmd.zig`
  - `zigux/tests/phase8_exec_cmd_only_build.zig`
  - `zigux/tests/phase8_build.zig`

## Why this slice exists

The Phase 8 roadmap explicitly calls for `tools/lib/subcmd/*.zig` as the first product foothold in repo-hosted userspace-adjacent tooling and says the goal is to prove Zigux inside serious repo-hosted tooling, not just tiny helpers.

The live repo still benefits from keeping `exec-cmd` parked as a helper-first, output-stable deferred-exec planning packet: it makes the path-choice, environment-shaping, and argv-shape contracts reviewable without widening into process-launch side effects or unrelated `help.c` behavior. That keeps the broader Phase 8 output-stable tooling behavior promise explicit at the deferred-exec planning layer.

That same parked command-boundary packet now also sits inside the shared Phase 8 validator-first route, so reviewers can recheck the command slice through `make -C zigux phase8-validate` before widening back out to the broader tooling bundle.

That validator-first coverage still needs a strict boundary. This Phase 8 slice stops before any ownership of `execv_cmd()` or `execvp()`, avoids scheduler-facing transport or queue claims, and leaves `kernel/workqueue.c` in the later Phase 14 boundary-study tranche rather than treating this tooling helper as an early workqueue port.

## Gates

1. run the focused Zig module tests
- `zig test tools/lib/subcmd/exec-cmd.zig`

2. run the focused exec-cmd shared replay
- `zig build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all`

3. run the shared Phase 8 validator route
- `make -C zigux phase8-validate`

4. run the bundled Phase 8 tooling gate
- `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

5. run the focused convenience target
- `make -C zigux phase8-exec-cmd-test`

## Current parity surface

The current parked deferred-exec packet covers:

- absolute-versus-prefixed `system_path()` resolution
- `get_argv_exec_path()` precedence across explicit path, environment path, and configured fallback
- `extract_argv0_path()` splitting for directory-prefixed tool invocations
- injected `exec_cmd_init()` and `set_argv_exec_path()` environment propagation for `PREFIX` and the configured exec-path variable
- `setup_path()`-adjacent path assembly plus `PATH` environment updates via relative-to-cwd normalization
- a pure `choosePwdCwd()` helper for caller-provided same-location decisions plus a stat-backed `sameLocation()` and `choosePwdCwdFromFilesystem()` pair that mirror the C helper's logical-`PWD` acceptance rule without widening into broader process or environment side effects
- `prepare_exec_cmd()`-style argv prefixing with a trailing null slot for later deferred `execv_cmd()`-style handoff planning, plus a pure `buildDeferredExecvCall()` helper that keeps that null-terminated argv packet reviewable before any direct launch ownership exists
- a pure `collectExeclArgs()` helper that models the `execl_cmd()` argument collector and its legacy `MAX_ARGS` guard, plus a pure `buildDeferredExeclCall()` helper that preserves the same deferred argv-handoff packet without claiming any direct process-launch behavior, scheduler-facing transport, or workqueue-facing deferred-execution ownership

The current tests check:

- path fallback precedence stays stable
- relative search-path entries become absolute against the current working directory input
- empty inherited `PATH` values preserve the C helper's trailing-colon shape instead of silently falling back to default search roots
- directory-prefixed `argv[0]` values split cleanly into path and command name
- the injected environment wrapper keeps `PREFIX`, the configured exec-path environment key, and the resulting `PATH` value aligned
- `choosePwdCwd()` still supports caller-provided same-location proofs while the shared logical-`PWD` replay now proves that a symlinked alias to the same directory is accepted by the new filesystem-backed helper path
- prepared argv vectors start with the configured executable name and keep a trailing null terminator, including the empty-tail case
- the pure deferred `execv` and `execl` handoff helpers keep the parked argv packet reviewable before any direct `execv_cmd()` or `execvp()` ownership exists
- the pure `execl_cmd()` collector preserves the command head, stops at the first null terminator, and rejects the C helper's overflow shape before any real `execvp()` call exists
- the focused `phase8_exec_cmd_only_build.zig` replay isolates the parked `exec-cmd` slice from the broader Phase 8 tooling packet when review needs a smaller build-backed proof, and the published `make -C zigux phase8-exec-cmd-test` wrapper now exposes that replay as a one-command route
- the shared `make -C zigux phase8-validate` route now keeps this parked command-boundary slice aligned with the live Phase 8 validator-first packet before the broader tooling replay runs

## Non-goals

This slice still does not claim:

- direct `execvp()` parity, `execv_cmd()` ownership, or process-launch behavior
- direct OS environment reads or writes
- deferred queue ownership or scheduler-facing transport
- the later `kernel/workqueue.c` Phase 14 boundary-study target
- the terminal/help listing surface from `tools/lib/subcmd/help.c`
- the larger Phase 8 anchors in `tools/lib/symbol/` or `tools/lib/bpf/`

## Next bounded step

Keep `tools/lib/subcmd/exec-cmd.zig` parked unless repo review specifically wants one more bounded parity step around another tiny helper-only path-choice or argv-shape guard inside this file family; if the lane reopens on reviewability alone, keep it to one equally small update around the focused replay surface instead of widening into sibling Phase 8 anchors.