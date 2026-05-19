# Phase 8 Exec Cmd Repo Reality Note

Lane key: `P8-L14`

Roadmap anchor:
- `Phase 8: Userspace-Adjacent Tooling Expansion`
- expected helper-first tooling anchor: `tools/lib/subcmd/exec-cmd.c`
- later non-goal boundary study: `kernel/workqueue.c` stays a Phase 14 target, not a Phase 8 port claim

Current directly readable deferred-exec packet on `master`:
- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `Documentation/zigux/phase8-exec-cmd-repo-reality-note.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/validate-phase8.py`
- `tools/lib/subcmd/exec-cmd.zig`
- `zigux/Makefile`
- `zigux/tests/README.md`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`

Current directly readable sibling Phase 8 anchors on `master`:
- `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`
- `Documentation/zigux/phase8-file-path-handle-bridge-slice.md`
- `scripts/zigux/check-phase8-tests-readme-alignment.py`
- `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
- `tools/lib/bpf/zigux_segments/file_path_handle_bridge.zig`
- `tools/lib/bpf/zigux_segments/perf_buffer_poll.zig`
- `zigux/tests/phase8_file_path_handle_bridge.zig`
- `zigux/tests/phase8_file_path_handle_bridge_only_build.zig`
- `zigux/tests/phase8_build.zig`
- `zigux/tests/phase8_perf_buffer_poll.zig`

Repo-reality reminder:
- the dedicated deferred-exec packet has been rematerialized on current `master`, so this note now exists only as a continuity surface beside `Documentation/zigux/phase8-exec-cmd-slice.md`
- keep the current Phase 8 deferred-exec reminder surface narrow and truthful: direct helper and focused test evidence now lives in `tools/lib/subcmd/exec-cmd.zig`, `zigux/tests/phase8_exec_cmd.zig`, and `zigux/tests/phase8_exec_cmd_only_build.zig`
- keep the roadmap split explicit: deferred exec stayed a helper-first tooling study in Phase 8, while any real workqueue ownership remains the later Phase 14 boundary-study target

Next step:
- if same-lane follow-through reopens, reread the restored helper, the focused build shard, the focused replay, the slice note, and the shared route surfaces together before widening into review-checklist wording, broader validator maintenance, or any queue-ownership claim
