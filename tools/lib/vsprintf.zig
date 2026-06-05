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

test "vscnprintf mirrors scnprintf across truncated caller buffers" {
    var direct = [_]u8{ 0xaa, 0xaa, 0xaa, 0xaa, 0xaa };
    var alias = [_]u8{ 0xbb, 0xbb, 0xbb, 0xbb, 0xbb };

    const direct_written = scnprintf(&direct, "{s}", .{"host-tools"});
    const alias_written = vscnprintf(&alias, "{s}", .{"host-tools"});

    try std.testing.expectEqual(direct_written, alias_written);
    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqualStrings(direct[0..direct_written], alias[0..alias_written]);
    try std.testing.expectEqual(@as(u8, 0), direct[direct_written]);
    try std.testing.expectEqual(@as(u8, 0), alias[alias_written]);
}

test "scnprintfPad clamps logical size to the caller buffer and preserves a terminator slot" {
    var buffer: [6]u8 = @splat(0xcc);
    const written = scnprintfPad(&buffer, 32, "{s}", .{"ab"});

    try std.testing.expectEqual(@as(usize, 5), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ' ', ' ', ' ', 0 }, &buffer);
}

test "scnprintfPad handles zero logical size and zero-length caller views" {
    var zero_logical: [4]u8 = @splat(0xdd);
    const zero_written = scnprintfPad(&zero_logical, 0, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), zero_written);
    try std.testing.expectEqual(@as(u8, 0), zero_logical[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0xdd, 0xdd, 0xdd }, &zero_logical);

    var backing = [_]u8{0xee};
    const empty_written = scnprintfPad(backing[0..0], 4, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqual(@as(u8, 0xee), backing[0]);
}

test "scnprintf and vscnprintf keep caller subview sentinels outside exact-fit windows" {
    var direct = [_]u8{
        0xa1, 0xa2, 0xa3, 0xa4,
        0xa5, 0xa6, 0xa7, 0xa8,
        0xa9, 0xaa,
    };
    var alias = [_]u8{
        0xb1, 0xb2, 0xb3, 0xb4,
        0xb5, 0xb6, 0xb7, 0xb8,
        0xb9, 0xba,
    };

    const direct_written = scnprintf(direct[2..7], "{s}", .{"core"});
    const alias_written = vscnprintf(alias[3..8], "{s}", .{"port"});

    try std.testing.expectEqual(@as(usize, 4), direct_written);
    try std.testing.expectEqual(@as(usize, 4), alias_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa1, 0xa2 }, direct[0..2]);
    try std.testing.expectEqualSlices(u8, "core", direct[2..6]);
    try std.testing.expectEqual(@as(u8, 0), direct[6]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa8, 0xa9, 0xaa }, direct[7..10]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xb1, 0xb2, 0xb3 }, alias[0..3]);
    try std.testing.expectEqualSlices(u8, "port", alias[3..7]);
    try std.testing.expectEqual(@as(u8, 0), alias[7]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xb9, 0xba }, alias[8..10]);
}

test "scnprintfPad reports full padded subview length while preserving sentinels" {
    var backing = [_]u8{
        0xc1, 0xc2, 0xc3, 0xc4,
        0xc5, 0xc6, 0xc7, 0xc8,
        0xc9, 0xca,
    };

    const window = backing[2..8];
    const written = scnprintfPad(window, 5, "{s}", .{"io"});

    try std.testing.expectEqual(@as(usize, 5), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xc1, 0xc2 }, backing[0..2]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'i', 'o', ' ', ' ', ' ', 0 }, backing[2..8]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xc9, 0xca }, backing[8..10]);
}

test "oversized renders return zero and leave caller buffers unchanged" {
    const too_wide = "x" ** (max_render_bytes + 1);

    var direct = [_]u8{ 0xa1, 0xa2, 0xa3, 0xa4 };
    var alias = [_]u8{ 0xb1, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6 };
    var padded = [_]u8{ 0xc1, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8 };

    const direct_written = scnprintf(&direct, "{s}", .{too_wide});
    const alias_written = vscnprintf(alias[1..5], "{s}", .{too_wide});
    const padded_written = scnprintfPad(padded[2..7], 4, "{s}", .{too_wide});

    try std.testing.expectEqual(@as(usize, 0), direct_written);
    try std.testing.expectEqual(@as(usize, 0), alias_written);
    try std.testing.expectEqual(@as(usize, 0), padded_written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xa1, 0xa2, 0xa3, 0xa4 }, &direct);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xb1, 0xb2, 0xb3, 0xb4, 0xb5, 0xb6 }, &alias);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0xc1, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8 }, &padded);
}
