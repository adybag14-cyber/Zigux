const std = @import("std");

const abi = @import("abi_bindings");
const chrdev_notify = @import("chrdev_notify_abi");

test "chrdev notify short aliases match the exported delivery window view layout" {
    try std.testing.expectEqual(
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
        @sizeOf(chrdev_notify.ChrdevNotifyDeliveryWindowView),
    );
    try std.testing.expectEqual(
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
        @alignOf(chrdev_notify.ChrdevNotifyDeliveryWindowView),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "ack_window"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowView, "ack_window"),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "delivery_window"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowView, "delivery_window"),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "status"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowView, "status"),
    );

    const view = chrdev_notify.ChrdevNotifyDeliveryWindowView{
        .ack_window = 4,
        .delivery_window = 8,
        .status = chrdev_notify.delivery_skipped_status,
    };
    try std.testing.expectEqual(@as(u32, 4), view.ack_window);
    try std.testing.expectEqual(@as(u32, 8), view.delivery_window);
    try std.testing.expectEqual(@as(u32, 1), view.status);
}

test "chrdev notify short aliases match the delivery window summary shape" {
    try std.testing.expectEqual(
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary),
        @sizeOf(chrdev_notify.ChrdevNotifyDeliveryWindowSummary),
    );
    try std.testing.expectEqual(
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary),
        @alignOf(chrdev_notify.ChrdevNotifyDeliveryWindowSummary),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "applied"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowSummary, "applied"),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "skipped"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowSummary, "skipped"),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary, "delivered"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowSummary, "delivered"),
    );

    const summary = chrdev_notify.ChrdevNotifyDeliveryWindowSummary{
        .applied = chrdev_notify.delivery_applied_flag,
        .skipped = chrdev_notify.delivery_skipped_status,
        .delivered = 7,
    };
    try std.testing.expectEqual(@as(u32, 1), summary.applied);
    try std.testing.expectEqual(@as(u32, 1), summary.skipped);
    try std.testing.expectEqual(@as(u32, 7), summary.delivered);
}

test "chrdev notify short aliases match the delivery budget view layout" {
    try std.testing.expectEqual(
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView),
        @sizeOf(chrdev_notify.ChrdevNotifyDeliveryWindowBudgetView),
    );
    try std.testing.expectEqual(
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView),
        @alignOf(chrdev_notify.ChrdevNotifyDeliveryWindowBudgetView),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "budget"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowBudgetView, "budget"),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "window"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowBudgetView, "window"),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView, "flags"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowBudgetView, "flags"),
    );

    const view = chrdev_notify.ChrdevNotifyDeliveryWindowBudgetView{
        .budget = 2,
        .window = 6,
        .flags = chrdev_notify.budget_applied_flag,
    };
    try std.testing.expectEqual(@as(u32, 2), view.budget);
    try std.testing.expectEqual(@as(u32, 6), view.window);
    try std.testing.expectEqual(@as(u32, 1), view.flags);
}

test "chrdev notify short aliases match the delivery budget summary shape" {
    try std.testing.expectEqual(
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary),
        @sizeOf(chrdev_notify.ChrdevNotifyDeliveryWindowBudgetSummary),
    );
    try std.testing.expectEqual(
        @alignOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary),
        @alignOf(chrdev_notify.ChrdevNotifyDeliveryWindowBudgetSummary),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "attempted"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowBudgetSummary, "attempted"),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "applied"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowBudgetSummary, "applied"),
    );
    try std.testing.expectEqual(
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary, "skipped"),
        @offsetOf(chrdev_notify.ChrdevNotifyDeliveryWindowBudgetSummary, "skipped"),
    );

    const summary = chrdev_notify.ChrdevNotifyDeliveryWindowBudgetSummary{
        .attempted = 9,
        .applied = chrdev_notify.budget_applied_flag,
        .skipped = chrdev_notify.budget_window_skipped_status,
    };
    try std.testing.expectEqual(@as(u32, 9), summary.attempted);
    try std.testing.expectEqual(@as(u32, 1), summary.applied);
    try std.testing.expectEqual(@as(u32, 1), summary.skipped);
}
