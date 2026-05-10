# Phase 3 ABI Binding Repair Helper

This note records the bounded helper that repairs the exact fused Phase 3 ABI bindings tail currently called out by the syntax gate.

## Status

- `PHASE3_ABI_BINDING_REPAIR_SCOPE=one exact fused chrdev notify ack tail pair`
- `PHASE3_ABI_BINDING_REPAIR_PATH=scripts/zigux/repair-phase3-fused-abi-bindings.py`
- `PHASE3_ABI_BINDING_REPAIR_TARGET=zigux/bindings/abi.zig`
- `PHASE3_ABI_BINDING_REPAIR_STATUS_SYMBOL=CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED`
- `PHASE3_ABI_BINDING_REPAIR_BUDGET_SYMBOL=CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED`
- `PHASE3_ABI_BINDING_REPAIR_USAGE=python3 scripts/zigux/repair-phase3-fused-abi-bindings.py zigux/bindings/abi.zig --in-place`
- `PHASE3_ABI_BINDING_REPAIR_CHECK=python3 scripts/zigux/repair-phase3-fused-abi-bindings.py zigux/bindings/abi.zig --check`
- `PHASE3_ABI_BINDING_REPAIR_SELF_TEST=python3 scripts/zigux/repair-phase3-fused-abi-bindings.py --self-test`

## Why It Exists

- the live Phase 3 ABI packet already has a focused syntax gate that reports the exact fused tail pair in `zigux/bindings/abi.zig`
- this helper gives the lane a trustworthy, narrow rewrite path for that one pair without hand-editing the whole large bindings blob
- the helper is deliberately exact-match only, so it does not pretend to be a general bindings formatter or a broader Phase 3 closure step

## Boundary

- it only rewrites one exact `; pub const` fragment
- it fails closed when the pair is missing, duplicated, or already in a mixed repaired-plus-fused state
- broader chrdev ladder growth, validator wiring, and wrapper-family work stay out of scope for this helper
