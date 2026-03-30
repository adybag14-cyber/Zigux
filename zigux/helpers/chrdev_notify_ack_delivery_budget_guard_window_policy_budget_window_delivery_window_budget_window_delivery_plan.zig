const std = @import("std");
const abi = @import("abi_bindings");
const budget_window_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_plan");
const ParentView = abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowView;
fn emptySummary() abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary {
    return std.mem.zeroInit(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary, .{});
}
pub fn viewFromParent(
    parent: ParentView,
    delivery_window_budget_window_delivery_budget: u32,
    deferred_delivery_window_budget_window_delivery_budget: u32,
) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryView {
    return .{
        .parent = parent,
        .delivery_window_budget_window_delivery_budget = delivery_window_budget_window_delivery_budget,
        .deferred_delivery_window_budget_window_delivery_budget = deferred_delivery_window_budget_window_delivery_budget,
        .reserved = 0,
    };
}
pub fn asParentView(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryView) ParentView {
    return view.parent;
}
pub fn isValid(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryView) bool {
    if (view.reserved != 0) return false;
    return budget_window_plan.isValid(view.parent);
}
pub fn summarize(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryView) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliverySummary {
    if (!isValid(view)) return emptySummary();
    const parent_summary = budget_window_plan.summarize(view.parent);
    var summary = emptySummary();
    summary.parent = parent_summary;
    summary.delivery_window_budget_window_delivery_flags = 0;
    summary.delivery_window_budget_window_delivery_before = view.delivery_window_budget_window_delivery_budget;
    summary.delivery_window_budget_window_delivery_after = view.delivery_window_budget_window_delivery_budget;
    summary.deferred_delivery_window_budget_window_delivery_before = view.deferred_delivery_window_budget_window_delivery_budget;
    summary.deferred_delivery_window_budget_window_delivery_after = view.deferred_delivery_window_budget_window_delivery_budget;
    summary.delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_NONE;
    switch (parent_summary.delivery_window_budget_window_status) {
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SUPPRESSED => {
            summary.delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SUPPRESSED;
            summary.suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED => {
            summary.delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_SKIPPED;
            summary.skipped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DROPPED => {
            summary.delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED;
            summary.dropped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_HELD => {
            summary.delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_HELD;
            summary.held_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DEFERRED => {
            summary.delivery_window_budget_window_delivery_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_BUDGET_APPLIED;
            if (summary.deferred_delivery_window_budget_window_delivery_after > 0) {
                summary.deferred_delivery_window_budget_window_delivery_after -= 1;
                summary.delivery_window_budget_window_delivery_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_DELIVERY_BUDGET_USED;
                summary.delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED;
                summary.deferred_count = 1;
            } else {
                summary.delivery_window_budget_window_delivery_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_DELIVERY_BUDGET_EXHAUSTED;
                summary.delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED;
                summary.dropped_count = 1;
            }
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_ACKED,
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_COALESCED,
        => {
            summary.delivery_window_budget_window_delivery_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_BUDGET_APPLIED;
            if (summary.delivery_window_budget_window_delivery_after > 0) {
                summary.delivery_window_budget_window_delivery_after -= 1;
                summary.delivery_window_budget_window_delivery_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_PRIMARY_DELIVERY_BUDGET_USED;
                if (parent_summary.delivery_window_budget_window_status == abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_ACKED) {
                    summary.delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_ACKED;
                    summary.acked_count = 1;
                } else {
                    summary.delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_COALESCED;
                    summary.coalesced_count = 1;
                }
            } else {
                summary.delivery_window_budget_window_delivery_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_PRIMARY_DELIVERY_BUDGET_EXHAUSTED;
                if (summary.deferred_delivery_window_budget_window_delivery_after > 0) {
                    summary.deferred_delivery_window_budget_window_delivery_after -= 1;
                    summary.delivery_window_budget_window_delivery_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_DELIVERY_BUDGET_USED;
                    summary.delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DEFERRED;
                    summary.deferred_count = 1;
                } else {
                    summary.delivery_window_budget_window_delivery_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_FLAG_DEFERRED_DELIVERY_BUDGET_EXHAUSTED;
                    summary.delivery_window_budget_window_delivery_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_STATUS_DROPPED;
                    summary.dropped_count = 1;
                }
            }
        },
        else => {},
    }
    return summary;
}
