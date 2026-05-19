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
}

test "scnprintfPad returns zero for zero logical size" {
    var buffer = [_]u8{ 0xaa, 0xaa, 0xaa };
    const written = scnprintfPad(&buffer, 0, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqual(@as(u8, 0), buffer[0]);
}

test "scnprintfPad clears single-byte buffers even when logical size is larger" {
    var buffer = [_]u8{0xaa};
    const written = scnprintfPad(&buffer, 8, "{s}", .{"zigux"});
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

test "vscnprintf mirrors scnprintf truncation and terminates single-byte buffers" {
    var vscn_buffer: [6]u8 = undefined;
    var scn_buffer: [6]u8 = undefined;

    const vscn_written = vscnprintf(&vscn_buffer, "{s}", .{"zigux!"});
    const scn_written = scnprintf(&scn_buffer, "{s}", .{"zigux!"});

    try std.testing.expectEqual(scn_written, vscn_written);
    try std.testing.expectEqualStrings(scn_buffer[0..scn_written], vscn_buffer[0..vscn_written]);
    try std.testing.expectEqual(@as(u8, 0), vscn_buffer[vscn_written]);

    var tiny = [_]u8{0xaa};
    const tiny_written = vscnprintf(&tiny, "{s}", .{"zigux"});
    try std.testing.expectEqual(@as(usize, 0), tiny_written);
    try std.testing.expectEqual(@as(u8, 0), tiny[0]);
}

test "scnprintf clears the first byte when formatting overflows the scratch buffer" {
    const oversized = [_]u8{'x'} ** (max_render_bytes + 1);
    var buffer = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd };

    const written = scnprintf(&buffer, "{s}", .{oversized[0..]});
    try std.testing.expectEqual(@as(usize, 0), written);
    try std.testing.expectEqual(@as(u8, 0), buffer[0]);
}

test "vscnprintf and scnprintfPad also clear the first byte on scratch overflow" {
    const oversized = [_]u8{'x'} ** (max_render_bytes + 1);

    var vscn_buffer = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd };
    const vscn_written = vscnprintf(&vscn_buffer, "{s}", .{oversized[0..]});
    try std.testing.expectEqual(@as(usize, 0), vscn_written);
    try std.testing.expectEqual(@as(u8, 0), vscn_buffer[0]);

    var padded_buffer = [_]u8{ 0xaa, 0xbb, 0xcc, 0xdd };
    const padded_written = scnprintfPad(&padded_buffer, padded_buffer.len - 1, "{s}", .{oversized[0..]});
    try std.testing.expectEqual(@as(usize, 0), padded_written);
    try std.testing.expectEqual(@as(u8, 0), padded_buffer[0]);
}
