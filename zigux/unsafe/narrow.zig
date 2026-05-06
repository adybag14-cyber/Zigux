const std = @import("std");

pub fn addressOf(ptr: anytype) usize {
    return @intFromPtr(ptr);
}

pub fn byteOffset(base: usize, offset: usize) usize {
    return std.math.add(usize, base, offset) catch @panic("phase3 narrow unsafe byte offset overflow");
}

pub fn pointerAt(comptime T: type, base: usize, offset: usize) *volatile T {
    return @ptrFromInt(byteOffset(base, offset));
}

pub fn constSliceAt(comptime T: type, base: usize, len: usize) []const T {
    const ptr: [*]const T = @ptrFromInt(base);
    return ptr[0..len];
}

pub fn constPointerAt(comptime T: type, addr: usize) *const T {
    return @ptrFromInt(addr);
}

pub fn writeValueAt(comptime T: type, addr: usize, value: T) void {
    const ptr: *T = @ptrFromInt(addr);
    ptr.* = value;
}

test "phase3 narrow unsafe wrappers stay bounded" {
    try std.testing.expectEqual(@as(usize, 12), byteOffset(9, 3));
    try std.testing.expectEqual(std.math.maxInt(usize), byteOffset(std.math.maxInt(usize) - 4, 4));

    var value: u32 = 0;
    const base = addressOf(&value);
    const ptr = pointerAt(u32, base, 0);
    ptr.* = 11;
    try std.testing.expectEqual(@as(u32, 11), value);

    const slice = constSliceAt(u32, base, 1);
    try std.testing.expectEqual(@as(u32, 11), slice[0]);

    const const_ptr = constPointerAt(u32, base);
    try std.testing.expectEqual(@as(u32, 11), const_ptr.*);

    writeValueAt(u32, base, 19);
    try std.testing.expectEqual(@as(u32, 19), value);
}
