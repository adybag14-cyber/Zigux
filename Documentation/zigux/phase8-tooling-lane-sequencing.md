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
- shipped shared coordination surfaces on `master`: `Documentation/zigux/README.md`, `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `scripts/zigux/validate-phase8.py`, `zigux/tests/README.md`, `zigux/tests/phase8_build.zig`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- current helper-family posture: the bounded libbpf packet is parked after the landed file-path bridge and perf-buffer poll review updates, and this sequencing note should reopen it only for another smaller same-lane helper, validator, checker, survey, README, or shared wording gap
- continuity wording guard: if another shared Phase 8 reminder still says the libbpf shard routes are active, treat that wording as a focused reopen-entrypoint cue only, not as a claim that the libbpf packet is currently active by default

## Why this note exists
The live docs-root Phase 8 summary already shows that the old command-help-symbol starter packet is no longer the whole tranche.
Current `master` carries parked `exec-cmd`, `help`, and `kallsyms` slices beside a libbpf helper family whose landed survey, docs-root summary, and lane memory now treat the packet as parked unless another same-lane gap appears.
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
The live heading for this lane is the parked wording above, and the helper-family packet itself remains parked after the landed file-path bridge and perf-buffer poll review updates. Reopen it only when a smaller same-lane libbpf helper, validator, checker, survey, README, or wording gap is visible again.
Current parked review packet:
- `Documentation/zigux/phase8-libbpf-cpu-mask-slice.md`
- `Documentation/zigux/phase8-bpf-type-names-slice.md`
- `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
- `Documentation/zigux/phase8-perf-buffer-poll-slice.md`
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
- `Documentation/zigux/phase8-libbpf-segment-survey.md`
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
- `tools/lib/bpf/zigux_segments/cpu_mask.zig`
- `tools/lib/bpf/zigux_segments/logging.zig`
- `tools/lib/bpf/zigux_segments/pin_path.zig`
- `tools/lib/bpf/zigux_segments/type_names.zig`
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
- `tools/lib/bpf/zigux_segments/verify.zig`
- `tools/lib/bpf/zigux_segments/manifest.json`
Keep the parked libbpf packet reviewable through its focused shard routes plus the shared replay routes:
- `make -C zigux phase8-cpu-mask-test`
- `make -C zigux phase8-file-path-handle-bridge-test`
- `make -C zigux phase8-libbpf-segments-test`
- `make -C zigux phase8-perf-buffer-poll-test`
- `make -C zigux phase8-test`
- `make -C zigux phase8`
Keep this lane helper-first.
Do not widen it into:
- direct procfs or bpffs ownership closure
- loader-facing libbpf work
- unrelated command or symbol packet repairs
- Phase 12 release-order work that merely references the same manifest tree

