# Phase 8 Userspace-Kernel Bridge Boundary Survey
## Status
- `PHASE8_USERSPACE_KERNEL_BRIDGE_STATUS=parked_gap_packet_landed`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_LANE_KEY=P8-L01`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_ROADMAP_PHASE=Phase 8`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_SCOPE=shared-command-environment-and-libbpf-bridge-boundary-review`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_C_ANCHORS=tools/lib/subcmd/exec-cmd.c;tools/lib/subcmd/help.c;tools/lib/symbol/kallsyms.c;tools/lib/bpf/libbpf.c`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_SHARED_NOTE=Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_VALIDATION_ENTRYPOINT=python3 scripts/zigux/validate-phase8.py`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_LINUX_STYLE_VALIDATION=make -C zigux phase8-validate`
## Purpose
This parked Phase 8 gap note keeps the roadmap-backed command and environment control surface reviewable without pretending that the current Zigux packet has closed direct process-launch, live environment-read, or terminal-probing parity.
The same shared boundary survey also keeps the landed helper-local file, path, and handle bridge packet plus the still-parked broader bridge boundary explicit without pretending that the current Zigux packet has closed token materialization or capability handoff, map reopen or bpffs compatibility closure, or fd close or ownership semantics.
Within the full Phase 8 anchor list, this note stays deliberately narrower than the dedicated symbol lane: it keeps the command, environment, and libbpf resource-boundary surfaces reviewable while the parser-local `kallsyms` packet remains owned by `Documentation/zigux/phase8-kallsyms-slice.md` and the shared Phase 8 sequencing note instead of being retold here as a command or bridge owner.

