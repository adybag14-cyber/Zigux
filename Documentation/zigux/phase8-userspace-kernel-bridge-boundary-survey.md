# Phase 8 Userspace/Kernel Bridge Boundary Survey

This note records the current cross-slice boundary for Phase 8 userspace-adjacent tooling in Zigux.

## Status

- `PHASE8_STATUS=active`
- `PHASE8_SLICE=userspace-kernel-bridge-boundary-survey`
- `surveyed_commit=f5a4d6990f701937b2a3bb9ae723bb6d0f27ba21`
- scope: parked command-preparation helpers under `tools/lib/subcmd/*.zig`, the bounded symbol-side parser helper under `tools/lib/symbol/*.zig`, the helper-first libbpf starter slices under `tools/lib/bpf/zigux_segments/`, and the bounded perf-buffer poll bookkeeping helper, with direct process-launch, directory, terminal, procfs, bpffs, handle-lifecycle, interrupt-routing-sensitive behavior, and downstream ELF-emission work still deferred
- product boundary:
  - `Documentation/zigux/phase8-exec-cmd-slice.md`
  - `Documentation/zigux/phase8-help-slice.md`
  - `Documentation/zigux/phase8-kallsyms-slice.md`
  - `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`
  - `Documentation/zigux/phase8-bpf-type-names-slice.md`
  - `Documentation/zigux/phase8-libbpf-segment-survey.md`
  - `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
  - `tools/lib/subcmd/exec-cmd.zig`
  - `tools/lib/subcmd/help.zig`
  - `tools/lib/symbol/kallsyms.zig`
  - `tools/lib/bpf/zigux_segments/cpu_mask.zig`
  - `tools/lib/bpf/zigux_segments/logging.zig`
  - `tools/lib/bpf/zigux_segments/pin_path.zig`
  - `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
  - `tools/lib/bpf/zigux_segments/type_names.zig`
  - `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
  - `zigux/tests/phase8_cpu_mask.zig`
  - `zigux/tests/phase8_logging.zig`
  - `zigux/tests/phase8_pin_path.zig`
  - `zigux/tests/phase8_file_path_handle_bridge.zig`
  - `zigux/tests/phase8_bpf_type_names.zig`
  - `zigux/tests/phase8_kallsyms.zig`
  - `zigux/tests/phase8_bridge_boundary_survey.zig`
  - `zigux/tests/phase8_libbpf_segments.zig`
  - `zigux/tests/phase8_libbpf_segments_only_build.zig`
  - `zigux/tests/phase8_perf_buffer_poll.zig`
  - `zigux/tests/phase8_build.zig`

## Why this note exists

The Phase 8 roadmap names `tools/lib/subcmd/*.zig`, `tools/lib/symbol/*.zig`, and `tools/lib/bpf/zigux_segments/` as the bounded Zigux footholds for serious repo-hosted tooling. The repo already had slice-local notes for `exec-cmd`, `help`, `kallsyms`, and the helper-first libbpf rollout, but it did not yet have one reviewable survey that states the current shared boundary between landed helper packets and the still-deferred syscall, handle-facing, and downstream-emission behavior.

This survey closes that documentation gap without widening the implementation surface. It keeps the command side, symbol side, and libbpf side in one place so reviewers can see exactly which userspace/kernel bridge behavior is already claimed and which behavior is still intentionally outside the current Phase 8 packet.

## Current boundary

The current parked subcommand and symbol boundary is helper-only:

- `tools/lib/subcmd/exec-cmd.zig` covers path-resolution, injected environment setup, cwd-choice modeling through `choosePwdCwdFromIdentities()` and `setupPathWithPwd()`, null-terminated argv preparation through `collectExeclArgs()`, pure `execv_cmd()`-style future handoff packaging through `buildDeferredExecvCall()`, the combined launch-free PATH-plus-argv planning wrapper through `planDeferredExecvCall()`, and pure `execl_cmd()`-style argument collection plus deferred future handoff carriers through `buildDeferredExeclCall()`
- `tools/lib/subcmd/help.zig` covers owned command-name handling, injected command-source filtering through `loadCommandListsFromEnvPath()`, raw `PATH` splitting, injected terminal-dimensions resolution through `resolveTerminalDimensions()`, and pure section-render planning or emission through `writeCommandSectionsForTerminal()`
- `tools/lib/symbol/kallsyms.zig` covers bounded `kallsyms__parse()`-style callback wrapping, line parsing, chunked overlong-line discard-after-boundary handling, and pure contents, reader, path, and in-directory adapters without claiming broader `api/io.h` parity or downstream ELF-emission behavior
- the current command-and-symbol packet does not claim direct `execvp()` parity, direct environment reads or writes, `opendir()` or `readdir()` parity, direct `ioctl()`-backed terminal probing, queue ownership, scheduler-facing transport behavior, any handoff into `kernel/workqueue.c`, which remains a separate Phase 14 boundary-study target, broader `api/io.h` parity, or downstream ELF-emission behavior

The current libbpf bridge packet is also helper-first:

- `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, and `tools/lib/bpf/zigux_segments/pin_path.zig` keep stable mask parsing, bounded version or errno reporting, and pure bpffs-style path shaping explicit without widening into sysfs reads, stderr emission, directory creation, or pinning side effects
- `tools/lib/bpf/zigux_segments/type_names.zig` plus `zigux/tests/phase8_bpf_type_names.zig` keep the exported attach, link, map, and program type-name tables reviewable as stable lookup helpers without claiming object-model, loader, or handle-lifecycle parity
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` plus `zigux/tests/phase8_file_path_handle_bridge.zig` now claim `/proc/<pid>/fdinfo/<fd>` path construction, the current-process `getpid()` convenience wrapper, bounded fdinfo text parsing from `bpf_get_map_info_from_fdinfo()` including `map_extra`, the reused-map-name chooser from `bpf_map__reuse_fd()`, the bounded missing-pinned-map classifier through `classifyReusePinnedMapOpenFailure()`, and the bounded map reuse compatibility comparison from `bpf_object__reuse_map()` that preserves the DEVMAP readonly-prog exception without claiming reopen or replacement side effects
- `Documentation/zigux/phase8-libbpf-segment-survey.md` keeps the deferred `file-path-and-handle-bridge` boundary explicit around `bpf_object_prepare_token()`, `bpf_object__reuse_map()`, `bpf_obj_get()` reopen flows, and `open()` or `close()` ownership, even after the bounded `planTokenPreparation()` helper made the optional-versus-mandatory token-path intent reviewable, `classifyTokenPreparationFailure()` made the optional-fallback versus mandatory-fail split explicit, and `classifyReusePinnedMapOpenFailure()` made missing pinned-map lookup versus hard open failure reviewable without claiming live handle creation
- the same survey keeps the separate `perf-buffer-online-cpu-routing` boundary explicit around `/sys/devices/system/cpu/online` reads, cached `/sys/devices/system/cpu/possible` counts from `libbpf_num_possible_cpus()`, online CPU filtering, per-CPU perf-event-array map updates, epoll-backed perf FD registration, and timeout-driven `perf_buffer__poll(timeout_ms)` waits that return ready-buffer counts, so the landed helper-first rollout still does not claim direct `/proc/.../fdinfo` reads, `fopen()` or `fclose()` ownership, bpffs path opens, `bpf_token_create()` handle lifecycle parity, or interrupt-routing-sensitive perf-buffer behavior. The current helper-only packet stops at `skip_missing_pinned_map`, `skip_optional_missing_delegation`, `skip_optional`, and mandatory `fail` planning instead of claiming the live open or token-creation side effects themselves, and it still keeps `bpf_obj_get()` reopen flows plus FD duplication or replacement behavior outside the current bridge packet. Phase 8 still ships no standalone timer helper and no standalone clockevent helper for this broader poll-adjacent path. The bounded `Documentation/zigux/phase8-perf-buffer-poll-slice.md` packet through `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` and `zigux/tests/phase8_perf_buffer_poll.zig` now covers wait-result classification and ready-buffer bookkeeping only, so it does not close the broader routing boundary or claim direct `epoll_wait()` parity, timer or clockevent parity, or interrupt-routing-sensitive delivery behavior.

## Review gate

The shared review path now follows the same validator-first Phase 8 sequence that current `master` publishes through `zigux/Makefile`: the broader validator self-test still runs first, the dedicated tests-readme alignment checker and its self-test stay in the same fail-closed packet, and only then do the focused survey and shared build replays run, so this cross-slice boundary note stays tied to the same docs-root, tests-root, Makefile, workflow, and segmented libbpf packet that current `master` already ships.

1. `python3 scripts/zigux/validate-phase8.py --self-test`
2. `python3 scripts/zigux/check-phase8-tests-readme-alignment.py --self-test`
3. `python3 scripts/zigux/validate-phase8.py`
4. `python3 scripts/zigux/check-phase8-tests-readme-alignment.py`
5. `make -C zigux phase8-validate`
6. `zig test zigux/tests/phase8_libbpf_segments.zig`
7. `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`
8. `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

## Non-goals

This survey does not reopen or claim:

- direct `execvp()` or other process-launch side effects
- direct environment inspection or mutation beyond injected helper inputs
- direct `opendir()`, `readdir()`, or `ioctl()` parity
- broader `api/io.h` parity or downstream ELF-emission behavior
- direct `/proc/.../fdinfo` reads
- direct `fopen()` or `fclose()` ownership
- direct `open()` or `close()` ownership
- `bpf_obj_get()` reopen flows
- `bpf_token_create()` handle lifecycle parity
- live token-creation side effects beyond the helper-only `classifyTokenPreparationFailure()` decision model
- direct `/sys/devices/system/cpu/online` reads or cached `libbpf_num_possible_cpus()` parity
- direct per-CPU perf-event-array updates or epoll-backed perf FD registration
- direct `epoll_wait()` parity or broader `perf_buffer__poll(timeout_ms)` routing-loop timeout behavior
- any standalone timer helper or standalone clockevent helper for perf-buffer polling
- object-model, ELF-loader, or perf-buffer runtime parity
- queue ownership, scheduler-facing transport behavior, or any `kernel/workqueue.c` handoff claim

## Next bounded step

Keep the current Phase 8 bridge packet parked unless repo reality exposes one more helper-first tooling slice that stays smaller than the existing deferred command or handle boundaries. If this note reopens, the next honest move should still be survey or validator precision around those explicit boundaries rather than widening into direct syscall-backed, parser-emission, or process-launch behavior.