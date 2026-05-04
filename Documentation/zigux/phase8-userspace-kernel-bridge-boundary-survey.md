# Phase 8 Userspace/Kernel Bridge Boundary Survey

This note records the current cross-slice boundary for Phase 8 userspace-adjacent tooling in Zigux.

## Status

- `PHASE8_STATUS=parked`
- `PHASE8_SLICE=userspace-kernel-bridge-boundary-survey`
- `surveyed_commit=897cdd2f62c4428d2a050275a187950e161b66eb`
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
  - `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
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

- `tools/lib/bpf/zigux_segments/cpu_mask.zig`, `tools/lib/bpf/zigux_segments/logging.zig`, and `tools/lib/bpf/zigux_segments/pin_path.zig` keep stable mask parsing, bounded version or errno reporting, and pure bpffs-style path shaping explicit without widening into sysfs reads, stderr emission, directory creation, or pinning side effects. The same cpu-mask helper packet also keeps the bounded perf-buffer auto-budget clamp, pure online-CPU eligibility checks, pure caller-pinned positive CPU planning, and pure auto-selected CPU planning from already-injected possible and online masks explicit without claiming `/sys` reads, epoll-backed registration, or interrupt-routing-sensitive behavior.
- `tools/lib/bpf/zigux_segments/type_names.zig` plus `zigux/tests/phase8_bpf_type_names.zig` keep the exported attach, link, map, and program type-name tables reviewable as stable lookup helpers without claiming object-model, loader, or handle-lifecycle parity
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` plus `zigux/tests/phase8_file_path_handle_bridge.zig` now claim `/proc/<pid>/fdinfo/<fd>` path construction, the current-process `getpid()` convenience wrapper, bounded fdinfo text parsing from `bpf_get_map_info_from_fdinfo()` including `map_extra`, the reused-map-name chooser from `bpf_map__reuse_fd()`, the bounded missing-pinned-map classifier through `classifyReusePinnedMapOpenFailure()`, the bounded token-acquisition result planner through `resolveTokenPreparationAcquisition()`, the bounded reuse-attempt result planner through `resolveReusePinnedMapAttempt()`, and the bounded map reuse compatibility comparison from `bpf_object__reuse_map()` that preserves the DEVMAP readonly-prog exception without claiming reopen or replacement side effects. The same helper-only packet now keeps `prepared` versus `cache_allocation_failed` token-acquisition outcomes plus the `should_close_token_fd`, `should_store_token_fd`, and `should_store_feat_cache_token_fd` ownership decisions reviewable without claiming live token creation, feature-cache allocation side effects, or reopened-handle behavior. It also keeps `reused`, `incompatible_map`, and `reuse_fd_failed` outcomes plus the `should_close_pin_fd` and `should_mark_map_pinned` ownership decisions reviewable without claiming live pinned-map reopen flow, replacement side effects, or FD duplication.
- `Documentation/zigux/phase8-libbpf-segment-survey.md` keeps the deferred `file-path-and-handle-bridge` boundary explicit around `bpf_object_prepare_token()`, `bpf_object__reuse_map()`, `bpf_obj_get()` reopen flows, and `open()` or `close()` ownership, even after the bounded `planTokenPreparation()` helper made the optional-versus-mandatory token-path intent reviewable, `classifyTokenPreparationFailure()` made the optional-fallback versus mandatory-fail split explicit, `classifyReusePinnedMapOpenFailure()` made missing pinned-map lookup versus hard open failure reviewable without claiming live handle creation, and `resolveReusePinnedMapAttempt()` made the bounded reuse result plus close-or-mark ownership planning reviewable without claiming live reopen or replacement side effects
- the same survey keeps the separate `perf-buffer-online-cpu-routing` boundary explicit around `/sys/devices/system/cpu/online` reads, cached `/sys/devices/system/cpu/possible` counts from `libbpf_num_possible_cpus()`, online CPU filtering, per-CPU perf-event-array map updates, epoll-backed perf FD registration, and timeout-driven `perf_buffer__poll(timeout_ms)` waits that return ready-buffer counts, so the landed helper-first rollout still does not claim direct `/proc/.../fdinfo` reads, `fopen()` or `fclose()` ownership, bpffs path opens, `bpf_token_create()` handle lifecycle parity, or interrupt-routing-sensitive perf-buffer behavior. The current helper-only packet stops at the pure auto-budget clamp, online-eligibility predicate, caller-pinned positive CPU planning, auto-selected CPU planning from already-injected possible and online masks, `prepared`, `cache_allocation_failed`, `skip_missing_pinned_map`, `skip_optional_missing_delegation`, `skip_optional`, mandatory `fail`, and bounded `reused` or `incompatible_map` or `reuse_fd_failed` planning, plus the explicit token `close`-or-`store` ownership decisions, instead of claiming the live open or token-creation side effects themselves, and it still keeps `bpf_obj_get()` reopen flows plus FD duplication or replacement behavior outside the current bridge packet. Phase 8 still ships no standalone timer helper and no standalone clockevent helper for this broader poll-adjacent path. The bounded `Documentation/zigux/phase8-perf-buffer-poll-slice.md` packet through `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig` and `zigux/tests/phase8_perf_buffer_poll.zig` now covers wait-result classification, ready-buffer bookkeeping, and the ordered `perf_buffer__process_records()` fail-fast summary including the cumulative processed-record count returned before the first failing ready buffer only, so it does not close the broader routing boundary or claim direct `epoll_wait()` parity, timer or clockevent parity, or interrupt-routing-sensitive delivery behavior.

