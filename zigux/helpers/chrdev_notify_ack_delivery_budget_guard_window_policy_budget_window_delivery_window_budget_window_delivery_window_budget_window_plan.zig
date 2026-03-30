const std = @import("std");
const abi = @import("abi_bindings");
const budget_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan");

const ParentView = abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView;

fn emptySummary() abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowSummary {
    return std.mem.zeroInit(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowSummary, .{});
}

pub fn viewFromParent(
    parent: ParentView,
    delivery_window_budget_window_delivery_window_budget_window: u32,
    delivery_window_budget_window_delivery_window_budget_window_floor: u32,
) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowView {
    return .{
        .parent = parent,
        .delivery_window_budget_window_delivery_window_budget_window = delivery_window_budget_window_delivery_window_budget_window,
        .delivery_window_budget_window_delivery_window_budget_window_floor = delivery_window_budget_window_delivery_window_budget_window_floor,
        .reserved = 0,
    };
}

pub fn asParentView(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowView) ParentView {
    return view.parent;
}

pub fn isValid(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowView) bool {
    if (view.reserved != 0) return false;
    return budget_plan.isValid(view.parent);
}

pub fn summarize(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowView) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowSummary {
    if (!isValid(view)) return emptySummary();

    const parent_summary = budget_plan.summarize(view.parent);
    var summary = emptySummary();
    summary.parent = parent_summary;
    summary.delivery_window_budget_window_delivery_window_budget_window_flags = 0;
    summary.delivery_window_budget_window_delivery_window_budget_window_before = view.delivery_window_budget_window_delivery_window_budget_window;
    summary.delivery_window_budget_window_delivery_window_budget_window_after = view.delivery_window_budget_window_delivery_window_budget_window;
    summary.delivery_window_budget_window_delivery_window_budget_window_floor = view.delivery_window_budget_window_delivery_window_budget_window_floor;
    summary.delivery_window_budget_window_delivery_window_budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_NONE;

    switch (parent_summary.delivery_window_budget_window_delivery_window_budget_status) {
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SUPPRESSED => {
            summary.delivery_window_budget_window_delivery_window_budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SUPPRESSED;
            summary.suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SKIPPED => {
            summary.delivery_window_budget_window_delivery_window_budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED;
            summary.skipped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED => {
            summary.delivery_window_budget_window_delivery_window_budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DROPPED;
            summary.dropped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_HELD => {
            summary.delivery_window_budget_window_delivery_window_budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_HELD;
            summary.held_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED,
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED,
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED,
        => {
            summary.delivery_window_budget_window_delivery_window_budget_window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED;
            if (summary.delivery_window_budget_window_delivery_window_budget_window_before == 0) {
                summary.delivery_window_budget_window_delivery_window_budget_window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_EXHAUSTED;
                summary.delivery_window_budget_window_delivery_window_budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DROPPED;
                summary.dropped_count = 1;
            } else if (summary.delivery_window_budget_window_delivery_window_budget_window_before <= view.delivery_window_budget_window_delivery_window_budget_window_floor) {
                summary.delivery_window_budget_window_delivery_window_budget_window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_FLOOR_HELD;
                summary.delivery_window_budget_window_delivery_window_budget_window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_FLOOR_BLOCKED;
                summary.delivery_window_budget_window_delivery_window_budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DEFERRED;
                summary.deferred_count = 1;
            } else {
                summary.delivery_window_budget_window_delivery_window_budget_window_after -= 1;
                summary.delivery_window_budget_window_delivery_window_budget_window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_USED;
                switch (parent_summary.delivery_window_budget_window_delivery_window_budget_status) {
                    abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED => {
                        summary.delivery_window_budget_window_delivery_window_budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_ACKED;
                        summary.acked_count = 1;
                    },
                    abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED => {
                        summary.delivery_window_budget_window_delivery_window_budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_COALESCED;
                        summary.coalesced_count = 1;
                    },
                    else => {
                        summary.delivery_window_budget_window_delivery_window_budget_window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_DEFERRED;
                        summary.deferred_count = 1;
                    },
                }
            }
        },
        else => {},
    }

    return summary;
}
