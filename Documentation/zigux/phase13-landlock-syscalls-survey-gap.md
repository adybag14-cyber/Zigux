# Phase 13 Landlock Syscalls Survey Gap

This note is now a historical breadcrumb for the restored helper-local survey packet on `master`.

## Current Repo Reality

The Phase 13 roadmap still keeps `security/landlock/syscalls.c` inside bounded security helper pilots. Current `master` now records the active helper-local summary in `Documentation/zigux/phase13-landlock-syscalls-survey.md` and carries `zigux/tests/phase13_landlock_syscalls.zig` as a returned direct replay companion and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` as a returned reviewability companion.

Keep future survey refreshes anchored to:
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `scripts/zigux/check-phase13-landlock-syscalls-packet.py`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`

## Remaining Gaps

The remaining directly coupled gaps stay outside this bounded helper-local step:
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_build.zig`
- the live fd-installation, credential-mutation, and broader ruleset-state surfaces that the current helper-first packet still does not claim

## Why This File Still Exists

This breadcrumb exists only so older lane notes or review references do not strand readers on a stale path after the survey came back. The active packet summary is now the restored survey, not this historical gap note.

## Next Bounded Step

Leave this breadcrumb parked unless one of two things happens:
- a future helper-local note points back here as though this were still the active survey surface
- current `master` rematerializes the direct manifest or shared-build companion and a dedicated validation-only follow-through can retarget the helper-local packet around that new repo reality

Do not widen this breadcrumb into anonymous-inode internals, live fd installation, credential mutation, or domain state.