## Roadmap gap snapshot

The current bridge packet now matches the roadmap shape, but it still leaves a bounded delivery gap in each named Phase 8 destination:

- `tools/lib/subcmd/*.zig`: the repo now has the helper-first foothold through `exec-cmd.zig` and `help.zig`, but the remaining roadmap gap is still direct process-launch and command-discovery side effects such as `execvp()`, environment reads or writes, `opendir()`, `readdir()`, and raw `ioctl()` terminal probing
- `tools/lib/symbol/*.zig`: the repo now has the parser-first foothold through `kallsyms.zig`, but the remaining roadmap gap is still broader `api/io.h` parity and downstream ELF-emission behavior
- `tools/lib/bpf/zigux_segments/`: the repo now meets the segmented-plan requirement through helper-first starter slices plus the bounded perf-buffer poll adjunct, but the remaining roadmap gap is still direct `/proc/.../fdinfo` reads, `open()` or `close()` ownership, `bpf_obj_get()` reopen flows, `bpf_token_create()` handle lifecycle parity, `perf-buffer-online-cpu-routing`, and the blocked object-model or ELF-loader follow-ons
- `output-stable tooling behavior`: the repo currently proves this only for helper-local command formatting and reviewable wait-result summaries, so it still does not claim live command execution, full directory-backed command discovery, or broader libbpf runtime output behavior

## Tooling lane sequencing

- `exec-cmd`, `help`, and `kallsyms` remain packet-local tooling lanes. Their next follow-up should stay inside the owning helper, focused Phase 8 test, slice note, and directly coupled checklist wording instead of reopening the shared bridge packet to repeat helper-local evidence.
- `Documentation/zigux/phase8-libbpf-segment-survey.md` plus `tools/lib/bpf/zigux_segments/manifest.json` remain the owning packet for the eleven-segment libbpf catalog and the six landed helper-first starter slices. This bridge note may reference that catalog, but it should not retag segment ownership, restate catalog counts as new progress, or absorb helper-local gate details that belong to the survey packet.
- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, and `zigux/tests/phase8_perf_buffer_poll_only_build.zig` own the bounded wait-result and ready-buffer bookkeeping adjunct. This shared bridge packet only names that helper as a neighboring boundary and must not treat it as closure for the broader `perf-buffer-online-cpu-routing` segment.
- the shared bridge packet owns only the cross-lane deferral wording: direct process launch, directory and terminal probes, `/proc/.../fdinfo` reads, bpffs handle lifecycle, and interrupt-routing-sensitive perf-buffer behavior. If one of those boundaries moves, refresh this note and the directly coupled shared Phase 8 survey gates without duplicating helper-local test growth across the packet-local tooling lanes.

## Review gate

The shared review path still follows the same validator-first Phase 8 sequence that current `master` publishes through `zigux/Makefile`: the broader validator self-test runs first, the dedicated validator-route audit plus the dedicated tests-readme alignment checker and the dedicated perf-buffer poll gate checker each keep their self-test and live pass inside the same fail-closed packet, and only then do the focused survey, focused perf-buffer poll shard, and shared build replays run, so this cross-slice boundary note stays tied to the same docs-root, tests-root, Makefile, workflow, and segmented libbpf packet that current `master` already ships.

1. `python3 scripts/zigux/validate-phase8.py --self-test`
2. `python3 scripts/zigux/check-phase8-validator-flow.py --self-test`
3. `python3 scripts/zigux/check-phase8-tests-readme-alignment.py --self-test`
4. `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py --self-test`
5. `python3 scripts/zigux/validate-phase8.py`
6. `python3 scripts/zigux/check-phase8-validator-flow.py`
7. `python3 scripts/zigux/check-phase8-tests-readme-alignment.py`
8. `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
9. `make -C zigux phase8-validate`
10. `zig test zigux/tests/phase8_libbpf_segments.zig`
11. `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`
12. `make -C zigux phase8-perf-buffer-poll-test`
13. `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`
14. `zig build test --build-file zigux/tests/phase8_build.zig --summary all`

`scripts/zigux/check-phase8-validator-flow.py` now stays inside that same published wrapper path instead of sitting beside it, and it currently publishes `PHASE8_VALIDATOR_FLOW_SELF_TEST_CASE_COUNT=15`.

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

Keep this shared bridge packet parked unless repo reality changes one of the shared deferred boundaries or exposes a real cross-lane overlap risk inside the current Phase 8 tooling packet. The next honest move should refresh this note plus the directly coupled shared survey gates, not reopen helper-local `exec-cmd`, `help`, `kallsyms`, or libbpf catalog packets just to restate already-landed evidence.
