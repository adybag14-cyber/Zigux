# Phase 8 Tooling Lane Sequencing

This note records the current anti-overlap owner map for the live Phase 8 userspace-adjacent tooling packet.

It is a coordination artifact, not a closure claim.

## Current posture
  * `PHASE8_STATUS=parked`
  * `PHASE8_SEQUENCE=tooling-lane-anti-overlap`
  * shared validator-first entrypoint: `python3 scripts/zigux/validate-phase8.py`
  * shared make validation route: `make -C zigux phase8-validate`
  * shared reminder surfaces still present on current `master`: `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
  * exact 2026-05-12 public default-branch tree readback shows the current Phase 8 shard packet is still present on `master`, including `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_help_kallsyms_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_cpu_mask_only_build.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_libbpf_segments_only_build.zig`, and `tools/lib/bpf/zigux_segments/manifest.json`
  * targeted current-file readback also shows `tools/lib/bpf/zigux_segments/manifest.json` still marks `cpu-mask-parsing` and `perf-buffer-poll-bookkeeping` as landed while keeping `perf-buffer-online-cpu-routing` deferred as the interrupt-routing packet
  * runtime readback caution: authenticated contents reads for some Phase 8 files are inconsistent from this environment, so public default-branch tree evidence plus exact readable blob content should win over older absent-file assumptions
  * current authenticated 2026-05-16 contents readback closes the older direct exec-cmd split: `Documentation/zigux/phase8-exec-cmd-slice.md`, `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig` now all read cleanly, while the broader shared `zigux/tests/phase8_build.zig` route and parts of the neighboring file-path bridge packet still stay mixed-source from this environment
  * current public default-branch raw readback now also serves `tools/lib/symbol/kallsyms.zig`, so the shared owner map should treat the helper path as readable current-tree evidence while the mixed help-plus-kallsyms build shard stays a shared validation route instead of turning help-local and symbol-local follow-through into one owner
  * `Documentation/zigux/phase8-libbpf-segment-survey.md` now carries the refreshed mixed 2026-05-12 libbpf readback, so the remaining overlap risk is the broader shared reminder packet rather than the dedicated libbpf survey lane itself
  * freeze-map posture: this lane stays in repo-hosted tooling review surfaces only and does not reopen any deep-core freeze anchor

## Lane map
### 1. Exec-cmd lane

Use this lane for bounded `exec-cmd` reminder, compile, or packet-truthfulness work only.

Current repo reality:
  * the older parked Phase 8 packet and several shared reminder surfaces still name `zigux/tests/phase8_exec_cmd.zig` and `zigux/tests/phase8_exec_cmd_only_build.zig`
  * public default-branch tree readback still lists `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig`
  * authenticated contents readback for the direct exec-cmd shard now reads cleanly across `Documentation/zigux/phase8-exec-cmd-slice.md`, `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig`; keep the remaining mixed-source caution on the broader shared `zigux/tests/phase8_build.zig` route and the neighboring bridge packet instead of treating the focused exec-cmd replay files as missing
  * `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` remains the dedicated boundary note that keeps the command-and-environment control surface smaller than broader process-launch and environment-plumbing parity claims
  * the help packet is no longer co-owned here: `tools/lib/subcmd/help.zig`, `zigux/tests/phase8_help.zig`, and `Documentation/zigux/phase8-help-slice.md` already carry their own parked helper-local packet, so exec-cmd follow-through should not reopen that help-local surface unless a directly coupled shared reminder line needs the same correction
Keep follow-up in this lane limited to truthful survey or reminder-surface repair around the now-readable direct exec-cmd shard. Do not reopen help-local output, sibling libbpf drift, or broader bridge/build instability from this lane unless a shared reminder surface is the exact blocker.

### 2. Symbol lane

Use this lane for bounded `kallsyms` reminder, compile, or packet-truthfulness work only.

Current repo reality:
  * the current Phase 8 test packet includes `zigux/tests/phase8_help_kallsyms_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig`
  * shared Phase 8 reminder surfaces still group the symbol shard with the same parked build-and-validator packet
  * `zigux/tests/phase8_help_kallsyms_only_build.zig` and `make -C zigux phase8-help-kallsyms-test` are still shared smoke coverage only, not a shared owner handoff between the parked help packet and the symbol lane
  * current public default-branch raw readback now also serves `tools/lib/symbol/kallsyms.zig`, so the live symbol lane should treat the helper path as readable current-tree evidence while the mixed help-plus-kallsyms build shard stays shared smoke coverage instead of turning help-local and symbol-local follow-through into one owner
  * `Documentation/zigux/phase8-kallsyms-slice.md` and the public raw helper path are both readable again, so shared reminder surfaces should keep help-local output or command-source drift in the dedicated help lane and reserve symbol follow-through for parser, truncation, or callback-wrapper truthfulness instead of replaying older unreadable-helper assumptions
Keep shared wording out of this lane unless a concrete symbol-lane packet drift appears on current `master`. If the symbol lane reopens next, compare the readable focused test, shared build shard, and slice note from one consistent source before retelling parser behavior.

### 3. Libbpf helper lane

Use this lane for bounded helper-first libbpf reminder, compile, behavior, or packet-truthfulness work only.

Current repo reality:
  * the current tree exposes `tools/lib/bpf/zigux_segments/manifest.json`
  * the current Phase 8 test packet includes `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_cpu_mask_only_build.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, and `zigux/tests/phase8_libbpf_segments.zig`
  * `tools/lib/bpf/zigux_segments/manifest.json` still records the helper-first landed slices around logging, pin-path helpers, cpu-mask parsing, type-name helpers, file-path helper-adjacent reviewability, and perf-buffer poll bookkeeping
  * the same manifest still keeps `perf-buffer-online-cpu-routing` deferred as the interrupt-routing boundary, so follow-up here should stay smaller than online-CPU setup, `perf_event_open()`, `mmap()`-backed ring state, epoll registration, or broader timeout-sensitive routing behavior
