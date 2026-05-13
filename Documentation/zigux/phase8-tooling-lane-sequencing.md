# Phase 8 Tooling Lane Sequencing

This note records the current anti-overlap owner map for the live Phase 8 userspace-adjacent tooling packet.

It is a coordination artifact, not a closure claim.

## Current posture
- `PHASE8_STATUS=parked`
- `PHASE8_SEQUENCE=tooling-lane-anti-overlap`
- shared validator-first entrypoint: `python3 scripts/zigux/validate-phase8.py`
- shared make validation route: `make -C zigux phase8-validate`
- shared reminder surfaces still present on current `master`: `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/README.md`, `zigux/tests/README.md`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, and `.github/workflows/zigux-bootstrap.yml`
- exact 2026-05-12 public default-branch tree readback shows the current Phase 8 shard packet is still present on `master`, including `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_build.zig`, `zigux/tests/phase8_exec_cmd.zig`, `zigux/tests/phase8_exec_cmd_only_build.zig`, `zigux/tests/phase8_help.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_help_kallsyms_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_cpu_mask_only_build.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, `zigux/tests/phase8_perf_buffer_poll_only_build.zig`, `zigux/tests/phase8_libbpf_segments.zig`, and `zigux/tests/phase8_libbpf_segments_only_build.zig`, and `tools/lib/bpf/zigux_segments/manifest.json`
- targeted current-file readback also shows `tools/lib/bpf/zigux_segments/manifest.json` still marks `cpu-mask-parsing` and `perf-buffer-poll-bookkeeping` as landed while keeping `perf-buffer-online-cpu-routing` deferred as the interrupt-routing packet
- runtime readback caution: authenticated contents reads for some Phase 8 files are inconsistent from this environment, so public default-branch tree evidence plus exact readable blob content should win over older absent-file assumptions
- current authenticated 2026-05-12 contents readback remains inconsistent around the direct exec-cmd shard: `Documentation/zigux/phase8-help-slice.md`, `Documentation/zigux/phase8-tooling-lane-sequencing.md`, and `zigux/tests/phase8_help.zig` still read cleanly, while the same contents route intermittently returns `404` for `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig` even though the public tree still lists them on `master`
- current authenticated 2026-05-13 contents readback widens that same instability beyond the direct exec-cmd shard: `Documentation/zigux/phase8-kallsyms-slice.md`, `tools/lib/symbol/kallsyms.zig`, `zigux/tests/phase8_help_only_build.zig`, `zigux/tests/phase8_help_kallsyms_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, `zigux/tests/phase8_kallsyms_only_build.zig`, and `zigux/tests/phase8_build.zig` all returned `404` through the authenticated blob route while the shared reminder surfaces and `scripts/zigux/check-phase8-help-kallsyms-packet.py` still name the same packet, so same-day absence claims should stay treated as route instability until both readable blob evidence and public-tree evidence drop the same files
- `Documentation/zigux/phase8-libbpf-segment-survey.md` now carries the refreshed mixed 2026-05-12 libbpf readback, so the remaining overlap risk is the broader shared reminder packet rather than the dedicated libbpf survey lane itself
- freeze-map posture: this lane stays in repo-hosted tooling review surfaces only and does not reopen any deep-core freeze anchor

## Lane map

### 1. Exec-cmd lane
Use this lane for bounded `exec-cmd` reminder, compile, or packet-truthfulness work only.

