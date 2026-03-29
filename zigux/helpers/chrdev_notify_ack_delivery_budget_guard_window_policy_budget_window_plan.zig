const std = @import("std");
const abi = @import("abi_bindings");
const budget_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_plan");

const ParentView = abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetView;

fn emptySummary() abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary {
    return std.mem.zeroInit(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary, .{});
}

pub fn viewFromParent(
    parent: ParentView,
    budget_window: u32,
    budget_window_floor: u32,
) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowView {
    return .{
        .parent = parent,
        .budget_window = budget_window,
        .budget_window_floor = budget_window_floor,
        .reserved = 0,
    };
}

pub fn asParentView(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowView) ParentView {
    return view.parent;
}

pub fn isValid(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowView) bool {
    if (view.reserved != 0) return false;
    return budget_plan.isValid(view.parent);
}

pub fn summarize(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowView) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowSummary {
    if (!isValid(view)) return emptySummary();

    const parent_summary = budget_plan.summarize(view.parent);
    var summary = emptySummary();
    summary.parent = parent_summary;
    summary.budget_window_flags = 0;
    summary.budget_window_before = view.budget_window;
    summary.budget_window_after = view.budget_window;
    summary.budget_window_floor = view.budget_window_floor;
    summary.budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_NONE;

    switch (parent_summary.budget_status) {
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_SUPPRESSED => {
            summary.budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SUPPRESSED;
            summary.suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_SKIPPED => {
            summary.budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_SKIPPED;
            summary.skipped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DROPPED => {
            summary.budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DROPPED;
            summary.dropped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_HELD => {
            summary.budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_HELD;
            summary.held_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_DEFERRED,
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_ACKED,
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_COALESCED,
        => {
            summary.budget_window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_APPLIED;
            if (summary.budget_window_before == 0) {
                summary.budget_window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_EXHAUSTED;
                summary.budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DROPPED;
                summary.dropped_count = 1;
            } else if (summary.budget_window_before <= view.budget_window_floor) {
                summary.budget_window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_FLOOR_HELD;
                summary.budget_window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_FLOOR_BLOCKED;
                summary.budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_HELD;
                summary.held_count = 1;
            } else {
                summary.budget_window_after -= 1;
                summary.budget_window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_FLAG_WINDOW_USED;
                switch (parent_summary.budget_status) {
                    abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_ACKED => {
                        summary.budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_ACKED;
                        summary.acked_count = 1;
                    },
                    abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_STATUS_COALESCED => {
                        summary.budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_COALESCED;
                        summary.coalesced_count = 1;
                    },
                    else => {
                        summary.budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_STATUS_DEFERRED;
                        summary.deferred_count = 1;
                    },
                }
            }
        },
        else => {},
    }

    return summary;
}