Keep follow-up in this lane limited to helper-local truthfulness, compile or behavior proof, or narrowly scoped reminder-surface repair.

### 4. Shared wording lane

Use this lane for bounded truthfulness work across the shared Phase 8 reminder surfaces when repo reality drifts.

Allowed surfaces:
  * `Documentation/zigux/README.md`
  * `Documentation/zigux/review-checklist.md`
  * `Documentation/zigux/phase8-tooling-lane-sequencing.md`
  * `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
  * `scripts/zigux/README.md`
  * `scripts/zigux/validate-phase8.py`
  * `zigux/tests/README.md`
  * `zigux/Makefile`
  * `.github/workflows/zigux-bootstrap.yml`

Current wording-lane caution:
  * do not let older absent-file assumptions overrule current tree evidence
  * the dedicated `Documentation/zigux/phase8-libbpf-segment-survey.md` note already carries the refreshed mixed 2026-05-12 libbpf readback, so shared wording follow-through should now focus on reminder surfaces that still speak more broadly than that dedicated survey proves
  * current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-packet.py`, so shared wording follow-through should not undercount that live checker while it narrows the libbpf reminder packet
  * current 2026-05-14 authenticated readback closes the older scripts-root missing-summary cue: `scripts/zigux/README.md` now carries a dedicated `Phase 8 flow` summary that keeps `scripts/zigux/validate-phase8.py`, `scripts/zigux/check-phase8-tests-readme-alignment.py`, `scripts/zigux/check-phase8-exec-cmd-packet.py`, `scripts/zigux/check-phase8-help-kallsyms-packet.py`, `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/check-phase8-libbpf-segment-gate.py`, `scripts/zigux/check-phase8-libbpf-shard-routes.py`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-libbpf-segment-survey.md`, `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `make -C zigux phase8-validate`, `make -C zigux phase8-exec-cmd-test`, `make -C zigux phase8-help-kallsyms-test`, `make -C zigux phase8-kallsyms-test`, `make -C zigux phase8-file-path-handle-bridge-test`, `make -C zigux phase8-test`, and `make -C zigux phase8` reviewable in one scripts-root packet
  * current 2026-05-27 reread closes the earlier scripts-root perf-buffer-poll omission cue: `scripts/zigux/README.md` now explicitly carries `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`, and `make -C zigux phase8-perf-buffer-poll-test` beside the shared validator-first packet, so shared-wording follow-through no longer needs a scripts-root perf-buffer reminder repair.
  * current 2026-05-27 reread also closes the older scripts-root symbol undercount cue: `scripts/zigux/README.md` now keeps `Documentation/zigux/phase8-kallsyms-slice.md`, `tools/lib/symbol/kallsyms.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig` visible as broader public-tree-backed companions, so the shared wording lane no longer needs a scripts-root kallsyms reminder repair either.
  * `Documentation/zigux/review-checklist.md` is no longer the first shared wording reopen cue: current `master` already refreshes that shared Phase 8 libbpf review question with `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/check-phase8-libbpf-segment-gate.py`, and `scripts/zigux/check-phase8-libbpf-shard-routes.py`, so the next shared-wording reread should start with `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `zigux/tests/README.md`, `scripts/zigux/README.md`, or `zigux/Makefile` instead of reopening the checklist
  * the help packet no longer shares ownership with exec-cmd: keep `tools/lib/subcmd/help.zig`, `zigux/tests/phase8_help.zig`, and `Documentation/zigux/phase8-help-slice.md` under the dedicated help packet unless a shared reminder surface truly cannot be made truthful without one directly coupled help line
  * when this lane reopens, re-read the shared reminder surfaces against `Documentation/zigux/phase8-libbpf-segment-survey.md`, the live Phase 8 test tree, `tools/lib/bpf/zigux_segments/manifest.json`, and the readable blob packet before calling any shard or helper family removed
  * prefer the next one-file or tightly coupled wording repair over broader Phase 8 expansion
  * the dedicated libbpf survey note and the broader shared reminder packet no longer point back to the same first reread surface because the checklist repair has already landed on current `master`; keep any future shared-wording follow-through limited to the next remaining sequencing-note, tests-root, or make-surface drift instead of reopening the checklist

## Sequencing rule
  1. Re-read the shared packet surfaces first.
  2. Confirm repo reality through the current default-branch tree and exact readable file content before trusting older Phase 8 inventories.
  3. Keep exec-cmd, help, symbol, and libbpf follow-up inside their parked packets unless a concrete same-lane drift appears.
  4. Keep interrupt-routing follow-up smaller than the deferred `perf-buffer-online-cpu-routing` boundary.
  5. Validate through exact readback before treating the packet as parked again.
  6. When the command-family packet reopens, treat `help` and `exec-cmd` as separate owners; do not reuse one parked tool lane as the fallback owner for the other.
  7. When the mixed `phase8-help-kallsyms` smoke route reopens, treat it as shared validation only: help-local output or command-source drift stays in the help lane, while parser, truncation, or callback-wrapper drift stays in the symbol lane even though `tools/lib/symbol/kallsyms.zig` is publicly readable again.

## Next bounded step
Exact 2026-05-15 reread keeps the earlier docs-root reopen cue closed instead of reopening it: current readable Phase 8 libbpf evidence still includes `tools/lib/bpf/zigux_segments/type_names.zig` and `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, and `Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary.
The earlier symbol-lane visible cue is no longer reopened: current public default-branch raw readback already serves `tools/lib/symbol/kallsyms.zig`, so shared sequencing should keep the mixed help-and-kallsyms build shard classified as validation overlap only while reserving parser follow-through for the dedicated `kallsyms` lane without replaying unreadable-helper assumptions.
The older combined command-lane assumption is closed too: `Documentation/zigux/phase8-help-slice.md` and `Documentation/zigux/phase8-exec-cmd-slice.md` already describe separate parked packets, and current authenticated contents reads now carry the direct exec-cmd shard cleanly through `Documentation/zigux/phase8-exec-cmd-slice.md`, `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig`, so future sequencing follow-through should keep the exec-cmd lane focused on direct command-packet truthfulness and leave the remaining mixed-source caution to the broader shared `zigux/tests/phase8_build.zig` route plus the neighboring file-path bridge surfaces.
The older tests-root reopen cue is closed too: `zigux/tests/README.md` now names `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`, `scripts/zigux/check-phase8-libbpf-segment-gate.py`, and `scripts/zigux/check-phase8-libbpf-shard-routes.py` together with the live libbpf shard routes, so the shared wording lane no longer needs a tests-root repair for that checker pair.
The older scripts-root missing-summary cue is closed too: `scripts/zigux/README.md` now carries a dedicated `Phase 8 flow` section that keeps the validator-first packet, the exec-cmd checker, the help-and-kallsyms plus libbpf shard checkers, the bridge survey notes, the focused exec-cmd and file-path bridge replays, and the shared `phase8-validate` route visible in one scripts-root packet.
The smallest remaining shared-wording truthfulness task is therefore this sequencing note itself: it should stop pointing future runs at a scripts-root omission that current `master` no longer has.
Keep the shared wording lane parked again after this note-local repair.
If the lane reopens, start with a fresh reread of `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml` together before widening to any validator, helper, or bridge-packet follow-through.
