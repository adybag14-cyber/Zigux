# Phase 8 Exec Cmd Repo Reality Note

Lane key: `P8-L13`

Roadmap anchor:
- `Phase 8: Userspace-Adjacent Tooling Expansion`
- expected helper-first tooling anchor: `tools/lib/subcmd/exec-cmd.c`
- later non-goal boundary study: `kernel/workqueue.c` stays a Phase 14 target, not a Phase 8 port claim

Current directly readable Phase 8 sibling anchors on `master`:
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase8-tests-readme-alignment.py`
- `scripts/zigux/check-phase8-perf-buffer-poll-gate.py`
- `zigux/tests/phase8_perf_buffer_poll.zig`

Repo-reality warning for the missing dedicated deferred-exec packet on current `master`:
- `Documentation/zigux/phase8-exec-cmd-slice.md`
- `tools/lib/subcmd/exec-cmd.c`
- `tools/lib/subcmd/exec-cmd.zig`
- `zigux/tests/phase8_exec_cmd.zig`
- `zigux/tests/phase8_exec_cmd_only_build.zig`
- `scripts/zigux/check-phase8-exec-cmd-packet.py`
- `scripts/zigux/validate-phase8.py`
- `zigux/Makefile`

Keep the current Phase 8 deferred-exec reminder surface narrow and truthful:
- do not present the missing dedicated `exec-cmd` packet as directly readable current-`master` evidence until a fresh same-lane reread or republish materializes it again
- keep the surviving Phase 8 reminder packet tied to the directly readable tests-root alignment checker plus the perf-buffer poll checker-and-test anchors instead of reconstructing the broader tooling packet from older route names alone
- keep the roadmap split explicit: deferred exec stayed a helper-first tooling study in Phase 8, while any real workqueue ownership remains the later Phase 14 boundary-study target

Next step:
- if same-lane follow-through reopens, recover the dedicated `exec-cmd` packet from a validated current-master source, then reread its note, focused replay, focused build shard, checker, and shared route surfaces together before restoring broader Phase 8 deferred-exec claims
