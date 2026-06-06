const std = @import("std");
const testing = std.testing;

const abi = @import("abi_bindings");
const layout_assert = @import("layout_assert_helpers");

test "layout assert chrdev delivery-window view mirrors ABI constants" {
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowViewLayout();

    try testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_size);
    try testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_align);
    try testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_ack_window_offset);
    try testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_delivery_window_offset);
    try testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_status_offset);

    try testing.expectEqual(
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_size,
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
    );
    try testing.expectEqual(
        abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_view_status_offset,
        @offsetOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView, "status"),
    );
}

test "layout assert chrdev delivery-window summary keeps applied skipped delivered order" {
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummaryLayout();

    try testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_size);
    try testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_align);
    try testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_applied_offset);
    try testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_skipped_offset);
    try testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_summary_delivered_offset);

    const summary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary{
        .applied = 2,
        .skipped = 1,
        .delivered = 3,
    };
    try testing.expectEqual(@as(u32, 2), summary.applied);
    try testing.expectEqual(@as(u32, 1), summary.skipped);
    try testing.expectEqual(@as(u32, 3), summary.delivered);
}

test "layout assert chrdev budget view and summary keep u32 triplets explicit" {
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetViewLayout();
    try layout_assert.assertChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummaryLayout();

    try testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_size);
    try testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_align);
    try testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_budget_offset);
    try testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_window_offset);
    try testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_view_flags_offset);

    try testing.expectEqual(@as(usize, 12), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_size);
    try testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_align);
    try testing.expectEqual(@as(usize, 0), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_attempted_offset);
    try testing.expectEqual(@as(usize, 4), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_applied_offset);
    try testing.expectEqual(@as(usize, 8), abi.chrdev_notify_ack_window_policy_budget_window_delivery_window_budget_summary_skipped_offset);
}

test "layout assert chrdev delivery-window status and flag bytes stay single-bit" {
    try testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED,
    );
    try testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED,
    );
    try testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED,
    );
    try testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED,
    );
    try testing.expectEqual(
        @as(u32, 1),
        abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED,
    );
}
