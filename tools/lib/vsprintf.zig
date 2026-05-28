const std = @import("std");

pub const max_render_bytes: usize = 1024;

fn render(buffer: []u8, logical_size: usize, pad: bool, comptime fmt: []const u8, args: anytype) usize {
    if (buffer.len == 0) {
        return 0;
    }

    var scratch: [max_render_bytes]u8 = undefined;
    const rendered = std.fmt.bufPrint(&scratch, fmt, args) catch {
        buffer[0] = 0;
        return 0;
    };
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
    try std.testing.expectEqual(@as(u8, 0), buffer[8]);
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
    var buffer = [_]u8{0xcc} ** 6;
    const written = scnprintfPad(&buffer, 32, "{s}", .{"ab"});

    try std.testing.expectEqual(@as(usize, 5), written);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 'a', 'b', ' ', ' ', ' ', 0 }, &buffer);
}

test "scnprintfPad handles zero logical size and zero-length caller views" {
    var zero_logical = [_]u8{0xdd} ** 4;
    const zero_written = scnprintfPad(&zero_logical, 0, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), zero_written);
    try std.testing.expectEqual(@as(u8, 0), zero_logical[0]);
    try std.testing.expectEqualSlices(u8, &[_]u8{ 0, 0xdd, 0xdd, 0xdd }, &zero_logical);

    var backing = [_]u8{0xee};
    const empty_written = scnprintfPad(backing[0..0], 4, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), empty_written);
    try std.testing.expectEqual(@as(u8, 0xee), backing[0]);
}

test "scnprintf clears the caller buffer when formatting exceeds scratch capacity" {
    var buffer = [_]u8{0xaa} ** 8;
    const written = scnprintf(&buffer, "{s}", .{&([_]u8{'x'} ** (max_render_bytes + 1))});

    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqual(@as(u8, 0), buffer[0]);
    try std.testing.expectEqual(@as(u8, 0xaa), buffer[1]);
}
