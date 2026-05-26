const std = @import("std");
const payload_preview_contract = @import("trace_events_payload_preview_contract");

test "phase 5 trace-events payload-preview companion keeps the direct anchor explicit" {
    const contract = payload_preview_contract.referencePattern();

    try std.testing.expectEqualStrings(
        "samples/trace_events/trace-events-sample.c",
        contract.anchor,
    );
    try std.testing.expectEqual(@as(usize, 6), contract.event_family_count);
    try std.testing.expectEqual(@as(usize, 2), contract.callback_family_count);
    try std.testing.expectEqualSlices(
        payload_preview_contract.SampleFocus,
        payload_preview_contract.anchorFocusOrder(),
        contract.review_focus,
    );
}

test "phase 5 trace-events payload-preview companion keeps the payload ladder reviewable" {
    const contract = payload_preview_contract.referencePattern();

    try std.testing.expect(contract.preserves_initialized_stage);
    try std.testing.expect(contract.conditional_paths_checked);
    try std.testing.expect(contract.vararg_payload_path_checked);
    try std.testing.expect(contract.relative_location_path_checked);

    const gandalf = contract.cases[2];
    try std.testing.expectEqualStrings("Gandalf", gandalf.selected_string);
    try std.testing.expectEqual(@as(usize, 2), gandalf.selected_string_slot);
    try std.testing.expectEqual(@as(usize, 2), gandalf.payload_preview_len);
    try std.testing.expectEqual(@as(usize, 2), gandalf.payload_len);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2 }, gandalf.payload_preview[0..gandalf.payload_preview_len]);
    try std.testing.expectEqual(@as(i32, 0), gandalf.array_sentinel);
    try std.testing.expectEqualStrings("iter=2", gandalf.formatted_message);

    const wrapped = contract.cases[4];
    try std.testing.expectEqualStrings("One ring to rule them all", wrapped.selected_string);
    try std.testing.expectEqual(@as(usize, 4), wrapped.selected_string_slot);
    try std.testing.expectEqualSlices(i32, &.{ 1, 2, 3, 4 }, wrapped.payload_preview[0..wrapped.payload_preview_len]);
    try std.testing.expectEqualStrings("iter=4", wrapped.formatted_message);
}
