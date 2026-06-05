const std = @import("std");

const abi = @import("abi_bindings");

const AckDeliveryView = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView;
const AckDeliverySummary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary;
const AckDeliveryBudgetView = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView;
const AckDeliveryBudgetSummary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary;

test "chrdev notify ack-window delivery structs keep published layout" {
    try std.testing.expectEqual(@as(usize, 12), @sizeOf(AckDeliveryView));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(AckDeliveryView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(AckDeliveryView, "ack_window"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(AckDeliveryView, "delivery_window"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(AckDeliveryView, "status"));

    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_ack_window_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_delivery_window_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_status_offset);

    const applied = AckDeliveryView{
        .ack_window = 7,
        .delivery_window = 3,
        .status = 0,
    };
    const skipped = AckDeliveryView{
        .ack_window = 0,
        .delivery_window = 0,
        .status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    };

    try std.testing.expectEqual(@as(u32, 7), applied.ack_window);
    try std.testing.expectEqual(@as(u32, 3), applied.delivery_window);
    try std.testing.expectEqual(@as(u32, 0), applied.status);
    try std.testing.expectEqual(@as(u32, 1), skipped.status);
}

test "chrdev notify ack-window delivery summary keeps published layout" {
    try std.testing.expectEqual(@as(usize, 12), @sizeOf(AckDeliverySummary));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(AckDeliverySummary));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(AckDeliverySummary, "applied"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(AckDeliverySummary, "skipped"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(AckDeliverySummary, "delivered"));

    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_applied_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_skipped_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_delivered_offset);

    const summary = AckDeliverySummary{
        .applied = 5,
        .skipped = 2,
        .delivered = 4,
    };

    try std.testing.expectEqual(@as(u32, 5), summary.applied);
    try std.testing.expectEqual(@as(u32, 2), summary.skipped);
    try std.testing.expectEqual(@as(u32, 4), summary.delivered);
}

test "chrdev notify ack-window delivery budget structs keep published layout" {
    try std.testing.expectEqual(@as(usize, 12), @sizeOf(AckDeliveryBudgetView));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(AckDeliveryBudgetView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(AckDeliveryBudgetView, "budget"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(AckDeliveryBudgetView, "window"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(AckDeliveryBudgetView, "flags"));

    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_budget_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_window_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_flags_offset);

    const budget = AckDeliveryBudgetView{
        .budget = 16,
        .window = 8,
        .flags = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
    };

    try std.testing.expectEqual(@as(u32, 16), budget.budget);
    try std.testing.expectEqual(@as(u32, 8), budget.window);
    try std.testing.expectEqual(@as(u32, 1), budget.flags);
}

test "chrdev notify ack-window delivery budget summary keeps published layout and flags" {
    try std.testing.expectEqual(@as(usize, 12), @sizeOf(AckDeliveryBudgetSummary));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(AckDeliveryBudgetSummary));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(AckDeliveryBudgetSummary, "attempted"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(AckDeliveryBudgetSummary, "applied"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(AckDeliveryBudgetSummary, "skipped"));

    try std.testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_size);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_align);
    try std.testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_attempted_offset);
    try std.testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_applied_offset);
    try std.testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_skipped_offset);

    const summary = AckDeliveryBudgetSummary{
        .attempted = 9,
        .applied = 6,
        .skipped = 3,
    };

    try std.testing.expectEqual(@as(u32, 9), summary.attempted);
    try std.testing.expectEqual(@as(u32, 6), summary.applied);
    try std.testing.expectEqual(@as(u32, 3), summary.skipped);
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
    );
}
