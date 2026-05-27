const std = @import("std");
const companion = @import("bytestream_fifo_window_contract");

test "phase 5 bytestream window companion keeps the anchor-local visible-window contract reviewable" {
    const contract = companion.referencePattern();

    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", contract.anchor);
    try std.testing.expectEqual(@as(usize, companion.fifo_capacity), contract.capacity);
    try std.testing.expect(contract.preview_is_non_destructive);
    try std.testing.expect(contract.wrapped_preview_is_non_destructive);
    try std.testing.expect(contract.rollover_refill_required_for_wrap);
    try std.testing.expect(contract.visible_windows_never_exceed_two);
    try std.testing.expect(contract.writable_windows_never_exceed_two);

    try std.testing.expectEqualStrings("preview_after_skip_and_requeue", contract.visible_windows[0].name);
    try std.testing.expectEqual(@as(usize, 7), contract.visible_windows[0].head_index);
    try std.testing.expectEqual(@as(usize, 17), contract.visible_windows[0].tail_index);
    try std.testing.expectEqual(@as(usize, 10), contract.visible_windows[0].total_visible);
    try std.testing.expectEqual(@as(usize, 10), contract.visible_windows[0].first_window_len);
    try std.testing.expectEqual(@as(usize, 0), contract.visible_windows[0].second_window_len);
    try std.testing.expect(!contract.visible_windows[0].wraps);

    try std.testing.expectEqualStrings("wrapped_full_after_refill", contract.visible_windows[1].name);
    try std.testing.expectEqual(@as(usize, companion.fifo_capacity), contract.visible_windows[1].total_visible);
    try std.testing.expectEqual(@as(usize, 28), contract.visible_windows[1].first_window_len);
    try std.testing.expectEqual(@as(usize, 4), contract.visible_windows[1].second_window_len);
    try std.testing.expect(contract.visible_windows[1].wraps);

    try std.testing.expectEqualStrings("partial_drain_after_wrap_refill", contract.visible_windows[2].name);
    try std.testing.expectEqual(@as(usize, 9), contract.visible_windows[2].head_index);
    try std.testing.expectEqual(@as(usize, 1), contract.visible_windows[2].tail_index);
    try std.testing.expectEqual(@as(usize, 24), contract.visible_windows[2].total_visible);
    try std.testing.expectEqual(@as(usize, 23), contract.visible_windows[2].first_window_len);
    try std.testing.expectEqual(@as(usize, 1), contract.visible_windows[2].second_window_len);
    try std.testing.expect(contract.visible_windows[2].wraps);
}

test "phase 5 bytestream window companion keeps writable-window rollover cues separate from visible state" {
    const contract = companion.referencePattern();

    try std.testing.expectEqualStrings("preview_after_skip_and_requeue", contract.writable_windows[0].name);
    try std.testing.expectEqual(@as(usize, 17), contract.writable_windows[0].tail_index);
    try std.testing.expectEqual(@as(usize, 22), contract.writable_windows[0].writable_count);
    try std.testing.expectEqual(@as(usize, 15), contract.writable_windows[0].first_window_len);
    try std.testing.expectEqual(@as(usize, 7), contract.writable_windows[0].second_window_len);
    try std.testing.expect(contract.writable_windows[0].wraps);

    try std.testing.expectEqualStrings("wrapped_full_after_refill", contract.writable_windows[1].name);
    try std.testing.expectEqual(@as(usize, 4), contract.writable_windows[1].tail_index);
    try std.testing.expectEqual(@as(usize, 0), contract.writable_windows[1].writable_count);
    try std.testing.expectEqual(@as(usize, 0), contract.writable_windows[1].first_window_len);
    try std.testing.expectEqual(@as(usize, 0), contract.writable_windows[1].second_window_len);
    try std.testing.expect(!contract.writable_windows[1].wraps);

    try std.testing.expectEqualStrings("partial_drain_after_wrap_refill", contract.writable_windows[2].name);
    try std.testing.expectEqual(@as(usize, 1), contract.writable_windows[2].tail_index);
    try std.testing.expectEqual(@as(usize, 8), contract.writable_windows[2].writable_count);
    try std.testing.expectEqual(@as(usize, 8), contract.writable_windows[2].first_window_len);
    try std.testing.expectEqual(@as(usize, 0), contract.writable_windows[2].second_window_len);
    try std.testing.expect(!contract.writable_windows[2].wraps);
}
