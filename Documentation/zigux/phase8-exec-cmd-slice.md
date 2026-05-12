# Phase 8 Exec-Cmd Slice

This document tracks the bounded Phase 8 userspace-adjacent tooling slice for Zigux around `tools/lib/subcmd/exec-cmd.c`.

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=exec-cmd-deferred-exec-packet`
- roadmap posture: prove Zigux inside serious repo-hosted tooling, not just tiny helpers
- scope: path-resolution, injected environment setup, `get_pwd_cwd()`-style cwd choice, null-terminated command-vector preparation, pure deferred `execv_cmd()`-style handoff planning, and pure `execl_cmd()`-style argv collection and handoff planning only

## Product Boundary
- `tools/lib/subcmd/exec-cmd.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `zigux/tests/phase8_build.zig`

## Why This Slice Exists
The Phase 8 roadmap explicitly calls for `tools/lib/subcmd/*.zig` as the first product foothold in repo-hosted userspace-adjacent tooling and says the goal is to prove Zigux inside serious repo-hosted tooling, not just tiny helpers.

The live repo still benefits from keeping `exec-cmd` parked as a helper-first, output-stable deferred-exec planning packet: it makes the path-choice, environment-shaping, and argv-shape contracts reviewable without widening into process-launch side effects or unrelated `help.c` behavior.

Within that parked packet, helper-local unit tests in `tools/lib/subcmd/exec-cmd.zig` own the low-level trailing-colon `PATH` edge, while the focused Phase 8 replay stays on the integrated deferred-exec packet so the live C helper anchors, checklist hook, and validator route stay aligned around one reviewable packet.

## Gates
1. Run the focused Zig module tests: `zig test tools/lib/subcmd/exec-cmd.zig`
2. Run the shared validator route: `make -C zigux phase8-validate`
3. Run the focused exec-cmd replay: `zig build test --build-file zigux/tests/phase8_exec_cmd_only_build.zig --summary all`
4. Run the focused convenience target: `make -C zigux phase8-exec-cmd-test`
5. Run the bundled Phase 8 tooling gate: `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

## Current Parity Surface
The current parked deferred-exec packet covers:
- absolute-versus-prefixed `system_path()` resolution
- `get_argv_exec_path()` precedence across explicit path, environment path, and configured fallback
- `extract_argv0_path()` splitting for directory-prefixed tool invocations
- injected `exec_cmd_init()` and `set_argv_exec_path()` environment propagation for `PREFIX` and the configured exec-path variable
- `setup_path()`-adjacent path assembly plus `PATH` environment updates via relative-to-cwd normalization
- a pure `choosePwdCwd()` helper for caller-provided same-location decisions plus identity-based `sameFileLocation()`, `samePathIdentity()`, `choosePwdCwdFromFileIdentity()`, and `choosePwdCwdFromIdentities()` helpers, with `setupPathWithPwd()` keeping the logical-`PWD` acceptance rule reviewable without widening into broader process or environment side effects
- `prepare_exec_cmd()`-style argv prefixing with a trailing null slot for later deferred `execv_cmd()`-style handoff planning, plus a pure `buildDeferredExecvCall()` helper that keeps that null-terminated argv packet reviewable before any direct launch ownership exists
- a pure `collectExeclArgs()` helper that models the `execl_cmd()` argument collector and its legacy `MAX_ARGS` guard, plus a pure `buildDeferredExeclCall()` helper that preserves the same deferred argv-handoff packet while the parked packet stops before any ownership of `execl_cmd()`

The current tests keep these bounded edges explicit:
- helper-local unit tests in `tools/lib/subcmd/exec-cmd.zig` own the low-level trailing-colon `PATH` edge and the rooted `argv[0]` slash-avoidance edge
- path fallback precedence stays stable
- relative search-path entries become absolute against the current working directory input
- empty inherited `PATH` values preserve the C helper's trailing-colon shape instead of silently falling back to default search roots
- directory-prefixed `argv[0]` values split cleanly into path and command name
- the injected environment wrapper keeps `PREFIX`, the configured exec-path environment key, and the resulting `PATH` value aligned
- the shared logical-`PWD` replay keeps the logical-`PWD` alias acceptance proof explicit while the identity-backed helper path accepts a same-device-and-inode alias to the same directory
- prepared argv vectors start with the configured executable name and keep a trailing null terminator, including the empty-tail case
- the pure deferred `execv` and `execl` handoff helpers keep the parked argv packet reviewable before any direct `execv_cmd()` or `execvp()` ownership exists
- the `collectExeclArgs()` overflow and missing-null guards stay reviewable before any direct varargs launch path exists
- the focused Phase 8 replay stays on the integrated deferred-exec packet and keeps the live C helper anchors, checklist hook, and validator route aligned before the broader tooling replay runs
- `make -C zigux phase8-exec-cmd-test` exposes that focused replay as a one-command route

## Non-Goals
This slice does not claim:
- direct `execvp()` parity, `execv_cmd()` ownership, or process-launch behavior
- any ownership of `execl_cmd()` or the direct varargs launch path
- direct OS environment reads or writes
- deferred queue ownership or scheduler-facing transport
- `kernel/workqueue.c` in the later Phase 14 boundary-study tranche
- the terminal/help listing surface from `tools/lib/subcmd/help.c`
- the larger Phase 8 anchors in `tools/lib/symbol/` or `tools/lib/bpf/`

## Next Bounded Step
Keep `tools/lib/subcmd/exec-cmd.zig` parked unless repo review specifically wants one more bounded parity step around another helper-only path-choice or argv-shape guard inside this file family. If the lane reopens on reviewability alone, keep it to one equally small update around the focused replay surface instead of widening into sibling Phase 8 anchors.