The note is intentionally narrow:
- keep the roadmap anchors explicit
- keep the parked current-tree command and help packet explicit
- keep the landed helper-local file-path-and-handle bridge packet and the still-parked broader bridge boundary explicit
- keep the landed bounded perf-buffer poll helper packet explicit
- keep the shared Phase 8 lane note and validation entrypoint explicit
- keep the next bounded follow-through step explicit until later Phase 8 work lands a smaller truthfulness or replay update inside the same command or bridge packet
## Current Measurable Status
Current public default-branch tree readback shows the parked command and help packet still exposes:
- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `Documentation/zigux/phase8-help-slice.md`
- `tools/lib/subcmd/exec-cmd.zig`
- `tools/lib/subcmd/help.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `zigux/tests/phase8_help.zig`
- `zigux/tests/phase8_help_only_build.zig`
The bounded evidence packet for that parked command surface remains:
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
- `Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `python3 scripts/zigux/validate-phase8.py`
- `make -C zigux phase8-validate`
The same shared Phase 8 boundary packet also keeps the landed helper-local file, path, and handle bridge packet, the landed helper-plus-build libbpf compile packet, the still-parked broader bridge boundary, and the already-landed bounded perf-buffer poll helper reviewable through:
- `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
- `tools/lib/bpf/zigux_segments/verify.zig`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
- `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`
- `zigux/tests/phase8_file_path_handle_bridge.zig`
- `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
- `zigux/tests/phase8_libbpf_segments.zig`
- `zigux/tests/phase8_libbpf_segments_only_build.zig`
- `zigux/tests/phase8_perf_buffer_poll.zig`
- `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
- `make -C zigux phase8-file-path-handle-bridge-test`
- `zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all`
- `make -C zigux phase8-libbpf-segments-test`
- `zig build test --build-file zigux/tests/phase8_libbpf_segments_only_build.zig --summary all`
- `make -C zigux phase8-perf-buffer-poll-test`
- `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`
- `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
- `python3 scripts/zigux/validate-phase8.py --self-test`
- `python3 scripts/zigux/validate-phase8.py`
Current 2026-05-22 authenticated contents readback from this environment still keeps that broader bridge-plus-build packet mixed rather than uniformly stable: `tools/lib/bpf/zigux_segments/verify.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, and `zigux/tests/phase8_build.zig` now read cleanly, while `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` and `zigux/tests/phase8_file_path_handle_bridge_only_build.zig` still return `404` through the same contents route.
The documented public default-branch blob and raw fallback nevertheless keeps those two remaining paths reviewable on current `master`, so the packet is still mixed-source rather than absent.
Current 2026-05-16 authenticated contents readback also keeps the smaller interrupt-routing-adjacent helper packet directly readable: `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` now reads cleanly through the same contents route, so the lane should keep that helper-local cursor and routing-summary evidence explicit instead of collapsing everything under the broader deferred setup-side boundary.
That same-lane bridge packet now has a landed helper-local core while the broader file-path-and-handle resource boundary stays parked: it names `mapReuseObservationFromFdinfo()`, `resolveReusePinnedMapAttempt()`, and `planTokenPreparation()` as a planning-only gate around a non-empty pinned path plus compatible fdinfo-derived map info and a non-empty token path plus a ready reused-map bridge plan.
The same shared note also keeps the already-landed `perf-buffer-poll-bookkeeping` packet explicit through the dedicated `scripts/zigux/check-phase8-perf-buffer-poll-gate.py` review gate and as a smaller helper-adjacent review surface around observed wait-result normalization, ready-buffer bookkeeping, bounded buffer-slot lookup, and ordered record-processing summaries rather than broader routing or event-loop ownership.
Current `master` also keeps a smaller helper-local online CPU cursor and routing-summary packet explicit through `tools/lib/bpf/zigux_segments/online_cpu_routing.zig`, where `advanceOnlineCpuCursor()`, `summarizeNextOnlineCpuRoute()`, and `summarizeOnlineCpuRouting()` stay reviewable below the deferred setup-side `perf-buffer-online-cpu-routing` packet.
Current `master` also keeps the helper-plus-build libbpf compile packet explicit through `tools/lib/bpf/zigux_segments/verify.zig`, where the combined segment proof still imports `logging.zig`, `pin_path.zig`, `cpu_mask.zig`, `type_names.zig`, `file_path_handle_bridge.zig`, `perf_buffer_poll.zig`, and `online_cpu_routing.zig`, and through `zigux/tests/phase8_libbpf_segments.zig` plus `zigux/tests/phase8_libbpf_segments_only_build.zig`, where the dedicated survey and focused build shard keep that manifest-backed helper bundle reviewable without widening into the deferred resource-boundary or interrupt-routing setup paths.
That packet still does not claim token materialization or capability handoff, map reopen or bpffs compatibility closure, or fd close or ownership semantics.
It also does not claim the deferred `perf-buffer-online-cpu-routing` packet, including `/sys/devices/system/cpu/online`, cached `/sys/devices/system/cpu/possible` counts via `libbpf_num_possible_cpus()`, online CPU filtering, per-CPU perf-event-array map updates, per-CPU `perf_event_open()` setup, perf-buffer ring `mmap()` setup, `PERF_EVENT_IOC_ENABLE` enablement, epoll-backed perf FD registration, or poll waits.
It likewise does not claim standalone timer helper behavior or standalone clockevent helper behavior. Authenticated contents reads for some Phase 8 files are inconsistent from this environment, so current public default-branch tree evidence and readable blob content should win over older absent-file assumptions.
Current 2026-05-16 authenticated readback closes the older focused exec-cmd replay split:
- `Documentation/zigux/phase8-exec-cmd-slice.md`, `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig` now read cleanly through the authenticated contents route
- the remaining Phase 8 readback instability in this area belongs to the neighboring bridge helper/build shard instead: `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` and `zigux/tests/phase8_file_path_handle_bridge_only_build.zig` still do not read uniformly through the same route
Treat that current state as a control-surface truthfulness improvement, not as a roadmap closure claim: the direct exec-cmd shard is readable again on current `master`, but the packet still only covers the parked command and environment planning surface and still does not claim direct `execvp()` parity, direct process-launch ownership, live OS environment reads, or direct terminal probing.
## Roadmap Gap
The product roadmap still names Phase 8 as the first tooling-expansion tranche for:
- `tools/lib/subcmd/exec-cmd.c`
- `tools/lib/subcmd/help.c`
- `tools/lib/symbol/kallsyms.c`
- `tools/lib/bpf/libbpf.c`
This boundary survey remains narrower than that full phase inventory: it keeps the command, environment, and libbpf bridge surfaces honest while the parser-local `kallsyms` reminder, compile, and packet-truthfulness work stays owned by the dedicated symbol lane.
Current `master` still preserves the parked command-and-help reminder packet, and it also preserves the landed helper-local file-path-and-handle bridge packet plus the still-parked broader file-path-and-handle resource boundary. Even so, the same packet still stops short of full process-launch, environment-plumbing, terminal-probing, token handoff, and reopened-handle closure behavior.
This note should therefore remain the truthful bridge between the roadmap target and the bounded current-tree evidence: the direct exec-cmd shard now reads cleanly through authenticated contents readback on current `master`, while the broader neighboring file-path bridge packet still needs mixed-source review evidence from this environment because authenticated contents reads for the helper and focused bridge build shard still return `404`, even though the documented public default-branch blob and raw fallback keeps those exact paths reviewable on current `master`.
The same survey must also keep the directly readable helper-local `online_cpu_routing.zig` cursor and routing-summary packet plus the dedicated `verify.zig` and `phase8_libbpf_segments` helper-plus-build control-plane packet explicit while leaving `/sys` reads, `perf_event_open()` setup, `mmap()`-backed ring ownership, epoll registration, and poll waits inside the deferred setup-side interrupt-routing boundary.
## Next Bounded Step
If a later Phase 8 lane changes any of the parked command-lane, help-lane, file-path-and-handle bridge, helper-plus-build libbpf compile packet, or bounded perf-buffer poll files, re-read this note together with `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `tools/lib/bpf/zigux_segments/verify.zig`, `python3 scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `python3 scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, `scripts/zigux/README.md`, `zigux/Makefile`, and the current Phase 8 test tree before widening broader Phase 8 summaries.
The next honest follow-through inside this packet is to keep the shared Phase 8 wording aligned with that narrower current split: the direct exec-cmd shard now reads cleanly through authenticated contents readback, while `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig` and `zigux/tests/phase8_file_path_handle_bridge_only_build.zig` still keep the neighboring bridge shard on mixed-source evidence from this environment because authenticated contents readback still returns `404` for those exact paths even while the documented public default-branch blob and raw fallback keeps them reviewable on current `master`.
`tools/lib/bpf/zigux_segments/verify.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_libbpf_segments_only_build.zig` now read cleanly again, and `tools/lib/bpf/zigux_segments/online_cpu_routing.zig` also reads cleanly as the smaller helper-local routing packet, so follow-up should keep that bounded compile, bridge, and cursor-summary evidence explicit without widening into `/sys` reads, `perf_event_open()` setup, `mmap()`-backed ring ownership, epoll registration, or poll waits.
Current `master` also shows that `Documentation/zigux/README.md` and `Documentation/zigux/review-checklist.md` already carry the refreshed shared-wording readback, so those two shared reminder surfaces are no longer the first reopen cues inside this boundary packet.
If the shared wording lane reopens again, start with `scripts/zigux/README.md`, `zigux/tests/README.md`, or `zigux/Makefile`, and re-read them against `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, and the current Phase 8 test tree before widening into helper-local or validator-local follow-through.
Until then, keep this survey parked and keep follow-up inside one bounded shared-wording, command-packet, bridge-summary, or replay step rather than widening into broader tooling-tranche restatement.
