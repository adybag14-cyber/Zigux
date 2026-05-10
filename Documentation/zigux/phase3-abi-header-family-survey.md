# Phase 3 ABI Header Family Survey

This note keeps one already-landed Phase 3 ABI header packet reviewable without widening beyond the shared ABI surface.

## Status

- `PHASE3_ABI_HEADER_FAMILY=chrdev_notify_ack_window_policy_budget_window_delivery_window-plus-delivery_budget_guard_window_policy_budget_window_delivery`
- `PHASE3_ABI_HEADER_PATH=include/zigux/abi.h`
- `PHASE3_ABI_HEADER_BLOB_SHA=c588b6d2c81659ff8996495d001dd1ebad7df1b1`
- `PHASE3_ABI_BINDINGS_PATH=zigux/bindings/abi.zig`
- `PHASE3_ABI_BINDINGS_BLOB_SHA=d8df5a2a888ed29c71d2c75e7f6cd0bd18d37771`
- `PHASE3_ABI_HEADER_FAMILY_SURVEY_PATH=scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `PHASE3_ABI_HEADER_FAMILY_SURVEY_SCOPE=two bounded adjacent chrdev notify ack header-family footholds inside the shared phase3 abi packet`
- `PHASE3_ABI_HEADER_PRIMARY_STATUS_SYMBOL=ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED`
- `PHASE3_ABI_BINDING_PRIMARY_STATUS_SYMBOL=CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED`
- `PHASE3_ABI_HEADER_PRIMARY_BUDGET_SYMBOL=ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED`
- `PHASE3_ABI_BINDING_PRIMARY_BUDGET_SYMBOL=CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED`
- `PHASE3_ABI_HEADER_PRIMARY_VIEW_SYMBOL=struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {`
- `PHASE3_ABI_BINDING_PRIMARY_VIEW_SYMBOL=pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView = extern struct {`
- `PHASE3_ABI_HEADER_PRIMARY_SUMMARY_SYMBOL=struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {`
- `PHASE3_ABI_BINDING_PRIMARY_SUMMARY_SYMBOL=pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary = extern struct {`
- `PHASE3_ABI_HEADER_ADJACENT_STATUS_SYMBOL=ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_HELD`
- `PHASE3_ABI_BINDING_ADJACENT_STATUS_SYMBOL=CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_STATUS_HELD`
- `PHASE3_ABI_HEADER_ADJACENT_BUDGET_SYMBOL=ZIGUX_CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_BUDGET_FLAG_BUDGET_APPLIED`
- `PHASE3_ABI_BINDING_ADJACENT_BUDGET_SYMBOL=CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_BUDGET_FLAG_BUDGET_APPLIED`
- `PHASE3_ABI_HEADER_ADJACENT_VIEW_SYMBOL=struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_view {`
- `PHASE3_ABI_BINDING_ADJACENT_VIEW_SYMBOL=pub const ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryView = extern struct {`
- `PHASE3_ABI_HEADER_ADJACENT_SUMMARY_SYMBOL=struct zigux_chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_summary {`
- `PHASE3_ABI_BINDING_ADJACENT_SUMMARY_SYMBOL=pub const ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliverySummary = extern struct {`
- `PHASE3_ABI_HEADER_FAMILY_GATE=python3 scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `PHASE3_ABI_HEADER_FAMILY_SURVEY_BLOB_SHA=f78604a8aabd0f53a936e5025a2207ef8b7221fc`
- `PHASE3_ABI_HEADER_FAMILY_NEXT_STEP=extend-the-landed-delivery-budget-guard-packet-one-foothold-at-a-time-before-widening-the-phase3-abi-surface`

## Current Repo Evidence

- the shared ABI packet already carried one exact chrdev view-plus-summary foothold in the baseline constant-parity survey, but that still left the directly adjacent delivery-budget-guard family implicit inside the larger header ladder.
- this dedicated survey now keeps two directly adjacent families explicit by fail-closing on one exact status constant pair, one exact budget-flag constant pair, and one exact view-plus-summary type pair for both the existing `chrdev_notify_ack_window_policy_budget_window_delivery_window` foothold and the adjacent `chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery` foothold across `include/zigux/abi.h` and `zigux/bindings/abi.zig`.
- the survey stays deliberately narrower than broader chrdev-family growth: it does not claim generator coverage, wider header-family closure, export/UAPI growth, helper behavior changes, or a new top-level ABI packet.
- live `master` already wires this dedicated survey through `scripts/zigux/validate_phase3_selftest.py` and the shipped `make -C zigux phase3-validate` route in `zigux/Makefile`, so the next honest same-lane gap is no longer the adjacent family foothold itself; it is keeping any further proof growth inside this same bounded packet rather than treating more top-level `abi.h` surface as implicitly covered.

## Shared Surface Reminder

- broad Phase 3 shared summaries should keep `Documentation/zigux/phase3-abi-header-family-survey.md` and `scripts/zigux/validate-phase3-abi-header-family-survey.py` explicit whenever they name the validator-support packet or the baseline constant-parity survey.
- `scripts/zigux/validate_phase3_selftest.py` and `zigux/Makefile` already treat the header-family survey as part of the shipped validator-support roster, so future same-lane shared-surface wording passes should refresh `scripts/zigux/README.md`, `Documentation/zigux/README.md`, `Documentation/zigux/review-checklist.md`, and `zigux/tests/README.md` before treating this landed two-family proof as implicit again.
- do not let `scripts/zigux/survey-phase3-abi-constant-parity.py` stand in for this narrower landed family proof; the baseline constant survey and this dedicated family survey carry different bounded reviewability claims.

## Boundary

- stay inside the authoritative C header and curated Zig bindings only
- extend this survey one exact foothold at a time inside the landed adjacent pair
- treat broader chrdev ladder growth as out of scope until it lands with its own bounded proof

## Non-Goals

- no new helper behavior
- no export-shim or UAPI widening
- no wider chrdev-family closure claim