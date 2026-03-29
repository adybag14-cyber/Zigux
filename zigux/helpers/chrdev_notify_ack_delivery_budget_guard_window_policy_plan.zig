const std = @import("std");
const abi = @import("abi_bindings");
const guard_window_plan = @import("chrdev_notify_ack_delivery_budget_guard_window_plan");

const allowed_policy_flags =
    abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED |
    abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_HELD |
    abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_DROPPED;

const ParentView = abi.ChrdevNotifyAckDeliveryBudgetGuardWindowView;

fn emptySummary() abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary {
    return std.mem.zeroInit(abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary, .{});
}

pub fn viewFromParent(
    parent: ParentView,
    policy_flags: u32,
) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyView {
    return .{
        .parent = parent,
        .policy_flags = policy_flags,
        .reserved = 0,
    };
}

pub fn asParentView(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyView) ParentView {
    return view.parent;
}

pub fn isValid(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyView) bool {
    if (view.reserved != 0) return false;
    if ((view.policy_flags & ~allowed_policy_flags) != 0) return false;
    return guard_window_plan.isValid(view.parent);
}

pub fn summarize(view: abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicyView) abi.ChrdevNotifyAckDeliveryBudgetGuardWindowPolicySummary {
    if (!isValid(view)) return emptySummary();

    const parent_summary = guard_window_plan.summarize(view.parent);
    var summary = emptySummary();
    summary.parent = parent_summary;
    summary.policy_flags = view.policy_flags;
    summary.effective_policy_flags = 0;
    summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_NONE;

    switch (parent_summary.window_status) {
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_NONE => {},
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_SKIPPED => {
            summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SKIPPED;
            summary.skipped_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_SUPPRESSED => {
            summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SUPPRESSED;
            summary.suppressed_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DROPPED => {
            if ((view.policy_flags & abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_DROPPED) != 0) {
                summary.effective_policy_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_DROPPED;
                summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SUPPRESSED;
                summary.suppressed_count = 1;
            } else {
                summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DROPPED;
                summary.dropped_count = 1;
            }
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_HELD => {
            if ((view.policy_flags & abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_HELD) != 0) {
                summary.effective_policy_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_SUPPRESS_HELD;
                summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_SUPPRESSED;
                summary.suppressed_count = 1;
            } else {
                summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_HELD;
                summary.held_count = 1;
            }
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_DEFERRED => {
            summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DEFERRED;
            summary.deferred_count = 1;
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_ACKED => {
            if ((view.policy_flags & abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED) != 0) {
                summary.effective_policy_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED;
                summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DEFERRED;
                summary.deferred_count = 1;
            } else {
                summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_ACKED;
                summary.acked_count = 1;
            }
        },
        abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_STATUS_COALESCED => {
            if ((view.policy_flags & abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED) != 0) {
                summary.effective_policy_flags = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_FLAG_FORCE_DEFERRED;
                summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_DEFERRED;
                summary.deferred_count = 1;
            } else {
                summary.policy_status = abi.CHRDEV_NOTIFY_ACK_DELIVERY_BUDGET_GUARD_WINDOW_POLICY_STATUS_COALESCED;
                summary.coalesced_count = 1;
            }
        },
        else => {},
    }

    return summary;
}
