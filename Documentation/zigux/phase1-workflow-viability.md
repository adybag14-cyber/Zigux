# Phase 1 Workflow Viability

- `PHASE1_WORKFLOW_STATUS=active`
- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 workflow-viability guard`
- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-viability`
- `PHASE1_WORKFLOW_PHASE1_TAIL=Self-test current Phase 1 shared reminder checker,Check current Phase 1 shared reminder packet,Self-test current Phase 1 closure validator,Check current Phase 1 closure packet`
- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 closure packet and before current Phase 3 interop packet`
- `PHASE1_WORKFLOW_REQUIRED_ADJACENCY=Check current Phase 1 closure packet,Self-test current Phase 1 workflow viability checker,Check current Phase 1 workflow viability,Self-test current Phase 3 interop packet`
- `PHASE1_WORKFLOW_PHASE3_BUFFER=Self-test current Phase 3 interop packet,Check current Phase 3 interop packet,Self-test current Phase 3 low-level wrapper survey validator,Check current Phase 3 low-level wrapper survey packet,Run current Phase 3 low-level wrapper replay,Run current Phase 3 shared tests-root packet,Run current Phase 3 ABI dump replay,Run current Phase 1 shared tests-root smoke`
- `PHASE1_WORKFLOW_PHASE4_ARTIFACT_DIFF_TAIL=Self-test current Phase 4 artifact-diff helper,Self-test current Phase 4 artifact-diff determinism checker,Check current Phase 4 artifact-diff determinism packet,Self-test current Phase 4 artifact-diff validator replay checker,Check current Phase 4 artifact-diff validator replay packet`
- `PHASE1_WORKFLOW_FORBIDDEN_HISTORICAL_SNIPPETS=scripts/zigux/validate-phase1.py,scripts/zigux/check-phase1-parity.py,zig build test --build-file zigux/tests/build.zig,zig build bench --build-file zigux/tests/build.zig,make -C zigux phase1-validate,make -C zigux phase1-test,make -C zigux phase1-bench`
- keep the lane scoped to the current closure-validator-plus-viability packet instead of reviving the older validator-first, parity, or make-route Phase 1 replay family.
- keep the workflow-viability pair immediately after the current Phase 1 closure packet, then preserve the current Phase 3 buffer before the shared Phase 1 smoke route.
- keep the current Phase 4 artifact-diff helper, determinism, and validator replay block explicit after the Phase 3 buffer when this packet is replayed.
- if the workflow moves again, refresh this same three-file packet first instead of widening into unrelated Phase 1 reminder or closure lanes.
