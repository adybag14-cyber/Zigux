# Phase 1 Workflow Viability

- `PHASE1_WORKFLOW_STATUS=active`
- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 workflow preflight and early-signal guard`
- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-preflight`
- `PHASE1_WORKFLOW_PREFLIGHT=Preflight current Phase 1 workflow viability checker after Setup Python and before the lane-local workflow viability pair`
- `PHASE1_WORKFLOW_EARLY_SIGNAL_ORDER=Setup Python,Preflight current Phase 1 workflow viability checker,Self-test current Phase 1 workflow viability checker,Check current Phase 1 workflow viability,Setup pinned Zig toolchain`
- `PHASE1_WORKFLOW_VIABILITY_PAIR=Self-test current Phase 1 workflow viability checker plus Check current Phase 1 workflow viability before pinned Zig setup`
- `PHASE1_WORKFLOW_VIABILITY_NEXT_STEP=exact-reread the next zigux-bootstrap verdict now that the lane-local viability pair runs before pinned Zig setup`
- keep this packet scoped to the lightweight Lane 17 workflow preflight and early-signal guard.
- run the preflight plus the lane-local workflow viability pair before pinned Zig setup so the branch still emits Lane 17 signal when the external archive path fails first.
- keep the broader Phase 1 closure and Phase 3 interop workflow packet order unchanged after this early-signal insertion.
