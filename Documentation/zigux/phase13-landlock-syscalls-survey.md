# Phase 13 Landlock Syscalls Survey

This document records the bounded Phase 13 survey lane around `security/landlock/syscalls.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=landlock-syscalls-helper-policy-survey`
- reviewed against live `master` `master-readback-2026-05-12`
- scope: the shipped `security/landlock/syscalls.zig` helper starter, the paired governance note, the direct helper-local replay packet, and the remaining shared-build and live-state gaps that still keep this packet bounded
- product boundary:
  - `security/landlock/syscalls.zig`
  - `Documentation/zigux/phase13-landlock-syscalls-slice.md`
  - `Documentation/zigux/phase13-landlock-syscalls-governance.md`
  - `Documentation/zigux/phase13-landlock-syscalls-survey.md`
  - `zigux/tests/phase13_landlock_syscalls.zig`
  - `zigux/tests/phase13_landlock_syscalls_reviewability.zig`
  - `zigux/tests/phase13_landlock_syscalls_manifest.json`

## Why this slice exists

The Phase 13 roadmap explicitly names `security/landlock/syscalls.c` as one of the shared subsystem-helper anchors.

That matters because the syscall side of Landlock sits right at the boundary between reviewable policy planning and live kernel enforcement. A truthful Zigux packet has to keep the credential gate, restrict-self logging flags, add-rule branch split, and release-side file-operation shaping explicit without pretending to mutate live credentials, live rulesets, live file descriptors, or real syscall state.

Current `master` now ships a small `security/landlock/syscalls.zig` helper starter together with a direct helper-local replay packet. The highest-value bounded work in this lane is therefore to keep the shipped helper surface and its direct validation companions aligned while continuing to leave the missing shared `zigux/tests/phase13_build.zig` route and live state out of scope.

## Survey findings

- `security/landlock/syscalls.zig` stays planning-only through `SyscallsHelperLab.descriptor()`, with `touches_live_credentials = false` and `touches_live_rulesets = false` keeping the helper honest about what it does not claim.
- the shipped `planRestrictSelf()` planner models the bounded `landlock_restrict_self()` credential gate by splitting between `CredentialGate.no_new_privs` and `CredentialGate.cap_sys_admin_override` without pretending to mutate the caller's live credentials.
- the shipped `planRestrictSelf()` planner keeps the current ABI 7 logging surface explicit by translating `LANDLOCK_RESTRICT_SELF_LOG_SAME_EXEC_OFF`, `LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON`, and `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF` into helper-visible logging booleans, while keeping the special detached `ruleset_fd = -1` plus `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF` path reviewable as a logging-only update instead of a new domain install.
- the shipped `planAddRule()` and `planLandlockAddRule()` planners keep the `landlock_add_rule()` branches explicit by separating `AddRuleAction.path_beneath` from `AddRuleAction.net_port`, requiring ruleset write access for both, keeping parent-fd lookup local to `path_beneath`, and keeping port handoff local to `net_port`.
- the helper starter also carries the release-side `planFopRulesetRelease()` and `planRulesetFops()` planners so the `fop_ruleset_release()` ownership drop and the combined `ruleset_fops` invalid read or write contract remain visible as bounded helper evidence.
- current `master` now pairs the helper with `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, this survey note, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, and `zigux/tests/phase13_landlock_syscalls_manifest.json`.
- the immediate repo-reality gap versus the roadmap is therefore no longer an absent helper-local replay packet. The remaining bounded gaps are the still-missing shared `zigux/tests/phase13_build.zig` route and the intentionally unmodeled live credential, FD-installation, and ruleset-state surfaces.

## Exact Live Readback

- live helper readback on current `master` still shows `.provides_restrict_self_planning = true`, `.provides_add_rule_planning = true`, `.provides_ruleset_release_planning = true`, `.provides_ruleset_fops_planning = true`, and `.validates_credential_gate = true` in `SyscallsHelperLab.descriptor()`.
- current `master` still shows `.validates_restrict_self_logging = true`, plus the exported `landlock_restrict_self_log_same_exec_off`, `landlock_restrict_self_log_new_exec_on`, `landlock_restrict_self_log_subdomains_off`, and `landlock_mask_restrict_self` constants, which keeps the named logging-flag contract visible in the helper surface itself instead of burying it in survey-only prose.
- current `master` still exports both `pub const CredentialGate` and `pub const AddRuleAction`, which keeps the syscall packet's two policy splits explicit in the helper surface itself instead of burying them in survey-only prose.
- current `master` still exports `pub fn planRestrictSelf(`, `pub fn planAddRule(`, `pub fn planLandlockAddRule(`, `pub fn planFopRulesetRelease(`, and `pub fn planRulesetFops(`, so the helper starter already covers the narrow policy-planning and release-side ownership surface that the roadmap permits for this bounded security pilot.
- current `master` now also materializes the direct helper-local replay packet through `phase13_landlock_syscalls.zig`, `phase13_landlock_syscalls_reviewability.zig`, and `phase13_landlock_syscalls_manifest.json`, while the older shared `phase13_build.zig` route still remains absent.

## Recorded Gaps

The current lane state is:

- landed `phase13-landlock-syscalls-helper-starter`
- landed `phase13-landlock-syscalls-slice-note`
- landed `phase13-landlock-syscalls-governance-note`
- landed `phase13-landlock-syscalls-survey-note`
- landed `phase13-landlock-syscalls-direct-test-gate`
- landed `phase13-landlock-syscalls-reviewability-gate`
- landed `phase13-landlock-syscalls-manifest`
- blocked `phase13-build-gate`
- blocked `phase13-landlock-live-fd-installation`
- blocked `phase13-landlock-live-credential-state`
- blocked `phase13-landlock-live-ruleset-state`

This keeps the packet honest: Zigux now has a reviewable helper starter plus paired note and replay companions for the syscall-facing Landlock packet, but it still does not claim the older shared build route, live credential mutation, live ruleset ownership, live file-descriptor installation, or live syscall enforcement.

## Non-goals

This slice does not claim:

- live credential mutation
- live ruleset lifecycle ownership
- live file-descriptor installation or revocation
- live syscall enforcement
- policy parity with the full Landlock subsystem
- ownership of `security/landlock/ruleset.zig` or broader Phase 13 reminder packets

## Next bounded step

If this helper-local packet reopens, compare `security/landlock/syscalls.zig`, `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, `zigux/tests/phase13_landlock_syscalls_manifest.json`, `zigux/tests/phase13_landlock_syscalls.zig`, and `zigux/tests/phase13_landlock_syscalls_reviewability.zig` together on current `master` before widening into anonymous-inode internals, live FD installation, or new ruleset state.
