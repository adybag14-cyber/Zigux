# Phase 8 Userspace/Kernel Bridge Boundary Survey

This note records the current cross-slice boundary for Phase 8 userspace-adjacent tooling in Zigux.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=userspace-kernel-bridge-boundary-survey`
- scope: parked command-preparation helpers under `tools/lib/subcmd/*.zig` plus the helper-first libbpf starter slices under `tools/lib/bpf/zigux_segments/`, with direct process-launch, directory, terminal, procfs, bpffs, and handle-lifecycle behavior still deferred
- product boundary:
  - `Documentation/zigux/phase8-exec-cmd-slice.md`
  - `Documentation/zigux/phase8-help-slice.md`
  - `Documentation/zigux/phase8-libbpf-segment-survey.md`
  - `tools/lib/subcmd/exec-cmd.zig`
  - `tools/lib/subcmd/help.zig`
  - `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
  - `zigux/tests/phase8_build.zig`

## Why this note exists

The Phase 8 roadmap names both `tools/lib/subcmd/*.zig` and `tools/lib/bpf/zigux_segments/` as the bounded Zigux footholds for serious repo-hosted tooling. The repo already had slice-local notes for `exec-cmd`, `help`, and the helper-first libbpf rollout, but it did not yet have one reviewable survey that states the current shared boundary between landed command-preparation helpers and the still-deferred syscall or handle-facing behavior.

This survey closes that documentation gap without widening the implementation surface. It keeps the command side and the libbpf side in one place so reviewers can see exactly which userspace/kernel bridge behavior is already claimed and which behavior is still intentionally outside the current Phase 8 packet.

## Current boundary

The current parked command boundary is helper-only:

- `tools/lib/subcmd/exec-cmd.zig` covers path-resolution, injected environment setup, cwd-choice modeling, null-terminated argv preparation, and pure `execl_cmd()`-style argument collection
- `tools/lib/subcmd/help.zig` covers owned command-name handling, injected command-source filtering, raw `PATH` splitting, injected terminal-dimensions resolution, and pure section-render planning or emission
- the current command packet does not claim direct `execvp()` parity, direct environment reads or writes, `opendir()` or `readdir()` parity, or direct `ioctl()`-backed terminal probing

The current libbpf bridge packet is also helper-first:

- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` only claims `/proc/<pid>/fdinfo/<fd>` path construction plus bounded fdinfo text parsing from `bpf_get_map_info_from_fdinfo()`
- `Documentation/zigux/phase8-libbpf-segment-survey.md` keeps the deferred `file-path-and-handle-bridge` boundary explicit around `bpf_object_prepare_token()`, `bpf_object__reuse_map()`, `bpf_obj_get()` reopen flows, and `open()` or `close()` ownership
- the same survey keeps the separate perf-buffer routing boundary explicit, so the landed helper-first rollout still does not claim direct `/proc/.../fdinfo` reads, `fopen()` or `fclose()` ownership, bpffs path opens, `bpf_token_create()` handle lifecycle parity, or interrupt-routing-sensitive perf-buffer behavior

## Review gate

Keep this survey aligned with:

1. `python3 scripts/zigux/validate-phase8.py`
2. `make -C zigux phase8-validate`
3. `zig build test --build-file zigux/tests/phase8_build.zig`

## Non-goals

This survey does not reopen or claim:

- direct `execvp()` or other process-launch side effects
- direct environment inspection or mutation beyond injected helper inputs
- direct `opendir()`, `readdir()`, or `ioctl()` parity
- direct `/proc/.../fdinfo` reads
- direct `fopen()` or `fclose()` ownership
- direct `open()` or `close()` ownership
- `bpf_obj_get()` reopen flows
- `bpf_token_create()` handle lifecycle parity
- object-model, ELF-loader, or perf-buffer runtime parity

## Next bounded step

Keep the current Phase 8 bridge packet parked unless repo reality exposes one more helper-first tooling slice that stays smaller than the existing deferred command or handle boundaries. If this note reopens, the next honest move should still be survey or validator precision around those explicit boundaries rather than widening into direct syscall-backed or process-launch behavior.