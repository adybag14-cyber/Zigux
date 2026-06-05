const std = @import("std");
const abi = @import("abi_bindings");

const DeliveryWindowView =
    abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView;
const DeliveryWindowSummary =
    abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary;
const DeliveryWindowBudgetView =
    abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView;
const DeliveryWindowBudgetSummary =
    abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary;

test "phase3 abi chrdev notify delivery window view layout stays C-visible" {
    try std.testing.expectEqual(@as(usize, 12), @sizeOf(DeliveryWindowView));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(DeliveryWindowView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(DeliveryWindowView, "ack_window"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(DeliveryWindowView, "delivery_window"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(DeliveryWindowView, "status"));

    const pending = DeliveryWindowView{
        .ack_window = 8,
        .delivery_window = 4,
        .status = 0,
    };
    const skipped = DeliveryWindowView{
        .ack_window = 8,
        .delivery_window = 0,
        .status = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    };

    try std.testing.expect(pending.status == 0);
    try std.testing.expect(skipped.status != 0);
    try std.testing.expectEqual(@as(u32, 8), pending.ack_window);
    try std.testing.expectEqual(@as(u32, 4), pending.delivery_window);
}

test "phase3 abi chrdev notify delivery summary stays counter-shaped" {
    try std.testing.expectEqual(@as(usize, 12), @sizeOf(DeliveryWindowSummary));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(DeliveryWindowSummary));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(DeliveryWindowSummary, "applied"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(DeliveryWindowSummary, "skipped"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(DeliveryWindowSummary, "delivered"));

    const summary = DeliveryWindowSummary{
        .applied = 3,
        .skipped = 2,
        .delivered = 11,
    };

    try std.testing.expectEqual(@as(u32, 5), summary.applied + summary.skipped);
    try std.testing.expect(summary.delivered >= summary.applied);
    try std.testing.expect(summary.delivered >= summary.skipped);
}

test "phase3 abi chrdev notify delivery budget view pins applied flag" {
    try std.testing.expectEqual(@as(usize, 12), @sizeOf(DeliveryWindowBudgetView));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(DeliveryWindowBudgetView));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(DeliveryWindowBudgetView, "budget"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(DeliveryWindowBudgetView, "window"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(DeliveryWindowBudgetView, "flags"));

    const untouched = DeliveryWindowBudgetView{
        .budget = 0,
        .window = 0,
        .flags = 0,
    };
    const applied = DeliveryWindowBudgetView{
        .budget = 16,
        .window = 8,
        .flags = abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
    };

    try std.testing.expect((untouched.flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED) == 0);
    try std.testing.expect((applied.flags & abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED) != 0);
    try std.testing.expectEqual(@as(u32, 16), applied.budget);
    try std.testing.expectEqual(@as(u32, 8), applied.window);
}

test "phase3 abi chrdev notify delivery budget summary separates attempts and skips" {
    try std.testing.expectEqual(@as(usize, 12), @sizeOf(DeliveryWindowBudgetSummary));
    try std.testing.expectEqual(@as(usize, 4), @alignOf(DeliveryWindowBudgetSummary));
    try std.testing.expectEqual(@as(usize, 0), @offsetOf(DeliveryWindowBudgetSummary, "attempted"));
    try std.testing.expectEqual(@as(usize, 4), @offsetOf(DeliveryWindowBudgetSummary, "applied"));
    try std.testing.expectEqual(@as(usize, 8), @offsetOf(DeliveryWindowBudgetSummary, "skipped"));

    const summary = DeliveryWindowBudgetSummary{
        .attempted = 7,
        .applied = 5,
        .skipped = 2,
    };

    try std.testing.expectEqual(summary.attempted, summary.applied + summary.skipped);
    try std.testing.expect(summary.applied <= summary.attempted);
    try std.testing.expect(summary.skipped <= summary.attempted);
}
