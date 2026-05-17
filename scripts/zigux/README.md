# scripts/zigux

This directory holds shipped Zigux validation helpers and compact reminder surfaces.

## Phase 1

- Phase 1 flow - the current host-tools reminder packet keeps the closed helper tranche reviewable through the live owner-map, string-review, and bench guards instead of rebuilding the broader installer-backed closure packet from older missing routes
- `python3 scripts/zigux/check-phase1-string-review-packet.py --self-test`, `python3 scripts/zigux/check-phase1-direct-owner-markers.py --self-test`, and `python3 scripts/zigux/check-phase1-bench.py --self-test` replay the shipped bounded Phase 1 reminder checks
- `scripts/zigux/check-phase1-string-review-packet.py`, `scripts/zigux/check-phase1-direct-owner-markers.py`, and `scripts/zigux/check-phase1-bench.py` keep the shipped string-review, direct-owner, and bench reminder packet explicit from the scripts root
- `Documentation/zigux/phase1-host-helper-lane-sequencing.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, `zigux/tests/README.md`, and `zigux/tests/fixtures/phase1_helper_manifest.json` remain the current reminder-surface companions for that packet
- repeated authenticated reads on current `master` still return missing for `scripts/zigux/install-zig.py`, `scripts/zigux/check-phase1-installer-review-surfaces.py`, `scripts/zigux/check-phase1-installer-companion-checks.py`, `Documentation/zigux/phase1-closure.md`, `scripts/zigux/validate-phase1.py`, `scripts/zigux/validate-phase1-closure.py`, `scripts/zigux/check-phase1-parity.py`, `zigux/tests/phase1_helpers.zig`, `zigux/tests/phase1_bench.zig`, `zigux/tests/fixtures/phase1_bench_expectations.json`, and `zigux/tests/fixtures/phase1_helpers_c_harness.c`, so treat those installer-backed, closure-side, and replay routes as historical packet members that need fresh re-materialization before they are reused as direct current-`master` reminder evidence
- the current direct-anchor tie-breakers stay helper-local: bitmap, find_bit, rbtree, and string reopen only inside their existing helper-local anchors or already-committed shared fixture keys, while the other nine closed helpers stay parked unless the shared replay or reminder packet drifts
