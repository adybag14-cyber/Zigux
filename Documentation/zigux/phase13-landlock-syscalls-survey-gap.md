# Phase 13 Landlock Syscalls Survey Gap

This note records the current helper-local survey posture for the Phase 13 Landlock syscall packet on `master`.

## Current Repo Reality

The Phase 13 roadmap still keeps `security/landlock/syscalls.c` inside bounded security helper pilots. On current `master`, that helper-local packet is now materially aligned and intentionally narrow:

- `security/landlock/syscalls.zig` keeps the create-ruleset, restrict-self, add-rule, ruleset-fd install, ruleset-fd stub, and `fop_ruleset_release()` planners explicit without claiming live FD installation, credential mutation, or enforcement
- `Documentation/zigux/phase13-landlock-syscalls-slice.md` and `Documentation/zigux/phase13-landlock-syscalls-governance.md` now match that helper boundary and truthfully record the absent direct survey, replay, reviewability, manifest, and shared-build companions as repo-reality gaps
- `scripts/zigux/check-phase13-landlock-syscalls-packet.py` now keeps the materialized helper-local packet companions honest without treating the still-missing direct survey or replay paths as shipped evidence
- the broader shared Phase 13 reminder packet already keeps those same direct syscall companions parked as repo-reality gaps instead of presenting them as shipped evidence

## Remaining Gaps

The helper-local packet no longer has the older review-noise drift that originally justified this note. The remaining gaps are unchanged and stay outside this bounded helper-local step:

- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_build.zig`
- the live FD-installation, credential-mutation, and broader ruleset-state surfaces that the current helper-first packet still does not claim

## Why This Still Matters

The lane should stay evidence-first. Once the helper-local notes are truthful, reopening the packet just to restate missing survey or replay files becomes churn. The honest next move is to leave those repo-reality gaps visible without pretending the helper packet needs another local wrapper or note refresh today.

## Next Bounded Step

Leave this lane parked unless one of two things happens:

- a future helper-local note starts overstating the visible syscall packet again
- current `master` rematerializes one of the direct survey or replay companions and a dedicated validation-only follow-up can retarget the helper-local packet around that new repo reality

Do not widen this note into anonymous-inode internals, live FD installation, credential mutation, or domain state.
