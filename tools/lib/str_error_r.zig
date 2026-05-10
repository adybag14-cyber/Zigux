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
