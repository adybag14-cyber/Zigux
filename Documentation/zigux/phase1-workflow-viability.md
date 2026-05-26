# Phase 1 Workflow Viability

- `PHASE1_WORKFLOW_STATUS=active`
- `PHASE1_WORKFLOW_SCOPE=current bootstrap Phase 1 workflow preflight guard`
- `PHASE1_WORKFLOW_NOTE_OWNER=lane17-phase1-workflow-preflight`
- `PHASE1_WORKFLOW_PREFLIGHT=Preflight current Phase 1 workflow viability checker after Setup Python and before Setup pinned Zig toolchain`
- `PHASE1_WORKFLOW_PREFLIGHT_ORDER=Setup Python,Preflight current Phase 1 workflow viability checker,Setup pinned Zig toolchain`
- `PHASE1_WORKFLOW_VIABILITY_NEXT_STEP=wire the lane-local workflow-viability self-test and packet-check pair after the current Phase 1 closure packet and before the current Phase 3 interop packet`
- keep this packet scoped to the lightweight Lane 17 workflow preflight guard.
- run the preflight before pinned Zig setup so the lane still emits direct signal when the external archive path fails first.
- leave the lane-local workflow-viability self-test and packet-check pair as a separate follow-up until the surrounding closure-to-Phase-3 handoff is restacked safely.
