const std = @import("std");
const abi = @import("abi_bindings");
const guard_plan = @import("chrdev_notify_ack_delivery_budget_guard_plan");

const ParentView = abi.ChrdevNotifyAckDeliveryBudgetGuardView;

fn emptySummary() abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary {
    return std.mem.zeroInit(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary, .{});
}

pub fn viewFromParent(
    parent: ParentView,
    primary_window: u32,
    deferred_window: u32,
    window_floor: u32,
) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowView {
    return .{
        .parent = parent,
        .primary_window = primary_window,
        .deferred_window = deferred_window,
        .window_floor = window_floor,
        .reserved = 0,
    };
}

pub fn asParentView(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowView) ParentView {
    return view.parent;
}

pub fn isValid(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowView) bool {
    if (view.reserved != 0) return false;
    return guard_plan.isValid(view.parent);
}

pub fn summarize(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowView) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowSummary {
    if (!isValid(view)) return emptySummary();

    const parent_summary = guard_plan.summarize(view.parent);
    var summary = emptySummary();
    summary.parent = parent_summary;
    summary.primary_window_before = view.primary_window;
    summary.primary_window_after = view.primary_window;
    summary.deferred_window_before = view.deferred_window;
    summary.deferred_window_after = view.deferred_window;
    summary.window_floor = view.window_floor;
    summary.window_flags = 0;
    summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_NONE;

    switch (parent_summary.guard_status) {
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_SUPPRESSED => {
            summary.window_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PASSTHROUGH;
            summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_SUPPRESSED;
            summary.suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_SKIPPED => {
            summary.window_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PASSTHROUGH;
            summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_SKIPPED;
            summary.skipped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_DROPPED => {
            summary.window_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PASSTHROUGH;
            if (summary.primary_window_before == 0 and summary.deferred_window_before == 0) {
                summary.window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_WINDOW_EXHAUSTED;
            }
            summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DROPPED;
            summary.dropped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_HELD => {
            summary.window_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PASSTHROUGH;
            summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_HELD;
            summary.held_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_DEFERRED => {
            summary.window_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_APPLIED;
            if (summary.deferred_window_before > view.window_floor) {
                summary.deferred_window_after -= 1;
                summary.window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_DEFERRED_WINDOW_USED;
                summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DEFERRED;
                summary.deferred_count = 1;
            } else if (summary.deferred_window_before == 0) {
                summary.window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_WINDOW_EXHAUSTED;
                summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DROPPED;
                summary.dropped_count = 1;
            } else {
                summary.window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_DEFERRED_HELD;
                summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_HELD;
                summary.held_count = 1;
            }
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_ACKED,
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_COALESCED,
        => {
            summary.window_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_APPLIED;
            if (summary.primary_window_before > view.window_floor) {
                summary.primary_window_after -= 1;
                summary.window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PRIMARY_WINDOW_USED;
                if (parent_summary.guard_status == abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_STATUS_ACKED) {
                    summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_ACKED;
                    summary.acked_count = 1;
                } else {
                    summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_COALESCED;
                    summary.coalesced_count = 1;
                }
            } else {
                if (summary.primary_window_before == 0) {
                    summary.window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_WINDOW_EXHAUSTED;
                } else {
                    summary.window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_PRIMARY_HELD;
                }
                if (summary.deferred_window_before > view.window_floor) {
                    summary.deferred_window_after -= 1;
                    summary.window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_DEFERRED_WINDOW_USED;
                    summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DEFERRED;
                    summary.deferred_count = 1;
                } else if (summary.deferred_window_before == 0) {
                    summary.window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_WINDOW_EXHAUSTED;
                    summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DROPPED;
                    summary.dropped_count = 1;
                } else {
                    summary.window_flags |= abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_FLAG_DEFERRED_HELD;
                    summary.window_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_HELD;
                    summary.held_count = 1;
                }
            }
        },
        else => {},
    }

    return summary;
}