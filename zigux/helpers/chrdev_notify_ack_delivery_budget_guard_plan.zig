const std = @import("std");
const abi = @import("abi_bindings");
const parent_plan = @import("chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_plan");

const ParentView = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetView;

fn emptySummary() abi.ChrdevNotifyAckDeliveryBudgetGuardSummary {
    return std.mem.zeroInit(abi.ChrdevNotifyAckDeliveryBudgetGuardSummary, .{});
}

pub fn viewFromParent(
    parent: ParentView,
    primary_guard_floor: u32,
    deferred_guard_floor: u32,
) abi.ChrdevNotifyAckDeliveryBudgetGuardView {
    return .{
        .parent = parent,
        .primary_guard_floor = primary_guard_floor,
        .deferred_guard_floor = deferred_guard_floor,
        .reserved = 0,
    };
}

pub fn asParentView(view: abi.ChrdevNotifyAckDeliveryBudgetGuardView) ParentView {
    return view.parent;
}

pub fn isValid(view: abi.ChrdevNotifyAckDeliveryBudgetGuardView) bool {
    if (view.reserved != 0) return false;
    return parent_plan.isValid(view.parent);
}

pub fn summarize(view: abi.ChrdevNotifyAckDeliveryBudgetGuardView) abi.ChrdevNotifyAckDeliveryBudgetGuardSummary {
    if (!isValid(view)) return emptySummary();

    const parent_summary = parent_plan.summarize(view.parent);
    var summary = emptySummary();
    summary.parent = parent_summary;
    summary.primary_before = parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_before;
    summary.primary_after = parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after;
    summary.deferred_before = parent_summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_before;
    summary.deferred_after = parent_summary.deferred_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_after;
    summary.primary_guard_floor = view.primary_guard_floor;
    summary.deferred_guard_floor = view.deferred_guard_floor;
    summary.guard_flags = 0;
    summary.guard_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_NONE;

    switch (parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status) {
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SUPPRESSED => {
            summary.guard_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PASSTHROUGH;
            summary.guard_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_SUPPRESSED;
            summary.suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_SKIPPED => {
            summary.guard_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PASSTHROUGH;
            summary.guard_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_SKIPPED;
            summary.skipped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DROPPED => {
            summary.guard_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PASSTHROUGH;
            if (summary.primary_after <= view.primary_guard_floor and summary.deferred_after <= view.deferred_guard_floor) {
                summary.guard_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_EXHAUSTED;
            }
            summary.guard_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_DROPPED;
            summary.dropped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_DEFERRED => {
            summary.guard_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_APPLIED;
            if (summary.deferred_after < view.deferred_guard_floor) {
                summary.deferred_after = summary.deferred_before;
                summary.guard_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_DEFERRED_HELD;
                if (summary.deferred_before <= view.deferred_guard_floor) {
                    summary.guard_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_EXHAUSTED;
                }
                summary.guard_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_HELD;
                summary.held_count = 1;
            } else {
                summary.guard_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PASSTHROUGH;
                summary.guard_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_DEFERRED;
                summary.deferred_count = 1;
            }
        },
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED,
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_COALESCED,
        => {
            summary.guard_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_APPLIED;
            if (summary.primary_after < view.primary_guard_floor) {
                summary.primary_after = summary.primary_before;
                summary.guard_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PRIMARY_HELD;
                if (summary.primary_before <= view.primary_guard_floor and summary.deferred_after <= view.deferred_guard_floor) {
                    summary.guard_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_EXHAUSTED;
                }
                summary.guard_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_HELD;
                summary.held_count = 1;
            } else {
                summary.guard_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_FLAG_PASSTHROUGH;
                if (parent_summary.window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_status == abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_STATUS_ACKED) {
                    summary.guard_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_ACKED;
                    summary.acked_count = 1;
                } else {
                    summary.guard_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_COALESCED;
                    summary.coalesced_count = 1;
                }
            }
        },
        else => {},
    }

    return summary;
}