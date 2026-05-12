# Phase 8 Tooling Lane Sequencing

This note records the current anti-overlap owner map for the live Phase 8 userspace-adjacent tooling packet.

It is a coordination artifact, not a closure claim.

## Current posture
- `PHASE8_STATUS=parked`
- `PHASE8_SEQUENCE=tooling-lane-anti-overlap`
- shared validator-first entrypoint: `python3 scripts/zigux/validate-phase8.py`
- shared make validation route: `make -C zigux phase8-validate`
- shared reminder surfaces still present on current `master`: `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- exact 2026-05-12 public default-branch tree readback shows the current Phase 8 shard packet is still present on `master`, including `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `tools/lib/bpf/zigux_segments/manifest.json`
- targeted current-file readback also shows `tools/lib/bpf/zigux_segments/manifest.json` still marks `cpu-mask-parsing` and `perf-buffer-poll-bookkeeping` as landed while keeping `perf-buffer-online-cpu-routing` deferred as the interrupt-routing packet
- runtime readback caution: authenticated contents reads for some Phase 8 files are inconsistent from this environment, so public default-branch tree evidence plus exact readable blob content should win over older absent-file assumptions
- current authenticated 2026-05-12 contents readback remains inconsistent around the direct exec-cmd shard: `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-tooling-lane-sequencing.md`, and `zigux/tests/phase8_help.zig` still read cleanly, while the same contents route intermittently returns `404` for `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig` even though the public tree still lists them on `master`
- freeze-map posture: this lane stays in repo-hosted tooling review surfaces only and does not reopen any deep-core freeze anchor

## Lane map

### 1. Command lane
Use this lane for bounded `exec-cmd` and `help` reminder, compile, or packet-truthfulness work only.

Current repo reality:
- the older parked Phase 8 packet and several shared reminder surfaces still name `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help.zig`, and `zigux/tests/phase8_help_only_build.zig`
- public default-branch tree readback still lists `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help.zig`, and `zigux/tests/phase8_help_only_build.zig`
- authenticated contents readback for the direct exec-cmd shard remains intermittent from this environment, so treat those `404` responses as route instability until both the public tree and readable blob evidence drop the same files
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` remains the dedicated boundary note that keeps the command-and-environment control surface smaller than broader process-launch and environment-plumbing parity claims

Keep follow-up in this lane limited to truthful survey or reminder-surface repair while the direct exec-cmd shard keeps this split between public-tree presence and intermittent authenticated blob reads.

### 2. Symbol lane
Use this lane for bounded `kallsyms` reminder, compile, or packet-truthfulness work only.

Current repo reality:
- the current Phase 8 test packet includes `zigux/tests/phase8_kallsyms.zig` and `zigux/tests/phase8_help_kallsyms_only_build.zig`
- shared Phase 8 reminder surfaces still group the symbol shard with the same parked build-and-validator packet

Keep follow-up parked unless a concrete symbol-lane packet drift appears on current `master`.

### 3. Libbpf helper lane
Use this lane for bounded helper-first libbpf reminder, compile, behavior, or packet-truthfulness work only.

Current repo reality:
- the current tree exposes `tools/lib/bpf/zigux_segments/manifest.json`
- the current Phase 8 test packet includes `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, and `zigux/tests/phase8_libbpf_segments.zig`
- `tools/lib/bpf/zigux_segments/manifest.json` still records the helper-first landed slices around logging, pin-path helpers, cpu-mask parsing, type-name helpers, file-path helper-adjacent reviewability, and perf-buffer poll bookkeeping
- the same manifest still keeps `perf-buffer-online-cpu-routing` deferred as the interrupt-routing boundary, so follow-up here should stay smaller than online-CPU setup, `perf_event_open()`, `mmap()`-backed ring state, epoll registration, or broader timeout-sensitive routing behavior

Keep follow-up in this lane limited to helper-local truthfulness, compile or behavior proof, or narrowly scoped reminder-surface repair.

### 4. Shared wording lane
Use this lane for bounded truthfulness work across the shared Phase 8 reminder surfaces when repo reality drifts.

Allowed surfaces:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase8.py`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

Current wording-lane caution:
- do not let older absent-file assumptions overrule current tree evidence
- current authenticated readback remains noisy around the direct exec-cmd shard: the help-side reminder packet still reads cleanly and the public tree still lists the exec-cmd files, but the same contents route intermittently returns `404` for those exec-cmd paths, so keep shared wording follow-through smaller than a broad tooling rewrite
- current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-packet.py`, so shared wording follow-through should not undercount that live checker while trimming stale Phase 8 inventory
- when this lane reopens, re-read the shared reminder surfaces against the live Phase 8 test tree, `tools/lib/bpf/zigux_segments/manifest.json`, and the readable blob packet before calling any shard or helper family removed
- prefer the next one-file or tightly coupled wording repair over broader Phase 8 expansion
- Keep follow-up inside the shared wording lane until the public survey packet and the current readable helper-plus-build evidence agree again.

## Sequencing rule
1. Re-read the shared packet surfaces first.
2. Confirm repo reality through the current default-branch tree and exact readable file content before trusting older Phase 8 inventories.
3. Keep command, symbol, and libbpf follow-up inside their parked shard packets unless a concrete same-lane drift appears.
4. Keep interrupt-routing follow-up smaller than the deferred `perf-buffer-online-cpu-routing` boundary.
5. Validate through exact readback before treating the packet as parked again.

## Next bounded step
The next honest shared-surface reopen cue now starts with keeping this sequencing note truthful: current public tree evidence still carries the direct exec-cmd shard on `master`, while authenticated contents reads for `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig` remain intermittent from this environment.

Keep the next reopen scoped to preserving that route-instability caution in the command-lane notes first; only widen to `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase8.py`, or `zigux/tests/README.md` if both the public tree and the readable blob packet stop carrying the same exec-cmd shard.
