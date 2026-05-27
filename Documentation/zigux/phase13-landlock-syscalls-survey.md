# Phase 13 Landlock Syscalls Survey

Current `master` survey anchor: `master-readback-2026-05-27`.

The Phase 13 roadmap still keeps `security/landlock/syscalls.c` inside bounded security-helper pilots. Current `master` now materializes a helper-local, direct replay, and reviewability packet around that anchor.

## Current Helper Boundary

Current `master` keeps the helper packet intentionally narrow:
- `security/landlock/syscalls.zig` keeps the create-ruleset, ABI-version query, ERRATA query, restrict-self, add-rule, ruleset-fd lookup, ruleset-fd install, ruleset-fd stub, and `fop_ruleset_release()` planners explicit as helper data
- the helper keeps handled-access, attr-size, flag, incoming-layer, and tree-walk validation reviewable, delegates ruleset creation plus rule-tree search plus rule insertion planning into `security/landlock/ruleset.zig`, and keeps the create-handle path separate from the ABI-version and ERRATA query paths before anon-inode installation planning
- the helper still does not claim live fd installation, file-buffer handling, credential replacement, task synchronization side effects, or full Landlock enforcement as shipped Zigux behavior

## Materialized Survey Packet

Current `master` now materializes this helper-local, direct replay, and reviewability packet through:
- `security/landlock/syscalls.zig`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `scripts/zigux/check-phase13-landlock-syscalls-packet.py`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`

Keep `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md` adjacent only as a historical breadcrumb for older lane notes and review references, not as active packet evidence.

Current `master` still leaves these directly coupled companions absent:
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_build.zig`

## Why This Packet Still Fits Phase 13

This is still honest Phase 13 product progress because it surveys one bounded shared helper, keeps the mixed-language boundary explicit, and adds a direct replay plus a direct reviewability witness without widening into live syscall ownership claims.

## Next Bounded Step

Leave this survey lane parked unless one of two things happens:
- current `master` materializes the direct manifest or shared-build companion and the packet can add a validation-only follow-through without widening into new helper behavior
- the syscall helper gains another equally bounded planner and this survey needs one same-packet refresh
