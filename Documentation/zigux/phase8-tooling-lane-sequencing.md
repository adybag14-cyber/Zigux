# Phase 8 Tooling Lane Sequencing

This note records the current anti-overlap owner map for the live Phase 8 userspace-adjacent tooling packet.

It is a coordination artifact, not a closure claim.

## Current posture
- `PHASE8_STATUS=parked`
- `PHASE8_SEQUENCE=tooling-lane-anti-overlap`
- shared validator-first entrypoint: `python3 scripts/zigux/validate-phase8.py`
- shared make validation route: `make -C zigux phase8-validate`
- shared build replay entrypoint: `zig build test --build-file zigux/tests/phase8_build.zig --summary all`
- Linux-style replay entrypoint: `make -C zigux phase8`
- shared wording and gate surfaces on current `master`: `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase8.py`, `scripts/zigux/check-phase8-libbpf-segment-gate.py`, `scripts/zigux/check-phase8-libbpf-shard-routes.py`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- freeze-map posture: this lane stays in repo-hosted tooling only and does not reopen any deep-core freeze anchor

## Lane map

### 1. Command lane
Use this lane only for the landed `tools/lib/subcmd/*.zig` packet when a fresh helper-local or route-local gap appears.

Current parked packet:
- `tools/lib/subcmd/exec-cmd.zig`
- `tools/lib/subcmd/help.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `zigux/tests/phase8_help.zig`
- `zigux/tests/phase8_help_only_build.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`

Focused replay routes:
- `make -C zigux phase8-exec-cmd-test`
- `make -C zigux phase8-help-test`
- `make -C zigux phase8-help-kallsyms-test`

Do not reopen this lane for shared Phase 8 wording cleanup or libbpf helper drift.

### 2. Symbol lane
Use this lane only for the landed `tools/lib/symbol/kallsyms.zig` packet when a fresh symbol-local gap appears.

Current parked packet:
- `tools/lib/symbol/kallsyms.zig`
- `zigux/tests/phase8_kallsyms.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`

Focused replay routes:
- `make -C zigux phase8-kallsyms-test`
- `make -C zigux phase8-help-kallsyms-test`

Do not reopen this lane for libbpf shard routing or shared wording-only drift.

### 3. Libbpf helper lane
Use this lane for bounded work inside `tools/lib/bpf/zigux_segments/` and the paired Phase 8 libbpf shard tests.

Current parked packet:
- `tools/lib/bpf/zigux_segments/cpu_mask.zig`
- `tools/lib/bpf/zigux_segments/logging.zig`
- `tools/lib/bpf/zigux_segments/pin_path.zig`
- `tools/lib/bpf/zigux_segments/type_names.zig`
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
- `tools/lib/bpf/zigux_segments/verify.zig`
- `tools/lib/bpf/zigux_segments/manifest.json`
- `zigux/tests/phase8_cpu_mask.zig`
- `zigux/tests/phase8_cpu_mask_only_build.zig`
- `zigux/tests/phase8_logging.zig`
- `zigux/tests/phase8_pin_path.zig`
- `zigux/tests/phase8_bpf_type_names.zig`
- `zigux/tests/phase8_file_path_handle_bridge.zig`
- `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
- `zigux/tests/phase8_perf_buffer_poll.zig`
- `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
- `zigux/tests/phase8_libbpf_segments.zig`
- `zigux/tests/phase8_libbpf_segments_only_build.zig`
- `zigux/tests/phase8_build.zig`

Focused replay routes:
- `make -C zigux phase8-cpu-mask-test`
- `make -C zigux phase8-file-path-handle-bridge-test`
- `make -C zigux phase8-libbpf-segments-test`
- `make -C zigux phase8-perf-buffer-poll-test`
- `make -C zigux phase8-test`
- `make -C zigux phase8`

Keep this lane helper-first and output-stable. Do not widen it into loader work, direct procfs or bpffs ownership closure, or Phase 12 release planning.

### 4. Shared wording lane
Use this lane only when the shared Phase 8 packet description drifts across docs, tests, validator, workflow, or Makefile wording.

Allowed surfaces:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase8-tooling-lane-sequencing.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase8.py`
- `scripts/zigux/check-phase8-libbpf-segment-gate.py`
- `scripts/zigux/check-phase8-libbpf-shard-routes.py`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`

Current wording-lane caution:
- the live tree no longer carries the older Phase 8 slice-note files that some broad summaries still name
- treat absent slice-note filenames as stale wording, not as current packet evidence
- when this lane reopens, use `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and the dedicated Phase 8 checkers as the first-pass truth surfaces for the parked packet

## Sequencing rule
1. Re-read the shared packet surfaces first.
2. If the gap is helper-local, keep it inside the owning command, symbol, or libbpf lane.
3. If the gap is wording-only, keep it inside the shared wording lane.
4. Prefer the next one-file or tightly coupled same-lane repair over broader Phase 8 expansion.
5. Validate through the narrowest honest shard route or direct readback available before treating the packet as parked again.

## Next bounded step
The next honest reopen cue is a shared wording-lane repair in `Documentation/zigux/README.md`: the docs-root Phase 8 summary still names removed slice-note files even though the live parked packet is now carried by the shared validator, tests-root packet, Makefile routes, workflow reminders, and this sequencing note.
