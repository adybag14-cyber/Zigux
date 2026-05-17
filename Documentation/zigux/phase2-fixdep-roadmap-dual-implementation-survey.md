# Phase 2 fixdep roadmap dual-implementation survey

Lane: `P2-L01`

Current `master` already satisfies the roadmap's selected dual-implementation expectation for the bounded `fixdep` lane.

## Roadmap anchor

- Phase 2 names `scripts/zigux/fixdep.zig` as a recommended Zigux destination under toolchain and Kbuild enablement.
- The same roadmap says selected dual implementations and wrapper-first handling should remain the default where parser-heavy tooling or risky semantics are involved.

## Ledger anchor

- The bootstrap ledger records the initial bounded dual-implementation delivery in commit-train item 11.
- The same ledger records the widened parity fixture packet in item 13, which is the bounded follow-through that made the direct diff surface reviewable instead of leaving the dual-implementation claim as a one-case stub.

## Current repo evidence

- `scripts/zigux/fixdep.zig` is present on current `master` and already carries helper-local replay coverage beyond the original seed fixture packet.
- `scripts/zigux/check-fixdep-diff.py` and `scripts/zigux/check-phase2-fixdep-gate.py` remain the dedicated scripts-side guards for the same lane.
- `zigux/tests/fixtures/fixdep/cases.json` remains the shared fixture packet that keeps the direct C-versus-Zig comparison explicit at the tests root.
- `Documentation/zigux/phase2-closure.md`, `scripts/zigux/README.md`, and `zigux/tests/README.md` already keep the live fixdep packet visible as part of the broader Phase 2 reminder surface.

## Survey result

- Current `master` already holds both halves that the roadmap asks for in this bounded lane: the Zig implementation in `scripts/zigux/fixdep.zig` and the continued dual-implementation proof surface around it.
- The active gap is not missing dual-implementation code or missing parity fixtures.
- The smaller remaining risk was traceability: the live reminder packet did not clearly preserve a shipped lane artifact that says the roadmap-facing dual-implementation survey is already satisfied and parked.

## Next safe step

1. Keep this lane parked unless a new fixdep-local or shared Phase 2 reminder drift reappears.
2. When the lane reopens, start by rerunning `python3 scripts/zigux/check-phase2-fixdep-roadmap-dual-implementation.py`, `python3 scripts/zigux/check-phase2-fixdep-gate.py`, `python3 scripts/zigux/check-fixdep-diff.py`, and `zig test scripts/zigux/fixdep.zig` before widening into any other Phase 2 tool.
