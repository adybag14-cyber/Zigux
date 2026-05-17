# Phase 2 Current Repo-Reality Gap

This note records the current directly readable Phase 2 toolchain packet on `master` as re-read on 2026-05-17.

## What Still Materializes

The older cross-preflight checker-side reminder drift is already closed on current `master`.

Direct current-`master` reads in this slot still materialize these bounded Phase 2 reminder surfaces:

- `Documentation/zigux/README.md`
- `Documentation/zigux/review-checklist.md`
- `zigux/tests/README.md`
- `scripts/zigux/check-phase2-tests-readme-alignment.py`
- `scripts/zigux/check-phase2-cross-selftest-alignment.py`
- `.github/workflows/zigux-bootstrap.yml`

The surviving docs-root and checker surfaces already agree that the `phase2-cross` target-mode replay reaches the same live toolchain preflight through `python3 scripts/zigux/check-phase2-cross.py --target <matrix-zig-target>`, because that target-mode path reruns `python3 scripts/zigux/check-zig-toolchain.py --zig "<resolved-zig>"` before the cross-target Zig tests.

## What Does Not Materialize

Direct current-`master` reads in this slot still return missing for these broader Phase 2 toolchain files:

- `Documentation/zigux/phase2-toolchain-bootstrap-notes.md`
- `Documentation/zigux/phase2-closure.md`
- `scripts/zigux/validate-phase2.py`
- `scripts/zigux/validate-phase2-closure.py`
- `scripts/zigux/check-phase2-cross.py`
- `scripts/zigux/check-phase2-toolchain-pin-scope.py`
- `zigux/tests/fixtures/phase2_cross_targets.json`
- `zigux/Makefile`

The current bootstrap workflow also no longer materializes a dedicated Phase 2 job in the directly readable file body.

## Follow-Through

The next honest same-lane follow-through should stay bounded to one reminder or checker surface at a time:

1. either align one shared Phase 2 reminder surface with the current repo-reality gap above
2. or re-materialize one missing Phase 2 toolchain file family before restoring validator-first, targets-manifest, or Linux-style Make-route claims

Do not reopen the older two-file checker-side cross-preflight residual from 2026-05-16 unless a fresh reread shows that wording drift has returned on current `master`.
