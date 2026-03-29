const std = @import("std");
const abi = @import("abi_bindings");
const policy_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_plan");

const ParentView = abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyView;

fn emptySummary() abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary {
    return std.mem.zeroInit(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary, .{});
}

pub fn viewFromParent(
    parent: ParentView,
    primary_budget: u32,
    deferred_budget: u32,
) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetView {
    return .{
        .parent = parent,
        .primary_budget = primary_budget,
        .deferred_budget = deferred_budget,
        .reserved = 0,
    };
}

pub fn asParentView(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetView) ParentView {
    return view.parent;
}

pub fn isValid(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetView) bool {
    if (view.reserved != 0) return false;
    return policy_plan.isValid(view.parent);
}

pub fn summarize(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetView) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetSummary {
    if (!isValid(view)) return emptySummary();

    const parent_summary = policy_plan.summarize(view.parent);
    var summary = emptySummary();
    summary.parent = parent_summary;
    summary.budget_flags = 0;
    summary.primary_budget_before = view.primary_budget;
    summary.primary_budget_after = view.primary_budget;
    summary.deferred_budget_before = view.deferred_budget;
    summary.deferred_budget_after = view.deferred_budget;
    summary.budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_NONE;

    switch (parent_summary.policy_status) {
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SKIPPED => {
            summary.budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_SKIPPED;
            summary.skipped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SUPPRESSED => {
            summary.budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_SUPPRESSED;
            summary.suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DROPPED => {
            summary.budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DROPPED;
            summary.dropped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_HELD => {
            summary.budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_HELD;
            summary.held_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DEFERRED => {
            summary.budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_BUDGET_APPLIED;
            if (summary.deferred_budget_after > 0) {
                summary.deferred_budget_after -= 1;
                summary.budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_BUDGET_USED;
                summary.budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DEFERRED;
                summary.deferred_count = 1;
            } else {
                summary.budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_BUDGET_EXHAUSTED;
                summary.budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DROPPED;
                summary.dropped_count = 1;
            }
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_ACKED,
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_COALESCED,
        => {
            summary.budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_BUDGET_APPLIED;
            if (summary.primary_budget_after > 0) {
                summary.primary_budget_after -= 1;
                summary.budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_PRIMARY_BUDGET_USED;
                if (parent_summary.policy_status == abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_ACKED) {
                    summary.budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_ACKED;
                    summary.acked_count = 1;
                } else {
                    summary.budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_COALESCED;
                    summary.coalesced_count = 1;
                }
            } else {
                summary.budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_PRIMARY_BUDGET_EXHAUSTED;
                if (summary.deferred_budget_after > 0) {
                    summary.deferred_budget_after -= 1;
                    summary.budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_BUDGET_USED;
                    summary.budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DEFERRED;
                    summary.deferred_count = 1;
                } else {
                    summary.budget_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_FLAG_DEFERRED_BUDGET_EXHAUSTED;
                    summary.budget_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DROPPED;
                    summary.dropped_count = 1;
                }
            }
        },
        else => {},
    }

    return summary;
}
