const std = @import("std");
const abi = @import("abi_bindings");

const DeliveryWindowView = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView;
const DeliveryWindowSummary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary;
const DeliveryWindowBudgetView = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView;
const DeliveryWindowBudgetSummary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary;

test "chrdev delivery-window budget-window constants stay public and single-bit" {
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
    );
    try std.testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
    );
}

test "chrdev delivery-window structs keep their published ABI layout" {
    try std.testing.expectEqual(@as(usize, 12), @sizeOf(DeliveryWindowView));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(DeliveryWindowView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(DeliveryWindowView, "ack_window"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(DeliveryWindowView, "delivery_window"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(DeliveryWindowView, "status"));
    try std.testing.expectEqual(
        @sizeOf(DeliveryWindowView),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_size,
    );
    try std.testing.expectEqual(
        @alignOf(DeliveryWindowView),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_align,
    );
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowView, "ack_window"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_ack_window_offset,
    );
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowView, "delivery_window"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_delivery_window_offset,
    );
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowView, "status"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_status_offset,
    );

    try std.testing.expectEqual(@as(usize, 12), @sizeOf(DeliveryWindowSummary));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(DeliveryWindowSummary));
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowSummary, "applied"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_applied_offset,
    );
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowSummary, "skipped"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_skipped_offset,
    );
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowSummary, "delivered"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_delivered_offset,
    );

    try std.testing.expectEqual(@as(usize, 12), @sizeOf(DeliveryWindowBudgetView));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(DeliveryWindowBudgetView));
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowBudgetView, "budget"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_budget_offset,
    );
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowBudgetView, "window"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_window_offset,
    );
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowBudgetView, "flags"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_flags_offset,
    );

    try std.testing.expectEqual(@as(usize, 12), @sizeOf(DeliveryWindowBudgetSummary));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(DeliveryWindowBudgetSummary));
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowBudgetSummary, "attempted"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_attempted_offset,
    );
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowBudgetSummary, "applied"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_applied_offset,
    );
    try std.testing.expectEqual(
        @offsetOf(DeliveryWindowBudgetSummary, "skipped"),
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_skipped_offset,
    );
}

test "chrdev delivery-window view records skipped delivery without mutating windows" {
    const skipped = DeliveryWindowView{
        .ack_window = 8,
        .delivery_window = 21,
        .status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    };
    const applied = DeliveryWindowSummary{
        .applied = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED,
        .skipped = 0,
        .delivered = 5,
    };

    try std.testing.expectEqual(@as(u32, 8), skipped.ack_window);
    try std.testing.expectEqual(@as(u32, 21), skipped.delivery_window);
    try std.testing.expectEqual(@as(u32, 1), skipped.status);
    try std.testing.expectEqual(@as(u32, 1), applied.applied);
    try std.testing.expectEqual(@as(u32, 0), applied.skipped);
    try std.testing.expectEqual(@as(u32, 5), applied.delivered);
}

test "chrdev delivery-window budget flags compose with explicit skipped summary" {
    const budgeted = DeliveryWindowBudgetView{
        .budget = 3,
        .window = 13,
        .flags = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED |
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
    };
    const summary = DeliveryWindowBudgetSummary{
        .attempted = 9,
        .applied = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
        .skipped = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
    };

    try std.testing.expectEqual(@as(u32, 3), budgeted.budget);
    try std.testing.expectEqual(@as(u32, 13), budgeted.window);
    try std.testing.expectEqual(@as(u32, 1), budgeted.flags);
    try std.testing.expectEqual(@as(u32, 9), summary.attempted);
    try std.testing.expectEqual(@as(u32, 1), summary.applied);
    try std.testing.expectEqual(@as(u32, 1), summary.skipped);
}
