// SPDX-License-Identifier: GPL-2.0
const std = @import("std");

pub fn errname(err: i32) ?[]const u8 {
    return switch (err) {
        1 => "EPERM",
        -1 => "-EPERM",
        2 => "ENOENT",
        -2 => "-ENOENT",
        5 => "EIO",
        -5 => "-EIO",
        11 => "EAGAIN",
        -11 => "-EAGAIN",
        12 => "ENOMEM",
        -12 => "-ENOMEM",
        13 => "EACCES",
        -13 => "-EACCES",
        16 => "EBUSY",
        -16 => "-EBUSY",
        17 => "EEXIST",
        -17 => "-EEXIST",
        19 => "ENODEV",
        -19 => "-ENODEV",
        22 => "EINVAL",
        -22 => "-EINVAL",
        28 => "ENOSPC",
        -28 => "-ENOSPC",
        32 => "EPIPE",
        -32 => "-EPIPE",
        34 => "ERANGE",
        -34 => "-ERANGE",
        95 => "EOPNOTSUPP",
        -95 => "-EOPNOTSUPP",
        110 => "ETIMEDOUT",
        -110 => "-ETIMEDOUT",
        512 => "ERESTARTSYS",
        -512 => "-ERESTARTSYS",
        517 => "EPROBE_DEFER",
        -517 => "-EPROBE_DEFER",
        else => null,
    };
}

pub fn errnameUnsigned(err: u32) ?[]const u8 {
    if (err > @as(u32, @intCast(std.math.maxInt(i32)))) return null;
    return errname(@intCast(err));
}

test "errname follows positive and negative Linux spellings" {
    try std.testing.expectEqualStrings("EINVAL", errname(22).?);
    try std.testing.expectEqualStrings("-EINVAL", errname(-22).?);
    try std.testing.expectEqualStrings("EIO", errname(5).?);
    try std.testing.expectEqualStrings("-ENOMEM", errname(-12).?);
    try std.testing.expectEqualStrings("EPROBE_DEFER", errname(517).?);
    try std.testing.expect(errname(0) == null);
    try std.testing.expect(errname(9999) == null);
}
