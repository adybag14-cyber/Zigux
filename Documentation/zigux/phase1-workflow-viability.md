# Phase 1 Workflow Viability

- `PHASE1_WORKFLOW_STATUS=active`
- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 workflow preflight guard`
- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-preflight`
- `PHASE1_WORKFLOW_PREFLIGHT=Preflight current Phase 1 workflow viability checker after Setup Python and before Setup pinned Zig toolchain`
- `PHASE1_WORKFLOW_INSERTION_POINT=after current Phase 1 shared reminder packet and before current Phase 3 interop packet`
- `PHASE1_WORKFLOW_REQUIRED_ADJACENCY=Check current Phase 1 shared reminder packet,Self-test current Phase 1 workflow viability checker,Check current Phase 1 workflow viability,Self-test current Phase 3 interop packet`
- keep this packet scoped to the lightweight Lane 17 workflow preflight and the existing workflow-viability pair.
- run the preflight before pinned Zig setup so the lane still emits direct signal when the external archive path fails first.
- preserve the shared-reminder to Phase 3 handoff around the lane-local workflow-viability pair instead of widening back into older closure-side cues.