### 4. Shared packet wording lane: docs or validator sequencing only
Use this lane only when the shared Phase 8 packet description drifts across docs-root, tests-root, validator wording, focused gate wording, or Makefile naming.
Allowed surfaces:
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase8.py`
- `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
- `scripts/zigux/check-phase8-libbpf-segment-gate.py`
- `scripts/zigux/check-phase8-libbpf-shard-routes.py`
- `zigux/tests/README.md`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
Use this wording lane for gate-only alignment too: if the parked perf-buffer poll review packet drifts only in `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, or if the parked libbpf survey-and-route packet drifts only in `scripts/zigux/check-phase8-libbpf-segment-gate.py` or `scripts/zigux/check-phase8-libbpf-shard-routes.py`, keep that follow-up here while the paired `tools/lib/bpf/zigux_segments/*.zig` helpers themselves stay unchanged instead of widening back into helper-local work.
When this wording lane reopens, treat `scripts/zigux/README.md` and `zigux/tests/README.md` as first-pass truth surfaces alongside `Documentation/zigux/README.md`, not as later summaries.
On current `master` the scripts-root Phase 8 flow keeps the compact shared packet inventory visible through `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_cpu_mask_only_build.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, and `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, and it already names `make -C zigux phase8-cpu-mask-test` alongside the parked file-path bridge, libbpf-segment, and perf-buffer-poll replays.
When this wording lane reopens, keep `scripts/zigux/check-phase8-libbpf-segment-gate.py` and `scripts/zigux/check-phase8-libbpf-shard-routes.py` explicit beside that same scripts-root packet so the parked libbpf survey gate and shard-route gate stay reviewable without widening back into helper-local work.
The docs-root reminder also keeps `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, the parked command plus shared symbol replay surfaces explicit through `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_help_kallsyms_only_build.zig`, `make -C zigux phase8-help-test`, and `make -C zigux phase8-help-kallsyms-test`, and the focused `make -C zigux phase8-cpu-mask-test`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8-libbpf-segments-test`, and `make -C zigux phase8-perf-buffer-poll-test` shard routes beside the parked libbpf packet.
The tests-root reminder now keeps `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_cpu_mask_only_build.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, and the focused `make -C zigux phase8-cpu-mask-test`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8-libbpf-segments-test`, and `make -C zigux phase8-perf-buffer-poll-test` shard routes explicit, so that older one-file tests-root reminder is now closed on current `master`.
The first wording-only reopen target here used to be the docs-root and scripts-root summary pair plus the validator reminder.
That docs-root, scripts-root, and validator follow-through is now closed on current `master`: `scripts/zigux/validate-phase8.py` already exact-requires both `Documentation/zigux/README.md` and `scripts/zigux/README.md` to keep `Documentation/zigux/phase8-tooling-lane-sequencing.md` visible in the shared Phase 8 packet, and it already directly fails closed if `zigux/tests/phase8_cpu_mask_only_build.zig` disappears from the shared validator inventory beside the shared Make route and `Documentation/zigux/phase8-libbpf-segment-survey.md`.
Do not use this lane to smuggle helper behavior changes. If a wording fix requires changing helper logic, split the helper change back into the owning command, symbol, or libbpf lane.

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
- keep docs-root, scripts-root, checklist, tests-root, validator wording repairs, and workflow-backed shard reminders separate from helper-local parity work so older active-tranche shorthand does not pull scheduled runs away from the parked posture
That split matches the live docs-root Phase 8 summary and prevents scheduled tooling runs from duplicating already-parked starter-slice work.

## Next bounded step
That older immediate next step is now closed on current `master`: `zigux/tests/README.md` directly names `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_cpu_mask_only_build.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, and the focused `make -C zigux phase8-cpu-mask-test`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8-libbpf-segments-test`, and `make -C zigux phase8-perf-buffer-poll-test` shard routes beside the parked libbpf packet.
The smaller shared tests-root cpu-mask reminder is therefore no longer a reopen cue for this lane. Leave the Phase 8 packet parked unless a fresh one-file same-lane helper, validator, checker, survey, README, checklist, or wording drift appears inside the shared command, symbol, or libbpf packet.
The docs-root summary already keeps this owner map explicit on current `master`: `Documentation/zigux/README.md` names `Documentation/zigux/phase8-tooling-lane-sequencing.md` beside the parked help-plus-kallsyms shard routes, the file-path bridge route, the libbpf segment-survey route, the dedicated shared `make -C zigux phase8-test` replay, and the perf-buffer-poll route.
The older validator-only reminder is now also closed on current `master`: `scripts/zigux/validate-phase8.py` already keeps the docs-root and scripts-root owner-map note explicit, and it already directly fails closed when `zigux/tests/phase8_cpu_mask_only_build.zig` disappears from the shared validator inventory. This sequencing note should therefore stop steering wording-lane follow-up toward that already-landed validator repair and keep any remaining work narrower.
The older scripts-root shared libbpf shard reminder is now also closed on current `master`: `scripts/zigux/README.md` already keeps `zigux/tests/phase8_cpu_mask_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, `zigux/tests/phase8_libbpf_segments_only_build.zig`, `make -C zigux phase8-cpu-mask-test`, `make -C zigux phase8-libbpf-segments-test`, and the shared `make -C zigux phase8-test` replay explicit beside the parked file-path bridge and perf-buffer-poll routes.
This sequencing note should therefore stop steering the shared wording lane back toward that already-landed scripts-root replay reminder.
The reviewer-facing packet is also aligned on current `master`: `Documentation/zigux/review-checklist.md` already keeps `scripts/zigux/check-phase8-perf-buffer-poll-gate.py` explicit beside `scripts/zigux/validate-phase8.py`, the shared `make -C zigux phase8-test` replay, and the focused `make -C zigux phase8-perf-buffer-poll-test` route, so this sequencing note should not steer the lane toward that already-landed checklist reminder either.
If a fresh wording drift does reopen the shared packet, reread `Documentation/zigux/README.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/check-phase8-libbpf-segment-gate.py`, and `scripts/zigux/check-phase8-libbpf-shard-routes.py` together so the parked libbpf shard markers, the survey-local `zigux/tests/phase8_cpu_mask_only_build.zig` shard, the survey-local `zigux/tests/phase8_perf_buffer_poll_only_build.zig` shard, the focused help-plus-kallsyms shard reminders, the pin-path and type-name helper inventory, the dedicated `scripts/zigux/check-phase8-perf-buffer-poll-gate.py` checker, the dedicated `scripts/zigux/check-phase8-libbpf-segment-gate.py` checker, the dedicated `scripts/zigux/check-phase8-libbpf-shard-routes.py` checker, and the focused `make -C zigux phase8-cpu-mask-test`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8-libbpf-segments-test`, `make -C zigux phase8-perf-buffer-poll-test`, plus the shared `make -C zigux phase8-test` replay stay aligned before reopening any helper-local Phase 8 follow-up.
The honest default is to leave this lane parked unless another one-file same-lane helper-local, validator, checker, survey, README, or wording drift appears inside the shared libbpf packet.
