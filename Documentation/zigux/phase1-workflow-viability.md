# Phase 1 Workflow Viability

- `PHASE1_WORKFLOW_STATUS=active`
- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 workflow-viability guard`
- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`
- `PHASE1_WORKFLOW_PHASE2_TAIL=Self-test current Phase 2 shared reminder checker,Check current Phase 2 shared reminder packet,Validate current Phase 2 tool packet`
- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 shared reminder packet and before current Phase 3 interop packet`
- `PHASE1_WORKFLOW_REQUIRED_ADJACENCY=Check current Phase 1 shared reminder packet,Self-test current Phase 1 workflow viability checker,Check current Phase 1 workflow viability,Self-test current Phase 3 interop packet`
- `PHASE1_WORKFLOW_PHASE3_BUFFER=Self-test current Phase 3 interop packet,Check current Phase 3 interop packet,Self-test current Phase 3 low-level wrapper survey validator,Check current Phase 3 low-level wrapper survey packet,Run current Phase 3 low-level wrapper replay,Run current Phase 3 shared tests-root packet,Run current Phase 1 shared tests-root smoke`
- `PHASE1_WORKFLOW_PHASE4_ARTIFACT_DIFF_TAIL=Self-test current Phase 4 artifact-diff helper,Self-test current Phase 4 artifact-diff determinism checker,Self-test current Phase 4 artifact-diff validator replay checker,Check current Phase 4 artifact-diff validator replay packet`
- `PHASE1_WORKFLOW_PHASE9_BUFFER=Self-test current Phase 9 review-checklist boundaries checker,Check current Phase 9 review-checklist boundaries packet,Self-test current Phase 9 trace-events runtime packet checker,Check current Phase 9 trace-events runtime packet`
- `PHASE1_WORKFLOW_PHASE7_HANDOFF=Self-test current Phase 7 shared-control gap checker,Check current Phase 7 shared-control gap packet`
- `PHASE1_WORKFLOW_FORBIDDEN_HISTORICAL_SNIPPETS=scripts/zigux/validate-phase1.py,scripts/zigux/validate-phase1-closure.py,make -C zigux phase1-validate,make -C zigux phase1-test,make -C zigux phase1-bench,python3 scripts/zigux/check-phase1-bench.py`
- keep the lane scoped to the current Phase 1 workflow-viability pair instead of reviving the older closure-side Phase 1 validator routes.
- keep the workflow-viability pair immediately after the current Phase 1 shared reminder packet, then preserve the current Phase 3 buffer before the shared Phase 1 smoke route.
- keep the current Phase 4 artifact-diff helper and validator replay block ahead of the current Phase 9 review-checklist and trace-events packet, then hand off to the Phase 7 shared-control pair.
- if the workflow moves again, refresh this same three-file packet first instead of widening into unrelated reminder or closure lanes.
