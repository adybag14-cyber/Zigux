# Phase 13 Landlock Syscalls Governance

This note records the bounded governance and review-owner split for the shared Phase 13 Landlock syscalls packet so contributor-facing reminder surfaces do not blur syscall policy into neighboring helper packets.

## Scope

This note is for the syscall side of the active Phase 13 Landlock packet only.

Current `master` materializes `security/landlock/syscalls.zig` as a helper-local starter for the roadmap-owned `security/landlock/syscalls.c` anchor. Keep the helper-owned wording tightly scoped to descriptor-backed create-ruleset planning, ABI-version query planning, ERRATA query planning, ruleset-fd lookup planning, one planning-only `landlock_restrict_self()` helper, top-level create-ruleset initialization plus attr-presence wrapper checks, create-handle-only reuse of the ruleset-fd install planner, add-rule planning, top-level add-rule initialization plus attr-presence wrapper checks, one planning-only ruleset-fd install helper, one planning-only ruleset-fd stub helper, and one planning-only `fop_ruleset_release()` helper.

Do not present that helper packet as live fd installation, file-buffer handling, credential replacement, or full Landlock enforcement.

## Current Repo Reality

Current `master` now materializes the active helper-local packet plus its direct validation, replay, and reviewability companions through:
- `security/landlock/syscalls.zig`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `scripts/zigux/check-phase13-landlock-syscalls-packet.py`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`

Keep `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md` adjacent only as a historical breadcrumb for older lane notes and review references, not as active packet evidence.

Current `master` still does not materialize the direct manifest or shared-build companions through:
- `zigux/tests/phase13_landlock_syscalls_manifest.json`
- `zigux/tests/phase13_build.zig`

Keep these neighboring surfaces distinct:
- `Documentation/zigux/phase13-roadmap-traceability.md` for the broader Phase 13 roadmap-to-repo owner map
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md` for the broader Phase 13 owner split and lane routing
- `Documentation/zigux/phase13-contributor-workflow-guide.md` for the contributor-facing workflow packet
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md` for ruleset-helper ownership and review boundaries when that surface materializes again

## Owned Review Surface

When contributors touch the syscall-facing Landlock packet, keep this note aligned first with the shipped helper-local packet:
- `security/landlock/syscalls.zig`
- `Documentation/zigux/phase13-landlock-syscalls-slice.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-landlock-syscalls-survey.md`
- `scripts/zigux/check-phase13-landlock-syscalls-packet.py`
- `zigux/tests/phase13_landlock_syscalls.zig`
- `zigux/tests/phase13_landlock_syscalls_reviewability.zig`

Keep `Documentation/zigux/phase13-landlock-syscalls-survey-gap.md` nearby only as historical breadcrumb context when older lane notes still cite it; do not treat it as an active packet owner or replay witness.

Keep contributor guidance anchored to the broader shipped reminder packet while the direct manifest and shared-build companions remain absent.

## Governance Boundaries

Use this note to keep these boundaries explicit:
- syscall policy wording, review prompts, and reminder-surface ownership belong here
- the helper-local packet plus the direct replay and direct reviewability companions belong here today
- the survey-gap breadcrumb remains historical context only and must not be promoted back into active packet ownership
- direct manifest ownership stays recorded as a repo-reality gap until that file returns on `master`
- future work should stay tied to descriptor-backed planning only instead of treating it as live syscall enforcement or as a claim that fd, file-buffer, credential, or domain ownership moved into Zigux

## Review Prompts

If a change updates the Phase 13 Landlock syscalls packet, verify that:
- the broad Phase 13 reminder surfaces keep this governance note explicit beside the survey, slice, checker, direct replay companion, and direct reviewability companion, and frame the survey-gap file only as historical breadcrumb context when it is mentioned
- no wording here promotes the still-missing direct manifest or shared-build companions into shipped current-`master` evidence
- helper-owned wording stays limited to create-ruleset, ABI-version query, ERRATA query, ruleset-fd lookup, restrict-self, add-rule, ruleset-fd install, ruleset-fd stub, and release planning
- note-versus-gap ownership stays explicit: this note owns the helper-local policy packet, the survey-gap file is breadcrumb-only context, while the remaining gaps stay `zigux/tests/phase13_landlock_syscalls_manifest.json` and `zigux/tests/phase13_build.zig`
