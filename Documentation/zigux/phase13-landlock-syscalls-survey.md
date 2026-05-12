# Phase 13 Landlock Syscalls Survey

This document records the bounded Phase 13 survey lane around `security/landlock/syscalls.c`.

## Status

- `PHASE13_STATUS=active`
- `PHASE13_SLICE=landlock-syscalls-helper-policy-survey`
- reviewed against live `master` `master-readback-2026-05-12`
- scope: the shipped `security/landlock/syscalls.zig` helper starter, the paired `Documentation/zigux/phase13-landlock-syscalls-governance.md` note, and the still-missing direct helper-local companions that would be needed before this packet could claim a dedicated replay bundle
- product boundary:
  - `security/landlock/syscalls.zig`
  - `Documentation/zigux/phase13-landlock-syscalls-governance.md`
  - `Documentation/zigux/phase13-landlock-syscalls-survey.md`

## Why this slice exists

The Phase 13 roadmap explicitly names `security/landlock/syscalls.c` as one of the shared subsystem-helper anchors.

That matters because the syscall side of Landlock sits right at the boundary between reviewable policy planning and live kernel enforcement. A truthful Zigux packet has to keep the credential gate, restrict-self logging flags, add-rule branch split, and release-side file-operation shaping explicit without pretending to mutate live credentials, live rulesets, or real syscall state.

Current `master` already ships a small `security/landlock/syscalls.zig` helper starter, but it still does not ship the direct helper-local slice note, replay, reviewability gate, or manifest companions that would turn this into a fuller helper-local packet. The highest-value bounded work in this lane is therefore to keep the shipped helper surface and its roadmap posture easy to reread instead of widening into ruleset ownership or shared reminder churn.

## Survey findings

- `security/landlock/syscalls.zig` stays planning-only through `SyscallsHelperLab.descriptor()`, with `touches_live_credentials = false` and `touches_live_rulesets = false` keeping the helper honest about what it does not claim.
- the shipped `planRestrictSelf()` planner already models the bounded `landlock_restrict_self()` credential gate by splitting between `CredentialGate.no_new_privs` and `CredentialGate.cap_sys_admin_override` without pretending to mutate the caller's live credentials.
- the shipped `planRestrictSelf()` planner now also keeps the current ABI 7 logging surface explicit by translating `LANDLOCK_RESTRICT_SELF_LOG_SAME_EXEC_OFF`, `LANDLOCK_RESTRICT_SELF_LOG_NEW_EXEC_ON`, and `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF` into helper-visible logging booleans, while keeping the special detached `ruleset_fd = -1` plus `LANDLOCK_RESTRICT_SELF_LOG_SUBDOMAINS_OFF` path reviewable as a logging-only update instead of a new domain install.
- the shipped `planAddRule()` planner keeps the `landlock_add_rule()` branches explicit by separating `AddRuleAction.path_beneath` from `AddRuleAction.net_port`, requiring ruleset write access for both, keeping parent-fd lookup local to `path_beneath`, and keeping port handoff local to `net_port`.
- the helper starter also carries the release-side `planFopRulesetRelease()` and `planRulesetFops()` planners so the `fop_ruleset_release()` ownership drop and the combined `ruleset_fops` read or write `-EINVAL` contract remain visible as bounded helper evidence.
- current `master` already pairs the helper with `Documentation/zigux/phase13-landlock-syscalls-governance.md` and this survey note, but it still does not ship `Documentation/zigux/phase13-landlock-syscalls-slice.md`, `zigux/tests/phase13_landlock_syscalls.zig`, `zigux/tests/phase13_landlock_syscalls_reviewability.zig`, or `zigux/tests/phase13_landlock_syscalls_manifest.json`.
- the immediate repo-reality gap versus the roadmap is therefore not an absent helper starter. It is the lack of direct helper-local slice, replay, reviewability, and manifest companions around the helper that current `master` already ships.

## Exact Live Readback

- live helper readback on current `master` still shows `.provides_restrict_self_planning = true`, `.provides_add_rule_planning = true`, `.provides_ruleset_release_planning = true`, `.provides_ruleset_fops_planning = true`, and `.validates_credential_gate = true` in `SyscallsHelperLab.descriptor()`.
- current `master` now also shows `.validates_restrict_self_logging = true`, plus the exported `landlock_restrict_self_log_same_exec_off`, `landlock_restrict_self_log_new_exec_on`, `landlock_restrict_self_log_subdomains_off`, and `landlock_mask_restrict_self` constants, which keeps the named logging-flag contract visible in the helper surface itself instead of burying it in survey-only prose.
- current `master` still exports both `pub const CredentialGate` and `pub const AddRuleAction`, which keeps the syscall packet's two policy splits explicit in the helper surface itself instead of burying them in survey-only prose.
- current `master` still exports `pub fn planRestrictSelf(`, `pub fn planAddRule(`, `pub fn planFopRulesetRelease(`, and `pub fn planRulesetFops(`, so the helper starter already covers the narrow policy-planning and release-side ownership surface that the roadmap permits for this bounded security pilot.
- direct helper-local companions for slice, replay, reviewability, and manifest state still return absent-path readback on current `master`, so this survey note must describe those paths as follow-up gaps rather than as shipped proof.

## Recorded gaps

The current lane state is:

- landed `phase13-landlock-syscalls-helper-starter`
- landed `phase13-landlock-syscalls-governance-note`
- landed `phase13-landlock-syscalls-survey-note`
- blocked `phase13-landlock-syscalls-slice-note`
- blocked `phase13-landlock-syscalls-direct-replay`
- blocked `phase13-landlock-syscalls-reviewability-gate`
- blocked `phase13-landlock-syscalls-manifest`
- blocked `phase13-landlock-live-credential-mutation`
- blocked `phase13-landlock-live-ruleset-ownership`
- blocked `phase13-landlock-live-syscall-enforcement`

This keeps the packet honest: Zigux now has a reviewable helper starter plus paired governance and survey notes for the syscall-facing Landlock packet, but it still does not claim helper-local replay coverage, live credential mutation, live ruleset ownership, or live syscall enforcement.

## Non-goals

This slice does not claim:

- live credential mutation
- live ruleset lifecycle ownership
- live file-descriptor installation or revocation
- live syscall enforcement
- policy parity with the full Landlock subsystem
- ownership of `security/landlock/ruleset.zig` or broader Phase 13 reminder packets

## Next bounded step

If this helper-local packet reopens, compare `security/landlock/syscalls.zig`, `Documentation/zigux/phase13-landlock-syscalls-governance.md`, `Documentation/zigux/phase13-landlock-syscalls-survey.md`, and the still-missing direct helper-local companions together on current `master` before widening into any new ruleset, notifier, or shared reminder work.
