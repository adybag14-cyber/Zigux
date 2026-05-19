# Phase 8 Exec Cmd Repo Reality Note

Lane key: `P8-L13`

Roadmap anchor:
- `Phase 8: Userspace-Adjacent Tooling Expansion`
- expected helper-first tooling anchor: `tools/lib/subcmd/exec-cmd.c`
- later non-goal boundary study: `kernel/workqueue.c` stays a Phase 14 target, not a Phase 8 port claim

Current directly readable deferred-exec reminder surfaces on `master`:
- `Documentation/zigux/phase8-exec-cmd-repo-reality-note.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/validate-phase8.py`
- `zigux/Makefile`
- `zigux/tests/README.md`
- `zigux/tests/phase8_exec_cmd.zig`

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

Repo-reality warning for the still-missing dedicated deferred-exec packet members on current `master`:
- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `tools/lib/subcmd/exec-cmd.c`
- `tools/lib/subcmd/exec-cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `scripts/zigux/check-phase8-exec-cmd-packet.py`

Keep the current Phase 8 deferred-exec reminder surface narrow and truthful:
- do not present the missing dedicated helper, slice note, focused build shard, or packet checker as directly readable current-`master` evidence until a fresh same-lane reread or republish materializes them again
- do keep the surviving direct reminder packet explicit through `zigux/tests/phase8_exec_cmd.zig`, `Documentation/zigux/review-checklist.md`, `scripts/zigux/validate-phase8.py`, `zigux/Makefile`, and `zigux/tests/README.md`, because those current surfaces still preserve the helper-first deferred-exec boundary and keep it separate from broader process-launch claims
- keep the roadmap split explicit: deferred exec stayed a helper-first tooling study in Phase 8, while any real workqueue ownership remains the later Phase 14 boundary-study target

Next step:
- if same-lane follow-through reopens, recover the missing dedicated `exec-cmd` packet members from a validated current-master source, then reread the repo-reality note, the surviving `zigux/tests/phase8_exec_cmd.zig` reminder witness, any restored focused build shard or checker, and the shared route surfaces together before restoring broader Phase 8 deferred-exec claims