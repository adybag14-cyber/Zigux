# Phase 8 Command / Syscall Boundary Gap

Lane key: `P8-L01`

Roadmap anchor:
- `Phase 8: Userspace-Adjacent Tooling Expansion`
- expected helper-first tooling anchors: `tools/lib/subcmd/exec-cmd.c`, `tools/lib/subcmd/help.c`, `tools/lib/symbol/kallsyms.c`, and `tools/lib/bpf/libbpf.c`

## Status
- `PHASE8_STATUS=parked`
- `PHASE8_GAP=command-syscall-boundary-reminder-drift`
- current inspected `master` head: `ff4367836d1c7d68139ac8d128f94f93d7c6429c`
- scope: roadmap-versus-repo survey truthfulness only

## Current directly readable packet on `master`
- `Documentation/zigux/phase8-exec-cmd-repo-reality-note.md`
- `Documentation/zigux/phase8-kallsyms-slice.md`
- `Documentation/zigux/phase8-libbpf-segment-survey.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `scripts/zigux/README.md`
- `zigux/tests/README.md`

## Current repo-reality gap
Current `master` no longer materializes the older shared bridge-boundary reminder packet files `Documentation/zigux/phase8-tooling-lane-sequencing.md`, `Documentation/zigux/phase8-userspace-kernel-bridge-boundary-survey.md`, `Documentation/zigux/phase8-perf-buffer-poll-slice.md`, or `scripts/zigux/validate-phase8.py`.

The surviving docs-root Phase 8 reminder in `Documentation/zigux/README.md` still cites those retired paths as if they were current packet members, so the broad command-and-syscall boundary story is no longer fully truthful against current repo state.

At the same time, the surviving Phase 8 packet is still real and roadmap-backed rather than churn:
- `Documentation/zigux/phase8-exec-cmd-repo-reality-note.md` keeps the deferred command boundary explicit as a missing dedicated packet instead of pretending `exec-cmd` is directly reviewable on current `master`
- `Documentation/zigux/phase8-kallsyms-slice.md` keeps the symbol-side parser-and-wrapper lane explicit while recording the mixed readback surface in this environment
- `Documentation/zigux/phase8-libbpf-segment-survey.md` still carries the helper-first libbpf segmentation story and the mixed-source bridge evidence below the heavier deferred resource-boundary packet

## Why this stays in lane
- it does not reopen helper behavior, build graph wiring, or shared validator ownership
- it records the roadmap-versus-repo gap inside the shared command-and-syscall boundary survey family only
- it keeps the helper-first Phase 8 discipline explicit instead of reconstructing missing packet members from older reminder wording

## Next bounded step
If the same-family shared reminder packet reopens, refresh the broad Phase 8 docs-root, tests-root, and checklist wording so it cites the surviving `phase8-exec-cmd-repo-reality-note.md`, `phase8-kallsyms-slice.md`, and `phase8-libbpf-segment-survey.md` packet instead of the removed bridge-boundary, tooling-lane sequencing, perf-buffer-poll, and `validate-phase8.py` paths until those paths are rematerialized on current `master`.
