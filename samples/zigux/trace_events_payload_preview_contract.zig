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

pub const PayloadBoundaryCase = struct {
    iteration_count: i32,
    selected_string: []const u8,
    selected_string_slot: usize,
    payload_preview: [4]i32,
    payload_preview_len: usize,
    payload_len: usize,
    array_sentinel: i32,
    formatted_message: []const u8,
};

pub const PayloadBoundaryContract = struct {
    anchor: []const u8,
    event_family_count: usize,
    callback_family_count: usize,
    preserves_initialized_stage: bool,
    conditional_paths_checked: bool,
    vararg_payload_path_checked: bool,
    relative_location_path_checked: bool,
    review_focus: []const SampleFocus,
    cases: [5]PayloadBoundaryCase,
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

pub fn referencePattern() PayloadBoundaryContract {
    return .{
        .anchor = linux_anchor,
        .event_family_count = 6,
        .callback_family_count = 2,
        .preserves_initialized_stage = true,
        .conditional_paths_checked = true,
        .vararg_payload_path_checked = true,
        .relative_location_path_checked = true,
        .review_focus = anchorFocusOrder(),
        .cases = .{
            .{
                .iteration_count = 0,
                .selected_string = "Mother Goose",
                .selected_string_slot = 0,
                .payload_preview = .{ 0, 0, 0, 0 },
                .payload_preview_len = 0,
                .payload_len = 0,
                .array_sentinel = 0,
                .formatted_message = "iter=0",
            },
            .{
                .iteration_count = 1,
                .selected_string = "Snoopy",
                .selected_string_slot = 1,
                .payload_preview = .{ 1, 0, 0, 0 },
                .payload_preview_len = 1,
                .payload_len = 1,
                .array_sentinel = 0,
                .formatted_message = "iter=1",
            },
            .{
                .iteration_count = 2,
                .selected_string = "Gandalf",
                .selected_string_slot = 2,
                .payload_preview = .{ 1, 2, 0, 0 },
                .payload_preview_len = 2,
                .payload_len = 2,
                .array_sentinel = 0,
                .formatted_message = "iter=2",
            },
            .{
                .iteration_count = 3,
                .selected_string = "Frodo",
                .selected_string_slot = 3,
                .payload_preview = .{ 1, 2, 3, 0 },
                .payload_preview_len = 3,
                .payload_len = 3,
                .array_sentinel = 0,
                .formatted_message = "iter=3",
            },
            .{
                .iteration_count = 4,
                .selected_string = "One ring to rule them all",
                .selected_string_slot = 4,
                .payload_preview = .{ 1, 2, 3, 4 },
                .payload_preview_len = 4,
                .payload_len = 4,
                .array_sentinel = 0,
                .formatted_message = "iter=4",
            },
        },
    };
}

test "trace-events payload-preview companion keeps the anchor and focus order explicit" {
    const contract = referencePattern();

    try std.testing.expectEqualStrings(linux_anchor, contract.anchor);
    try std.testing.expectEqual(@as(usize, 6), contract.event_family_count);
    try std.testing.expectEqual(@as(usize, 2), contract.callback_family_count);
    try std.testing.expect(contract.preserves_initialized_stage);
    try std.testing.expect(contract.conditional_paths_checked);
    try std.testing.expect(contract.vararg_payload_path_checked);
    try std.testing.expect(contract.relative_location_path_checked);
    try std.testing.expectEqual(@as(usize, 6), contract.review_focus.len);
    try std.testing.expectEqualSlices(SampleFocus, anchorFocusOrder(), contract.review_focus);
}

test "trace-events payload-preview companion keeps the modulo-selected payload ladder explicit" {
    const contract = referencePattern();
    const expected_prefix_lens = [_]usize{ 0, 1, 2, 3, 4 };
    const expected_strings = [_][]const u8{
        "Mother Goose",
        "Snoopy",
        "Gandalf",
        "Frodo",
        "One ring to rule them all",
    };

    for (contract.cases, 0..) |current, index| {
        try std.testing.expectEqual(@as(i32, @intCast(index)), current.iteration_count);
        try std.testing.expectEqualStrings(expected_strings[index], current.selected_string);
        try std.testing.expectEqual(expected_prefix_lens[index], current.selected_string_slot);
        try std.testing.expectEqual(expected_prefix_lens[index], current.payload_preview_len);
        try std.testing.expectEqual(expected_prefix_lens[index], current.payload_len);
        try std.testing.expectEqual(@as(i32, 0), current.array_sentinel);
    }
}

test "trace-events payload-preview companion keeps the largest bounded preview case explicit" {
    const contract = referencePattern();
    const largest = contract.cases[4];

    try std.testing.expectEqualStrings("One ring to rule them all", largest.selected_string);
    try std.testing.expectEqual(@as(usize, 4), largest.selected_string_slot);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 3, 4 }, largest.payload_preview[0..largest.payload_preview_len]);
    try std.testing.expectEqualStrings("iter=4", largest.formatted_message);
}
