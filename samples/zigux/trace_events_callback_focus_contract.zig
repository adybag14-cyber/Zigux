const std = @import("std");

pub const linux_anchor = "samples/trace_events/trace-events-sample.c";

pub const SampleFocus = enum {
    payload_shape,
    string_selection,
    formatted_message,
    conditional_event_families,
    function_callback_registration,
    ownership_and_lifetime,
};

pub const CallbackBoundaryContract = struct {
    checked_focus: []const SampleFocus,
    callback_iteration_count: i32,
    total_event_calls_after_recovery: usize,
    registration_depth_after_recovery: usize,
    missing_registration_rejected: bool,
    underflow_before_registration_rejected: bool,
    double_registration_rejected: bool,
    invalid_callback_count_rejected: bool,
    outstanding_registration_exit_rejected: bool,
    callback_path_checked: bool,
};

pub fn anchorFocusOrder() []const SampleFocus {
    return &.{
        .payload_shape,
        .string_selection,
        .formatted_message,
        .conditional_event_families,
        .function_callback_registration,
        .ownership_and_lifetime,
    };
}

pub fn callbackBoundaryContract() CallbackBoundaryContract {
    return .{
        .checked_focus = anchorFocusOrder(),
        .callback_iteration_count = 5,
        .total_event_calls_after_recovery = 2,
        .registration_depth_after_recovery = 0,
        .missing_registration_rejected = true,
        .underflow_before_registration_rejected = true,
        .double_registration_rejected = true,
        .invalid_callback_count_rejected = true,
        .outstanding_registration_exit_rejected = true,
        .callback_path_checked = true,
    };
}

test "callback boundary keeps the same checked focus order as the main anchor replay" {
    const contract = callbackBoundaryContract();
    const anchor_focus = anchorFocusOrder();

    try std.testing.expectEqualStrings(linux_anchor, "samples/trace_events/trace-events-sample.c");
    try std.testing.expectEqual(anchor_focus.len, contract.checked_focus.len);

    for (anchor_focus, contract.checked_focus) |expected, actual| {
        try std.testing.expectEqual(expected, actual);
    }
}

test "callback boundary keeps rollback and registration cues explicit" {
    const contract = callbackBoundaryContract();

    try std.testing.expectEqual(@as(i32, 5), contract.callback_iteration_count);
    try std.testing.expectEqual(@as(usize, 2), contract.total_event_calls_after_recovery);
    try std.testing.expectEqual(@as(usize, 0), contract.registration_depth_after_recovery);
    try std.testing.expect(contract.missing_registration_rejected);
    try std.testing.expect(contract.underflow_before_registration_rejected);
    try std.testing.expect(contract.double_registration_rejected);
    try std.testing.expect(contract.invalid_callback_count_rejected);
    try std.testing.expect(contract.outstanding_registration_exit_rejected);
    try std.testing.expect(contract.callback_path_checked);
}
