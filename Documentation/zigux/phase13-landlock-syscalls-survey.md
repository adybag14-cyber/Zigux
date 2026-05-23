# Phase 13 Landlock Syscalls Survey

Current `master` survey anchor: `master-readback-2026-05-23`.

The Phase 13 roadmap still keeps `security/landlock/syscalls.c` inside bounded security-helper pilots. Current `master` now materializes a helper-local survey packet around that anchor rather than leaving the syscall packet summarized only through a survey-gap placeholder.

## Current Helper Boundary

Current `master` keeps the helper packet intentionally narrow:

- `security/landlock/syscalls.zig` keeps the create-ruleset, ABI-version query, restrict-self, add-rule, ruleset-fd lookup, ruleset-fd install, ruleset-fd stub, and `fop_ruleset_release()` planners explicit as helper data
- the helper keeps handled-access, attr-size, flag, incoming-layer, and tree-walk validation reviewable, delegates ruleset creation plus rule-tree search plus rule insertion planning into `security/landlock/ruleset.zig`, and keeps the create-handle path separate from the ABI-version query path before anon-inode installation planning
- the helper still does not claim live FD installation, file-buffer handling, credential replacement, task synchronization side effects, or full Landlock enforcement as shipped Zigux behavior

## Materialized Survey Packet

Current `master` now materializes this helper-local packet through:

- `security/landlock/syscalls.zig`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `scripts/zigux/check-phase13-landlock-syscalls-packet.py`

`Documentation/zigux/phase13-landlock-syscalls-survey-gap.md` now remains only as a historical breadcrumb pointing back to this survey rather than as the active packet summary.

Current `master` still leaves these directly coupled companions absent:

- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_build.zig`

## Why This Packet Still Fits Phase 13

This is still honest Phase 13 product progress because it surveys one bounded shared helper and keeps the mixed-language boundary explicit. The helper packet is substantive enough to review, but it is still intentionally below live FD ownership, credential mutation, and enforcement claims.

## Next Bounded Step

Leave this survey lane parked unless one of two things happens:

- the syscall helper gains another equally bounded planner and this survey needs one same-packet refresh
- current `master` materializes the direct replay, reviewability, or manifest companions and the packet can add a validation-only follow-through without widening into new helper behavior
