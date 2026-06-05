const std = @import("std");

fn copyMessage(buffer: []u8, message: []const u8) []const u8 {
    if (buffer.len == 0) {
        return buffer[0..0];
    }

    const count = @min(message.len, buffer.len - 1);
    if (count != 0) {
        @memcpy(buffer[0..count], message[0..count]);
    }
    buffer[count] = 0;
    return buffer[0..count];
}

fn knownMessage(errnum: i32) ?[]const u8 {
    return switch (errnum) {
        0 => "Success",
        2 => "No such file or directory",
        12 => "Cannot allocate memory",
        13 => "Permission denied",
        22 => "Invalid argument",
        else => null,
    };
}

pub fn strErrorR(errnum: i32, buffer: []u8) []const u8 {
    if (knownMessage(errnum)) |message| {
        return copyMessage(buffer, message);
    }

    var scratch: [64]u8 = undefined;
    const rendered = std.fmt.bufPrint(
        &scratch,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ errnum, buffer.len },
    ) catch "INTERNAL ERROR: strerror_r failed";
    return copyMessage(buffer, rendered);
}

test "strErrorR returns deterministic Linux-style messages" {
    var buffer: [64]u8 = undefined;
    try std.testing.expectEqualStrings("No such file or directory", strErrorR(2, &buffer));
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 64)=22", strErrorR(4096, &buffer));
}

test "strErrorR accepts zero-length caller buffers for known and fallback messages" {
    var empty = [_]u8{};
    try std.testing.expectEqual(@as(usize, 0), strErrorR(13, empty[0..]).len);
    try std.testing.expectEqual(@as(usize, 0), strErrorR(4096, empty[0..]).len);
}

test "strErrorR truncates known and synthesized messages with a trailing terminator" {
    var known: [8]u8 = @splat(0xaa);
    const known_rendered = strErrorR(13, &known);
    try std.testing.expectEqualStrings("Permiss", known_rendered);
    try std.testing.expectEqual(@as(u8, 0), known[7]);

    var fallback: [8]u8 = @splat(0xbb);
    const fallback_rendered = strErrorR(4096, &fallback);
    try std.testing.expectEqualStrings("INTERNA", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0), fallback[7]);
}

test "strErrorR preserves exact-fit caller terminators and surrounding bytes" {
    var known: [20]u8 = @splat(0xaa);
    const known_window = known[2..19];
    const known_rendered = strErrorR(22, known_window);
    try std.testing.expectEqualStrings("Invalid argument", known_rendered);
    try std.testing.expectEqual(@as(u8, 0xaa), known[0]);
    try std.testing.expectEqual(@as(u8, 0xaa), known[1]);
    try std.testing.expectEqual(@as(u8, 0), known[18]);
    try std.testing.expectEqual(@as(u8, 0xaa), known[19]);

    var fallback: [52]u8 = @splat(0xbb);
    const fallback_window = fallback[3..50];
    const fallback_rendered = strErrorR(4096, fallback_window);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 47)=22", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback[0]);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback[1]);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback[2]);
    try std.testing.expectEqual(@as(u8, 0), fallback[49]);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback[50]);
    try std.testing.expectEqual(@as(u8, 0xbb), fallback[51]);
}

test "strErrorR rewrites reused caller buffers with a fresh terminator" {
    var buffer: [48]u8 = @splat(0xcc);

    const fallback_rendered = strErrorR(4096, &buffer);
    try std.testing.expectEqualStrings("INTERNAL ERROR: strerror_r(4096, [buf], 48)=22", fallback_rendered);
    try std.testing.expectEqual(@as(u8, 0), buffer[fallback_rendered.len]);

    const known_rendered = strErrorR(0, &buffer);
    try std.testing.expectEqualStrings("Success", known_rendered);
    try std.testing.expectEqual(@as(u8, 0), buffer[known_rendered.len]);
    try std.testing.expectEqual(@as(u8, ' '), buffer[known_rendered.len + 1]);
}
