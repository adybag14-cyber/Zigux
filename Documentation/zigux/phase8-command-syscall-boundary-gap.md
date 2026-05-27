# Phase 8 Command And Syscall Boundary Gap

This note records the current Phase 8 command-side gap against the roadmap for userspace-adjacent tooling.

## Status

- `PHASE8_COMMAND_SYSCALL_GAP=userspace-adjacent-tooling`
- `PHASE8_COMMAND_PACKET=exec-cmd-helper-first`
- `PHASE8_COMMAND_SYSCALL_STATUS=gap-recorded`

## Roadmap Anchors

Phase 8 in the roadmap still names these userspace-adjacent tooling anchors:

- `tools/lib/subcmd/exec-cmd.c`
- `tools/lib/subcmd/help.c`
- `tools/lib/symbol/kallsyms.c`
- `tools/lib/bpf/libbpf.c`

That roadmap scope makes the command boundary narrower than a general runtime or kernel execution substrate. The Phase 8 question here is whether Zigux has a truthful helper-first command-side foothold, not whether it owns live process launch or a broader syscall-backed execution service.

## Current Repo Reality

Current `master` already carries a bounded command-side packet through:

- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `scripts/zigux/check-phase8-exec-cmd-packet.py`
- `scripts/zigux/validate-phase8.py`
- `tools/lib/subcmd/exec-cmd.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `zigux/tests/phase8_build.zig`
- `make -C zigux phase8-exec-cmd-test`

That landed packet proves a helper-first command foothold. The current `exec-cmd` slice covers path shaping, environment propagation, `get_pwd_cwd()`-style cwd choice, argv preparation, and deferred `execv_cmd()` / `execl_cmd()` carriers without widening into direct process launch.

The sibling `help` and `kallsyms` Phase 8 anchors remain separate tooling packets, and the userspace/kernel bridge note under `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` remains the libbpf-side control-boundary packet. Those neighboring surfaces should stay visible, but they do not close the command-side syscall gap by themselves.

## Gap Versus The Roadmap

Against the roadmap, Zigux still does not materialize a live command-execution boundary.

The current gap stays explicit:

- no direct `execvp()` parity
- no child launch
- no exit-status collection
- no process waiting
- no retry scheduling, timeout handling, or poll-loop ownership around deferred execution
- no syscall-backed runtime command boundary beyond helper-local deferred carriers
- no queue ownership, worker-pool control, or scheduler-visible execution substrate

That gap matters because the current packet is intentionally reviewable and side-effect free. It demonstrates the command preparation boundary inside repo-hosted tooling, but it does not yet claim live syscall ownership or a broader execution runtime.

## Lane Guardrail

Follow-up in this lane should stay limited to command-boundary truthfulness work around the existing `exec-cmd` packet, this gap note, or a similarly bounded checker surface.

Do not treat this note as proof that:

- Phase 8 already owns live command execution
- Phase 8 already owns a generic syscall bridge
- `kernel/workqueue.c` or any later runtime substrate has moved into active delivery

## Next Bounded Step

The next honest same-lane step is to keep this note aligned with the live `exec-cmd` helper-first packet and the broader Phase 8 reminder surfaces, without widening into helper semantics or shared validator ownership unless the command-side packet itself changes.
