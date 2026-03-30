const std = @import("std");
const abi = @import("abi_bindings");
const delivery_window_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_plan");

const ParentView = abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowView;

fn emptySummary() abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetSummary {
    return std.mem.zeroInit(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, .{});
}

pub fn viewFromParent(
    parent: ParentView,
    delivery_window_budget: u32,
    deferred_delivery_window_budget: u32,
) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetView {
    return .{
        .parent = parent,
        .delivery_window_budget = delivery_window_budget,
        .deferred_delivery_window_budget = deferred_delivery_window_budget,
        .reserved = 0,
    };
}

pub fn asParentView(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetView) ParentView {
    return view.parent;
}

pub fn isValid(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetView) bool {
    if (view.reserved != 0) return false;
    return delivery_window_plan.isValid(view.parent);
}

pub fn summarize(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetView) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetSummary {
    if (!isValid(view)) return emptySummary();

    const parent_summary = delivery_window_plan.summarize(view.parent);
    var summary = emptySummary();
    summary.parent = parent_summary;
    summary.delivery_window_budget_flags = 0;
    summary.delivery_window_budget_before = view.delivery_window_budget;
    summary.delivery_window_budget_after = view.delivery_window_budget;
    summary.deferred_delivery_window_budget_before = view.deferred_delivery_window_budget;
    summary.deferred_delivery_window_budget_after = view.deferred_delivery_window_budget;
    summary.delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE;

    switch (parent_summary.delivery_window_status) {
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SUPPRESSED => {
            summary.delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SUPPRESSED;
            summary.suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED => {
            summary.delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SKIPPED;
            summary.skipped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED => {
            summary.delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED;
            summary.dropped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_HELD => {
            summary.delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_HELD;
            summary.held_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED => {
            summary.delivery_window_budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED;
            if (summary.deferred_delivery_window_budget_after > 0) {
                summary.deferred_delivery_window_budget_after -= 1;
                summary.delivery_window_budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_DELIVERY_WINDOW_BUDGET_USED;
                summary.delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED;
                summary.deferred_count = 1;
            } else {
                summary.delivery_window_budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_DELIVERY_WINDOW_BUDGET_EXHAUSTED;
                summary.delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED;
                summary.dropped_count = 1;
            }
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED,
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_COALESCED,
        => {
            summary.delivery_window_budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED;
            if (summary.delivery_window_budget_after > 0) {
                summary.delivery_window_budget_after -= 1;
                summary.delivery_window_budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DELIVERY_WINDOW_BUDGET_USED;
                if (parent_summary.delivery_window_status == abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED) {
                    summary.delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED;
                    summary.acked_count = 1;
                } else {
                    summary.delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED;
                    summary.coalesced_count = 1;
                }
            } else {
                summary.delivery_window_budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DELIVERY_WINDOW_BUDGET_EXHAUSTED;
                if (summary.deferred_delivery_window_budget_after > 0) {
                    summary.deferred_delivery_window_budget_after -= 1;
                    summary.delivery_window_budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_DELIVERY_WINDOW_BUDGET_USED;
                    summary.delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED;
                    summary.deferred_count = 1;
                } else {
                    summary.delivery_window_budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_DEFERRED_DELIVERY_WINDOW_BUDGET_EXHAUSTED;
                    summary.delivery_window_budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED;
                    summary.dropped_count = 1;
                }
            }
        },
        else => {},
    }

    return summary;
}
