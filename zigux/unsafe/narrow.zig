const std = @import("std");

pub fn addressOf(ptr: anytype) usize {
    return @intFromPtr(ptr);
}

pub fn byteOffset(base: usize, offset: usize) usize {
    return base + offset;
}

pub fn pointerAt(comptime T: type, base: usize, offset: usize) *volatile T {
    return @ptrFromInt(byteOffset(base, offset));
}

test "phase3 narrow unsafe wrappers stay bounded" {
    var value: u32 = 0;
    const base = addressOf(&value);
    const ptr = pointerAt(u32, base, 0);
    ptr.* = 11;
    try std.testing.expectEqual(@as(u32, 11), value);
}
