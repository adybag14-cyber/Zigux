# Phase 13 Landlock Ruleset Ownership Note

This note records the bounded ownership split for `security/landlock/ruleset.zig` as it exists on current `master`.
Its job is to keep contributor-facing guidance honest about the helper-local review surface that is actually present today, without blurring the ruleset lane into adjacent syscall governance or into helper-local companions that have not landed.

## Scope

This note is for the ruleset helper only.
It does not claim ownership of the adjacent syscall lane, notifier work, or a broader shared-subsystems packet beyond the current ruleset review surface that is already visible on `master`.

## Current owned surface

When contributors touch the ruleset helper, keep this note aligned with the ruleset-local and shared review surfaces that are present now:

- `security/landlock/ruleset.zig`
- `Documentation/zigux/phase13-landlock-ruleset-ownership.md`
- `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- `Documentation/zigux/phase10-phase11-phase13-contributor-surface-sync.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase13-release-notes-survey.md`
- `Documentation/zigux/phase13-roadmap-traceability.md`
- `Documentation/zigux/phase13-notifier-list-survey.md`
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/README.md`
- `scripts/zigux/README.md`
- `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- `scripts/zigux/validate-phase13-release.py`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

## Repo-reality gaps

Current `master` does not show helper-local ruleset companions such as:

- `Documentation/zigux/phase13-landlock-ruleset-slice.md`
- `Documentation/zigux/phase13-landlock-ruleset-survey.md`
- `zigux/tests/phase13_landlock_ruleset.zig`
- `zigux/tests/phase13_landlock_ruleset_manifest.json`
- `zigux/tests/phase13_build.zig`

Treat those paths as follow-up gaps unless and until they actually land.
Do not present them here as shipped evidence, required current-master review anchors, or already-owned helper-local replay surfaces.

## Ownership boundaries

Use this note to keep these boundaries explicit:

- ruleset-helper truthfulness belongs with `security/landlock/ruleset.zig`, this ownership note, and the shipped Phase 13 docs-root and checker surfaces above
- syscall behavior, policy posture, and helper-local governance belong with `Documentation/zigux/phase13-landlock-syscalls-governance.md`
- shared packet routing belongs with the shipped validator, dedicated ruleset packet checker, the paired syscall-governance note, the broader release-notes, roadmap-traceability, and notifier-survey reminder notes, and the make routes already present on `master`
- any future slice, survey, manifest, or helper-local Zig test should be recorded here only after it is visible in the repository

## Review prompts

If a change updates the Phase 13 Landlock ruleset helper, verify that:

- this note still names only the helper-local and shared review surfaces that are actually present on current `master`
- helper-local truthfulness stays anchored to `security/landlock/ruleset.zig` and `scripts/zigux/check-phase13-landlock-ruleset-packet.py`
- syscall-governance edits remain in the paired `Documentation/zigux/phase13-landlock-syscalls-governance.md` note instead of being duplicated here
- the broader `Documentation/zigux/phase13-release-notes-survey.md`, `Documentation/zigux/phase13-roadmap-traceability.md`, and `Documentation/zigux/phase13-notifier-list-survey.md` reminder surfaces stay explicit whenever ruleset ownership wording changes
- any still-missing direct ruleset companions stay framed as repo-reality gaps rather than as shipped current-master evidence
