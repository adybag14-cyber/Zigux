const std = @import("std");

const abi = @import("abi_bindings");

test "phase3 abi keeps chrdev window status constants explicit" {
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

    try std.testing.expectEqual(
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
        delivery_view.status,
    );
    try std.testing.expectEqual(
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED,
        delivery_summary.applied,
    );
    try std.testing.expectEqual(
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
        delivery_summary.skipped,
    );
    try std.testing.expectEqual(
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED |
            abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
        budget_view.flags,
    );
    try std.testing.expectEqual(
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
        budget_summary.applied,
    );
    try std.testing.expectEqual(
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
        budget_summary.skipped,
    );
}

test "phase3 abi keeps chrdev window status layouts explicit" {
    try std.testing.expectEqual(
        @as(usize, 12),
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
    );
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
        @as(usize, 12),
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary),
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
        @as(usize, 12),
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView),
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
        @as(usize, 12),
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary),
    );
    try std.testing.expectEqual(
        @as(usize, 4),
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary),
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
