const std = @import("std");

pub const linux_anchor = "samples/kfifo/bytestream-example.c";
pub const fifo_capacity: usize = 32;

pub const VisibleWindow = struct {
    name: []const u8,
    head_index: usize,
    tail_index: usize,
    total_visible: usize,
    first_window_len: usize,
    second_window_len: usize,
    wraps: bool,
};

pub const WritableWindow = struct {
    name: []const u8,
    tail_index: usize,
    writable_count: usize,
    first_window_len: usize,
    second_window_len: usize,
    wraps: bool,
};

pub const WindowContract = struct {
    anchor: []const u8,
    capacity: usize,
    visible_windows: [3]VisibleWindow,
    writable_windows: [3]WritableWindow,
    preview_is_non_destructive: bool,
    wrapped_preview_is_non_destructive: bool,
    rollover_refill_required_for_wrap: bool,
    visible_windows_never_exceed_two: bool,
    writable_windows_never_exceed_two: bool,
};

pub fn referencePattern() WindowContract {
    const visible = [_]VisibleWindow{
        .{
            .name = "preview_after_skip_and_requeue",
            .head_index = 7,
            .tail_index = 17,
            .total_visible = 10,
            .first_window_len = 10,
            .second_window_len = 0,
            .wraps = false,
        },
        .{
            .name = "wrapped_full_after_refill",
            .head_index = 4,
            .tail_index = 4,
            .total_visible = fifo_capacity,
            .first_window_len = 28,
            .second_window_len = 4,
            .wraps = true,
        },
        .{
            .name = "partial_drain_after_wrap_refill",
            .head_index = 9,
            .tail_index = 1,
            .total_visible = 24,
            .first_window_len = 23,
            .second_window_len = 1,
            .wraps = true,
        },
    };

    const writable = [_]WritableWindow{
        .{
            .name = "preview_after_skip_and_requeue",
            .tail_index = 17,
            .writable_count = 22,
            .first_window_len = 15,
            .second_window_len = 7,
            .wraps = true,
        },
        .{
            .name = "wrapped_full_after_refill",
            .tail_index = 4,
            .writable_count = 0,
            .first_window_len = 0,
            .second_window_len = 0,
            .wraps = false,
        },
        .{
            .name = "partial_drain_after_wrap_refill",
            .tail_index = 1,
            .writable_count = 8,
            .first_window_len = 8,
            .second_window_len = 0,
            .wraps = false,
        },
    };

    return .{
        .anchor = linux_anchor,
        .capacity = fifo_capacity,
        .visible_windows = visible,
        .writable_windows = writable,
        .preview_is_non_destructive = true,
        .wrapped_preview_is_non_destructive = true,
        .rollover_refill_required_for_wrap = !visible[0].wraps and visible[1].wraps and visible[2].wraps,
        .visible_windows_never_exceed_two = visibleWindowsNeverExceedTwo(visible),
        .writable_windows_never_exceed_two = writableWindowsNeverExceedTwo(writable),
    };
}

fn visibleWindowsNeverExceedTwo(windows: [3]VisibleWindow) bool {
    inline for (windows) |window| {
        if (window.first_window_len + window.second_window_len != window.total_visible) return false;
        if (!window.wraps and window.second_window_len != 0) return false;
        if (window.wraps and window.second_window_len == 0) return false;
    }
    return true;
}

fn writableWindowsNeverExceedTwo(windows: [3]WritableWindow) bool {
    inline for (windows) |window| {
        if (window.first_window_len + window.second_window_len != window.writable_count) return false;
        if (!window.wraps and window.second_window_len != 0) return false;
        if (window.wraps and window.second_window_len == 0) return false;
    }
    return true;
}

test "bytestream fifo companion keeps the two-window kfifo contract explicit" {
    const contract = referencePattern();

    try std.testing.expectEqualStrings("samples/kfifo/bytestream-example.c", contract.anchor);
    try std.testing.expectEqual(@as(usize, fifo_capacity), contract.capacity);
    try std.testing.expect(contract.preview_is_non_destructive);
    try std.testing.expect(contract.wrapped_preview_is_non_destructive);
    try std.testing.expect(contract.rollover_refill_required_for_wrap);
    try std.testing.expect(contract.visible_windows_never_exceed_two);
    try std.testing.expect(contract.writable_windows_never_exceed_two);

    try std.testing.expectEqualStrings("preview_after_skip_and_requeue", contract.visible_windows[0].name);
    try std.testing.expectEqualStrings("wrapped_full_after_refill", contract.visible_windows[1].name);
    try std.testing.expectEqualStrings("partial_drain_after_wrap_refill", contract.visible_windows[2].name);

    try std.testing.expectEqual(@as(usize, 7), contract.visible_windows[0].head_index);
    try std.testing.expectEqual(@as(usize, 17), contract.visible_windows[0].tail_index);
    try std.testing.expectEqual(@as(usize, 10), contract.visible_windows[0].total_visible);
    try std.testing.expectEqual(@as(usize, 10), contract.visible_windows[0].first_window_len);
    try std.testing.expectEqual(@as(usize, 0), contract.visible_windows[0].second_window_len);
    try std.testing.expect(!contract.visible_windows[0].wraps);

    try std.testing.expectEqual(@as(usize, 4), contract.visible_windows[1].head_index);
    try std.testing.expectEqual(@as(usize, 4), contract.visible_windows[1].tail_index);
    try std.testing.expectEqual(@as(usize, fifo_capacity), contract.visible_windows[1].total_visible);
    try std.testing.expectEqual(@as(usize, 28), contract.visible_windows[1].first_window_len);
    try std.testing.expectEqual(@as(usize, 4), contract.visible_windows[1].second_window_len);
    try std.testing.expect(contract.visible_windows[1].wraps);

    try std.testing.expectEqual(@as(usize, 9), contract.visible_windows[2].head_index);
    try std.testing.expectEqual(@as(usize, 1), contract.visible_windows[2].tail_index);
    try std.testing.expectEqual(@as(usize, 24), contract.visible_windows[2].total_visible);
    try std.testing.expectEqual(@as(usize, 23), contract.visible_windows[2].first_window_len);
    try std.testing.expectEqual(@as(usize, 1), contract.visible_windows[2].second_window_len);
    try std.testing.expect(contract.visible_windows[2].wraps);
}

test "bytestream fifo companion keeps wrapped visibility and writable-span shapes separate" {
    const contract = referencePattern();

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
