# Phase 3 IDA Policy Slice

PHASE3_STATUS=active
PHASE3_SLICE=ida-policy-view-interop
PHASE3_VALIDATE_GATE=python3 scripts/zigux/validate-phase3.py
PHASE3_INTEROP_GATE=python3 scripts/zigux/run-phase3-checks.py --slug ida-policy
PHASE3_TEST_GATE=zig build phase3-test --build-file zigux/tests/build.zig

Scope
- add a bounded `ida` fit-policy planning view over raw allocation bits
- expose `first-fit` and `last-fit` selection without pretending to allocate
- keep the summary explicit about truncation, discovery, exhaustion, and longest-free-run state
- export both the selected fit and the alternate fit for parity checking

Files
- `include/zigux/abi.h`
- `include/linux/zigux.h`
- `zigux/helpers/ida_policy_view.zig`
- `zigux/tests/phase3_ida_policy_dump.zig`
- `zigux/tests/fixtures/phase3_ida_policy/phase3_ida_policy_c_harness.c`
- `scripts/zigux/check-phase3-ida-policy.py`

Boundary
- this is not full `ida`
- this is not a live allocator
- this only proves bounded fit-policy summary parity over committed bitmap fixtures
