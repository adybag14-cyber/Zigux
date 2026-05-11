# Phase 13 Landlock Ruleset Ownership Note

This note records the bounded ownership split for the shared Phase 13 Landlock ruleset packet so contributor-facing review surfaces do not point at an absent file or blur the ruleset slice into the adjacent syscall-governance packet.

## Scope

This note is for the ruleset side of the landed Phase 13 Landlock packet only.

Keep these adjacent surfaces distinct:
- `Documentation/zigux/phase13-landlock-ruleset-slice.md` for the slice-local ruleset contract
- `Documentation/zigux/phase13-landlock-ruleset-survey.md` for the shipped reviewer-facing ruleset evidence summary
- `Documentation/zigux/phase13-landlock-syscalls-slice.md` and `Documentation/zigux/phase13-landlock-syscalls-survey.md` for the separate syscall-facing packet
- `Documentation/zigux/phase13-landlock-syscalls-governance.md` for syscall-policy and governance reminders that should not be restated here as ruleset ownership

## Owned Review Surface

When contributors touch the ruleset helper packet, this owner note should stay aligned with:
- `Documentation/zigux/review-checklist.md`
- `Documentation/zigux/README.md`
- `Documentation/zigux/phase13-contributor-workflow-guide.md`
- `Documentation/zigux/phase13-shared-helper-lane-sequencing.md`
- `Documentation/zigux/phase10-phase11-phase13-tests-root-review-companion.md`
- `scripts/zigux/README.md`
- `zigux/Makefile`
- `make -C zigux phase13-validate`
- `make -C zigux phase13`

If direct companions such as `zigux/tests/phase13_landlock_ruleset.zig`, `zigux/tests/phase13_landlock_ruleset_manifest.json`, or `zigux/tests/phase13_build.zig` cannot be materialized on current `master`, record them as repo-reality gaps and keep reviewer guidance anchored to the shipped docs-root and make-route surfaces above instead of presenting those direct paths as independently shipped evidence.

The intent is simple: keep the ruleset packet reviewable as one bounded Phase 13 helper surface without implying that syscall policy, notifier evidence, or broader release-packet ownership has moved into the ruleset note.

## Ownership Boundaries

Use this note to keep these boundaries explicit:
- ruleset-helper contract and review prompts belong with the ruleset slice, survey, and this ownership note
- syscall behavior, reviewability, and governance belong with the syscall slice, syscall survey, and syscall-governance note
- shared packet routing belongs with the shipped docs-root and make-route surfaces above; if `zigux/tests/phase13_build.zig` is absent, keep that direct build path recorded as repo reality rather than as shipped evidence
- broader Phase 13 contributor sequencing belongs with `Documentation/zigux/phase13-contributor-workflow-guide.md` and the shared docs-root summaries

## Review Prompts

If a change updates the Phase 13 Landlock ruleset packet, verify that:
- the ruleset slice, ruleset survey, and this ownership note still describe the same bounded helper surface
- the shared Phase 13 reviewer packet keeps the ruleset note explicit wherever it names the adjacent ruleset survey and syscall-governance note together
- no new wording here implies extra shared replay steps beyond the current Phase 13 build-and-make route
- syscall-governance edits are recorded in the syscall-governance note instead of being duplicated here
- any still-missing direct ruleset companions stay framed as repo-reality gaps rather than as shipped current-`master` evidence
