const std = @import("std");

const abi = @import("abi_bindings");

test "phase3 abi chrdev window constants stay explicit in a standalone replay" {
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

test "phase3 abi chrdev delivery and budget summaries keep their visible window math" {
    const delivery_view = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView{
        .ack_window = 7,
        .delivery_window = 11,
        .status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    };
    const delivery_summary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary{
        .applied = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED,
        .skipped = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
        .delivered = 3,
    };
    const budget_view = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView{
        .budget = 5,
        .window = 9,
        .flags = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED |
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
    };
    const budget_summary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary{
        .attempted = 4,
        .applied = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
        .skipped = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
    };

    try std.testing.expectEqual(@as(u32, 18), delivery_view.ack_window + delivery_view.delivery_window);
    try std.testing.expectEqual(@as(u32, 1), delivery_view.status);
    try std.testing.expectEqual(@as(u32, 1), delivery_summary.applied);
    try std.testing.expectEqual(@as(u32, 1), delivery_summary.skipped);
    try std.testing.expectEqual(@as(u32, 2), delivery_summary.applied + delivery_summary.skipped);
    try std.testing.expectEqual(@as(u32, 3), delivery_summary.delivered);

    try std.testing.expectEqual(@as(u32, 14), budget_view.budget + budget_view.window);
    try std.testing.expectEqual(@as(u32, 1), budget_view.flags);
    try std.testing.expectEqual(@as(u32, 1), budget_summary.applied);
    try std.testing.expectEqual(@as(u32, 1), budget_summary.skipped);
    try std.testing.expectEqual(@as(u32, 4), budget_summary.attempted);
}

test "phase3 abi chrdev structs keep the published three-u32 layout in isolation" {
    inline for (.{
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView,
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary,
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView,
        abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary,
    }) |StructType| {
        try std.testing.expectEqual(@as(usize, 12), @sizeOf(StructType));
        try std.testing.expectEqual(@as(usize, 4), @alignOf(StructType));
    }

    try std.testing.expectEqual(
        @as(usize, 0),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "ack_window"),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "delivery_window"),
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "status"),
    );

    try std.testing.expectEqual(
        @as(usize, 0),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "applied"),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "skipped"),
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "delivered"),
    );

    try std.testing.expectEqual(
        @as(usize, 0),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "budget"),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window"),
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "flags"),
    );

    try std.testing.expectEqual(
        @as(usize, 0),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "attempted"),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "applied"),
    );
    try std.testing.expectEqual(
        @as(usize, 8),
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "skipped"),
    );
}
