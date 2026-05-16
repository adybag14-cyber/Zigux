# Phase 13 Release Notes Survey

## Purpose

This note keeps the shared Phase 13 release summary honest against the live current-`master` packet.

It is a release-surface survey only. It does not claim a closed tranche, a new replay route, or a broader shipped helper packet than the current tree can actually materialize.

## Roadmap Fit

Phase 13 in the Zigux roadmap stays bounded to four shared-helper anchors:

- `fs/libfs.c`
- `lib/devres.c`
- `security/landlock/ruleset.c`
- `security/landlock/syscalls.c`

Broad release wording should stay tied to those four anchors instead of collapsing them into one generic Phase 13 bucket or promoting adjacent notifier evidence into a fifth helper family.

## Current Shared Reminder Surfaces

Direct current-`master` readback in this run materialized these shared reminder surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `zigux/tests/README.md`

Those files are enough to keep the Phase 13 release packet visible as an active roadmap-backed documentation slice, but they are not enough to justify the older broader "already shipped helper-and-validator packet" wording that some nearby reminders still imply.

## Repo-Reality Gaps

The same direct current-`master` readback in this run did not materialize these release-facing Phase 13 surfaces, so broad summaries should keep them framed as repo-reality gaps instead of shipped evidence:

- `scripts/zigux/README.md`
- `scripts/zigux/validate-phase13-release.py`
- `scripts/zigux/check-phase13-shared-summary-surfaces.py`
- `scripts/zigux/check-phase13-devres-packet-alignment.py`
- `scripts/zigux/check-phase13-notifier-priority-signal.py`
- `zigux/Makefile`
- `.github/workflows/zigux-bootstrap.yml`
- `zigux/tests/phase13_build.zig`
- `Documentation/zigux/phase13-libfs-survey.md`
- `Documentation/zigux/phase13-devres-survey.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `fs/libfs.zig`
- `lib/devres.zig`
- `security/landlock/ruleset.zig`
- `security/landlock/syscalls.zig`
- `zigux/tests/phase13_libfs.zig`
- `zigux/tests/phase13_devres.zig`

This note itself was one of those gaps before this run. The release summary should now treat the survey as present, while keeping the remaining missing scripts-root, build-route, helper-local, and focused-test surfaces explicit until current `master` materializes them again.

## Release-Surface Posture

Keep Phase 13 release wording inside these boundaries:

- the Phase 13 packet is active and roadmap-backed, not closed
- the current directly readable packet is documentation-first rather than helper-and-validator complete
- missing helper-local, scripts-root, build-route, and notifier packet surfaces should stay recorded as repo-reality gaps
- adjacent notifier evidence may still matter for release truthfulness, but it does not become a fifth roadmap anchor
- contributor-facing reminder edits in this lane should stay narrow and should not reopen helper implementation, validator code, or checklist coupling

## Re-Read Before Updating This Note Again

When this survey changes, reread these shared reminder surfaces together first:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-coordination-matrix.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `zigux/tests/README.md`

Only widen beyond this survey if a fresh current-`master` reread shows that one of those coupled reminder surfaces cannot stay truthful without the adjacent same-lane follow-through.

## Non-Goals

- This note does not claim a stable shared replay route.
- This note does not claim shipped helper-local parity for the four Phase 13 anchors.
- This note does not widen into notifier implementation, release-validator repair, or helper-local tranche closure.
