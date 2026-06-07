const std = @import("std");
const abi = @import("abi_bindings");

const delivery_applied =
    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED;
const delivery_skipped =
    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED;
const budget_applied =
    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED;
const budget_window_applied =
    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED;
const budget_window_skipped =
    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED;

test "chrdev notify window constants stay single-bit sentinels" {
    try std.testing.expectEqual(@as(u32, 1), delivery_applied);
    try std.testing.expectEqual(@as(u32, 1), delivery_skipped);
    try std.testing.expectEqual(@as(u32, 1), budget_applied);
    try std.testing.expectEqual(@as(u32, 1), budget_window_applied);
    try std.testing.expectEqual(@as(u32, 1), budget_window_skipped);

    try std.testing.expectEqual(delivery_applied, delivery_skipped);
    try std.testing.expectEqual(budget_applied, budget_window_applied);
    try std.testing.expectEqual(budget_applied, budget_window_skipped);
}

test "chrdev notify delivery view and summary keep published layout" {
    try std.testing.expectEqual(@as(usize, 12), @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "ack_window"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "delivery_window"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "status"));

    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_ack_window_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_delivery_window_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_status_offset);

    try std.testing.expectEqual(@as(usize, 12), @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "applied"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "skipped"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "delivered"));

    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_applied_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_skipped_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_delivered_offset);
}

test "chrdev notify budget view and summary keep published layout" {
    try std.testing.expectEqual(@as(usize, 12), @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "budget"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "flags"));

    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_budget_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_window_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_flags_offset);

    try std.testing.expectEqual(@as(usize, 12), @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "attempted"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "applied"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "skipped"));

    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_attempted_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_applied_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_skipped_offset);
}

test "chrdev notify window values remain independent from generic ABI records" {
    const delivery_view = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView{
        .ack_window = 7,
        .delivery_window = 11,
        .status = delivery_skipped,
    };
    const delivery_summary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary{
        .applied = delivery_applied,
        .skipped = delivery_skipped,
        .delivered = 5,
    };
    const budget_view = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView{
        .budget = 3,
        .window = 13,
        .flags = budget_applied | budget_window_applied,
    };
    const budget_summary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary{
        .attempted = 9,
        .applied = budget_applied,
        .skipped = budget_window_skipped,
    };

    try std.testing.expectEqual(@as(u32, 7), delivery_view.ack_window);
    try std.testing.expectEqual(@as(u32, 11), delivery_view.delivery_window);
    try std.testing.expectEqual(delivery_skipped, delivery_view.status);
    try std.testing.expectEqual(delivery_applied, delivery_summary.applied);
    try std.testing.expectEqual(delivery_skipped, delivery_summary.skipped);
    try std.testing.expectEqual(@as(u32, 5), delivery_summary.delivered);

    try std.testing.expectEqual(@as(u32, 3), budget_view.budget);
    try std.testing.expectEqual(@as(u32, 13), budget_view.window);
    try std.testing.expectEqual(@as(u32, 1), budget_view.flags);
    try std.testing.expectEqual(@as(u32, 9), budget_summary.attempted);
    try std.testing.expectEqual(budget_applied, budget_summary.applied);
    try std.testing.expectEqual(budget_window_skipped, budget_summary.skipped);

    try std.testing.expectEqual(@as(usize, 8), abi.export_status_size);
    try std.testing.expectEqual(@as(usize, 4), abi.interop_policy_size);
}
