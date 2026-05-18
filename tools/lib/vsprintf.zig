const std = @import("std");

pub const max_render_bytes: usize = 1024;

fn render(buffer: []u8, logical_size: usize, pad: bool, comptime fmt: []const u8, args: anytype) usize {
    if (buffer.len == 0) {
        return 0;
    }

    var scratch: [max_render_bytes]u8 = undefined;
    const rendered = std.fmt.bufPrint(&scratch, fmt, args) catch return 0;
    const bounded_size = @min(logical_size, buffer.len - 1);
    const limit = bounded_size;
    const copied = @min(rendered.len, limit);

    if (copied != 0) {
        @memcpy(buffer[0..copied], rendered[0..copied]);
    }

    if (pad and copied < limit) {
        @memset(buffer[copied..limit], ' ');
        buffer[limit] = 0;
        return limit;
    }

    buffer[copied] = 0;
    return copied;
}

pub fn vscnprintf(buffer: []u8, comptime fmt: []const u8, args: anytype) usize {
    return render(buffer, buffer.len -| 1, false, fmt, args);
}

pub fn scnprintf(buffer: []u8, comptime fmt: []const u8, args: anytype) usize {
    return render(buffer, buffer.len -| 1, false, fmt, args);
}

pub fn scnprintfPad(buffer: []u8, logical_size: usize, comptime fmt: []const u8, args: anytype) usize {
    return render(buffer, logical_size, true, fmt, args);
}

test "scnprintf truncates to buffer minus terminator" {
    var buffer: [8]u8 = undefined;
    const written = scnprintf(&buffer, "{s}:{d}", .{ "zigux", 7 });
    try std.testing.expectEqual(@as(usize, 7), written);
    try std.testing.expectEqualStrings("zigux:7", buffer[0..written]);
}

test "scnprintfPad pads the remaining bytes with spaces" {
    var buffer: [9]u8 = undefined;
    const written = scnprintfPad(&buffer, buffer.len - 1, "id={d}", .{7});
    try std.testing.expectEqual(@as(usize, 8), written);
    try std.testing.expectEqualStrings("id=7    ", buffer[0 .. buffer.len - 1]);
}

test "scnprintfPad returns zero for zero logical size" {
    var buffer = [_]u8{ 0xaa, 0xaa, 0xaa };
    const written = scnprintfPad(&buffer, 0, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqual(@as(u8, 0), buffer[0]);
}

test "scnprintfPad clamps oversized logical size to buffer minus terminator" {
    var buffer: [7]u8 = undefined;
    const written = scnprintfPad(&buffer, 64, "{s}", .{"id"});
    try std.testing.expectEqual(@as(usize, buffer.len - 1), written);
    try std.testing.expectEqualStrings("id    ", buffer[0 .. buffer.len - 1]);
    try std.testing.expectEqual(@as(u8, 0), buffer[buffer.len - 1]);
}

test "scnprintfPad truncates without adding padding when logical size is smaller than the rendered value" {
    var buffer: [8]u8 = undefined;
    const written = scnprintfPad(&buffer, 4, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 4), written);
    try std.testing.expectEqualStrings("zigu", buffer[0..written]);
    try std.testing.expectEqual(@as(u8, 0), buffer[written]);
}
