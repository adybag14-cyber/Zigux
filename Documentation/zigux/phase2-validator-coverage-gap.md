# Phase 2 Validator Coverage Gap

Current `master` already ships the bootstrap-workflow guard in the workflow and the Phase 2 tools make route, including `scripts/zigux/check-phase2-bootstrap-workflow-routes.py` and the aggregate `make -C zigux phase2` route.

The live repo-tooling gap is narrower than a missing-surface problem: `scripts/zigux/validate-phase2.py` already tracks the checker path, `phase2-tools`, and `phase2-validate`, but the validator still does not require those exact workflow or makefile markers.

This note exists so repo-tooling follow-through can stay truthful while that validator lag remains current. The next bounded repo-tooling step is to widen `validate-phase2.py` so the shipped bootstrap-workflow guard and aggregate `phase2` route become validator-enforced.
