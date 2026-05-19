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

test "strErrorR truncates known messages and keeps a terminator" {
    var buffer: [6]u8 = undefined;
    const rendered = strErrorR(0, &buffer);
    try std.testing.expectEqualStrings("Succe", rendered);
    try std.testing.expectEqual(@as(u8, 0), buffer[5]);
}

test "strErrorR truncates generated internal errors and keeps a terminator" {
    var buffer: [12]u8 = undefined;
    const rendered = strErrorR(4096, &buffer);

    var expected_storage: [64]u8 = undefined;
    const full = try std.fmt.bufPrint(
        &expected_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 4096, buffer.len },
    );

    try std.testing.expectEqualStrings(full[0 .. buffer.len - 1], rendered);
    try std.testing.expectEqual(@as(u8, 0), buffer[buffer.len - 1]);
}

test "strErrorR handles empty and single-byte buffers without exposing bytes" {
    var empty: [0]u8 = undefined;
    try std.testing.expectEqualStrings("", strErrorR(2, &empty));

    var tiny = [_]u8{0xaa};
    const rendered = strErrorR(4096, &tiny);
    try std.testing.expectEqualStrings("", rendered);
    try std.testing.expectEqual(@as(u8, 0), tiny[0]);
}

test "strErrorR returns full messages when buffers fit exactly" {
    var success_buffer: [8]u8 = undefined;
    const success_rendered = strErrorR(0, &success_buffer);
    try std.testing.expectEqualStrings("Success", success_rendered);
    try std.testing.expectEqual(@as(u8, 0), success_buffer[success_rendered.len]);

    var internal_storage: [64]u8 = undefined;
    const expected_internal = try std.fmt.bufPrint(
        &internal_storage,
        "INTERNAL ERROR: strerror_r({d}, [buf], {d})=22",
        .{ 4096, 48 },
    );

    var exact_buffer: [48]u8 = undefined;
    const exact_rendered = strErrorR(4096, &exact_buffer);
    try std.testing.expectEqualStrings(expected_internal, exact_rendered);
    try std.testing.expectEqual(@as(u8, 0), exact_buffer[exact_rendered.len]);
}
