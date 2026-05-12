# Phase 8 Userspace-Kernel Bridge Boundary Survey

## Status
- `PHASE8_USERSPACE_KERNEL_BRIDGE_STATUS=parked_gap_packet_landed`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_LANE_KEY=P8-L01`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_ROADMAP_PHASE=Phase 8`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_SCOPE=runtime-command-and-environment-plumbing`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_C_ANCHORS=tools/lib/subcmd/exec-cmd.c;tools/lib/subcmd/help.c`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_SHARED_NOTE=Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_VALIDATION_ENTRYPOINT=python3 scripts/zigux/validate-phase8.py`
- `PHASE8_USERSPACE_KERNEL_BRIDGE_LINUX_STYLE_VALIDATION=make -C zigux phase8-validate`

## Purpose

This parked Phase 8 gap note keeps the roadmap-backed command and environment
control surface reviewable without pretending that the current Zigux packet has
closed direct process-launch, live environment-read, or terminal-probing parity.

The same shared boundary survey also keeps the already-landed file, path, and
handle bridge packet reviewable without pretending that the current Zigux packet
has closed token materialization or capability handoff, map reopen or bpffs
compatibility closure, or fd close or ownership semantics.

The note is intentionally narrow:
- keep the roadmap anchors explicit
- keep the parked current-tree command and help packet explicit
- keep the already-landed file-path-and-handle bridge packet explicit
- keep the shared Phase 8 lane note and validation entrypoint explicit
- keep the next bounded follow-through step explicit until later Phase 8 work lands
  a smaller truthfulness or replay update inside the same command or bridge packet

## Current Measurable Status

Current public default-branch tree readback shows the parked command and help
packet still exposes:
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

The same shared Phase 8 boundary packet also keeps the queued file, path, and
handle bridge work reviewable through:
- `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
- `zigux/tests/phase8_file_path_handle_bridge.zig`
- `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
- `make -C zigux phase8-file-path-handle-bridge-test`
- `zig build test --build-file zigux/tests/phase8_file_path_handle_bridge_only_build.zig --summary all`
- `make -C zigux phase8-perf-buffer-poll-test`
- `zig build test --build-file zigux/tests/phase8_perf_buffer_poll_only_build.zig --summary all`
- `python3 scripts/zigux/validate-phase8.py --self-test`
- `python3 scripts/zigux/validate-phase8.py`

That queued bridge packet stays helper-first and planning-only: it names
`mapReuseObservationFromFdinfo()`, `resolveReusePinnedMapAttempt()`, and
`planTokenPreparation()` as a planning-only gate around a non-empty pinned path
plus compatible fdinfo-derived map info and a non-empty token path plus a ready
reused-map bridge plan.

That packet still does not claim token materialization or capability handoff,
map reopen or bpffs compatibility closure, or fd close or ownership semantics.
It also does not claim the deferred `perf-buffer-online-cpu-routing` packet,
including `/sys/devices/system/cpu/online`, cached `/sys/devices/system/cpu/possible`
counts via `libbpf_num_possible_cpus()`, online CPU filtering, per-CPU perf-event-array
map updates, per-CPU `perf_event_open()` setup, perf-buffer ring `mmap()` setup,
`PERF_EVENT_IOC_ENABLE` enablement, epoll-backed perf FD registration, or poll waits.

Authenticated contents reads for some Phase 8 files are inconsistent from this
environment, so current public default-branch tree evidence and readable blob
content should win over older absent-file assumptions.

Current authenticated 2026-05-12 contents readback now shows that inconsistency
more sharply for the command packet itself:
- `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-tooling-lane-sequencing.md`,
  and `zigux/tests/phase8_help.zig` remain readable
- `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and
  `zigux/tests/phase8_exec_cmd_only_build.zig` currently return `404` through the
  same contents route

Treat that split as the current truthful control-surface posture: the roadmap-backed
command and environment lane still exists, the shared parked reminder packet still
names it, the help-side reminder surface remains readable, and the direct exec-cmd
starter shard is not presently readable on `master` from this environment.

That packet keeps the roadmap-backed command and environment plumbing gap explicit
without claiming direct `execvp()` parity, direct process-launch ownership, live
OS environment reads, or direct terminal probing on current `master`.

## Roadmap Gap

The product roadmap still names Phase 8 as the first tooling-expansion tranche for:
- `tools/lib/subcmd/exec-cmd.c`
- `tools/lib/subcmd/help.c`

Current `master` still preserves parked help-lane reminder surfaces around this
area, and it also preserves the bounded file-path-and-handle bridge packet as a
planning-only gate for file, path, and handle reuse decisions. Even so, the
same packet still stops short of full process-launch, environment-plumbing,
terminal-probing, token handoff, and reopened-handle closure behavior, and the
current authenticated readback now shows the direct exec-cmd starter shard as a
live repo-reality gap instead of a cleanly present parked packet.

This note should therefore remain the truthful bridge between the roadmap target
and the bounded current-tree evidence rather than reverting to older missing-file
wording or overstating the parked command packet as fully present.

## Next Bounded Step

If a later Phase 8 lane changes any of the parked command-lane, help-lane, or
file-path-and-handle bridge files, re-read this note together with
`Documentation/zigux/phase8-tooling-lane-sequencing.md`,
`Documentation/zigux/phase8-file-path-handle-bridge-slice.md`,
`python3 scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`,
`scripts/zigux/README.md`, `zigux/Makefile`, and the current Phase 8 test tree
before widening broader Phase 8 summaries.

The next honest follow-through inside this packet is no longer the older generic
"parked command packet still present" reminder. It is the smaller truthfulness step
of keeping the shared Phase 8 wording aligned with the mixed current readback:
help-side reminder surfaces still read cleanly, while the direct exec-cmd shard
currently reads as absent through authenticated contents.

Until then, keep this survey parked and keep follow-up inside one bounded command-packet,
bridge-summary, or replay step rather than rebuilding the older missing-control-surface claim.
