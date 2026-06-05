const abi = @import("abi_bindings");

pub const DeliveryWindowView = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView;
pub const DeliveryWindowSummary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary;
pub const DeliveryWindowBudgetView = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView;
pub const DeliveryWindowBudgetSummary = abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary;

pub const ChrdevNotifyDeliveryWindowView = DeliveryWindowView;
pub const ChrdevNotifyDeliveryWindowSummary = DeliveryWindowSummary;
pub const ChrdevNotifyDeliveryWindowBudgetView = DeliveryWindowBudgetView;
pub const ChrdevNotifyDeliveryWindowBudgetSummary = DeliveryWindowBudgetSummary;

pub const delivery_window_view_size = @sizeOf(DeliveryWindowView);
pub const delivery_window_view_align = @alignOf(DeliveryWindowView);
pub const delivery_window_view_ack_window_offset = @offsetOf(DeliveryWindowView, "ack_window");
pub const delivery_window_view_delivery_window_offset = @offsetOf(DeliveryWindowView, "delivery_window");
pub const delivery_window_view_status_offset = @offsetOf(DeliveryWindowView, "status");

pub const delivery_window_summary_size = @sizeOf(DeliveryWindowSummary);
pub const delivery_window_summary_align = @alignOf(DeliveryWindowSummary);
pub const delivery_window_summary_applied_offset = @offsetOf(DeliveryWindowSummary, "applied");
pub const delivery_window_summary_skipped_offset = @offsetOf(DeliveryWindowSummary, "skipped");
pub const delivery_window_summary_delivered_offset = @offsetOf(DeliveryWindowSummary, "delivered");

pub const delivery_window_budget_view_size = @sizeOf(DeliveryWindowBudgetView);
pub const delivery_window_budget_view_align = @alignOf(DeliveryWindowBudgetView);
pub const delivery_window_budget_view_budget_offset = @offsetOf(DeliveryWindowBudgetView, "budget");
pub const delivery_window_budget_view_window_offset = @offsetOf(DeliveryWindowBudgetView, "window");
pub const delivery_window_budget_view_flags_offset = @offsetOf(DeliveryWindowBudgetView, "flags");

pub const delivery_window_budget_summary_size = @sizeOf(DeliveryWindowBudgetSummary);
pub const delivery_window_budget_summary_align = @alignOf(DeliveryWindowBudgetSummary);
pub const delivery_window_budget_summary_attempted_offset = @offsetOf(DeliveryWindowBudgetSummary, "attempted");
pub const delivery_window_budget_summary_applied_offset = @offsetOf(DeliveryWindowBudgetSummary, "applied");
pub const delivery_window_budget_summary_skipped_offset = @offsetOf(DeliveryWindowBudgetSummary, "skipped");

pub const delivery_applied_flag =
    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_FLAG_DELIVERY_APPLIED;
pub const delivery_skipped_status =
    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_STATUS_SKIPPED;
pub const budget_applied_flag =
    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_FLAG_BUDGET_APPLIED;
pub const budget_window_applied_flag =
    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_FLAG_WINDOW_APPLIED;
pub const budget_window_skipped_status =
    abi.CHRDEV_NOTIFY_ACK_WINDOW_POLICY_BUDGET_WINDOW_DELIVERY_WINDOW_BUDGET_WINDOW_STATUS_SKIPPED;

test "chrdev notify ABI aliases stay layout-identical to the shared ABI structs" {
    try @import("std").testing.expectEqual(
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowView),
        @sizeOf(ChrdevNotifyDeliveryWindowView),
    );
    try @import("std").testing.expectEqual(
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowSummary),
        @sizeOf(ChrdevNotifyDeliveryWindowSummary),
    );
    try @import("std").testing.expectEqual(
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetView),
        @sizeOf(ChrdevNotifyDeliveryWindowBudgetView),
    );
    try @import("std").testing.expectEqual(
        @sizeOf(abi.ChrdevNotifyAckWindowPolicyBudgetWindowDeliveryWindowBudgetSummary),
        @sizeOf(ChrdevNotifyDeliveryWindowBudgetSummary),
    );
}