Current repo reality:
- the older parked Phase 8 packet and several shared reminder surfaces still name `zigux/tests/phase8_exec_cmd.zig` and `zigux/tests/phase8_exec_cmd_only_build.zig`
- public default-branch tree readback still lists `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig`
- authenticated contents readback for the direct exec-cmd shard remains intermittent from this environment, so treat those `404` responses as route instability until both the public tree and readable blob evidence drop the same files
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md` remains the dedicated boundary note that keeps the command-and-environment control surface smaller than broader process-launch and environment-plumbing parity claims
- the help packet is no longer co-owned here: `tools/lib/subcmd/help.zig`, `zigux/tests/phase8_help.zig`, and `Documentation/zigux/phase8-help-slice.md` already carry their own parked helper-local packet, so exec-cmd follow-through should not reopen that help-local surface unless a directly coupled shared reminder line needs the same correction

Keep follow-up in this lane limited to truthful survey or reminder-surface repair while the direct exec-cmd shard keeps this split between public-tree presence and intermittent authenticated blob reads. Do not reopen help-local output or slice-note drift from this lane.

### 2. Symbol lane
Use this lane for bounded `kallsyms` reminder, compile, or packet-truthfulness work only.

Current repo reality:
- the current Phase 8 test packet includes `zigux/tests/phase8_help_kallsyms_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig`
- shared Phase 8 reminder surfaces still group the symbol shard with the same parked build-and-validator packet
- exact readable 2026-05-13 contents from this environment still fetch the shared help-and-symbol reminder surfaces plus `scripts/zigux/check-phase8-help-kallsyms-packet.py`, but direct blob reads for `Documentation/zigux/phase8-kallsyms-slice.md`, `tools/lib/symbol/kallsyms.zig`, `zigux/tests/phase8_help_kallsyms_only_build.zig`, `zigux/tests/phase8_kallsyms.zig`, and `zigux/tests/phase8_kallsyms_only_build.zig` now intermittently return `404`, so keep same-day symbol-lane absence claims parked as route instability until the same path can read those files again or public-tree evidence drops them too

Keep follow-up parked unless a concrete symbol-lane packet drift appears on current `master`.

### 3. Libbpf helper lane
Use this lane for bounded helper-first libbpf reminder, compile, behavior, or packet-truthfulness work only.

Current repo reality:
- the current tree exposes `tools/lib/bpf/zigux_segments/manifest.json`
- the current Phase 8 test packet includes `zigux/tests/phase8_cpu_mask.zig`, `zigux/tests/phase8_cpu_mask_only_build.zig`, `zigux/tests/phase8_logging.zig`, `zigux/tests/phase8_pin_path.zig`, `zigux/tests/phase8_bpf_type_names.zig`, `zigux/tests/phase8_file_path_handle_bridge.zig`, `zigux/tests/phase8_perf_buffer_poll.zig`, and `zigux/tests/phase8_libbpf_segments.zig`
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
- the dedicated `Documentation/zigux/phase8-libbpf-segment-survey.md` note already carries the refreshed mixed 2026-05-12 readback, so shared wording follow-through should now focus on reminder surfaces that still speak more broadly than that dedicated survey proves
- current readable scripts-root evidence still includes `scripts/zigux/check-phase8-exec-cmd-packet.py`, so shared wording follow-through should not undercount that live checker while it narrows the libbpf reminder packet
- current 2026-05-12 exact readback also shows `scripts/zigux/README.md` now keeps `zigux/tests/phase8_exec_cmd_only_build.zig` and `zigux/tests/phase8_cpu_mask_only_build.zig` correctly cased beside the shared Phase 8 packet, so the earlier scripts-root filename repair is no longer the active reopen cue
- `Documentation/zigux/review-checklist.md` already keeps the live pin-path, perf-buffer-poll, and focused libbpf-segment replay markers explicit beside the dedicated survey note and public tree readback, so the checklist is no longer the first shared wording reopen cue
- the help packet no longer shares ownership with exec-cmd: keep `tools/lib/subcmd/help.zig`, `zigux/tests/phase8_help.zig`, and `Documentation/zigux/phase8-help-slice.md` under the dedicated help packet unless a shared reminder surface truly cannot be made truthful without one directly coupled help line
- when this lane reopens, re-read the shared reminder surfaces against `Documentation/zigux/phase8-libbpf-segment-survey.md`, the live Phase 8 test tree, `tools/lib/bpf/zigux_segments/manifest.json`, and the readable blob packet before calling any shard or helper family removed
- prefer the next one-file or tightly coupled wording repair over broader Phase 8 expansion
- Keep follow-up inside the shared wording lane until the dedicated libbpf survey note and the broader shared reminder packet agree again.

## Sequencing rule
1. Re-read the shared packet surfaces first.
2. Confirm repo reality through the current default-branch tree and exact readable file content before trusting older Phase 8 inventories.
3. Keep exec-cmd, help, symbol, and libbpf follow-up inside their parked packets unless a concrete same-lane drift appears.
4. Keep interrupt-routing follow-up smaller than the deferred `perf-buffer-online-cpu-routing` boundary.
5. Validate through exact readback before treating the packet as parked again.
6. When the command-family packet reopens, treat `help` and `exec-cmd` as separate owners; do not reuse one parked tool lane as the fallback owner for the other.

## Next bounded step
Exact 2026-05-13 readback closes the earlier docs-root reopen cue instead of reopening it: public Phase 8 readback still serves both `Documentation/zigux/phase8-bpf-type-names-slice.md` and `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`, and `Documentation/zigux/README.md` now names the live file-path bridge note in the broad Phase 8 docs summary. The older combined command-lane assumption is closed too: `Documentation/zigux/phase8-help-slice.md` and `Documentation/zigux/phase8-exec-cmd-slice.md` already describe separate parked packets, so future sequencing follow-through should keep help-local output or slice-note drift out of the exec-cmd lane and out of the shared wording lane unless a shared reminder surface is the real blocker. Keep the shared wording lane parked until a fresh one-file reminder-surface drift appears.
