const std = @import("std");
const sample = @import("bytestream_fifo.zig");

pub const linux_anchor = "samples/kfifo/bytestream-example.c";
pub const fifo_capacity: usize = 32;

pub const WindowCheckpoint = enum {
    preview_after_skip_and_requeue,
    wrapped_full_after_refill,
    partial_drain_after_wrap_refill,
};

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

pub fn checkpointName(checkpoint: WindowCheckpoint) []const u8 {
    return switch (checkpoint) {
        .preview_after_skip_and_requeue => "preview_after_skip_and_requeue",
        .wrapped_full_after_refill => "wrapped_full_after_refill",
        .partial_drain_after_wrap_refill => "partial_drain_after_wrap_refill",
    };
}

pub fn referencePattern() WindowContract {
    const visible = [_]VisibleWindow{
        .{
            .name = checkpointName(.preview_after_skip_and_requeue),
            .head_index = 7,
            .tail_index = 17,
            .total_visible = 10,
            .first_window_len = 10,
            .second_window_len = 0,
            .wraps = false,
        },
        .{
            .name = checkpointName(.wrapped_full_after_refill),
            .head_index = 4,
            .tail_index = 4,
            .total_visible = fifo_capacity,
            .first_window_len = 28,
            .second_window_len = 4,
            .wraps = true,
        },
        .{
            .name = checkpointName(.partial_drain_after_wrap_refill),
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
            .name = checkpointName(.preview_after_skip_and_requeue),
            .tail_index = 17,
            .writable_count = 22,
            .first_window_len = 15,
            .second_window_len = 7,
            .wraps = true,
        },
        .{
            .name = checkpointName(.wrapped_full_after_refill),
            .tail_index = 4,
            .writable_count = 0,
            .first_window_len = 0,
            .second_window_len = 0,
            .wraps = false,
        },
        .{
            .name = checkpointName(.partial_drain_after_wrap_refill),
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

pub fn visibleWindowForCheckpoint(checkpoint: WindowCheckpoint) VisibleWindow {
    return referencePattern().visible_windows[@intFromEnum(checkpoint)];
}

pub fn writableWindowForCheckpoint(checkpoint: WindowCheckpoint) WritableWindow {
    return referencePattern().writable_windows[@intFromEnum(checkpoint)];
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

fn expectVisibleWindowMatches(actual: sample.VisibleSpanSummary, expected: VisibleWindow) !void {
    try std.testing.expectEqual(expected.head_index, actual.head_index);
    try std.testing.expectEqual(expected.tail_index, actual.tail_index);
    try std.testing.expectEqual(expected.total_visible, actual.total_visible);
    try std.testing.expectEqual(expected.first_window_len, actual.first_window_len);
    try std.testing.expectEqual(expected.second_window_len, actual.second_window_len);
    try std.testing.expectEqual(expected.wraps, actual.wraps);
}

fn expectWritableWindowMatches(actual: sample.WritableSpanSummary, expected: WritableWindow) !void {
    try std.testing.expectEqual(expected.tail_index, actual.tail_index);
    try std.testing.expectEqual(expected.writable_count, actual.writable_count);
    try std.testing.expectEqual(expected.first_window_len, actual.first_window_len);
    try std.testing.expectEqual(expected.second_window_len, actual.second_window_len);
    try std.testing.expectEqual(expected.wraps, actual.wraps);
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

test "bytestream fifo companion keeps checkpoint lookups aligned with the shipped window contract" {
    const preview_visible = visibleWindowForCheckpoint(.preview_after_skip_and_requeue);
    const wrapped_visible = visibleWindowForCheckpoint(.wrapped_full_after_refill);
    const partial_visible = visibleWindowForCheckpoint(.partial_drain_after_wrap_refill);

    try std.testing.expectEqualStrings(checkpointName(.preview_after_skip_and_requeue), preview_visible.name);
    try std.testing.expectEqualStrings(checkpointName(.wrapped_full_after_refill), wrapped_visible.name);
    try std.testing.expectEqualStrings(checkpointName(.partial_drain_after_wrap_refill), partial_visible.name);
    try std.testing.expectEqual(@as(usize, 10), preview_visible.total_visible);
    try std.testing.expectEqual(@as(usize, fifo_capacity), wrapped_visible.total_visible);
    try std.testing.expectEqual(@as(usize, 24), partial_visible.total_visible);

    const preview_writable = writableWindowForCheckpoint(.preview_after_skip_and_requeue);
    const wrapped_writable = writableWindowForCheckpoint(.wrapped_full_after_refill);
    const partial_writable = writableWindowForCheckpoint(.partial_drain_after_wrap_refill);

    try std.testing.expectEqualStrings(checkpointName(.preview_after_skip_and_requeue), preview_writable.name);
    try std.testing.expectEqualStrings(checkpointName(.wrapped_full_after_refill), wrapped_writable.name);
    try std.testing.expectEqualStrings(checkpointName(.partial_drain_after_wrap_refill), partial_writable.name);
    try std.testing.expectEqual(@as(usize, 22), preview_writable.writable_count);
    try std.testing.expectEqual(@as(usize, 0), wrapped_writable.writable_count);
    try std.testing.expectEqual(@as(usize, 8), partial_writable.writable_count);

    try std.testing.expectEqualStrings(sample.BytestreamFifoSample.descriptor().anchor, linux_anchor);

    var module = sample.BytestreamFifoSample{};
    try module.init();

    const preview = try module.runPreviewBoundaryReplay();
    try expectVisibleWindowMatches(preview.visible_span_after_preview, preview_visible);
    try expectWritableWindowMatches(module.writableSpanSummary(), preview_writable);
    try std.testing.expect(!module.usesWrappedStorageWindow());

    const wrapped = try module.runWrappedPreviewReplay();
    try expectVisibleWindowMatches(wrapped.visible_span_after_preview, wrapped_visible);
    try expectWritableWindowMatches(module.writableSpanSummary(), wrapped_writable);
    try std.testing.expect(module.usesWrappedStorageWindow());

    const remaining = try module.runRemainingCapacityReplay();
    try expectVisibleWindowMatches(remaining.visible_span_after_partial_drain, partial_visible);
    try expectWritableWindowMatches(module.writableSpanSummary(), partial_writable);
    try std.testing.expect(module.usesWrappedStorageWindow());
}
