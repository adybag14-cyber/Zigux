const std = @import("std");
const abi = @import("abi_bindings");
const parent_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_policy_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_plan");

pub const ParentView = abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowDeliveryView;
pub const ParentSummary = abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowDeliveryWindowBudgetWindowDeliverySummary;

pub const FLAG_WINDOW_APPLIED: u32 = 1 << 0;
pub const FLAG_WINDOW_USED: u32 = 1 << 1;
pub const FLAG_FLOOR_HELD: u32 = 1 << 2;
pub const FLAG_FLOOR_BLOCKED: u32 = 1 << 3;
pub const FLAG_WINDOW_EXHAUSTED: u32 = 1 << 4;

pub const STATUS_NONE: u32 = 0;
pub const STATUS_ACKED: u32 = 1;
pub const STATUS_DEFERRED: u32 = 2;
pub const STATUS_SUPPRESSED: u32 = 3;
pub const STATUS_COALESCED: u32 = 4;
pub const STATUS_DROPPED: u32 = 5;
pub const STATUS_SKIPPED: u32 = 6;
pub const STATUS_HELD: u32 = 7;

pub const View = extern struct {
    parent: ParentView,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window: u32,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_floor: u32,
    reserved: u32,
};

pub const Summary = extern struct {
    parent: ParentSummary,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_flags: u32,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_before: u32,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_after: u32,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_floor: u32,
    delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status: u32,
    acked_count: u32,
    deferred_count: u32,
    suppressed_count: u32,
    coalesced_count: u32,
    dropped_count: u32,
    skipped_count: u32,
    held_count: u32,
};

fn emptySummary() Summary {
    return std.mem.zeroInit(Summary, .{});
}

pub fn viewFromParent(parent: ParentView, delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window: u32, delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_floor: u32) View {
    return .{
        .parent = parent,
        .delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window = delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window,
        .delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_floor = delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_floor,
        .reserved = 0,
    };
}

pub fn asParentView(view: View) ParentView {
    return view.parent;
}

pub fn isValid(view: View) bool {
    if (view.reserved != 0) return false;
    return parent_plan.isValid(view.parent);
}

pub fn summarize(view: View) Summary {
    if (!isValid(view)) return emptySummary();

    const parent_summary = parent_plan.summarize(view.parent);
    var summary = emptySummary();
    summary.parent = parent_summary;
    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_flags = 0;
    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_before = view.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window;
    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_after = view.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window;
    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_floor = view.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_floor;
    summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status = STATUS_NONE;

    switch (parent_summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_status) {
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SUPPRESSED => {
            summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status = STATUS_SUPPRESSED;
            summary.suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED => {
            summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status = STATUS_SKIPPED;
            summary.skipped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DROPPED => {
            summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status = STATUS_DROPPED;
            summary.dropped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_HELD => {
            summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status = STATUS_HELD;
            summary.held_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED,
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_DEFERRED,
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_COALESCED,
        => {
            summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_flags |= FLAG_WINDOW_APPLIED;

            if (summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_before == 0) {
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_flags |= FLAG_WINDOW_EXHAUSTED;
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status = STATUS_DROPPED;
                summary.dropped_count = 1;
            } else if (summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_before <= view.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_floor) {
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_flags |= FLAG_FLOOR_HELD | FLAG_FLOOR_BLOCKED;
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status = STATUS_DEFERRED;
                summary.deferred_count = 1;
            } else {
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_after = summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_before - 1;
                summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_flags |= FLAG_WINDOW_USED;

                switch (parent_summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_status) {
                    abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_ACKED => {
                        summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status = STATUS_ACKED;
                        summary.acked_count = 1;
                    },
                    abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_COALESCED => {
                        summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status = STATUS_COALESCED;
                        summary.coalesced_count = 1;
                    },
                    else => {
                        summary.delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_budget_window_delivery_window_status = STATUS_DEFERRED;
                        summary.deferred_count = 1;
                    },
                }
            }
        },
        else => {},
    }

    return summary;
}
