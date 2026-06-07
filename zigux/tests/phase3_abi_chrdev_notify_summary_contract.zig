const std = @import("std");
const abi = @import("abi_bindings");

test "chrdev notify delivery-window view exposes stable ABI layout" {
    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_ack_window_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_delivery_window_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_status_offset);

    try std.testing.expectEqual(abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_size, @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView));
    try std.testing.expectEqual(abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_align, @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView));
}

test "chrdev notify delivery-window summary exposes stable ABI layout" {
    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_applied_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_skipped_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_delivered_offset);

    try std.testing.expectEqual(abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_size, @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary));
    try std.testing.expectEqual(abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_align, @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary));
}

test "chrdev notify budget view and summary expose stable ABI layout" {
    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_budget_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_window_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_flags_offset);
    try std.testing.expectEqual(abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_size, @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView));

    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_attempted_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_applied_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_skipped_offset);
    try std.testing.expectEqual(abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_size, @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary));
}

test "chrdev notify delivery-window counters stay independent from status flags" {
    const skipped_view = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView{
        .ack_window = 4,
        .delivery_window = 9,
        .status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    };
    const delivered_summary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary{
        .applied = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED,
        .skipped = 0,
        .delivered = skipped_view.delivery_window - skipped_view.ack_window,
    };
    const skipped_summary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary{
        .applied = 0,
        .skipped = skipped_view.status,
        .delivered = 0,
    };

    try std.testing.expectEqual(@as(u32, 5), delivered_summary.delivered);
    try std.testing.expectEqual(@as(u32, 0), delivered_summary.skipped);
    try std.testing.expectEqual(@as(u32, 0), skipped_summary.applied);
    try std.testing.expectEqual(abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED, skipped_summary.skipped);
}

test "chrdev notify budget-window flags compose without changing summary counters" {
    const budget_view = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView{
        .budget = 8,
        .window = 3,
        .flags = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED |
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
    };
    const budget_summary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary{
        .attempted = budget_view.budget,
        .applied = budget_view.window,
        .skipped = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
    };

    try std.testing.expectEqual(@as(u32, 1), budget_view.flags);
    try std.testing.expectEqual(
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
    );
    try std.testing.expectEqual(@as(u32, 8), budget_summary.attempted);
    try std.testing.expectEqual(@as(u32, 3), budget_summary.applied);
    try std.testing.expectEqual(@as(u32, 1), budget_summary.skipped);
}
