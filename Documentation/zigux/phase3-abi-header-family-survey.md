# Phase 3 ABI Header Family Survey

This note keeps one already-landed Phase 3 ABI header family reviewable without widening beyond the shared ABI packet.

## Status

- `PHASE3_ABI_HEADER_FAMILY=chrdev_notify_ack_window_policy_budget_window_delivery_window`
- `PHASE3_ABI_HEADER_PATH=include/zigux/abi.h`
- `PHASE3_ABI_HEADER_BLOB_SHA=c588b6d2c81659ff8996495d001dd1ebad7df1b1`
- `PHASE3_ABI_BINDINGS_PATH=zigux/bindings/abi.zig`
- `PHASE3_ABI_BINDINGS_BLOB_SHA=d8df5a2a888ed29c71d2c75e7f6cd0bd18d37771`
- `PHASE3_ABI_HEADER_FAMILY_SURVEY_PATH=scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `PHASE3_ABI_HEADER_FAMILY_SURVEY_SCOPE=one bounded chrdev notify ack window policy budget window delivery window family survey`
- `PHASE3_ABI_HEADER_STATUS_SYMBOL=ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED`
- `PHASE3_ABI_BINDING_STATUS_SYMBOL=CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED`
- `PHASE3_ABI_HEADER_BUDGET_SYMBOL=ZIGUX_CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED`
- `PHASE3_ABI_BINDING_BUDGET_SYMBOL=CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED`
- `PHASE3_ABI_HEADER_VIEW_SYMBOL=struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_view {`
- `PHASE3_ABI_BINDING_VIEW_SYMBOL=pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView = extern struct {`
- `PHASE3_ABI_HEADER_SUMMARY_SYMBOL=struct zigux_chrdev_notify_ack_window_policy_budget_window_delivery_window_summary {`
- `PHASE3_ABI_BINDING_SUMMARY_SYMBOL=pub const ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary = extern struct {`
- `PHASE3_ABI_HEADER_FAMILY_GATE=python3 scripts/zigux/validate-phase3-abi-header-family-survey.py`
- `PHASE3_ABI_HEADER_FAMILY_SURVEY_BLOB_SHA=cee93aa28721df7cad2f744cb4dd7709de41f8a8`
- `PHASE3_ABI_HEADER_FAMILY_NEXT_STEP=extend-the-same-family-survey-one-foothold-at-a-time-before-widening-the-phase3-abi-surface`

## Current Repo Evidence

- the shared ABI packet already carried one exact chrdev view-plus-summary foothold in the baseline constant-parity survey, but it did not yet carry a dedicated family note for the landed `chrdev_notify_ack_window_policy_budget_window_delivery_window` boundary.
- this dedicated survey keeps the bounded family explicit by fail-closing on one exact status constant pair, one exact budget-flag constant pair, and the current view-plus-summary type pair across `include/zigux/abi.h` and `zigux/bindings/abi.zig`.
- the survey stays deliberately narrower than broader chrdev-family growth: it does not claim generator coverage, wider header-family closure, export/UAPI growth, helper behavior changes, or a new top-level ABI packet.

## Boundary

- stay inside the authoritative C header and curated Zig bindings only
- extend this survey one exact family foothold at a time
- treat broader chrdev ladder growth as out of scope until it lands with its own bounded proof

## Non-Goals

- no new helper behavior
- no export-shim or UAPI widening
- no wider chrdev-family closure claim
