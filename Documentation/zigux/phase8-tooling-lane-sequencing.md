# Phase 8 Tooling Lane Sequencing

This note records the current anti-overlap sequencing for the live Phase 8 userspace-adjacent tooling packet.

It is a coordination artifact, not a closure claim.

## Current posture
- `PHASE8_STATUS=parked`
- `PHASE8_SEQUENCE=tooling-lane-anti-overlap`
- shared validator-first entrypoint: `python3 scripts/zigux/validate-phase8.py`
- shared make validation route: `make -C zigux phase8-validate`
- shared build replay entrypoint: `zig build test --build-file zigux/tests/phase8_build.zig --summary all`
- Linux-style replay entrypoint: `make -C zigux phase8`
- shipped shared coordination surfaces on `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, `zigux/tests/phase8_build.zig`, and `zigux/Makefile`
- current helper-family posture: the bounded libbpf packet is parked after the landed file-path bridge and perf-buffer poll review updates, and this sequencing note should reopen it only for another smaller same-lane helper, validator, checker, survey, README, or shared wording gap

## Why this note exists

The live docs-root Phase 8 summary already shows that the old command-help-symbol starter packet is no longer the whole tranche. Current `master` carries parked `exec-cmd`, `help`, and `kallsyms` slices beside a libbpf helper family whose landed survey, docs-root summary, and lane memory now treat the packet as parked unless another same-lane gap appears.

This note turns that current evidence into one bounded lane map so nearby scheduled tooling runs do not reopen parked slices just because they are easier to touch than the parked libbpf review packet.

## Lane map

### 1. Command lane: parked unless a fresh parity gap appears
Use this lane only for `tools/lib/subcmd/*.zig` behavior that changes the already-landed command packet itself.

Current parked packet:
- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `Documentation/zigux/phase8-help-slice.md`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `zigux/tests/phase8_help.zig`
- `zigux/tests/phase8_help_only_build.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`

Keep the parked command packet reviewable through its own focused shard plus the one shared cross-packet shard:
- `make -C zigux phase8-help-test`
- `make -C zigux phase8-help-kallsyms-test`

Do not reopen this lane for:
- libbpf survey drift
- file-path bridge or perf-buffer poll work
- symbol classification follow-up
- shared docs-root wording cleanup that belongs to the whole Phase 8 packet

### 2. Symbol lane: parked unless symbol parsing or classification moves again
Use this lane only for `tools/lib/symbol/*.zig` behavior plus the paired `kallsyms` review packet.

Current parked packet:
- `Documentation/zigux/phase8-kallsyms-slice.md`
- `tools/lib/symbol/kallsyms.zig`
- `zigux/tests/phase8_kallsyms.zig`
- `zigux/tests/phase8_kallsyms_only_build.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`

Keep the parked symbol packet reviewable through its own focused shard plus the same shared cross-packet shard:
- `make -C zigux phase8-kallsyms-test`
- `make -C zigux phase8-help-kallsyms-test`

Do not reopen this lane for:
- libbpf bridge sequencing
- shared segment-survey snapshot refreshes
- help or exec-cmd wording drift

The next honest symbol reopen should stay helper-local, such as one fresh symbol-class parity gap or callback-contract mismatch, not a broad Phase 8 wording pass.

### 3. Libbpf helper lane: parked unless a tighter same-lane gap appears
Use this lane for bounded work inside the current `tools/lib/bpf/zigux_segments/` helper family and its paired tests and surveys.

Legacy validator continuity marker: `### 3. Libbpf helper lane: the current active Phase 8 implementation surface` still names this shared owner lane even though the helper-family packet itself is parked between bounded follow-ups.

This heading stays stable for shared validator continuity, and the live helper-family packet itself is currently parked after the landed file-path bridge, perf-buffer poll, and shared tests-root reminder updates. Reopen it only when a smaller same-lane libbpf helper, validator, checker, survey, README, or wording gap is visible again.

Current parked review packet:
- `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`
- `Documentation/zigux/phase8-bpf-type-names-slice.md`
- `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `zigux/tests/phase8_cpu_mask.zig`
- `zigux/tests/phase8_logging.zig`
- `zigux/tests/phase8_pin_path.zig`
- `zigux/tests/phase8_bpf_type_names.zig`
- `zigux/tests/phase8_file_path_handle_bridge.zig`
- `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
- `zigux/tests/phase8_perf_buffer_poll.zig`
- `zigux/tests/phase8_perf_buffer_poll_only_build.zig`
- `zigux/tests/phase8_libbpf_segments.zig`
- `zigux/tests/phase8_libbpf_segments_only_build.zig`
- `tools/lib/bpf/zigux_segments/manifest.json`

Keep this lane helper-first.
Do not widen it into:
- direct procfs or bpffs ownership closure
- loader-facing libbpf work
- unrelated command or symbol packet repairs
- Phase 12 release-order work that merely references the same manifest tree

### 4. Shared packet wording lane: docs or validator sequencing only
Use this lane only when the shared Phase 8 packet description drifts across docs-root, tests-root, validator wording, or Makefile naming.

Allowed surfaces:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/validate-phase8.py`
- `zigux/tests/README.md`
- `zigux/Makefile`

Do not use this lane to smuggle helper behavior changes.
If a wording fix requires changing helper logic, split the helper change back into the owning command, symbol, or libbpf lane.

## Sequencing rule
1. Re-read the shared packet surfaces first.
2. If they already agree that `exec-cmd`, `help`, and `kallsyms` are parked, do not start there.
3. If a fresh same-lane gap exists, prefer the next bounded step inside the libbpf helper lane before widening into broader Phase 8 wording work.
4. Use the shared packet wording lane only when the coordination surfaces themselves have drifted.
5. Keep every reopened task small enough to validate through its focused shard before rerunning the shared `phase8_build.zig` path.

## Current anti-overlap correction

Today the strongest Phase 8 sequencing correction is simple:
- treat `exec-cmd`, `help`, and `kallsyms` as parked tooling slices
- treat the libbpf helper family plus its bridge and survey notes as the currently parked reviewable Phase 8 libbpf packet, reopening it only for tighter same-lane gaps
- keep shared wording-only repairs separate from helper-local parity work

That split matches the live docs-root Phase 8 summary and prevents scheduled tooling runs from duplicating already-parked starter-slice work.

## Next bounded step

Before reopening another tooling helper lane, refresh the shared tests-root reminder so it keeps the parked libbpf shard routes explicit beside the parked `exec-cmd`, `help`, and `kallsyms` packet.

That older immediate next step is now complete, and that shared tests-root reminder is now refreshed on `master`, so the honest default is to leave this lane parked unless another one-file same-lane helper-local, validator, checker, survey, README, or wording drift appears inside the shared libbpf packet.
