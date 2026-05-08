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
- shipped shared coordination surfaces on `master`: `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, `zigux/tests/phase8_build.zig`, and `zigux/Makefile`
- current helper-family posture: the bounded libbpf packet is parked after the landed file-path bridge and perf-buffer poll review updates, and this sequencing note should reopen it only for another smaller same-lane helper, validator, checker, survey, README, or shared wording gap
- continuity wording guard: if another shared Phase 8 reminder still says the libbpf shard routes are active, treat that wording as a focused reopen-entrypoint cue only, not as a claim that the libbpf packet is currently active by default

## Why this note exists

The live docs-root Phase 8 summary already shows that the old command-help-symbol starter packet is no longer the whole tranche. Current `master` carries parked `exec-cmd`, `help`, and `kallsyms` slices beside a libbpf helper family whose landed survey, docs-root summary, and lane memory now treat the packet as parked unless another same-lane gap appears.

This note turns that current evidence into one bounded lane map so nearby scheduled tooling runs do not reopen parked slices just because they are easier to touch than the parked libbpf review packet.

## Lane map

### 1. Command lane: parked unless a fresh parity gap appears
Use this lane only for `tools/lib/subcmd/*.zig` behavior that changes the already-landed command packet itself.

Current parked packet:
- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `Documentation/zigux/phase8-help-slice.md`
- `tools/lib/subcmd/exec-cmd.zig`
- `tools/lib/subcmd/help.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `zigux/tests/phase8_help.zig`
- `zigux/tests/phase8_help_only_build.zig`
- `zigux/tests/phase8_help_kallsyms_only_build.zig`

Keep the parked command packet reviewable through its focused exec-cmd shard, its help-local helper surface, and the one shared cross-packet shard:
- `make -C zigux phase8-exec-cmd-test`
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

Legacy validator continuity marker: older Phase 8 checker readbacks may still mention `### 3. Libbpf helper lane: the current active Phase 8 implementation surface`, but that phrase is retained only as compatibility context, not as the live lane heading.

The live heading for this lane is the parked wording above, and the helper-family packet itself remains parked after the landed file-path bridge, perf-buffer poll, and shared tests-root reminder updates. Reopen it only when a smaller same-lane libbpf helper, validator, checker, survey, README, or wording gap is visible again.

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
- `zigux/tests/phase8_build.zig`
- `tools/lib/bpf/zigux_segments/cpu_mask.zig`
- `tools/lib/bpf/zigux_segments/logging.zig`
- `tools/lib/bpf/zigux_segments/pin_path.zig`
- `tools/lib/bpf/zigux_segments/type_names.zig`
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
- `tools/lib/bpf/zigux_segments/verify.zig`
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
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase8.py`
- `zigux/tests/README.md`
- `zigux/Makefile`

When this wording lane reopens, treat `scripts/zigux/README.md` and `zigux/tests/README.md` as first-pass truth surfaces alongside `Documentation/zigux/README.md`, not as later summaries. On current `master` the scripts-root Phase 8 flow keeps the compact shared packet inventory visible through `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, and `zigux/tests/phase8_libbpf_segments_only_build.zig`, while the tests-root reminder also needs to keep the parked command and shared symbol replay surfaces explicit through `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_help_kallsyms_only_build.zig`, `make -C zigux phase8-help-test`, and `make -C zigux phase8-help-kallsyms-test` alongside the focused `make -C zigux phase8-file-path-handle-bridge-test` and `make -C zigux phase8-libbpf-segments-test` shard routes beside the parked libbpf packet.

The first wording-only reopen target here should usually be the docs-root plus scripts-root pair when the shared packet falls back to older active-tranche shorthand for the parked libbpf packet.

Do not use this lane to smuggle helper behavior changes.
If a wording fix requires changing helper logic, split the helper change back into the owning command, symbol, or libbpf lane.

## Sequencing rule
1. Re-read the shared packet surfaces first.
2. If they already agree that `exec-cmd`, `help`, and `kallsyms` are parked, do not start there.
3. If a fresh same-lane gap exists, prefer the next bounded step inside the libbpf helper lane before widening into broader Phase 8 wording work.
4. If `Documentation/zigux/README.md` or `scripts/zigux/README.md` falls back to older active-tranche shorthand for the parked libbpf packet, treat that as a wording-only reopen and correct the shared reminder pair before helper-local follow-up.
5. Use the shared packet wording lane only when the coordination surfaces themselves have drifted.
6. Keep every reopened task small enough to validate through its focused shard before rerunning the shared `phase8_build.zig` path.

## Current anti-overlap correction

Today the strongest Phase 8 sequencing correction is simple:
- treat `exec-cmd`, `help`, and `kallsyms` as parked tooling slices
- treat the libbpf helper family plus its bridge and survey notes as the currently parked reviewable Phase 8 libbpf packet, reopening it only for tighter same-lane gaps
- keep docs-root, scripts-root, checklist, tests-root, and validator wording repairs separate from helper-local parity work so older active-tranche shorthand does not pull scheduled runs away from the parked posture

That split matches the live docs-root Phase 8 summary and prevents scheduled tooling runs from duplicating already-parked starter-slice work.

## Next bounded step

The older shared tests-root reminder refresh is already complete.
That older immediate next step is now complete, and `zigux/tests/README.md` should now be read as a parked-packet reminder plus focused reopen map rather than as a reason to treat the libbpf packet as already active again by default.

If another wording-only drift appears first, start by rereading `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, and `Documentation/zigux/phase8-libbpf-segment-survey.md` together so the parked libbpf shard markers, the focused help-plus-kallsyms shard reminders, and the focused make routes stay aligned before reopening any helper-local Phase 8 follow-up.

The honest default is to leave this lane parked unless another one-file same-lane helper-local, validator, checker, survey, README, or wording drift appears inside the shared libbpf packet.
